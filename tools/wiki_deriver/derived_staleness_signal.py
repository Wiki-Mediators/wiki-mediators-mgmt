"""Flag stale _DERIVED artifacts without regenerating them.

Layer 3.8 dumb tool: compare known derived artifacts to the source files they
are generated from. It reports CURRENT / STALE / UNKNOWN only. It never edits,
fixes, or regenerates an artifact.
"""
from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import os
import pathlib
import sys
from dataclasses import dataclass
from typing import Iterable


THIS_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = THIS_DIR / "link_reference_checker.config.json"
DEFAULT_REPORT_PATH = pathlib.Path("_DERIVED/derived_staleness.md")
DEFAULT_JSON_PATH = pathlib.Path("_DERIVED/derived_staleness.json")
EPSILON_SECONDS = 0.000001


@dataclass(frozen=True)
class ArtifactSpec:
    name: str
    artifact_rel: str
    source_rels: tuple[str, ...]
    source_policy: str
    generation_marker: str


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel_posix(path: pathlib.Path, root: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def exists_rel(root: pathlib.Path, rel: str) -> bool:
    return (root / rel).exists()


def is_ignored(rel: str, ignore_globs: Iterable[str]) -> bool:
    rel = rel.replace("\\", "/")
    parts = rel.split("/")
    for glob in ignore_globs:
        g = glob.replace("\\", "/")
        if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g):
            return True
        if "/" not in g and not g.endswith("/*") and any(part == g for part in parts):
            return True
    return False


def iter_all_files(root: pathlib.Path, ignore_globs: Iterable[str] = ()) -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for dirpath, dirs, files in os.walk(root):
        dir_path = pathlib.Path(dirpath)
        kept_dirs = []
        for d in dirs:
            rel = (dir_path / d).relative_to(root).as_posix()
            if d == ".git" or rel == ".git" or rel.startswith(".git/"):
                continue
            if is_ignored(rel, ignore_globs):
                continue
            kept_dirs.append(d)
        dirs[:] = sorted(kept_dirs)
        for name in sorted(files):
            path = dir_path / name
            rel = path.relative_to(root).as_posix()
            if rel.startswith("_DERIVED/"):
                continue
            if is_ignored(rel, ignore_globs):
                continue
            out.append(path)
    return sorted(out, key=lambda p: p.relative_to(root).as_posix())


def unique_rels(root: pathlib.Path, paths: Iterable[pathlib.Path | str]) -> tuple[str, ...]:
    rels = []
    for p in paths:
        path = pathlib.Path(p)
        if not path.is_absolute():
            rel = path.as_posix()
        else:
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
        if rel.startswith("_DERIVED/"):
            continue
        if (root / rel).exists():
            rels.append(rel)
    return tuple(sorted(set(rels)))


def generation_marker_for(root: pathlib.Path, artifact_rel: str) -> str:
    path = root / artifact_rel
    if not path.exists():
        return ""
    try:
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            for key in ("generated_from", "tool", "config_path"):
                value = data.get(key)
                if value:
                    return f"{key}: {value}"
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    for line in text.splitlines()[:20]:
        lower = line.lower()
        if "generated" in lower or "generated_from" in lower:
            return line.strip()
    return ""


