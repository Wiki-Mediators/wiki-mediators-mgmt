"""Search the vault with optional corpus-derived query expansion."""
from __future__ import annotations

import argparse
import json
import pathlib

from retrieval_common import (
    build_corpus,
    expand_query_terms,
    is_cooccurrence_stale,
    link_neighbor_suggestions,
    load_term_cooccurrence,
    query_terms,
    retrieve_weighted,
    structural_alias_suggestions,
)

from two_lane_search import render_text as render_two_lane_text
from two_lane_search import run_two_lane_search, write_outputs as write_two_lane_outputs


DEFAULT_COOCCURRENCE = pathlib.Path("_DERIVED/term_cooccurrence.json")
DEFAULT_QUERY_FILE = pathlib.Path("tools/wiki_deriver/retrieval_test_queries.json")
EXPANSION_DISCOUNT = 0.5
EXPANSION_PARTNERS = 10


def search(root: pathlib.Path, query: str, top_k: int, cooccurrence_path: pathlib.Path,
           query_file: pathlib.Path, recall_assist: bool = False,
           link_neighbor_assist: bool = False,
           structural_assist: bool = False) -> dict:
    corpus, unreadable = build_corpus(root)
    terms = query_terms(query)
    stale, reason = is_cooccurrence_stale(root, cooccurrence_path, query_file)
    cooccurrence = None if stale else load_term_cooccurrence(cooccurrence_path)
    weighted_terms, expansions = expand_query_terms(
        terms,
        cooccurrence,
        top_n=EXPANSION_PARTNERS,
        discount=EXPANSION_DISCOUNT,
    )
    lexical_results = None
    suggestions = []
    if recall_assist and cooccurrence is not None:
        lexical_results = retrieve_weighted(corpus, {term: 1.0 for term in terms}, top_k)
        lexical_paths = {r["path"] for r in lexical_results}
        expanded_pool = retrieve_weighted(corpus, weighted_terms, top_k * 5)
        suggestions = [r for r in expanded_pool if r["path"] not in lexical_paths][:top_k]
        results = lexical_results + suggestions
    else:
        results = retrieve_weighted(corpus, weighted_terms, top_k)
    related = []
    if link_neighbor_assist:
        base_related = link_neighbor_suggestions(root, [r["path"] for r in results], limit=top_k * 5)
        related = list(base_related)
        if structural_assist and cooccurrence is not None:
            link_source_paths = [r["path"] for r in lexical_results] + [
                r["path"] for r in retrieve_weighted(corpus, weighted_terms, top_k * 5)
            ]
            seen_related = {r["path"] for r in related}
            for link_item in link_neighbor_suggestions(root, link_source_paths, limit=top_k * 20):
                if link_item["path"] not in seen_related:
                    related.append(link_item)
                    seen_related.add(link_item["path"])
        results = results + related
    alias_rows = []
    if structural_assist:
        existing_paths = {r["path"] for r in results}
        alias_rows = structural_alias_suggestions(root, terms, corpus, existing_paths, limit=top_k * 5)
        results = results + alias_rows
    return {
        "query": query,
        "mode": "lexical" if stale else ("cooccurrence_recall_assist" if recall_assist else "cooccurrence_expanded"),
        "degrade_reason": reason if stale else "",
        "terms": terms,
        "weighted_terms": dict(sorted(weighted_terms.items())),
        "expansions": expansions,
        "top_k": top_k,
        "results": results,
        "lexical_results": lexical_results or [],
        "recall_suggestions": suggestions,
        "related_references": related,
        "structural_alias_suggestions": alias_rows,
        "documents_scanned": len(corpus),
        "unreadable_markdown_count": len(unreadable),
        "unreadable_markdown": unreadable,
    }


def render_text(data: dict) -> str:
    lines = []
    if data["mode"] == "lexical":
        lines.append(f"MODE lexical fallback: {data['degrade_reason']}")
    else:
        lines.append(f"MODE {data['mode']}")
    lines.append(f"QUERY {data['query']}")
    lines.append("TERMS " + ", ".join(data["terms"]))
    if data["expansions"]:
        lines.append("EXPANSIONS")
        for term in sorted(data["expansions"]):
            expanded = ", ".join(
                f"{row['term']}:{row['score']:.3f}"
                for row in data["expansions"][term]
            )
            lines.append(f"  {term} -> {expanded}")
    else:
        lines.append("EXPANSIONS none")
    if data["mode"] == "cooccurrence_recall_assist":
        lines.append("LEXICAL RESULTS")
        for index, row in enumerate(data["lexical_results"], start=1):
            lines.append(f"{index:02d}. {row['score']:.6f} {row['path']}")
        lines.append("RECALL SUGGESTIONS")
        for index, row in enumerate(data["recall_suggestions"], start=1):
            lines.append(f"{index:02d}. {row['score']:.6f} {row['path']}")
    else:
        lines.append("RESULTS")
        for index, row in enumerate(data["results"], start=1):
            lines.append(f"{index:02d}. {row['score']:.6f} {row['path']}")
    if data["related_references"]:
        lines.append("RELATED REFERENCES")
        for index, row in enumerate(data["related_references"], start=1):
            lines.append(f"{index:02d}. via {row['source']} -> {row['path']}")
    if data["structural_alias_suggestions"]:
        lines.append("STRUCTURAL ALIAS SUGGESTIONS")
        for index, row in enumerate(data["structural_alias_suggestions"], start=1):
            overlaps = ", ".join(row.get("overlap_terms", []))
            lines.append(f"{index:02d}. {row['score']:.1f} {row['path']} [{overlaps}]")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--root", default=".")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--cooccurrence", default=str(DEFAULT_COOCCURRENCE))
    parser.add_argument("--query-file", default=str(DEFAULT_QUERY_FILE))
    parser.add_argument("--recall-assist", action="store_true")
    parser.add_argument("--link-neighbor-assist", action="store_true")
    parser.add_argument("--structural-assist", action="store_true")
    parser.add_argument("--two-lane", action="store_true")
    parser.add_argument("--two-lane-config", default="tools/wiki_deriver/vault_search_config.json")
    parser.add_argument("--json-out", default="_DERIVED/two_lane_search_last.json")
    parser.add_argument("--md-out", default="_DERIVED/two_lane_search_last.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    if args.two_lane:
        data = run_two_lane_search(
            args.query,
            root,
            pathlib.Path(args.two_lane_config),
            args.top_k,
        )
        write_two_lane_outputs(root, data, pathlib.Path(args.json_out), pathlib.Path(args.md_out))
        if args.json:
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(render_two_lane_text(data))
        return 0
    cooccurrence_path = pathlib.Path(args.cooccurrence)
    if not cooccurrence_path.is_absolute():
        cooccurrence_path = root / cooccurrence_path
    query_file = pathlib.Path(args.query_file)
    if not query_file.is_absolute():
        query_file = root / query_file
    data = search(
        root,
        args.query,
        args.top_k,
        cooccurrence_path,
        query_file,
        recall_assist=args.recall_assist,
        link_neighbor_assist=args.link_neighbor_assist,
        structural_assist=args.structural_assist,
    )
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(render_text(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
