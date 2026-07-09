"""Link / reference integrity checker — Layer 3 dumb tool #1.

Job: scan vault notes for [[wikilinks]], [markdown](links), and plain
file/path references; check each for existence; emit
`_DERIVED/broken_links.md`. Flags only — never fixes, never edits source.

Domain-agnostic. No LLM. No embeddings. Regenerates from source each run.
Deterministic output (byte-identical when vault state is unchanged).

Authority: TASK_017, _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md §3.1.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
import traceback
from collections import Counter, defaultdict
from urllib.parse import unquote

from capture_integrity_checker import frontmatter, note_can_be_loud, starts_with_prefix


# ----- Defaults (config can override) ----------------------------------------

DEFAULT_CONFIG_PATH = pathlib.Path(__file__).parent / "link_reference_checker.config.json"

BASELINE_BROKEN_REFERENCES = 1382
BASELINE_AMBIGUOUS_REFERENCES = 24
BASELINE_EXTERNAL_LOCAL_REFERENCES = 37
SUPPORTED_VAULT_INDEX_SCHEMA = 1

VAULT_EXTENSIONS = {
    ".md", ".txt", ".py", ".json", ".csv", ".html",
    ".bat", ".cs", ".ps1", ".toml", ".yaml", ".yml",
}

YAML_PATH_FIELDS = {
    "home", "related", "source_artifact", "source", "implementation",
    "canonical_spec", "related_paths", "related_probes", "related_candidates",
}


# ----- Regex -----------------------------------------------------------------

# Wikilink: [[target]], [[target|alias]], [[target#heading]], [[target#heading|alias]]
WIKILINK_RE = re.compile(r"\[\[([^\]\[\n]+?)\]\]")

# Markdown link: [label](target) or [label](<target with spaces>)
MDLINK_RE = re.compile(r"\[([^\]\n]*?)\]\(\s*<?([^)>\n]+?)>?\s*\)")

# Backtick-delimited tokens
BACKTICK_RE = re.compile(r"`([^`\n]+?)`")

# YAML frontmatter
YAML_FENCE_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

# Date/version look-alikes (avoid path-extraction false positives)
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}")
VERSION_PREFIX_RE = re.compile(r"^v?\d+\.\d+(?:\.\d+)?$")
SEMVER_FULL_RE = re.compile(r"^v?\d+\.\d+\.\d+([+\-].+)?$")


# ----- Helpers ---------------------------------------------------------------

def is_external_url(s: str) -> bool:
    return s.startswith(("http://", "https://", "mailto:", "tel:",
                          "ftp://", "ftps://", "file://", "ws://", "wss://"))


def is_windows_absolute(s: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[/\\]", s))


def normalize_target(target: str) -> str:
    """Strip fragment+query, URL-decode, normalize slashes, strip whitespace."""
    if not target: return ""
    s = target.strip()
    # Strip angle brackets if present
    if s.startswith("<") and s.endswith(">"):
        s = s[1:-1]
    # Strip query then fragment
    s = s.split("?", 1)[0]
    s = s.split("#", 1)[0]
    try:
        s = unquote(s)
    except Exception:
        pass
    return s.strip()


def looks_like_path(token: str) -> bool:
    """Conservative filter for plain-path extraction."""
    if not token: return False
    s = token.strip()
    if not s: return False
    if is_external_url(s): return False
    if s.startswith("#"): return False
    if any(c in s for c in ["\n", "\r", "\t"]): return False
    # Reject glob-style patterns in prose: "*.md", "foo*", "x_YYYYMMDD_*.txt"
    if "*" in s or "?" in s: return False
    # Reject pure date/version strings
    if DATE_PREFIX_RE.match(s) and "/" not in s and "\\" not in s: return False
    if VERSION_PREFIX_RE.match(s): return False
    if SEMVER_FULL_RE.match(s): return False
    # Reject obvious code/CLI snippets
    if s.startswith(("$", ">", "$(", "pip ", "python ", "git ", "npm ",
                      "ls ", "cd ", "echo ", "cat ", "sudo ", "&&", "||")):
        return False
    if " " in s and not (s.endswith("/") or s.endswith("\\")):
        # Whitespace inside often means it's not a single path token; allow
        # only if it starts looking like a Windows abs path with a space.
        if not is_windows_absolute(s):
            return False
    has_slash = ("/" in s) or ("\\" in s)
    name = s.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    has_ext = any(name.lower().endswith(ext) for ext in VAULT_EXTENSIONS)
    return has_slash or has_ext


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def strip_locator_suffix(target: str) -> str:
    """Strip path locators such as `file.py:37-46` or `file.py::symbol`."""
    return re.sub(r"(?::\d+(?:[-–]\d+)?|::[A-Za-z_][A-Za-z0-9_]*)$", "", target)


def line_text(text: str, line_number: int) -> str:
    lines = text.splitlines()
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return ""


def fenced_code_ranges(text: str) -> list[tuple[int, int]]:
    """Return byte/char offset ranges for fenced code blocks."""
    ranges = []
    fence_start = None
    offset = 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            if fence_start is None:
                fence_start = offset
            else:
                ranges.append((fence_start, offset + len(line)))
                fence_start = None
        offset += len(line)
    if fence_start is not None:
        ranges.append((fence_start, len(text)))
    return ranges


def offset_in_ranges(offset: int | None, ranges: list[tuple[int, int]]) -> bool:
    if offset is None:
        return False
    return any(start <= offset < end for start, end in ranges)


def matches_any_glob(rel_posix: str, globs: list[str]) -> bool:
    rel = rel_posix.replace("\\", "/")
    for g in globs:
        gnorm = g.replace("\\", "/")
        if fnmatch.fnmatch(rel, gnorm) or fnmatch.fnmatch(rel + "/", gnorm):
            return True
    return False


def starts_with_any(value: str, prefixes: list[str]) -> bool:
    normalized = value.replace("/", "\\")
    for prefix in prefixes:
        if value.startswith(prefix) or normalized.startswith(prefix.replace("/", "\\")):
            return True
    return False


# ----- Loading + iteration ---------------------------------------------------

def load_config(path: pathlib.Path) -> dict:
    if not path.exists():
        print(f"config not found: {path}", file=sys.stderr)
        sys.exit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def source_role(source_rel: str, fm: dict[str, str], severity_config: dict) -> str:
    """Classify source role with the capture-integrity role/status doctrine."""
    if starts_with_prefix(source_rel, severity_config.get("informational_path_prefixes", [])):
        return "informational"
    if starts_with_prefix(source_rel, severity_config.get("loud_path_prefixes", [])):
        return "loud_path"
    loud_statuses = {s.lower() for s in severity_config.get("loud_statuses", [])}
    note_status = fm.get("status", "").lower()
    note_type = fm.get("type", "").lower()
    if note_status in loud_statuses or any(
        s in note_type for s in ("verdict", "decision", "canonical", "living")
    ):
        return "status_loud"
    return "regular"


def row_severity(status: str, source_rel: str, fm: dict[str, str], severity_config: dict) -> str:
    if status == "suppressed":
        return "INFO"
    if status == "external_local_documented":
        return "INFO"
    if status in {"broken", "external_local_missing"} and note_can_be_loud(source_rel, fm, severity_config):
        return "LOUD"
    return "PLAIN"


def iter_scan_files(vault_root: pathlib.Path, ignore_globs, include_txt: bool):
    """Yield paths to scan, deterministic order (sorted by rel-posix-path)."""
    exts = {".md"}
    if include_txt:
        exts.add(".txt")
    results = []
    for root, dirs, files in os.walk(vault_root):
        rel_root = pathlib.Path(root).relative_to(vault_root).as_posix()
        # Filter dirs in-place
        kept = []
        for d in dirs:
            rel = (pathlib.Path(rel_root) / d).as_posix() if rel_root != "." else d
            ignored = False
            for g in ignore_globs:
                gnorm = g.replace("\\", "/")
                if fnmatch.fnmatch(rel, gnorm) or fnmatch.fnmatch(rel + "/", gnorm):
                    ignored = True
                    break
                # Also check the bare dir name (e.g. ".git" anywhere)
                if "/" not in gnorm and not gnorm.endswith("/*"):
                    if d == gnorm:
                        ignored = True
                        break
            if not ignored:
                kept.append(d)
        dirs[:] = sorted(kept)
        for f in sorted(files):
            ext = pathlib.Path(f).suffix.lower()
            if ext not in exts:
                continue
            rel = (pathlib.Path(rel_root) / f).as_posix() if rel_root != "." else f
            results.append((vault_root / rel))
    return results


def build_basename_index(files):
    """basename -> list of absolute paths. Sorted for determinism."""
    idx = defaultdict(list)
    for f in files:
        idx[f.name].append(f)
    return {k: sorted(v) for k, v in idx.items()}


def load_vault_index(vault_root: pathlib.Path, index_rel: str):
    index_path = (vault_root / index_rel).resolve()
    if not index_path.exists():
        raise FileNotFoundError(
            f"vault index missing: {index_path}. Run tools/wiki_deriver/build_vault_index.py first."
        )
    data = json.loads(index_path.read_text(encoding="utf-8"))
    schema = data.get("schema_version")
    if schema != SUPPORTED_VAULT_INDEX_SCHEMA:
        print(
            f"warning: vault index schema_version={schema}; "
            f"checker expects {SUPPORTED_VAULT_INDEX_SCHEMA}",
            file=sys.stderr,
        )
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"vault index has no entries list: {index_path}")
    idx = defaultdict(list)
    for entry in entries:
        rel = entry.get("path")
        basename = entry.get("basename")
        if not rel or not basename:
            continue
        idx[basename].append(vault_root / rel)
    return {k: sorted(v) for k, v in idx.items()}, data


# ----- Extractors ------------------------------------------------------------

def extract_wikilinks(text):
    """Yield (line, kind, raw_match, raw_target_stripped, alias)."""
    for m in WIKILINK_RE.finditer(text):
        inner = m.group(1).strip()
        if not inner:
            continue
        # alias split
        if "|" in inner:
            target_part, alias = inner.rsplit("|", 1)
        else:
            target_part, alias = inner, None
        # heading split (don't drop yet; signal in-note if pure heading)
        if target_part.startswith("#"):
            # in-note heading link
            continue
        # strip heading fragment from target_part
        target_only = target_part.split("#", 1)[0].strip()
        if not target_only:
            continue
        line = line_no(text, m.start())
        yield {
            "line": line,
            "offset": m.start(),
            "kind": "wikilink",
            "raw_match": m.group(0),
            "raw_target": target_part.strip(),
            "target": target_only,
        }


def extract_mdlinks(text):
    for m in MDLINK_RE.finditer(text):
        target = m.group(2).strip()
        if not target:
            continue
        if is_external_url(target):
            continue
        # Pure anchor
        if target.startswith("#"):
            continue
        norm = normalize_target(target)
        if not norm:
            continue
        line = line_no(text, m.start())
        yield {
            "line": line,
            "offset": m.start(),
            "kind": "markdown_link",
            "raw_match": m.group(0),
            "raw_target": target,
            "target": norm,
        }


def extract_backtick_paths(text):
    """Conservative: backtick token must look like a path."""
    for m in BACKTICK_RE.finditer(text):
        token = m.group(1).strip()
        if not looks_like_path(token):
            continue
        if is_external_url(token):
            continue
        norm = normalize_target(token)
        if not norm:
            continue
        line = line_no(text, m.start())
        yield {
            "line": line,
            "offset": m.start(),
            "kind": "plain_path",
            "raw_match": m.group(0),
            "raw_target": token,
            "target": norm,
        }


def extract_yaml_paths(text):
    m = YAML_FENCE_RE.match(text)
    if not m:
        return
    fm = m.group(1)
    fm_start_offset = m.start(1)
    lines = fm.split("\n")
    current_field = None
    for i, line in enumerate(lines):
        line_no_in_doc = 1 + i + 1  # +1 for the opening "---\n"
        stripped = line.lstrip()
        # field: value
        fm_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if fm_match:
            current_field = fm_match.group(1)
            rest = fm_match.group(2).strip()
            if rest:
                # Inline scalar
                if current_field in YAML_PATH_FIELDS:
                    val = rest.strip().strip("\"'")
                    if val and val != "null" and not is_external_url(val) and looks_like_path(val):
                        yield {
                            "line": line_no_in_doc,
                            "offset": None,
                            "kind": "yaml_path",
                            "raw_match": line.strip(),
                            "raw_target": val,
                            "target": normalize_target(val),
                        }
            continue
        # list item under a known field
        if current_field in YAML_PATH_FIELDS and stripped.startswith("- "):
            val = stripped[2:].strip().strip("\"'")
            if val and val != "null" and not is_external_url(val) and looks_like_path(val):
                yield {
                    "line": line_no_in_doc,
                    "offset": None,
                    "kind": "yaml_path",
                    "raw_match": stripped,
                    "raw_target": val,
                    "target": normalize_target(val),
                }


def extract_all(text):
    """Combine extractors; deduplicate same (line, kind, target)."""
    seen = set()
    out = []
    for source in (extract_yaml_paths(text), extract_wikilinks(text),
                    extract_mdlinks(text), extract_backtick_paths(text)):
        for hit in source:
            key = (hit["line"], hit["kind"], hit["target"])
            if key in seen:
                continue
            seen.add(key)
            out.append(hit)
    return out


# ----- Resolution ------------------------------------------------------------

def resolve(target_str: str, source_file: pathlib.Path | None,
            vault_root: pathlib.Path, basename_index, *, kind: str,
            strip_locators: bool = True):
    """Try to resolve. Returns (status, resolved_or_matches_or_None, reason).

    status in:
      'resolved'                  -> exists
      'broken'                    -> nothing found
      'ambiguous_reference'       -> filename-only with multiple matches
      'external_local_missing'    -> Windows abs path outside vault, missing
      'external_local_resolved'   -> outside vault, exists (not reported)
      'skipped_anchor'            -> in-note anchor
    """
    s = normalize_target(target_str)
    if strip_locators:
        s = strip_locator_suffix(s)
    if not s:
        return "broken", None, "empty target"
    if s.startswith("#"):
        return "skipped_anchor", None, "anchor-only"

    # Windows absolute path?
    if is_windows_absolute(s):
        p = pathlib.Path(s)
        try:
            vrabs = vault_root.resolve()
            try:
                p_resolved = p
                # use resolve() if path exists, else absolute path
                p_check = p
                # Check inside vault
                try:
                    rel = pathlib.Path(s.replace("\\", "/")).resolve().relative_to(vrabs)
                    inside_vault = True
                except Exception:
                    inside_vault = False
                # exists test (works for both)
                if p.exists():
                    if inside_vault:
                        return "resolved", p, ""
                    return "external_local_resolved", p, ""
                else:
                    if inside_vault:
                        return "broken", None, f"absolute path under vault root does not exist: {s}"
                    return "external_local_missing", p, f"absolute path outside vault root not accessible: {s}"
            except Exception:
                # Treat broadly
                if p.exists():
                    return "resolved", p, ""
                return "broken", None, f"absolute path not found: {s}"
        except Exception:
            return "broken", None, f"could not resolve absolute path: {s}"

    # Unix-style absolute starting with '/'? Treat as vault-relative.
    if s.startswith("/"):
        candidate = vault_root / s.lstrip("/")
        if candidate.exists():
            return "resolved", candidate, ""
        # fall through to try with .md
    else:
        candidate = None

    # Build candidate list, try in order
    candidates = []
    if source_file is not None:
        candidates.append(source_file.parent / s)
    candidates.append(vault_root / s)
    if candidate is not None:
        candidates.insert(0, candidate)

    for c in candidates:
        try:
            if c.exists():
                return "resolved", c, ""
        except OSError:
            pass

    # If no extension on the final segment, try .md (Obsidian-style for wikilinks)
    name_only = pathlib.PurePosixPath(s.replace("\\", "/")).name
    if "." not in name_only and kind in {"wikilink", "plain_path"}:
        # Try candidates with .md appended
        for c in candidates:
            c2 = c.with_suffix(".md") if c.suffix == "" and c.name else None
            if c2 is not None:
                try:
                    if c2.exists():
                        return "resolved", c2, ""
                except OSError:
                    pass

    # Filename-only fallback to basename index
    has_slash = "/" in s or "\\" in s
    if not has_slash:
        matches = basename_index.get(s, [])
        if "." not in name_only and kind in {"wikilink", "plain_path"}:
            matches = list(matches) + basename_index.get(s + ".md", [])
        if len(matches) == 1:
            return "resolved", matches[0], ""
        if len(matches) > 1:
            return "ambiguous_reference", matches, f"{len(matches)} candidates found by basename"
        return "broken", None, "no candidate found at source-dir, vault-root, or by basename"

    return "broken", None, "no candidate found at source-dir or vault-root"


# ----- Suppression -----------------------------------------------------------

def compiled_regexes(patterns: list[str]):
    compiled = []
    for pattern in patterns:
        try:
            compiled.append((pattern, re.compile(pattern)))
        except re.error as exc:
            print(f"warning: invalid ignore regex {pattern!r}: {exc}", file=sys.stderr)
    return compiled


def suppression_reason(hit: dict, source_rel: str, text: str, config: dict,
                       fence_ranges: list[tuple[int, int]],
                       target_regexes, context_regexes):
    if bool(config.get("ignore_example_fences", False)) and offset_in_ranges(hit.get("offset"), fence_ranges):
        return "example_fence", "inside ignored fenced code block"

    if matches_any_glob(source_rel, config.get("ignored_source_globs", [])):
        return "ignored_source_glob", "source note matched ignored_source_globs"

    raw = hit.get("raw_target", "")
    target = hit.get("target", "")
    for pattern, regex in target_regexes:
        if regex.search(raw) or regex.search(target):
            return f"ignored_target_regex:{pattern}", "target matched ignored_target_regexes"

    context = line_text(text, hit["line"])
    for pattern, regex in context_regexes:
        if regex.search(context):
            return f"ignored_context_regex:{pattern}", "source line matched ignored_context_regexes"

    return None, None


# ----- Report rendering ------------------------------------------------------

def md_link_to(p: pathlib.Path, vault_root: pathlib.Path, report_path: pathlib.Path) -> str:
    """Produce a Markdown-link target from report path to p."""
    try:
        rel = os.path.relpath(p, report_path.parent).replace("\\", "/")
    except ValueError:
        rel = p.as_posix()
    # If path has spaces, use angle brackets
    if " " in rel:
        return f"<{rel}>"
    return rel


def safe_label(p: pathlib.Path, vault_root: pathlib.Path) -> str:
    try:
        rel = p.relative_to(vault_root).as_posix()
    except ValueError:
        rel = p.as_posix()
    return rel


def render_report(rows, vault_root: pathlib.Path, report_path: pathlib.Path,
                   files_scanned: int, refs_total: int, stats: dict) -> str:
    """Build the deterministic Markdown report from the row list."""
    actionable = []
    ambiguous = []
    external_documented = []
    suppressed = []
    for r in rows:
        if r["status"] in {"broken", "external_local_missing"}:
            actionable.append(r)
        elif r["status"] == "ambiguous_reference":
            ambiguous.append(r)
        elif r["status"] == "external_local_documented":
            external_documented.append(r)
        elif r["status"] == "suppressed":
            suppressed.append(r)

    def keyfn(r):
        return (r["source_rel"], r["line"], r["kind"], r["raw_target"])
    actionable.sort(key=keyfn)
    ambiguous.sort(key=keyfn)
    external_documented.sort(key=keyfn)
    suppressed.sort(key=keyfn)

    suppressed_counts = Counter(r["suppression_category"] for r in suppressed)
    severity_counts = Counter(r.get("severity", "PLAIN") for r in rows)

    def header():
        return [
            "| severity | role | source note | line | kind | raw target | normalized target | reason |",
            "|---|---|---|---:|---|---|---|---|",
        ]

    def row_line(r):
        src_md = md_link_to(r["source_path"], vault_root, report_path)
        src_label = r["source_rel"]
        return (f"| `{r.get('severity', '')}` | `{r.get('source_role', '')}` | "
                f"[{src_label}]({src_md}) | {r['line']} | {r['kind']} | "
                f"`{r['raw_target_escaped']}` | `{r['normalized_target_escaped']}` | "
                f"{r['reason']} |")

    out = []
    out.append("# Link and Reference Integrity Report")
    out.append("")
    out.append("Generated by `tools/wiki_deriver/link_reference_checker.py` "
                "(Layer 3 dumb tool #1).")
    out.append("Regenerated from source each run; this is a derived view, not a source of truth.")
    out.append("")
    out.append("## Headline")
    out.append("")
    out.append(f"- Scanned files: {files_scanned}")
    out.append(f"- References extracted: {refs_total}")
    out.append(f"- Actionable broken: {len(actionable)}")
    out.append(f"- LOUD actionable broken: {sum(1 for r in actionable if r.get('severity') == 'LOUD')}")
    out.append(f"- Ambiguous references: {len(ambiguous)}")
    out.append(f"- External-local documented: {len(external_documented)}")
    out.append(f"- Suppressed by config: {len(suppressed)}")
    out.append(f"- Severity counts: {dict(sorted(severity_counts.items()))}")
    out.append(f"- Baseline broken references before Tool 3: {BASELINE_BROKEN_REFERENCES}")
    out.append(f"- Actionable drop from baseline: {BASELINE_BROKEN_REFERENCES - len(actionable)}")
    out.append("")
    out.append("## Resolver Upgrade Stats")
    out.append("")
    out.append(f"- Resolved via all-file vault index: {stats.get('resolved_by_index', 0)}")
    out.append(f"- Resolved after line/symbol suffix strip: {stats.get('resolved_after_suffix_strip', 0)}")
    out.append(f"- Broken -> ambiguous via all-file collision index: {stats.get('broken_to_ambiguous', 0)}")
    out.append(f"- TASK_018 estimate: 533 index resolves, 61 suffix resolves, 291 broken-to-ambiguous")
    if stats.get("unreadable_sources"):
        out.append(f"- Unreadable source files skipped: {len(stats['unreadable_sources'])}")
        for src in stats["unreadable_sources"]:
            out.append(f"  - `{escape_for_cell(src)}`")
    out.append("")

    out.append("## 1. Actionable broken")
    out.append("")
    if not actionable:
        out.append("_None._")
    else:
        out.extend(header())
        for r in actionable:
            out.append(row_line(r))
    out.append("")

    out.append("## 2. Ambiguous")
    out.append("")
    if not ambiguous:
        out.append("_None._")
    else:
        out.extend(header())
        for r in ambiguous:
            out.append(row_line(r))
    out.append("")

    out.append("## 3. External-local documented")
    out.append("")
    if not external_documented:
        out.append("_None._")
    else:
        out.extend(header())
        for r in external_documented:
            out.append(row_line(r))
    out.append("")

    out.append("## 4. Suppressed by config")
    out.append("")
    if not suppressed:
        out.append("_None._")
    else:
        out.append("### Suppressed counts")
        out.append("")
        out.append("| category | count |")
        out.append("|---|---:|")
        for category, count in sorted(suppressed_counts.items()):
            out.append(f"| `{escape_for_cell(category)}` | {count} |")
        out.append("")
        out.append("### Suppressed rows")
        out.append("")
        out.extend(header())
        for r in suppressed:
            out.append(row_line(r))
    out.append("")
    return "\n".join(out) + "\n"


def render_json_summary(rows, vault_root: pathlib.Path, markdown_path: pathlib.Path,
                        files_scanned: int, refs_total: int, stats: dict,
                        severity_config_path: pathlib.Path) -> dict:
    items = []
    for r in sorted(rows, key=lambda row: (
        row["source_rel"], row["line"], row["kind"], row["raw_target"], row["status"]
    )):
        items.append({
            "severity": r.get("severity", "PLAIN"),
            "source_role": r.get("source_role", "regular"),
            "source_status": r.get("source_status", ""),
            "source_type": r.get("source_type", ""),
            "source": r["source_rel"],
            "line": r["line"],
            "kind": r["kind"],
            "status": r["status"],
            "raw_target": r["raw_target"],
            "normalized_target": strip_locator_suffix(r.get("target", "")),
            "reason": r["reason"],
            "suppression_category": r.get("suppression_category", ""),
        })
    by_severity = Counter(item["severity"] for item in items)
    by_role = Counter(item["source_role"] for item in items)
    by_status = Counter(item["status"] for item in items)
    actionable = [
        item for item in items
        if item["status"] in {"broken", "external_local_missing"}
    ]
    loud_items = [item for item in actionable if item["severity"] == "LOUD"]
    try:
        markdown_rel = markdown_path.relative_to(vault_root).as_posix()
    except ValueError:
        markdown_rel = str(markdown_path)
    try:
        severity_config_rel = severity_config_path.relative_to(vault_root).as_posix()
    except ValueError:
        severity_config_rel = str(severity_config_path)
    return {
        "schema_version": 1,
        "tool": "tools/wiki_deriver/link_reference_checker.py",
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "vault_root": str(vault_root),
        "source_markdown": markdown_rel,
        "severity_policy_config": severity_config_rel,
        "counts": {
            "files_scanned": files_scanned,
            "references_extracted": refs_total,
            "total": len(items),
            "actionable_broken": len(actionable),
            "loud_actionable_broken": len(loud_items),
            "ambiguous_references": by_status.get("ambiguous_reference", 0),
            "external_local_documented": by_status.get("external_local_documented", 0),
            "suppressed": by_status.get("suppressed", 0),
            "by_severity": dict(sorted(by_severity.items())),
            "by_role": dict(sorted(by_role.items())),
            "by_status": dict(sorted(by_status.items())),
        },
        "resolver_stats": stats,
        "items": items,
        "loud_items": loud_items,
    }


# ----- Escaping helpers for Markdown table cells ----------------------------

def escape_for_cell(s: str) -> str:
    # Pipes and backticks must be escaped inside table cells
    if s is None: return ""
    return (s.replace("\\", "\\\\")
              .replace("`", "\\`")
              .replace("|", "\\|")
              .replace("\n", " ")
              .replace("\r", " "))


# ----- Main driver -----------------------------------------------------------

def run_scan(config: dict, *, vault_root_override: pathlib.Path | None = None,
              output_override: pathlib.Path | None = None,
              suppress_worker_report: bool = False) -> int:
    vault_root = (vault_root_override or
                   pathlib.Path(config["vault_root"])).resolve()
    if not vault_root.is_dir():
        print(f"vault root not found: {vault_root}", file=sys.stderr)
        return 3
    output_rel = config.get("output_path", "_DERIVED/broken_links.md")
    output_path = (output_override or (vault_root / output_rel)).resolve()
    json_rel = config.get("output_json")
    if json_rel:
        output_json_path = (vault_root / json_rel).resolve()
    else:
        output_json_path = output_path.with_suffix(".json")
    severity_config_rel = config.get(
        "severity_policy_config",
        "tools/wiki_deriver/capture_integrity_checker.config.json",
    )
    severity_config_path = (vault_root / severity_config_rel).resolve()
    try:
        severity_config = load_config(severity_config_path)
    except SystemExit:
        return 4
    configured_worker_report_rel = config.get("worker_report_path")
    configured_worker_report_path = (
        (vault_root / configured_worker_report_rel).resolve()
        if configured_worker_report_rel else None
    )
    worker_report_path = None if suppress_worker_report else configured_worker_report_path
    vault_index_rel = config.get("vault_index_path", "_DERIVED/vault_index.json")
    ignore_globs = config.get("ignore_globs", [])
    include_txt = bool(config.get("include_txt", False))
    target_regexes = compiled_regexes(config.get("ignored_target_regexes", []))
    context_regexes = compiled_regexes(config.get("ignored_context_regexes", []))
    allowed_external_prefixes = config.get("allowed_external_prefixes", [])

    # Ensure the output directory AND placeholder file exist BEFORE scanning.
    # This is required for deterministic byte-identical reruns: references to
    # `_DERIVED/` (the directory) and `_DERIVED/broken_links.md` (the output
    # file) in source notes resolve consistently from the first run onward,
    # regardless of whether they pre-existed.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.exists():
        output_path.write_text("", encoding="utf-8", newline="\n")

    files = iter_scan_files(vault_root, ignore_globs, include_txt)
    skip_outputs = {output_path, output_json_path}
    if configured_worker_report_path is not None:
        skip_outputs.add(configured_worker_report_path)
    files = [f for f in files if f.resolve() not in skip_outputs]
    markdown_basename_index = build_basename_index(files)
    try:
        basename_index, vault_index = load_vault_index(vault_root, vault_index_rel)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 4

    rows = []
    refs_total = 0
    stats = {
        "resolved_by_index": 0,
        "resolved_after_suffix_strip": 0,
        "broken_to_ambiguous": 0,
        "unreadable_sources": [],
    }

    def add_row(f, src_rel, hit, status, reason, source_fm, suppression_category=""):
        rows.append({
            "source_path": f,
            "source_rel": src_rel,
            "line": hit["line"],
            "kind": hit["kind"],
            "raw_target": hit["raw_target"],
            "target": strip_locator_suffix(hit["target"]),
            "raw_target_escaped": escape_for_cell(hit["raw_target"]),
            "normalized_target_escaped": escape_for_cell(strip_locator_suffix(hit["target"])),
            "status": status,
            "reason": reason,
            "suppression_category": suppression_category,
            "source_status": source_fm.get("status", ""),
            "source_type": source_fm.get("type", ""),
            "source_role": source_role(src_rel, source_fm, severity_config),
            "severity": row_severity(status, src_rel, source_fm, severity_config),
        })

    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            try:
                stats["unreadable_sources"].append(f.relative_to(vault_root).as_posix())
            except ValueError:
                stats["unreadable_sources"].append(f.as_posix())
            continue
        try:
            src_rel = f.relative_to(vault_root).as_posix()
        except ValueError:
            src_rel = f.as_posix()
        source_fm = frontmatter(text)
        fence_ranges = fenced_code_ranges(text)
        hits = extract_all(text)
        for hit in hits:
            refs_total += 1
            markdown_status, _, _ = resolve(
                hit["target"], f, vault_root, markdown_basename_index,
                kind=hit["kind"], strip_locators=False)
            status, resolved, reason = resolve(
                hit["target"], f, vault_root, basename_index, kind=hit["kind"])
            stripped = strip_locator_suffix(hit["target"])
            had_locator = stripped != hit["target"]

            if status in ("resolved", "skipped_anchor", "external_local_resolved"):
                if markdown_status not in ("resolved", "skipped_anchor", "external_local_resolved"):
                    if had_locator:
                        stats["resolved_after_suffix_strip"] += 1
                    else:
                        stats["resolved_by_index"] += 1
                continue

            if markdown_status == "broken" and status == "ambiguous_reference":
                stats["broken_to_ambiguous"] += 1

            early_category, early_reason = suppression_reason(
                hit, src_rel, text, config, fence_ranges, target_regexes, context_regexes)
            if early_category in {"example_fence", "ignored_source_glob"}:
                add_row(f, src_rel, hit, "suppressed", early_reason, source_fm, early_category)
                continue

            if status == "ambiguous_reference":
                add_row(f, src_rel, hit, status, reason, source_fm)
                continue

            normalized = strip_locator_suffix(normalize_target(hit["target"]))
            if (is_windows_absolute(normalized) or normalized.startswith("/")) and starts_with_any(normalized, allowed_external_prefixes):
                add_row(f, src_rel, hit, "external_local_documented",
                        "matched allowed_external_prefixes", source_fm)
                continue

            category, suppress_reason = (
                (early_category, early_reason)
                if early_category
                else suppression_reason(
                    hit, src_rel, text, config, fence_ranges, target_regexes, context_regexes)
            )
            if category:
                add_row(f, src_rel, hit, "suppressed", suppress_reason, source_fm, category)
                continue

            if status in ("resolved", "skipped_anchor", "external_local_resolved"):
                continue
            add_row(f, src_rel, hit, status, reason, source_fm)

    report = render_report(rows, vault_root, output_path,
                            files_scanned=len(files), refs_total=refs_total,
                            stats=stats)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8", newline="\n")
    summary = render_json_summary(
        rows, vault_root, output_path,
        files_scanned=len(files), refs_total=refs_total, stats=stats,
        severity_config_path=severity_config_path,
    )
    output_json_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    if worker_report_path is not None:
        worker_report_path.parent.mkdir(parents=True, exist_ok=True)
        worker_report_path.write_text(report, encoding="utf-8", newline="\n")
    return 0


# ----- Synthetic-fixture tests ----------------------------------------------

def run_tests() -> int:
    """In-process synthetic-fixture acceptance tests."""
    failures = []

    def check(name, cond, detail=""):
        if cond:
            print(f"  PASS  {name}")
        else:
            failures.append((name, detail))
            print(f"  FAIL  {name}: {detail}")

    print("[tests] running synthetic-fixture acceptance tests")
    with tempfile.TemporaryDirectory(prefix="lrc_test_") as td:
        root = pathlib.Path(td)
        # Build fixture:
        #   A.md: links to B.md (good), Z.md (broken), http://x (external),
        #         [[unique_target]] (resolves by basename), [[dup]] (ambiguous)
        #   B.md: empty
        #   sub1/dup.md, sub2/dup.md  -> ambiguous on basename
        #   nested/unique_target.md  -> resolves filename-only basename
        (root / "B.md").write_text("hello", encoding="utf-8")
        (root / "sub1").mkdir(); (root / "sub2").mkdir()
        (root / "sub1" / "dup.md").write_text("dup1", encoding="utf-8")
        (root / "sub2" / "dup.md").write_text("dup2", encoding="utf-8")
        (root / "nested").mkdir()
        (root / "nested" / "unique_target.md").write_text("u", encoding="utf-8")
        # Real path that should resolve when backticked
        (root / "scripts").mkdir()
        (root / "scripts" / "real_tool.py").write_text("# fake", encoding="utf-8")
        a_content = (
            "# A\n"
            "[good](./B.md)\n"             # line 2 — valid
            "[bad-link](./Z.md)\n"          # line 3 — broken
            "[ext](http://example.com)\n"   # line 4 — external, ignored
            "[[NonexistentNote]]\n"         # line 5 — broken
            "[[unique_target]]\n"           # line 6 — resolves via basename
            "[[dup]]\n"                     # line 7 — ambiguous
            "Valid backtick path: `scripts/real_tool.py`\n"          # line 8 — valid plain
            "Broken backtick path: `scripts/missing_tool.py`\n"      # line 9 — broken plain
            "Anchor-only: [section](#section)\n"                      # line 10 — ignored
            "[[#InNoteHeading]]\n"                                    # line 11 — heading-only, ignored
        )
        (root / "A.md").write_text(a_content, encoding="utf-8")

        config = {
            "vault_root": str(root),
            "output_path": "_DERIVED/broken_links.md",
            "output_json": "_DERIVED/broken_links.json",
            "severity_policy_config": str(DEFAULT_CONFIG_PATH.parent / "capture_integrity_checker.config.json"),
            "vault_index_path": "_DERIVED/vault_index.json",
            "include_txt": False,
            "ignore_globs": [
                "_DERIVED", "_DERIVED/*", ".git", ".git/*",
            ],
        }

        index_entries = []
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.suffix.lower() in VAULT_EXTENSIONS:
                rel = p.relative_to(root).as_posix()
                if rel.startswith("_DERIVED/"):
                    continue
                index_entries.append({
                    "path": rel,
                    "basename": p.name,
                    "extension": p.suffix.lower(),
                    "descriptor": "test fixture",
                    "basename_collision": p.name == "dup.md",
                })
        collisions = {
            "dup.md": sorted(
                e["path"] for e in index_entries if e["basename"] == "dup.md"
            )
        }
        (root / "_DERIVED").mkdir(exist_ok=True)
        (root / "_DERIVED" / "vault_index.json").write_text(
            json.dumps({
                "schema_version": SUPPORTED_VAULT_INDEX_SCHEMA,
                "tool": "test",
                "config_path": "test",
                "entry_count": len(index_entries),
                "counts_by_extension": {},
                "basename_collision_count": 1,
                "basename_collisions": collisions,
                "entries": index_entries,
            }, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        rc = run_scan(config)
        check("run_scan returns 0", rc == 0)
        out = root / "_DERIVED" / "broken_links.md"
        check("output file exists", out.exists())

        report_text = out.read_text(encoding="utf-8") if out.exists() else ""

        # Test individual assertions
        check("broken wikilink flagged (NonexistentNote)",
               "NonexistentNote" in report_text,
               "expected NonexistentNote in broken section")
        check("broken markdown link flagged (./Z.md)",
               "Z.md" in report_text,
               "expected ./Z.md in broken section")
        check("valid markdown link NOT flagged (./B.md)",
               "./B.md" not in report_text,
               "expected ./B.md not in report (it should resolve)")
        check("external URL ignored (http://example.com)",
               "example.com" not in report_text,
               "external URL leaked into report")
        check("anchor-only link ignored (#section)",
               "#section" not in report_text,
               "anchor-only link leaked into report")
        check("filename-only unique target resolved (unique_target)",
               "unique_target" not in report_text,
               "unique_target should have resolved via basename")
        check("filename-only duplicate reported ambiguous (dup)",
               "ambiguous" in report_text.lower() and "`dup`" in report_text,
               "dup should appear in ambiguous section")
        check("valid backticked plain path NOT flagged (real_tool.py)",
               "real_tool.py" not in report_text,
               "valid backticked plain path leaked into report")
        check("broken backticked plain path IS flagged (missing_tool.py)",
               "missing_tool.py" in report_text,
               "broken backticked plain path missed by extractor")

        # Acceptance: do not modify source notes
        a_after = (root / "A.md").read_text(encoding="utf-8")
        check("source note A.md unchanged after scan", a_after == a_content)

        # Acceptance: rerun produces byte-identical output
        report_first = out.read_bytes()
        rc2 = run_scan(config)
        check("rerun returns 0", rc2 == 0)
        report_second = out.read_bytes()
        check("byte-identical rerun (no source changes)",
               report_first == report_second,
               f"first={len(report_first)}B second={len(report_second)}B")

        # Acceptance: _DERIVED/ ignored (the report itself didn't appear as
        # a scanned source).
        # The output file contains a section "Scanned files: N". With our
        # fixture: 5 .md files (A, B, sub1/dup, sub2/dup, nested/unique_target).
        # scripts/real_tool.py is .py, excluded from scan (we only scan .md).
        check("scanned-file count excludes _DERIVED",
               "Scanned files: 5" in report_text,
               f"expected 5 scanned files; report contains: {report_text[-200:]!r}")

    print()
    if failures:
        print(f"[tests] {len(failures)} failures")
        return 1
    print(f"[tests] all passed")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--test", action="store_true",
                          help="Run synthetic-fixture acceptance tests, then exit.")
    parser.add_argument("--vault-root", default=None,
                          help="Override vault_root from config.")
    parser.add_argument("--output", default=None,
                          help="Override output_path from config.")
    parser.add_argument("--no-worker-report", action="store_true",
                          help="Do not mirror output to worker_report_path from config.")
    args = parser.parse_args(argv)

    if args.test:
        return run_tests()

    cfg = load_config(pathlib.Path(args.config))
    vroot = pathlib.Path(args.vault_root) if args.vault_root else None
    outpath = pathlib.Path(args.output) if args.output else None
    return run_scan(
        cfg,
        vault_root_override=vroot,
        output_override=outpath,
        suppress_worker_report=args.no_worker_report,
    )


if __name__ == "__main__":
    sys.exit(main())