def discover_working_specs(root: pathlib.Path, config: dict) -> list[ArtifactSpec]:
    specs: list[ArtifactSpec] = []
    checker_path = THIS_DIR / "link_reference_checker.py"
    index_builder_path = THIS_DIR / "build_vault_index.py"
    digest_builder_path = THIS_DIR / "build_orientation_digest.py"

    checker = load_module(checker_path, "link_reference_checker")
    index_builder = load_module(index_builder_path, "build_vault_index")
    ignore_globs = config.get("ignore_globs", [])

    index_sources = list(index_builder.iter_index_files(
        root,
        ignore_globs,
        set(checker.VAULT_EXTENSIONS),
    ))
    index_sources.extend([checker_path, index_builder_path, pathlib.Path(config["_config_path"])])
    index_source_rels = unique_rels(root, index_sources)

    for rel in ("_DERIVED/vault_index.json", "_DERIVED/vault_index.md"):
        if exists_rel(root, rel):
            specs.append(ArtifactSpec(
                name=pathlib.PurePosixPath(rel).name,
                artifact_rel=rel,
                source_rels=index_source_rels,
                source_policy="vault index sources: indexed files plus index/checker code and config",
                generation_marker=generation_marker_for(root, rel),
            ))

    if exists_rel(root, "_DERIVED/broken_links.md"):
        scan_files = checker.iter_scan_files(
            root,
            ignore_globs,
            bool(config.get("include_txt", False)),
        )
        sources = list(scan_files) + [checker_path, pathlib.Path(config["_config_path"])]
        if exists_rel(root, config.get("vault_index_path", "_DERIVED/vault_index.json")):
            sources.append(root / config.get("vault_index_path", "_DERIVED/vault_index.json"))
        specs.append(ArtifactSpec(
            name="broken_links.md",
            artifact_rel="_DERIVED/broken_links.md",
            source_rels=unique_rels(root, sources),
            source_policy="link checker sources: scanned notes, checker code/config, and vault index when present",
            generation_marker=generation_marker_for(root, "_DERIVED/broken_links.md"),
        ))

    if exists_rel(root, "_DERIVED/orientation_digest.md"):
        # The digest reads the vault index plus canonical pointers, statuses,
        # bucket usage JSON, current-state lines, and recent worker reports. A
        # conservative dumb dependency is: all indexed Markdown/JSON files plus
        # the digest generator. That can over-flag, but never under-flags.
        digest_sources: list[pathlib.Path | str] = [digest_builder_path, "_DERIVED/vault_index.json"]
        try:
            index = json.loads((root / "_DERIVED/vault_index.json").read_text(encoding="utf-8"))
            for entry in index.get("entries", []):
                if entry.get("extension") in {".md", ".json"}:
                    digest_sources.append(entry["path"])
        except Exception:
            digest_sources.extend(["AGENTS.md", "_PROJECT_ALTITUDE_MAP.md"])
        specs.append(ArtifactSpec(
            name="orientation_digest.md",
            artifact_rel="_DERIVED/orientation_digest.md",
            source_rels=unique_rels(root, digest_sources),
            source_policy="orientation digest sources: vault index plus indexed Markdown/JSON source files",
            generation_marker=generation_marker_for(root, "_DERIVED/orientation_digest.md"),
        ))

    return specs


def discover_management_specs(root: pathlib.Path) -> list[ArtifactSpec]:
    specs: list[ArtifactSpec] = []
    sources = unique_rels(root, iter_all_files(root))

    for rel in (
        "_DERIVED/vault_index.json",
        "_DERIVED/vault_index.md",
        "_DERIVED/management_digest.json",
        "_DERIVED/management_digest.md",
        "_DERIVED/management_state.json",
        "_DERIVED/management_state.md",
    ):
        if exists_rel(root, rel):
            specs.append(ArtifactSpec(
                name=pathlib.PurePosixPath(rel).name,
                artifact_rel=rel,
                source_rels=sources,
                source_policy="management-vault derived artifact sources: staged non-_DERIVED management tree",
                generation_marker=generation_marker_for(root, rel),
            ))
    return specs


def discover_specs(root: pathlib.Path, config: dict) -> tuple[list[ArtifactSpec], str]:
    has_management_digest = exists_rel(root, "_DERIVED/management_digest.md") or exists_rel(
        root, "_DERIVED/management_digest.json"
    )
    if has_management_digest:
        return discover_management_specs(root), "management"
    return discover_working_specs(root, config), "working"


def evaluate_spec(root: pathlib.Path, spec: ArtifactSpec) -> dict:
    artifact = root / spec.artifact_rel
    if not artifact.exists():
        return {
            "artifact": spec.artifact_rel,
            "status": "MISSING",
            "source_policy": spec.source_policy,
            "generation_marker": spec.generation_marker,
            "source_count": len(spec.source_rels),
            "newer_sources": [],
        }
    artifact_mtime = artifact.stat().st_mtime
    newer = []
    missing_sources = []
    newest_source_mtime = None
    for rel in spec.source_rels:
        source = root / rel
        if not source.exists():
            missing_sources.append(rel)
            continue
        mtime = source.stat().st_mtime
        newest_source_mtime = mtime if newest_source_mtime is None else max(newest_source_mtime, mtime)
        if mtime > artifact_mtime + EPSILON_SECONDS:
            newer.append({
                "path": rel,
                "source_mtime": mtime,
                "source_mtime_iso": iso_from_mtime(mtime),
            })
    if missing_sources:
        status = "UNKNOWN"
    elif newer:
        status = "STALE"
    else:
        status = "CURRENT"
    method = "generation-marker observed + mtime fallback" if spec.generation_marker else "mtime fallback"
    return {
        "artifact": spec.artifact_rel,
        "status": status,
        "artifact_mtime": artifact_mtime,
        "artifact_mtime_iso": iso_from_mtime(artifact_mtime),
        "newest_source_mtime": newest_source_mtime,
        "newest_source_mtime_iso": iso_from_mtime(newest_source_mtime) if newest_source_mtime else "",
        "source_policy": spec.source_policy,
        "source_count": len(spec.source_rels),
        "generation_marker": spec.generation_marker,
        "method": method,
        "newer_sources": newer,
        "missing_sources": missing_sources,
    }


