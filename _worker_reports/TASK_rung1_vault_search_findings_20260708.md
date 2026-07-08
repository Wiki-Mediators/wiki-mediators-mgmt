---
title: "Rung 1 Vault Search Findings"
session_ref: 019de27f-876d-71b1-a6e4-f6f670178e07
created: 2026-07-08
status: complete
---

# Rung 1 Vault Search Findings

## Review confirmation

Revision 2 of the brief addressed the review points:

- shared scorer/corpus extraction required;
- one pinned configuration;
- stale rule defined;
- artifact capped;
- pre-committed ship threshold set at miss rate <= 0.20.

One implementation nuance: "byte-identical detector verification" was treated
as semantic output parity on the headline benchmark metrics and rows, because
the refactor legitimately changes implementation location while preserving the
retrieval behavior.

## Built

- `tools/wiki_deriver/retrieval_common.py`
- `tools/wiki_deriver/build_term_cooccurrence.py`
- `tools/wiki_deriver/vault_search.py`
- `_DERIVED/term_cooccurrence.json`
- `_DERIVED/term_cooccurrence.md`
- `_DERIVED/retrieval_detector_rung1.json`
- `_DERIVED/retrieval_detector_rung1.md`

The detector was refactored to use `retrieval_common.py`, then extended with
`--use-expansion` for the Rung 1 benchmark path.

## Pinned configuration

- Context unit: blank-line-delimited paragraph.
- Term filter: shared detector stopwords, length >= 3, appears in >= 2
  contexts, appears in <= 15% of contexts.
- Association: Jaccard over paragraph context sets.
- Expansion: top 10 partners per query term.
- Expansion discount: 0.5.
- Ranking: shared `retrieval_common` scorer.

## Refactor verification

After extracting the shared scorer/corpus helpers, the lexical detector
baseline remained unchanged:

| Mode | Queries | Hits | Misses | Miss rate |
|---|---:|---:|---:|---:|
| lexical baseline | 28 | 19 | 9 | 0.321 |

## Co-occurrence artifact

First build:

- Paragraph contexts: 38,424
- Kept terms: 14,630
- Unreadable Markdown skipped: 1

Verification build during the report pass:

- Paragraph contexts: 38,455
- Kept terms: 14,637
- Unreadable Markdown skipped: 1
- JSON artifact size: 8,706,222 bytes

Implementation note: the first JSON rendering was about 19.4 MB, too large
for the "capped and inspectable" intent and potentially hostile to the vault's
size guard. The artifact format was compacted and unused partner metadata was
removed. Retrieval parameters and benchmark behavior did not change.

## Sanity check

`vault_search.py "position sizing rules"` used co-occurrence expansion. It did
expand partly toward useful bridge vocabulary (`contract`, `contracts`,
`cushion`, `risk`, `eval`, `50k`, `prop`), but also expanded toward noisy
neighbors (`march`, `that`, `one`, `working`, `automatically`). The known
answer did not land in the top 10.

This was treated as diagnostic evidence, not a tuning loop.

## One benchmark run

The single pinned Rung 1 benchmark run worsened retrieval:

| Mode | Queries | Hits | Misses | Miss rate | Ship? |
|---|---:|---:|---:|---:|---|
| lexical baseline | 28 | 19 | 9 | 0.321 | baseline |
| Rung 1 co-occurrence | 28 | 13 | 15 | 0.536 | NO |

Pre-committed ship threshold was miss rate <= 0.20. Rung 1 v1 did not ship.
No `AGENTS.md` inserts were applied.

## Per-query flips

No baseline misses became hits. Six baseline hits became misses:

| Query | Baseline | Rung 1 |
|---|---|---|
| q03_video_meanrev_rejection | HIT | MISS |
| q11_external_source_trust | HIT | MISS |
| q14_archive_why | HIT | MISS |
| q15_agent_intake_quarantine | HIT | MISS |
| q23_session_reference_index | HIT | MISS |
| q25_source_census | HIT | MISS |

## Roadmap update

Roadmap 3.9 now records: Rung 1 v1 built and measured, not shipped; benchmark
worsened from 9/28 misses to 15/28 misses; ladder advancement returns to the
operator before LSA or embeddings.

## Verdict

RUNG1_V1_NO_SHIP. The implementation is useful as a probe artifact, but the
naive paragraph/Jaccard expansion is too noisy to route into agent workflow.

## Follow-up: why v1 got worse, and v3 recovery

Post-failure inspection showed the cause was not lack of bridge terms. The
right targets often existed in the expanded pool but were buried far below the
top 10 (`q01` target rank 108, `q06` rank 155, `q13` rank 478). Naive
expansion also let hub notes outrank precise notes.

