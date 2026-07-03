"""Build the Layer 3 vault index derived artifact.

The index is intentionally dumb and deterministic: it walks the vault using
the link checker's ignore rules, records known-extension files, flags basename
collisions, and emits machine-readable JSON plus a Markdown rendering.
"""
from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import os
import pathlib
import re
import sys
from collections import Counter, defaultdict


THIS_DIR = pathlib.Path(__file__).resolve().parent
CHECKER_PATH = THIS_DIR / "link_reference_checker.py"
DEFAULT_CONFIG_PATH = THIS_DIR / "link_reference_checker.config.json"


def load_checker():
    spec = importlib.util.spec_from_file_location("link_reference_checker", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load checker module: {CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_ignored(rel_posix: str, ignore_globs: list[str]) -> bool:
    rel = rel_posix.replace("\\", "/")
    parts = rel.split("/")
    for glob in ignore_globs:
        g = glob.replace("\\", "/")
        if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g):
            return True
        if "/" not in g and not g.endswith("/*") and any(part == g for part in parts):
            return True
    return False


def iter_index_files(vault_root: pathlib.Path, ignore_globs: list[str],
                     extensions: set[str]):
    results: list[pathlib.Path] = []
    for root, dirs, files in os.walk(vault_root):
        root_path = pathlib.Path(root)
        kept_dirs = []
        for d in dirs:
            rel = (root_path / d).relative_to(vault_root).as_posix()
            if not is_ignored(rel, ignore_globs):
                kept_dirs.append(d)
        dirs[:] = sorted(kept_dirs)
        for name in sorted(files):
            path = root_path / name
            rel = path.relative_to(vault_root).as_posix()
            if is_ignored(rel, ignore_globs):
                continue
            if path.suffix.lower() in extensions:
                results.append(path)
    return sorted(results, key=lambda p: p.relative_to(vault_root).as_posix())


def strip_wrapping_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def markdown_descriptor(text: str, fallback: str) -> str:
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if frontmatter:
        fields: dict[str, str] = {}
        for line in frontmatter.group(1).splitlines():
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$", line)
            if m:
                fields[m.group(1).lower()] = strip_wrapping_quotes(m.group(2))
        for key in ("title", "tagline"):
            if fields.get(key):
                return clean_descriptor(fields[key])
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return clean_descriptor(stripped.lstrip("#").strip())
    return fallback


def code_descriptor(path: pathlib.Path, text: str, fallback: str) -> str:
    suffix = path.suffix.lower()
    lines = text.splitlines()

    if suffix == ".py":
        joined = "\n".join(lines[:20]).lstrip()
        doc = re.match(r'(?s)(?:[rubfRUBF]*)([\'"]{3})(.*?)\1', joined)
        if doc:
            first = first_meaningful_line(doc.group(2))
            if first:
                return clean_descriptor(first)

    comment_prefixes = {
        ".py": ("#",),
        ".cs": ("//", "/*", "*"),
        ".ps1": ("#",),
        ".bat": ("REM", "::"),
        ".toml": ("#",),
        ".yaml": ("#",),
        ".yml": ("#",),
        ".html": ("<!--",),
        ".txt": ("#",),
    }
    for line in lines[:40]:
        stripped = line.strip()
        if not stripped:
            continue
        for prefix in comment_prefixes.get(suffix, ()):
            if stripped.startswith(prefix):
                desc = stripped[len(prefix):].strip(" -/*>")
                if desc:
                    return clean_descriptor(desc)
        if suffix in {".json", ".csv"}:
            return fallback
    return fallback


def first_meaningful_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def clean_descriptor(value: str, limit: int = 140) -> str:
    one_line = re.sub(r"\s+", " ", value).strip()
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 3].rstrip() + "..."


def descriptor_for(path: pathlib.Path, rel: str) -> str:
    suffix = path.suffix.lower()
    parent = pathlib.PurePosixPath(rel).parent.as_posix()
    if parent == ".":
        parent = "vault root"
    fallback = f"{suffix or 'file'} file in {parent}"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return fallback
    if suffix == ".md":
        return markdown_descriptor(text, fallback)
    return code_descriptor(path, text, fallback)