def iso_from_mtime(mtime: float) -> str:
    import datetime as dt

    return dt.datetime.fromtimestamp(mtime).isoformat(timespec="seconds")


def render_markdown(payload: dict) -> str:
    rows = payload["artifacts"]
    lines = [
        "# Derived Staleness Signal",
        "",
        "Dumb Layer 3.8 report. Flags `_DERIVED/` artifacts whose sources are newer than the artifact.",
        "",
        "It never regenerates, fixes, or edits derived artifacts.",
        "",
        "## Summary",
        "",
        f"- Vault root: `{payload['vault_root']}`",
        f"- Vault type: `{payload['vault_type']}`",
        f"- Artifacts checked: {len(rows)}",
        f"- CURRENT: {sum(1 for r in rows if r['status'] == 'CURRENT')}",
        f"- STALE: {sum(1 for r in rows if r['status'] == 'STALE')}",
        f"- UNKNOWN/MISSING: {sum(1 for r in rows if r['status'] in {'UNKNOWN', 'MISSING'})}",
        "",
        "## Design Choice",
        "",
        "The tool records generation-marker text when an artifact exposes it, but current artifacts do not carry comparable source-state hashes. Freshness is therefore decided by filesystem mtime fallback. This can over-flag after manual edits or copies, but it is a safe dumb signal: it does not understate drift when a source is newer.",
        "",
        "## Artifact Status",
        "",
        "| artifact | status | method | sources | newer sources |",
        "|---|---|---|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['artifact']}` | {row['status']} | {escape(row.get('method', ''))} | "
            f"{row['source_count']} | {len(row.get('newer_sources', []))} |"
        )
    lines.extend(["", "## Stale Details", ""])
    stale_rows = [r for r in rows if r["status"] == "STALE"]
    if not stale_rows:
        lines.append("No stale artifacts flagged.")
    for row in stale_rows:
        lines.extend([
            f"### `{row['artifact']}`",
            "",
            f"- Artifact mtime: `{row.get('artifact_mtime_iso', '')}`",
            f"- Newest source mtime: `{row.get('newest_source_mtime_iso', '')}`",
            f"- Source policy: {row['source_policy']}",
            f"- Generation marker: {row.get('generation_marker') or 'none'}",
            "",
            "| newer source | source mtime |",
            "|---|---|",
        ])
        for source in row.get("newer_sources", [])[:50]:
            lines.append(f"| `{source['path']}` | `{source['source_mtime_iso']}` |")
        omitted = len(row.get("newer_sources", [])) - 50
        if omitted > 0:
            lines.append(f"| ... | {omitted} more newer source(s) omitted from Markdown; see JSON |")
        lines.append("")
    unknown_rows = [r for r in rows if r["status"] in {"UNKNOWN", "MISSING"}]
    if unknown_rows:
        lines.extend(["## Unknown / Missing", ""])
        for row in unknown_rows:
            lines.append(f"- `{row['artifact']}`: {row['status']} ({len(row.get('missing_sources', []))} missing source paths)")
    lines.append("")
    return "\n".join(lines)


def escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault-root", default=None)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--json", default=str(DEFAULT_JSON_PATH))
    args = parser.parse_args(argv)

    config = load_config(pathlib.Path(args.config))
    config["_config_path"] = str(pathlib.Path(args.config))
    root = pathlib.Path(args.vault_root or config["vault_root"]).resolve()
    if not root.is_dir():
        print(f"vault root not found: {root}", file=sys.stderr)
        return 2
    specs, vault_type = discover_specs(root, config)
    artifacts = [evaluate_spec(root, spec) for spec in specs]
    payload = {
        "schema_version": 1,
        "tool": "tools/wiki_deriver/derived_staleness_signal.py",
        "vault_root": str(root),
        "vault_type": vault_type,
        "artifacts": artifacts,
    }
    report_path = (root / args.report).resolve()
    json_path = (root / args.json).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    report_path.write_text(render_markdown(payload), encoding="utf-8", newline="\n")
    stale = sum(1 for row in artifacts if row["status"] == "STALE")
    unknown = sum(1 for row in artifacts if row["status"] in {"UNKNOWN", "MISSING"})
    print(f"checked {len(artifacts)} artifacts in {root}")
    print(f"stale={stale} unknown_or_missing={unknown}")
    print(f"wrote {report_path}")
    print(f"wrote {json_path}")
    return 1 if stale or unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())