Two follow-up modes were tested after operator approval:

| Mode | Shape | Hits | Misses | Miss rate | Read |
|---|---|---:|---:|---:|---|
| Rung 1 v2 | lexical top 10 protected; co-occurrence only as recall suggestions | 19 | 9 | 0.321 | safe but flat |
| Rung 1 v3 | v2 plus link-neighbor suggestions from surfaced files | 24 | 4 | 0.143 | strong candidate, not auto-routed |

V3 recovered five baseline misses and regressed none:

| Query | Recovered known answer |
|---|---|
| q08_stale_generated_views | `_FRAMEWORK/drift_reduction_program_20260706.md`; `_worker_reports/BUILD_3_8_derived_staleness_signal_20260630.md` |
| q12_oos_delayed_be_result | `step3_v03_oos_deployable_size_validation_protocol.md` |
| q13_capture_portability | `_FRAMEWORK/capture_tool_spec.md` |
| q20_research_instruments | `AGENTS.md` |
| q28_secret_scan_push_gate | `tools/management_bridge/README.md` |

Remaining misses:

- q01_account_size_allocation
- q06_machine_migration
- q26_regime_attribution
- q27_drift_reduction

V3 clears the earlier ship threshold of miss rate <= 0.20, but it does not
clear the ladder's 10% aspiration. Because link-neighbor assist was introduced
after diagnosing the v1 failure, routing through `AGENTS.md` should wait for
operator approval.

## Supplemental example check

After the v3 recovery, the operator asked for a few more examples. A
12-query exploratory supplemental set was created under `codex_tmp/` and kept
out of the committed benchmark.

| Set | Mode | Hits | Misses | Miss rate |
|---|---|---:|---:|---:|
| supplemental examples | lexical baseline | 11 | 1 | 0.083 |
| supplemental examples | v3 expanded + link-neighbor assist | 12 | 0 | 0.000 |

The single recovered supplemental query was:

| Query | Recovered known answer |
|---|---|
| x09_agent_state_snapshot | `_DERIVED/orientation_digest.md` |

Read: the extra examples did not stress the system as hard as the committed
28-query benchmark, but they confirm the v3 shape does not obviously harm
ordinary operator-style retrieval and can recover at least one generated-view
target that lexical alone missed.

## Follow-up: driverless structural aliases

The operator asked whether the tool could improve without becoming a
hand-maintained synonym table. A v4 structural assist was tested using only
already-authored structure:

- path / filename words;
- selected frontmatter fields (`title`, `status`, `related`,
  `executes_spec`, `vault_destination`, `artifact_type`, `source`, `purpose`,
  `home`, `tagline`);
- Markdown headings.

No manual alias pairs were added.

| Mode | Shape | Hits | Misses | Miss rate |
|---|---|---:|---:|---:|
| lexical baseline | original detector | 19 | 9 | 0.321 |
| v3 | lexical protected + co-occurrence recall + link-neighbor assist | 24 | 4 | 0.143 |
| v4 | v3 + structural aliases from authored structure | 26 | 2 | 0.071 |

V4 recovered two more misses beyond v3:

| Query | Recovered known answer |
|---|---|
| q01_account_size_allocation | `prop_account_stage_deployment_map_2026_06.md` |
| q27_drift_reduction | `_FRAMEWORK/drift_reduction_program_20260706.md` |

Remaining misses:

- q06_machine_migration
- q26_regime_attribution

Read: v4 clears the 10% detector bar without hand-maintained synonyms. Because
it was developed after inspecting benchmark failures, it should get cold review
or a fresh supplemental challenge set before becoming the default search door.

## Supplemental 60-query confirmation

The operator asked for a larger confirmation set. An initial broad 60-query
draft included code/config targets, which was rejected as a bad yardstick
because the current detector searches Markdown notes. A clean Markdown-only
60-query set was then generated under `codex_tmp/`, excluding `_DERIVED/` and
other skipped directories.

| Set | Mode | Hits | Misses | Miss rate | Verdict |
|---|---|---:|---:|---:|---|
| 60-query Markdown-only challenge | lexical baseline | 53 | 7 | 0.117 | TRIGGER-EVIDENCE |
| 60-query Markdown-only challenge | v3 expanded + link-neighbor assist | 55 | 5 | 0.083 | TRIGGER-NOT-FIRED |
| 60-query Markdown-only challenge | v4 + structural aliases | 57 | 3 | 0.050 | TRIGGER-NOT-FIRED |

V4 remaining misses:

- c23_regime_panel -> `_worker_reports/TASK_regime_attribution_panel_20260706.md`
- c25_orientation_digest_build -> `_worker_reports/TASK_020_orientation_digest_build.md`
- c29_sync_boundary -> `_worker_reports/CONSULT_sync_set_boundary_proposal.md`