def build_index(vault_root: pathlib.Path, config: dict, checker) -> dict:
    ignore_globs = config.get("ignore_globs", [])
    files = iter_index_files(vault_root, ignore_globs, set(checker.VAULT_EXTENSIONS))
    basename_counts = Counter(path.name for path in files)
    collisions = {
        basename: [
            path.relative_to(vault_root).as_posix()
            for path in files
            if path.name == basename
        ]
        for basename, count in sorted(basename_counts.items())
        if count > 1
    }
    entries = []
    for path in files:
        rel = path.relative_to(vault_root).as_posix()
        entries.append({
            "path": rel,
            "basename": path.name,
            "extension": path.suffix.lower(),
            "descriptor": descriptor_for(path, rel),
            "basename_collision": basename_counts[path.name] > 1,
        })
    counts_by_extension = dict(sorted(Counter(e["extension"] for e in entries).items()))
    return {
        "schema_version": 1,
        "tool": "tools/wiki_deriver/build_vault_index.py",
        "config_path": "tools/wiki_deriver/link_reference_checker.config.json",
        "entry_count": len(entries),
        "counts_by_extension": counts_by_extension,
        "basename_collision_count": len(collisions),
        "basename_collisions": collisions,
        "entries": entries,
    }


def markdown_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_index_md(index: dict) -> str:
    lines = [
        "# Vault Index",
        "",
        "Deterministic all-file index generated from `_DERIVED/vault_index.json`.",
        "",
        "## Summary",
        "",
        f"- Entries: {index['entry_count']}",
        f"- Basename collisions: {index['basename_collision_count']}",
        "",
        "## Counts By Extension",
        "",
        "| Extension | Count |",
        "|---|---:|",
    ]
    for ext, count in index["counts_by_extension"].items():
        label = ext if ext else "(none)"
        lines.append(f"| `{markdown_escape(label)}` | {count} |")
    lines.extend([
        "",
        "## Basename Collisions",
        "",
    ])
    if not index["basename_collisions"]:
        lines.append("_None._")
    else:
        lines.extend(["| Basename | Count | Paths |", "|---|---:|---|"])
        for basename, paths in index["basename_collisions"].items():
            joined = "<br>".join(f"`{markdown_escape(p)}`" for p in paths)
            lines.append(f"| `{markdown_escape(basename)}` | {len(paths)} | {joined} |")
    lines.extend([
        "",
        "## Entries",
        "",
        "| Path | Basename | Ext | Collision | Descriptor |",
        "|---|---|---|---:|---|",
    ])
    for entry in index["entries"]:
        lines.append(
            f"| `{markdown_escape(entry['path'])}` | "
            f"`{markdown_escape(entry['basename'])}` | "
            f"`{markdown_escape(entry['extension'])}` | "
            f"{'true' if entry['basename_collision'] else 'false'} | "
            f"{markdown_escape(entry['descriptor'])} |"
        )
    return "\n".join(lines) + "\n"


def strip_line_or_symbol_suffix(target: str) -> str:
    return re.sub(r"(?::\d+(?:[-–]\d+)?|::[A-Za-z_][A-Za-z0-9_]*)$", "", target)


def estimate_link_checker_wins(vault_root: pathlib.Path, config: dict, checker,
                               all_file_index: dict) -> dict:
    scan_files = checker.iter_scan_files(
        vault_root,
        config.get("ignore_globs", []),
        bool(config.get("include_txt", False)),
    )
    markdown_index = checker.build_basename_index(scan_files)
    index_paths = [vault_root / entry["path"] for entry in all_file_index["entries"]]
    all_basename_index = checker.build_basename_index(index_paths)

    all_file_resolves = 0
    suffix_resolves = 0
    broken_to_ambiguous = 0
    unreadable_sources = []
    for source in scan_files:
        try:
            text = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            unreadable_sources.append(source.relative_to(vault_root).as_posix())
            continue
        for hit in checker.extract_all(text):
            old_status, _, _ = checker.resolve(
                hit["target"], source, vault_root, markdown_index, kind=hit["kind"]
            )
            if old_status in {"resolved", "skipped_anchor", "external_local_resolved"}:
                continue
            new_status, _, _ = checker.resolve(
                hit["target"], source, vault_root, all_basename_index, kind=hit["kind"]
            )
            if new_status in {"resolved", "skipped_anchor", "external_local_resolved"}:
                all_file_resolves += 1
                continue
            if old_status == "broken" and new_status == "ambiguous_reference":
                broken_to_ambiguous += 1
            stripped = strip_line_or_symbol_suffix(hit["target"])
            if stripped != hit["target"]:
                stripped_status, _, _ = checker.resolve(
                    stripped, source, vault_root, all_basename_index, kind=hit["kind"]
                )
                if stripped_status in {"resolved", "external_local_resolved"}:
                    suffix_resolves += 1
    return {
        "all_file_basename_resolves": all_file_resolves,
        "line_or_symbol_suffix_resolves_after_index": suffix_resolves,
        "broken_to_ambiguous": broken_to_ambiguous,
        "unreadable_sources": unreadable_sources,
    }


