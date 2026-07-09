"""Config-owned two-lane vault/periphery search.

This is intentionally dumb infrastructure: compute from configured roots,
label provenance lanes, emit a scope receipt, and never promote or modify
periphery files.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
from collections import Counter
from typing import Any


DEFAULT_CONFIG = pathlib.Path("tools/wiki_deriver/vault_search_config.json")
DEFAULT_JSON = pathlib.Path("_DERIVED/two_lane_search_last.json")
DEFAULT_MD = pathlib.Path("_DERIVED/two_lane_search_last.md")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does",
    "for", "from", "get", "happen", "happens", "how", "if", "in", "is",
    "it", "of", "on", "only", "or", "our", "the", "this", "to", "two",
    "we", "what", "when", "where", "why", "with",
}

VAULT_SKIP_DIRS = {
    ".git",
    ".agents",
    ".codex",
    ".obsidian",
    "__pycache__",
    "_snapshots",
    "_HANDOFFS",
    "codex_tmp",
    "databento",
    "node_modules",
    "tools/wiki_logger/runtime",
}

VAULT_SKIP_FILES = {
    "_DERIVED/two_lane_search_last.md",
}


def norm(path: pathlib.Path) -> str:
    return str(path.resolve()).rstrip("\\/").lower()


def is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z0-9_]+", text)]


def query_terms(query: str) -> list[str]:
    terms = set()
    for token in tokenize(query):
        if len(token) < 3 or token in STOPWORDS:
            continue
        terms.add(token)
        if token.endswith("s") and len(token) > 4:
            terms.add(token[:-1])
        else:
            terms.add(token + "s")
        if token.endswith("ing") and len(token) > 6:
            terms.add(token[:-3])
        if token.endswith("ed") and len(token) > 5:
            terms.add(token[:-2])
    return sorted(terms)


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def should_skip_vault(vault_root: pathlib.Path, path: pathlib.Path) -> bool:
    rel = path.relative_to(vault_root).as_posix()
    if rel in VAULT_SKIP_FILES:
        return True
    return any(rel == d or rel.startswith(d.rstrip("/") + "/") for d in VAULT_SKIP_DIRS)


def iter_vault_docs(vault_root: pathlib.Path) -> list[pathlib.Path]:
    out = []
    for path in vault_root.rglob("*.md"):
        if should_skip_vault(vault_root, path):
            continue
        out.append(path)
    return sorted(out, key=lambda p: p.relative_to(vault_root).as_posix().lower())


def iter_periphery_docs(
    root: pathlib.Path,
    extensions: set[str],
    max_bytes: int,
    deny_roots: list[pathlib.Path],
) -> tuple[list[pathlib.Path], str | None]:
    if not root.exists():
        return [], "missing"
    for deny in deny_roots:
        if norm(root) == norm(deny) or is_under(root, deny) or is_under(deny, root):
            return [], f"denied by configured root: {deny}"
    out = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        if any(is_under(path, deny) for deny in deny_roots):
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
        except OSError:
            continue
        out.append(path)
    return sorted(out, key=lambda p: str(p).lower()), None


def build_doc(path: pathlib.Path, lane: str, display_root: pathlib.Path) -> dict[str, Any] | None:
    try:
        text = read_text(path)
    except OSError:
        return None
    try:
        rel = path.relative_to(display_root).as_posix()
    except ValueError:
        rel = str(path)
    path_text = rel.replace("/", " ").replace("_", " ").replace("-", " ")
    tokens = tokenize(text)
    return {
        "lane": lane,
        "path": rel,
        "absolute_path": str(path.resolve()),
        "body_counts": Counter(tokens),
        "path_counts": Counter(tokenize(path_text)),
        "title_counts": Counter(tokenize(path.stem.replace("_", " ").replace("-", " "))),
        "token_count": len(tokens),
    }


def score_doc(doc: dict[str, Any], terms: list[str]) -> float:
    score = 0.0
    for term in terms:
        tf = doc["body_counts"].get(term, 0)
        path_tf = doc["path_counts"].get(term, 0)
        title_tf = doc["title_counts"].get(term, 0)
        if tf:
            score += 1.0 + math.log(tf)
        if title_tf:
            score += 3.0 * title_tf
        if path_tf:
            score += 2.0 * path_tf
    if score and doc["token_count"]:
        score /= 1.0 + math.log(doc["token_count"])
    return score


def search_docs(docs: list[dict[str, Any]], query: str, limit: int) -> list[dict[str, Any]]:
    terms = query_terms(query)
    rows = []
    for doc in docs:
        score = score_doc(doc, terms)
        if score <= 0:
            continue
        rows.append({
            "lane": doc["lane"],
            "path": doc["path"],
            "absolute_path": doc["absolute_path"],
            "score": round(score, 6),
            "matched_terms": sorted(term for term in terms if (
                doc["body_counts"].get(term, 0)
                or doc["path_counts"].get(term, 0)
                or doc["title_counts"].get(term, 0)
            )),
        })
    rows.sort(key=lambda r: (-r["score"], r["path"].lower()))
    return rows[:limit]


def load_config(root: pathlib.Path, config_path: pathlib.Path) -> dict[str, Any]:
    if not config_path.is_absolute():
        config_path = root / config_path
    return json.loads(config_path.read_text(encoding="utf-8-sig"))


def run_two_lane_search(
    query: str,
    root: pathlib.Path,
    config_path: pathlib.Path = DEFAULT_CONFIG,
    limit: int = 8,
) -> dict[str, Any]:
    if not config_path.is_absolute():
        config_path = root / config_path
    config = load_config(root, config_path)
    vault_root = pathlib.Path(config["vault_root"]).resolve()
    deny_roots = [pathlib.Path(p).resolve() for p in config.get("deny_roots", [])]
    extensions = {str(ext).lower() for ext in config.get("periphery_extensions", [".md", ".txt"])}
    max_bytes = int(config.get("max_file_bytes", 500000))

    vault_docs = [
        doc for path in iter_vault_docs(vault_root)
        if (doc := build_doc(path, "VAULT", vault_root))
    ]
    periphery_docs = []
    receipts = []
    for root_text in config.get("periphery_roots", []):
        periphery_root = pathlib.Path(root_text).resolve()
        paths, skipped_reason = iter_periphery_docs(periphery_root, extensions, max_bytes, deny_roots)
        status = "scanned" if skipped_reason is None else f"skipped: {skipped_reason}"
        receipts.append({"root": str(periphery_root), "status": status, "docs_scanned": len(paths)})
        for path in paths:
            doc = build_doc(path, "PERIPHERY", periphery_root)
            if doc:
                periphery_docs.append(doc)

    return {
        "schema_version": 1,
        "tool": "tools/wiki_deriver/two_lane_search.py",
        "query": query,
        "config_path": str(config_path.resolve()),
        "vault_root": str(vault_root),
        "deny_roots": [str(p) for p in deny_roots],
        "lane_contract": config.get("lane_contract", {}),
        "periphery_root_receipts": receipts,
        "vault_scanned": len(vault_docs),
        "periphery_scanned": len(periphery_docs),
        "results": {
            "VAULT": search_docs(vault_docs, query, limit),
            "PERIPHERY": search_docs(periphery_docs, query, limit),
        },
        "promotion_boundary": "Periphery results are searchable intake only. Search never copies, moves, imports, promotes, or rewrites them.",
    }


def render_text(data: dict[str, Any]) -> str:
    lines = [
        "TWO-LANE SEARCH",
        f"QUERY {data['query']}",
        "",
        "SCOPE RECEIPT",
        f"  config: {data['config_path']}",
        f"  vault_root: {data['vault_root']}",
        f"  vault_docs_scanned: {data['vault_scanned']}",
        f"  periphery_docs_scanned: {data['periphery_scanned']}",
        "  periphery_roots:",
    ]
    for row in data["periphery_root_receipts"]:
        lines.append(f"    - {row['root']} | {row['status']} | docs={row['docs_scanned']}")
    lines += ["", "VAULT - " + data["lane_contract"].get("VAULT", "")]
    for index, row in enumerate(data["results"]["VAULT"], 1):
        terms = ", ".join(row["matched_terms"])
        lines.append(f"{index:02d}. {row['score']:.6f} {row['path']} [{terms}]")
    lines += ["", "PERIPHERY - " + data["lane_contract"].get("PERIPHERY", "")]
    for index, row in enumerate(data["results"]["PERIPHERY"], 1):
        terms = ", ".join(row["matched_terms"])
        lines.append(f"{index:02d}. {row['score']:.6f} {row['absolute_path']} [{terms}]")
    lines += ["", "PROMOTION BOUNDARY", data["promotion_boundary"]]
    return "\n".join(lines)


def render_md(data: dict[str, Any]) -> str:
    lines = [
        "# Two-Lane Search",
        "",
        f"Query: `{data['query']}`",
        "",
        "Agent contract: the agent supplies only the query. The tool owns lane labels, deny roots, scope receipt, and the intake-only boundary.",
        "",
        "## Scope Receipt",
        "",
        f"- Config: `{data['config_path']}`",
        f"- Vault root: `{data['vault_root']}`",
        f"- Vault docs scanned: {data['vault_scanned']}",
        f"- Periphery docs scanned: {data['periphery_scanned']}",
        f"- Deny roots: {', '.join('`' + p + '`' for p in data['deny_roots'])}",
        "",
        "### Periphery Roots",
        "",
        "| Root | Status | Docs scanned |",
        "|---|---|---:|",
    ]
    for row in data["periphery_root_receipts"]:
        lines.append(f"| `{row['root']}` | {row['status']} | {row['docs_scanned']} |")
    lines.append("")
    for lane in ["VAULT", "PERIPHERY"]:
        lines += [f"## {lane}", "", data["lane_contract"].get(lane, ""), ""]
        rows = data["results"][lane]
        if not rows:
            lines += ["No matches.", ""]
            continue
        lines += ["| Rank | Score | Path | Matched terms |", "|---:|---:|---|---|"]
        for idx, row in enumerate(rows, 1):
            path = row["path"] if lane == "VAULT" else row["absolute_path"]
            lines.append(
                f"| {idx} | {row['score']:.6f} | `{path}` | {', '.join(row['matched_terms'])} |"
            )
        lines.append("")
    lines += ["## Promotion Boundary", "", data["promotion_boundary"], ""]
    return "\n".join(lines)


def write_outputs(root: pathlib.Path, data: dict[str, Any],
                  json_path: pathlib.Path = DEFAULT_JSON,
                  md_path: pathlib.Path = DEFAULT_MD) -> None:
    if not json_path.is_absolute():
        json_path = root / json_path
    if not md_path.is_absolute():
        md_path = root / md_path
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_md(data), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json-out", default=str(DEFAULT_JSON))
    parser.add_argument("--md-out", default=str(DEFAULT_MD))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    data = run_two_lane_search(args.query, root, pathlib.Path(args.config), args.limit)
    write_outputs(root, data, pathlib.Path(args.json_out), pathlib.Path(args.md_out))
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(render_text(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