Read: on a larger fresh Markdown-only challenge, v4 stayed below the 10% miss
bar and improved over baseline by 6.7 percentage points. The remaining misses
are fine-grained worker-report selection problems rather than broad topic
blindness: the search lands near composition nodes, ground-truth snapshot /
orientation digest material, and management-bridge boundary material, but not
the exact expected worker report.

## Two-lane intake/periphery search probe

The operator asked whether a future v5 could let agents search the organized
vault and a broader loose-information area without promoting the loose files.
A scratch probe (`codex_tmp/two_lane_search_probe.py`) tested that shape:

- left lane: VAULT, durable workspace Markdown;
- right lane: PERIPHERY, read-only `.md` / `.txt` files from an explicit
  external root;
- every result carries its lane, score, path, and matched terms;
- periphery matches are explicitly intake-only and are not promoted.

Sample query: `best MNQ strategy candidates profit factor robustness`.

| Periphery root | Vault docs scanned | Periphery docs scanned | Vault hits | Periphery hits | Read |
|---|---:|---:|---:|---:|---|
| `C:\VMShare` | 740 | 2387 | 8 | 8 | Mechanically works, but too broad: it rediscovers working-vault files and handoff snapshots as "periphery." |
| `C:\Users\meme\Downloads` | 740 | 343 | 8 | 8 | Better small sample: vault lane found banked candidate/source notes; periphery lane found loose Downloads prompts/artifacts, clearly unpromoted. |

Read: the two-lane design is viable and matches the intake discipline better
than automatic import. A real v5 should use explicit periphery roots with
default deny rules for the working vault, management mirrors, handoff snapshots,
archives, and generated/cache folders. It should remain read-only and require a
separate explicit "bank this" action before any periphery file enters the vault.

## Config-owned two-lane probe

The operator correctly pushed back that "explicit roots / deny mirrors / label
lanes / never promote" must not become agent chores. A second scratch probe
tested the stricter shape:

- config file owns `vault_root`, `periphery_roots`, `deny_roots`, allowed
  extensions, max file size, and lane contracts;
- agent supplies only the query;
- output includes a scope receipt with scanned/skipped roots;
- periphery remains read-only intake and cannot be promoted by the search tool.

Prototype files:

- `codex_tmp/two_lane_search_configured_probe.py`
- `codex_tmp/two_lane_search_config.json`

Happy-path test:

| Query | Configured periphery | Vault docs | Periphery docs | Vault hits | Periphery hits |
|---|---|---:|---:|---:|---:|
| `best MNQ strategy candidates profit factor robustness` | `C:\Users\meme\Downloads` | 740 | 343 | 8 | 8 |

Bad-config safety test:

| Configured periphery | Result |
|---|---|
| `C:\VMShare\NT8lab` | skipped with receipt: `denied by configured root: C:\VMShare\NT8lab`; periphery docs scanned = 0 |

Read: yes, this can remain a dumb tool. The durable v5 design should make the
tool own lane separation, deny roots, labels, and receipts; agents should only
issue the query and read the two-lane result. Promotion/import remains a
separate explicit tool/action, not a side effect of search.

## Rung 1 v5 production build

Built the config-owned two-lane search door:

- `tools/wiki_deriver/two_lane_search.py`
- `tools/wiki_deriver/vault_search_config.json`
- `tools/wiki_deriver/vault_search.py --two-lane`
- generated output: `_DERIVED/two_lane_search_last.json` and
  `_DERIVED/two_lane_search_last.md`

The config owns `vault_root`, `periphery_roots`, `deny_roots`, allowed
extensions, max file size, lane labels, and the scope receipt. The agent supplies
only the query. Periphery results remain read-only intake; the tool never
promotes, copies, moves, imports, or rewrites them.

Production validation:

| Test | Result |
|---|---|
| Direct `two_lane_search.py` happy path | scanned 740 vault Markdown docs, 343 Downloads `.md/.txt` periphery docs, 8 vault hits, 8 periphery hits |
| `vault_search.py --two-lane` integration | scanned 740 vault Markdown docs, 343 Downloads `.md/.txt` periphery docs, 10 vault hits, 10 periphery hits |
| bad periphery root `C:\VMShare\NT8lab` | skipped with receipt `denied by configured root: C:\VMShare\NT8lab`; periphery docs scanned = 0 |
| existing v4 search smoke | still runs through the original recall/link-neighbor/structural-assist path |
| compile check | `py_compile` passed for `two_lane_search.py` and `vault_search.py` |

One Windows-specific fix landed during testing: the config loader accepts
`utf-8-sig` because Windows PowerShell 5 may create JSON files with a UTF-8 BOM.
