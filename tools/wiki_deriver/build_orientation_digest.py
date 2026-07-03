"""Build the Layer 3.3 orientation digest derived artifact.

The digest is intentionally dumb and deterministic. It loads the verified
vault index, copies only plainly stated fields or source lines, and emits
`UNSTATED` instead of inferring missing project state.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys
from collections import Counter


THIS_DIR = pathlib.Path(__file__).resolve().parent
VAULT_INDEX_SCHEMA = 1
DEFAULT_INDEX_PATH = pathlib.Path("_DERIVED/vault_index.json")
DEFAULT_OUTPUT_PATH = pathlib.Path("_DERIVED/orientation_digest.md")
DEFAULT_REPORT_PATH = pathlib.Path("_worker_reports/TASK_020_orientation_digest_build.md")
BUILD_VAULT_INDEX_PATH = THIS_DIR / "build_vault_index.py"


def load_index_builder():
    spec = importlib.util.spec_from_file_location("build_vault_index", BUILD_VAULT_INDEX_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load vault index builder: {BUILD_VAULT_INDEX_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_index(vault_root: pathlib.Path, index_path: pathlib.Path) -> dict:
    resolved = (vault_root / index_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"vault index missing: {resolved}")
    index = json.loads(resolved.read_text(encoding="utf-8"))
    if index.get("schema_version") != VAULT_INDEX_SCHEMA:
        raise ValueError(
            f"unsupported vault index schema_version={index.get('schema_version')!r}; "
            f"expected {VAULT_INDEX_SCHEMA}"
        )
    for key in ("entries", "basename_collisions"):
        if key not in index:
            raise ValueError(f"vault index missing required key: {key}")
    return index


def markdown_escape(value: object) -> str:
    text = str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def source_link(source: str, line: int | None = None) -> str:
    target = f"../{source}"
    if line is not None:
        target += f":{line}"
    label = source if line is None else f"{source}:{line}"
    return f"[{markdown_escape(label)}]({target})"


def source_ref(source: str, line: int | None = None) -> str:
    if source == "UNSTATED":
        return "`UNSTATED -- no canonical source`"
    return source_link(source, line)


def strip_yaml_quotes(value: str) -> str:
    value = value.strip()
    if "#" in value:
        before_hash = value.split("#", 1)[0].rstrip()
        if before_hash:
            value = before_hash
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value.strip()


def parse_frontmatter(text: str) -> tuple[dict[str, str], dict[str, int]]:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return {}, {}
    fields: dict[str, str] = {}
    lines: dict[str, int] = {}
    start_line = 2
    for offset, line in enumerate(match.group(1).splitlines(), start=start_line):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*?)\s*$", line)
        if not m:
            continue
        key = m.group(1).lower()
        fields[key] = strip_yaml_quotes(m.group(2))
        lines[key] = offset
    return fields, lines


def indexed_paths(index: dict, extension: str | None = None) -> list[str]:
    entries = index.get("entries", [])
    paths = [e["path"] for e in entries if extension is None or e.get("extension") == extension]
    return sorted(paths)


def line_hits(vault_root: pathlib.Path, rel: str, patterns: list[re.Pattern[str]],
              limit: int | None = None) -> list[tuple[int, str]]:
    path = vault_root / rel
    if not path.exists():
        return []
    hits = []
    for i, line in enumerate(read_text(path).splitlines(), start=1):
        stripped = line.strip()
        if any(p.search(stripped) for p in patterns):
            hits.append((i, stripped))
            if limit is not None and len(hits) >= limit:
                break
    return hits


def extract_agents_read_order(vault_root: pathlib.Path) -> list[dict]:
    rel = "AGENTS.md"
    rows = []
    for line_no, line in enumerate(read_text(vault_root / rel).splitlines(), start=1):
        m = re.match(r"^\d+\.\s+\*\*`([^`]+)`\*\*", line.strip())
        if m:
            rows.append({
                "thing": f"bootstrap read-order: {m.group(1)}",
                "pointer": m.group(1),
                "source": rel,
                "line": line_no,
            })
    return rows


def extract_agents_canonical_tables(vault_root: pathlib.Path) -> list[dict]:
    rel = "AGENTS.md"
    rows = []
    for line_no, line in enumerate(read_text(vault_root / rel).splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"Role", "---"}:
            continue
        path_match = re.search(r"`([^`]+)`", cells[1])
        if not path_match:
            continue
        rows.append({
            "thing": cells[0],
            "pointer": path_match.group(1),
            "source": rel,
            "line": line_no,
        })
    return rows


def extract_strategy_readme_canonicals(vault_root: pathlib.Path) -> list[dict]:
    rel = "nb_lib/strategy_specs/README.md"
    path = vault_root / rel
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        m = re.match(r"^-\s+`([^`]+)`\s+--\s+(.*)$", line.strip())
        if not m:
            continue
        if m.group(1).startswith("canonical/"):
            rows.append({
                "thing": m.group(2).strip(),
                "pointer": f"nb_lib/strategy_specs/{m.group(1)}",
                "source": rel,
                "line": line_no,
            })
    return rows


def extract_frontmatter_statuses(vault_root: pathlib.Path, index: dict) -> tuple[list[dict], list[str]]:
    prefixes = (
        "nb_lib/strategy_specs/canonical/",
        "nb_lib/strategy_specs/candidates/",
        "nb_lib/strategy_specs/composition_nodes/",
        "nb_lib/strategy_specs/tools/",
    )
    rows = []
    missing_status = []
    for rel in indexed_paths(index, ".md"):
        if not rel.startswith(prefixes):
            continue
        text = read_text(vault_root / rel)
        fields, lines = parse_frontmatter(text)
        if not fields:
            if rel.startswith(("nb_lib/strategy_specs/canonical/", "nb_lib/strategy_specs/candidates/")):
                missing_status.append(rel)
            continue
        status = fields.get("status")
        if not status:
            if rel.startswith(("nb_lib/strategy_specs/canonical/", "nb_lib/strategy_specs/candidates/")):
                missing_status.append(rel)
            continue
        rows.append({
            "path": rel,
            "title": fields.get("title") or pathlib.PurePosixPath(rel).name,
            "status": status,
            "created": fields.get("created", ""),
            "updated": fields.get("updated", ""),
            "source": rel,
            "line": lines.get("status"),
        })
    return sorted(rows, key=lambda r: (r["path"], r["status"])), sorted(set(missing_status))


def canonical_alpha_collisions(index: dict) -> list[tuple[str, list[str]]]:
    rows = []
    for basename, paths in sorted(index.get("basename_collisions", {}).items()):
        if basename.endswith("_canonical_alpha.md"):
            rows.append((basename, sorted(paths)))
    return rows


def bucket_usage_rows(vault_root: pathlib.Path, index: dict) -> list[dict]:
    rows = []
    for rel in indexed_paths(index, ".json"):
        if not rel.endswith("_bucket_usage.json"):
            continue
        path = vault_root / rel
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"path": rel, "state": f"UNREADABLE: {exc}", "source": rel})
            continue
        for bucket_name in sorted(data):
            value = data[bucket_name]
            if isinstance(value, list):
                rows.append({
                    "path": rel,
                    "state": f"{bucket_name}: {len(value)} record(s)",
                    "source": rel,
                })
            else:
                rows.append({
                    "path": rel,
                    "state": f"{bucket_name}: {type(value).__name__}",
                    "source": rel,
                })
    return rows


def current_state_rows(vault_root: pathlib.Path) -> list[dict]:
    rel = "_PROJECT_ALTITUDE_MAP.md"
    text = read_text(vault_root / rel)
    rows = []
    in_current = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("## Current state"):
            in_current = True
            rows.append({"fact": stripped, "source": rel, "line": line_no})
            continue
        if in_current and stripped.startswith("## 2."):
            break
        if in_current and (stripped.startswith("**") or stripped.startswith("Layer 2") or stripped.startswith("Eight MNQ")):
            rows.append({"fact": stripped, "source": rel, "line": line_no})
    return rows


def sealed_boundary_rows(vault_root: pathlib.Path) -> list[dict]:
    files = ["_PROJECT_ALTITUDE_MAP.md", "ninja-traitorate-methodology-reference.md"]
    patterns = [
        re.compile(r"\bOOS\b", re.I),
        re.compile(r"\bseal", re.I),
        re.compile(r"\bbucket", re.I),
        re.compile(r"\bvalidation\b", re.I),
    ]
    rows = []
    for rel in files:
        for line_no, text in line_hits(vault_root, rel, patterns):
            if len(text) > 220:
                text = text[:217].rstrip() + "..."
            rows.append({"fact": text, "source": rel, "line": line_no})
    return rows


def bright_line_rows(vault_root: pathlib.Path) -> list[dict]:
    rows = []
    rel = "_PROJECT_ALTITUDE_MAP.md"
    text = read_text(vault_root / rel).splitlines()
    in_guardrails = False
    for line_no, line in enumerate(text, start=1):
        stripped = line.strip()
        if stripped == "## 7. Guardrails":
            in_guardrails = True
            rows.append({"fact": stripped, "source": rel, "line": line_no})
            continue
        if in_guardrails and stripped.startswith("## 8."):
            break
        if in_guardrails and stripped.startswith("- "):
            rows.append({"fact": stripped, "source": rel, "line": line_no})

    rel = "AGENTS.md"
    authority_patterns = [
        re.compile(r"methodology reference.*wins", re.I),
        re.compile(r"Rule of thumb", re.I),
        re.compile(r"AGENTS\.md is the authority", re.I),
    ]
    for line_no, text_hit in line_hits(vault_root, rel, authority_patterns):
        rows.append({"fact": text_hit, "source": rel, "line": line_no})

    rel = "_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md"
    tool_patterns = [
        re.compile(r"flags or computes,\s*never interprets or fixes", re.I),
        re.compile(r"Never hand-written\.\s*Never", re.I),
    ]
    for line_no, text_hit in line_hits(vault_root, rel, tool_patterns):
        rows.append({"fact": text_hit, "source": rel, "line": line_no})
    return rows


def recent_report_rows(vault_root: pathlib.Path) -> list[dict]:
    report_dir = vault_root / "_worker_reports"
    if not report_dir.exists():
        return []
    paths = sorted(
        [p for p in report_dir.glob("*.md")],
        key=lambda p: (-p.stat().st_mtime, p.name),
    )
    rows = []
    for p in paths[:12]:
        rel = p.relative_to(vault_root).as_posix()
        text = read_text(p)
        fields, lines = parse_frontmatter(text)
        status = fields.get("status", "UNSTATED")
        rows.append({
            "path": rel,
            "status": status,
            "source": rel,
            "line": lines.get("status"),
        })
    return sorted(rows, key=lambda r: r["path"])


def render_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(v) for v in row) + " |")
    return lines


def unstated_row(fact_class: str, wanted: str) -> dict:
    return {"fact_class": fact_class, "wanted": wanted, "source": "UNSTATED"}


def build_digest(vault_root: pathlib.Path, index: dict) -> tuple[str, dict]:
    stats: dict[str, object] = {}
    canonical_rows = (
        extract_agents_read_order(vault_root)
        + extract_agents_canonical_tables(vault_root)
        + extract_strategy_readme_canonicals(vault_root)
    )
    status_rows, missing_status = extract_frontmatter_statuses(vault_root, index)
    collisions = canonical_alpha_collisions(index)
    buckets = bucket_usage_rows(vault_root, index)
    sealed_rows = sealed_boundary_rows(vault_root)
    current_rows = current_state_rows(vault_root)
    bright_rows = bright_line_rows(vault_root)
    report_rows = recent_report_rows(vault_root)

    unstated = []
    if not canonical_rows:
        unstated.append(unstated_row("canonical_pointers", "authoritative canonical file pointers"))
    if not status_rows:
        unstated.append(unstated_row("live_edge_status", "strategy spec status fields"))
    if not buckets:
        unstated.append(unstated_row("sealed_boundaries", "*_bucket_usage.json trackers"))
    if not current_rows:
        unstated.append(unstated_row("in_flight_work", "altitude map current-state block"))
    if report_rows and all(r["status"] == "UNSTATED" for r in report_rows):
        unstated.append(unstated_row("in_flight_work", "_worker_reports frontmatter status fields"))
    if not bright_rows:
        unstated.append(unstated_row("bright_lines", "guardrail/bright-line source lines"))

    status_counts = Counter(row["status"] for row in status_rows)

    lines = [
        "# Orientation Digest",
        "",
        "Generated by `tools/wiki_deriver/build_orientation_digest.py` from `_DERIVED/vault_index.json` plus explicit source fields/lines.",
        "",
        "This is a deterministic ground-truth snapshot. It is not an LLM summary and does not infer missing facts.",
        "",
        "## Index Contract",
        "",
        f"- Source index: `_DERIVED/vault_index.json`",
        f"- Index schema: `{index.get('schema_version')}`",
        f"- Indexed entries: `{index.get('entry_count')}`",
        f"- Basename collisions: `{index.get('basename_collision_count')}`",
        "",
        "## Canonical Pointers",
        "",
    ]
    if canonical_rows:
        lines.extend(render_table(
            ["thing", "pointer", "source_path"],
            [[r["thing"], r["pointer"], source_ref(r["source"], r.get("line"))] for r in canonical_rows],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")

    lines.extend(["", "## Canonical-Duplication Warnings", ""])
    if collisions:
        collision_rows = []
        for basename, paths in collisions:
            collision_rows.append([
                basename,
                "<br>".join(f"`{p}`" for p in paths),
                "`_DERIVED/vault_index.json`",
            ])
        lines.extend(render_table(["basename", "paths", "source_path"], collision_rows))
    else:
        lines.append("- No `*_canonical_alpha.md` basename collisions found. Source: `_DERIVED/vault_index.json`")

    lines.extend(["", "## Live Edge / Candidate / Dead Status Fields", ""])
    if status_rows:
        lines.extend(render_table(
            ["path", "status", "created", "updated", "source_path"],
            [
                [r["path"], r["status"], r["created"], r["updated"], source_ref(r["source"], r.get("line"))]
                for r in status_rows
            ],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")

    lines.extend(["", "## Sealed Boundaries And Bucket State", ""])
    if sealed_rows:
        lines.extend(render_table(
            ["fact_line", "source_path"],
            [[r["fact"], source_ref(r["source"], r["line"])] for r in sealed_rows],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")
    lines.extend(["", "### Bucket Usage Trackers", ""])
    if buckets:
        lines.extend(render_table(
            ["tracker", "state", "source_path"],
            [[r["path"], r["state"], source_ref(r["source"])] for r in buckets],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")

    lines.extend(["", "## In-Flight Work", ""])
    if current_rows:
        lines.extend(render_table(
            ["current_state_line", "source_path"],
            [[r["fact"], source_ref(r["source"], r["line"])] for r in current_rows],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")

    lines.extend(["", "### Recent Worker Reports", ""])
    if report_rows:
        lines.extend(render_table(
            ["report", "frontmatter_status", "source_path"],
            [[r["path"], r["status"], source_ref(r["source"], r.get("line"))] for r in report_rows],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")

    lines.extend(["", "## Bright Lines", ""])
    if bright_rows:
        lines.extend(render_table(
            ["quoted_line", "source_path"],
            [[r["fact"], source_ref(r["source"], r["line"])] for r in bright_rows],
        ))
    else:
        lines.append("- UNSTATED -- no canonical source")

    lines.extend(["", "## Unstated Fields", ""])
    if unstated:
        lines.extend(render_table(
            ["fact_class", "wanted", "source_path"],
            [[r["fact_class"], r["wanted"], "`UNSTATED -- no canonical source`"] for r in unstated],
        ))
    else:
        lines.append("- No top-level digest fact class was fully unstated.")

    stats.update({
        "canonical_pointer_count": len(canonical_rows),
        "canonical_alpha_collision_count": len(collisions),
        "status_field_count": len(status_rows),
        "status_counts": dict(sorted(status_counts.items())),
        "missing_status_count": len(missing_status),
        "bucket_tracker_count": len(buckets),
        "sealed_boundary_line_count": len(sealed_rows),
        "current_state_line_count": len(current_rows),
        "bright_line_count": len(bright_rows),
        "recent_report_count": len(report_rows),
        "recent_report_unstated_status_count": sum(1 for r in report_rows if r["status"] == "UNSTATED"),
        "unstated_fact_classes": unstated,
        "missing_status_sources": missing_status,
    })
    return "\n".join(lines) + "\n", stats


def render_report(stats: dict) -> str:
    lines = [
        "# TASK 020 Orientation Digest Build Report",
        "",
        "## Verdict",
        "",
        "Built the deterministic Layer 3.3 orientation digest against `_DERIVED/vault_index.json`.",
        "",
        "## Artifacts",
        "",
        "- `tools/wiki_deriver/build_orientation_digest.py` -- deterministic generator",
        "- `_DERIVED/orientation_digest.md` -- generated ground-truth snapshot",
        "- `_worker_reports/TASK_020_orientation_digest_build.md` -- this report",
        "",
        "## Found vs Unstated",
        "",
        f"- Canonical pointer rows: {stats['canonical_pointer_count']}",
        f"- Canonical-alpha collision groups: {stats['canonical_alpha_collision_count']}",
        f"- Status rows: {stats['status_field_count']}",
        f"- Source notes missing wanted status fields: {stats['missing_status_count']}",
        f"- Bucket tracker rows: {stats['bucket_tracker_count']}",
        f"- Sealed-boundary source lines: {stats['sealed_boundary_line_count']}",
        f"- Current-state source lines: {stats['current_state_line_count']}",
        f"- Bright-line source lines: {stats['bright_line_count']}",
        f"- Recent worker reports listed: {stats['recent_report_count']}",
        f"- Recent worker reports with `UNSTATED` frontmatter status: {stats['recent_report_unstated_status_count']}",
        "",
        "## Status Counts",
        "",
    ]
    status_counts = stats["status_counts"]
    if status_counts:
        lines.extend(render_table(["status", "count"], [[k, v] for k, v in status_counts.items()]))
    else:
        lines.append("_None._")
    lines.extend(["", "## Unstated Fact Classes", ""])
    unstated = stats["unstated_fact_classes"]
    if unstated:
        lines.extend(render_table(
            ["fact_class", "wanted"],
            [[r["fact_class"], r["wanted"]] for r in unstated],
        ))
    else:
        lines.append("_None at the top-level fact-class level._")
    lines.extend(["", "## Source Notes Missing Wanted Status Field", ""])
    missing = stats["missing_status_sources"]
    if missing:
        lines.extend(render_table(["source note"], [[p] for p in missing]))
    else:
        lines.append("_None._")
    lines.extend([
        "",
        "## Determinism Check",
        "",
        "The generator writes stable sorted Markdown and depends only on the checked-in index plus source files. Running it twice on an unchanged vault should produce a zero diff.",
        "",
    ])
    return "\n".join(lines)


def atomic_write(path: pathlib.Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault-root", default=None)
    parser.add_argument("--index", default=str(DEFAULT_INDEX_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args(argv)

    index_builder = load_index_builder()
    if args.vault_root:
        vault_root = pathlib.Path(args.vault_root).resolve()
    else:
        config = index_builder.load_config(index_builder.DEFAULT_CONFIG_PATH)
        vault_root = pathlib.Path(config["vault_root"]).resolve()
    if not vault_root.is_dir():
        print(f"vault root not found: {vault_root}", file=sys.stderr)
        return 2

    index = load_index(vault_root, pathlib.Path(args.index))
    digest, stats = build_digest(vault_root, index)
    report = render_report(stats)
    output_path = (vault_root / args.output).resolve()
    report_path = (vault_root / args.report).resolve()
    atomic_write(output_path, digest)
    atomic_write(report_path, report)
    print(f"wrote {output_path}")
    print(f"wrote {report_path}")
    print(f"status rows {stats['status_field_count']}")
    print(f"unstated fact classes {len(stats['unstated_fact_classes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