def render_report(index: dict, resolver_win: dict) -> str:
    lines = [
        "# Tool 2 Vault Index Build Report",
        "",
        "## Verdict",
        "",
        "Built the standalone all-file vault index artifacts for Tool 2.",
        "",
        "## Artifacts",
        "",
        "- `_DERIVED/vault_index.json` — canonical machine-readable index",
        "- `_DERIVED/vault_index.md` — human/agent-readable rendering from JSON",
        "- `tools/wiki_deriver/build_vault_index.py` — deterministic builder",
        "",
        "## Counts",
        "",
        f"- Entries indexed: {index['entry_count']}",
        f"- Basename collisions: {index['basename_collision_count']}",
        "",
        "| Extension | Count |",
        "|---|---:|",
    ]
    for ext, count in index["counts_by_extension"].items():
        label = ext if ext else "(none)"
        lines.append(f"| `{markdown_escape(label)}` | {count} |")
    lines.extend([
        "",
        "## Collision List",
        "",
    ])
    if not index["basename_collisions"]:
        lines.append("_None._")
    else:
        lines.extend(["| Basename | Count | Paths |", "|---|---:|---|"])
        for basename, paths in index["basename_collisions"].items():
            joined = "<br>".join(f"`{markdown_escape(p)}`" for p in paths)
            lines.append(f"| `{markdown_escape(basename)}` | {len(paths)} | {joined} |")
    lines.extend([
        "",
        "## Link Checker Resolver Win Estimate",
        "",
        f"- Broken rows that would resolve via all-file basename index: {resolver_win['all_file_basename_resolves']}",
        f"- Additional line/symbol suffix rows that would resolve after index: {resolver_win['line_or_symbol_suffix_resolves_after_index']}",
        f"- Broken rows that would become honest ambiguity: {resolver_win['broken_to_ambiguous']}",
    ])
    if resolver_win["unreadable_sources"]:
        lines.append(f"- Unreadable source files skipped during estimate: {len(resolver_win['unreadable_sources'])}")
        for source in resolver_win["unreadable_sources"][:10]:
            lines.append(f"  - `{markdown_escape(source)}`")
    lines.extend([
        "",
        "## Hand-Off To Tool 3",
        "",
        "The validator upgrade should load `_DERIVED/vault_index.json`, use its all-file basename map for resolution, strip `:line`, `:line-range`, and `::symbol` suffixes before resolving, then add config-driven suppression and severity sections.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(vault_root: pathlib.Path, index: dict, resolver_win: dict,
                  output_dir: pathlib.Path, report_path: pathlib.Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "vault_index.json"
    md_path = output_dir / "vault_index.md"
    json_path.write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    md_path.write_text(render_index_md(index), encoding="utf-8", newline="\n")
    report_path.write_text(render_report(index, resolver_win), encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--vault-root", default=None)
    parser.add_argument("--output-dir", default="_DERIVED")
    parser.add_argument("--report", default="_worker_reports/TASK_018_vault_index_build.md")
    args = parser.parse_args(argv)

    checker = load_checker()
    config = load_config(pathlib.Path(args.config))
    vault_root = pathlib.Path(args.vault_root or config["vault_root"]).resolve()
    if not vault_root.is_dir():
        print(f"vault root not found: {vault_root}", file=sys.stderr)
        return 2
    index = build_index(vault_root, config, checker)
    resolver_win = estimate_link_checker_wins(vault_root, config, checker, index)
    output_dir = (vault_root / args.output_dir).resolve()
    report_path = (vault_root / args.report).resolve()
    write_outputs(vault_root, index, resolver_win, output_dir, report_path)
    print(f"indexed {index['entry_count']} files")
    print(f"basename collisions {index['basename_collision_count']}")
    print(f"wrote {output_dir / 'vault_index.json'}")
    print(f"wrote {output_dir / 'vault_index.md'}")
    print(f"wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
