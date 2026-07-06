# NT8lab — Bootstrap for new sessions

This directory holds the live trading research workspace. New Codex
sessions should self-orient by reading the core bootstrap files in order
before doing any work:

1. **`AGENTS.md`** (this file) — pointers and read-order
2. **`ninja-traitorate-methodology-reference.md`** — framework authority
   for the project (see the file itself for its current length and
   section list). The methodology is the durable asset; strategies come
   and go.
3. **`_PROJECT_ALTITUDE_MAP.md`** - current high-level map of the live
   research fronts. Read this before choosing a next task so the session
   does not tunnel into one probe, one strategy, or one stale fleet
   framing.
4. **`_FRAMEWORK/PATTERNS.md`** -- project-agnostic
   research-with-agents discipline patterns. Read once per session as
   supplementary framework material. Patterns are general;
   project-specific methodology in
   `ninja-traitorate-methodology-reference.md` wins on conflicts.
5. **`_FRAMEWORK/OPERATIONS.md`** — cross-agent operational notes (how
   the wiki_logger and shared-vs-private memory work). Read once per
   session.
   Deferred derived-layer tooling candidates live in
   `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`; route there
   rather than expanding the bootstrap door.
6. **`file_inventory.md`** — index of available context: what scripts
   live where, what data is in `databento/`, what bucket-usage trackers
   exist, what's in `session_history/downloads_archive/`.
7. **`ninja-traitorate-traders-frame-v5.md`** — active strategic spine
   and methodology-lock reference for the per-trade empirical fleet.

After reading those core files, check **`session_history/`** for the most
recent dated checkpoint, plus **`session_history/downloads_archive/`**
for the historical archive (see `file_inventory.md` for the session-by-
session index).

## Authority

`ninja-traitorate-methodology-reference.md` is the framework authority for
all methodology questions (bucket discipline, criteria calibration,
robustness gates, deployability tags). If a session checkpoint contradicts
the methodology reference, the methodology wins — checkpoints record
findings, not rule changes. Methodology updates go in the reference file
itself.

## Working directories

- Live work: `C:\VMShare\NT8lab\` (this directory)
- Realsim outputs: `C:\VMShare\NT8lab\prj_realsim\`
- 1-second OHLCV data: `C:\VMShare\NT8lab\databento\MNQ\ohlcv-1s\`
- Per-session checkpoints: `C:\VMShare\NT8lab\session_history\`
- Past conversations/session tape: `C:\VMShare\conversation_archive`
  (read-only). Search it cold when asked about prior discussions.
  Extracts and scratch go in `codex_tmp/` (untracked), never as new
  tracked vault files.

## Layer 1 writer conventions

- Quantitative claims copied from source artifacts need an anchor: source
  path, section if useful, and as-of date.
- Point to statuses/verdicts/numbers instead of restating them; if prose
  must restate one, anchor it. Structured fields and report headers are
  the source; prose is a projection.

## Runtime / Environment

Before any DBN load, bridge replay, or data-load test, verify the real
Databento Python package is active:

```powershell
python tools\env_check\databento_preflight.py
```

If it fails, install the pinned runtime deps for the active Python:

```powershell
python -m pip install -r nb_lib\requirements_runtime.txt
```

Important shadowing trap: this workspace contains a `databento\` DATA
folder. When the real `databento` package is missing, running Python
from the workspace root can import that data folder as a namespace
package. Symptom: `databento.DBNStore` is missing and DBN loads fail.
Mitigation: install/activate the real package, or run from a script/app
folder with the installed package ahead of the workspace root on
`sys.path`; the preflight script prints the resolved import path so this
does not need to be re-diagnosed.

## Git / wiki_logger abstraction

Treat Git capture as background infrastructure. The human-run
`wiki_logger` owns routine commits; worker agents should write the
requested files and reports, then stop. Do not include "no commit",
"left dirty", "logger will capture", or similar Git-status boilerplate
in ordinary task reports or final summaries.

Only talk about Git when the task itself is about capture/history, when
the operator explicitly asks whether something was committed, or when a
Git state blocks the requested work. In normal research/build work,
report the artifact paths and findings; leave repository capture out of
the foreground.

## Most recent checkpoint

For the most recent checkpoint, take the newest dated `*.md` in
`session_history/`. For current project state (the broader picture a
single checkpoint cannot give), read `_PROJECT_ALTITUDE_MAP.md`, which
carries a dated current-state block. The historical session archive
lives in `session_history/downloads_archive/` — see `file_inventory.md`
for the session-by-session index.

## Canonical methodology reference

The root `ninja-traitorate-methodology-reference.md` was promoted on
2026-04-28 from the archive's `(2).md` revision (40,179 bytes,
hash `6f6757019c581b76e185beb1a7a16987`). The two older revisions
(`(1).md` 32,510 bytes; the original 23,409 bytes) remain in the archive
as historical record. If you find another `methodology-reference*.md`
in the archive with a newer mtime AND larger size, promote it the same
way (overwrite the root file; do not delete the archive copy).

## Canonical files (use these; ignore the rest)

The repo carries multiple revisions, .bak/.pybak siblings, and copies
under `session_history\extracted\`. Those are historical artifacts. For
any work in a current session, use ONLY the files listed here. If a
script or config in another location looks newer or different, treat it
as historical until you've confirmed otherwise — do NOT silently switch
to it.

| Role | Canonical path | Notes |
|---|---|---|
| Realsim engine | `C:\VMShare\NT8lab\prj_realsim_v2.py` | Project root. The older `prj_realsim.py` is retained but not canonical. |
| ATR sentinel (Python) | `C:\VMShare\NT8lab\Sentinel\atr_sentinel.py` | Live Sentinel folder. NOT `atr_sentinel.py.bak`, `atr_sentinelbak3.py`, `atr_sentinel.bak2.py`, or any `__pycache__` `.pyc`. |
| ATR history regenerator | `C:\VMShare\NT8lab\Sentinel\generate_atr_history.py` | Live Sentinel folder. NOT the copy under `session_history\extracted\PRJ_6_NoiseBrk\Sentinel\generate_atr_history.py`. |
| Databento downloader | `C:\VMShare\NT8lab\databento_downloader.py` | Project root. NOT `Sentinel\databento_downloader.py`, `Sentinel\databento_downloaderORG.py`, or `bakmarch8th26\databento_downloader.py`. |
| ATR history data file | `C:\VMShare\NT8lab\atr_history.csv` | Project-root copy is what `prj_realsim_v2.py` reads (`ATR_HISTORY_PATH` constant). The Sentinel folder also has its own `atr_history.csv` for the live system; keep the two consistent if you regenerate. |
| 1-second OHLCV store | `C:\VMShare\NT8lab\databento\MNQ\ohlcv-1s\` | The `Sentinel\data\MNQ\ohlcv-1m\` store is 1-MINUTE data for the live ATR sentinel — different schema, different purpose. |
| Databento import preflight | `C:\VMShare\NT8lab\tools\env_check\databento_preflight.py` | Run before DBN loads, bridge replays, replay viewer work, or snapshot batches. It catches the local `databento\` data-folder namespace-shadowing trap before `DBNStore` calls fail. |
| MNQ replay viewer server | `C:\VMShare\NT8lab\tools\mnq_replay_viewer\app\server.py` | Local stdlib HTTP server for forward-only manual replay and snapshot data APIs from the 1-second DBN store. Use with `tools\mnq_replay_viewer\start_replay_viewer.ps1`; docs live at `tools\mnq_replay_viewer\README.md` and `nb_lib\strategy_specs\tools\mnq_replay_viewer.md`. |
| MNQ batch snapshot exporter | `C:\VMShare\NT8lab\tools\mnq_replay_viewer\batch_snapshot.py` | Playwright exporter for strategy trade CSV review images (`1m`, `5m`, `30m`, `4h`), sidecar JSON, and `_run_summary.json`. Defaults skip OOS rows dated 2026-02-01 or later unless `--allow-oos` is deliberately set. |
| Mechanism-class screen | `C:\VMShare\NT8lab\nb_lib\screening.py` | Lightweight pre-build gate for proxy trade lists: skew/concentration, cost-distance, frequency-power, regime concentration, and cross-correlation. Use before spending build effort on new entry mechanisms. |

### Live NB strategy .cs files (PRJ_6 generation, deployed 2026-04-25)

The live NoiseBrk strategy ships as a five-file bundle. The
**`session_history\extracted\PRJ_6_NoiseBrk\`** copies are the canonical
workspace mirrors of what's deployed on the live VPS. The
`strategy_version=PRJ_6_v1_20260425` stamp in
`Sentinel\fired_YYYYMMDD_*.txt` records is the diegetic confirmation —
that string identifies these files specifically. NEWER PRJ_6 generations
(if a future PRJ_7 / PRJ_6_v2 / etc. ships) will change the stamp; if
fire records show a different stamp, find the matching extracted bundle.

| Role | Canonical path | Notes |
|---|---|---|
| Live signal brain (band logic) | `session_history\extracted\PRJ_6_NoiseBrk\PRJ_6_ANoiseBrk_AlphaSignal.cs` | The reference-price capture is here at line 439. AlphaMaster and AlphaSlave consume `Signal._openPrice` from this file rather than computing their own. |
| Live master (ATM execution) | `session_history\extracted\PRJ_6_NoiseBrk\PRJ_6_ANoiseBrk_AlphaMaster.cs` | WPF-button strategy with relay writer. |
| Live slave (relay follower) | `session_history\extracted\PRJ_6_NoiseBrk\PRJ_6_ANoiseBrk_AlphaSlave.cs` | One instance per non-master account. |
| Execution exporter | `session_history\extracted\PRJ_6_NoiseBrk\PRJ_6_ExecutionExporter.cs` | Daily NT8-execution → portable CSV. AddOn. |
| Trade logger | `session_history\extracted\PRJ_6_NoiseBrk\PRJ_6_TradeLogger.cs` | Apex-friendly decision audit. AddOn (static utility class). |

NOT canonical for live:
- `Sentinel\ANoiseBrkSignal_vps.cs` and its byte-identical sibling under
  `extracted\PRJ_6_NoiseBrk\Sentinel\` (md5 `9be3a8f918…`) are the
  PRE-PRJ_6 (2026-04-16) monolith, retained as a verification artifact.
- Root `ANoiseBrkStrategycs.cs` (2026-04-10) predates PRJ_6 by two weeks.
- `ANoiseBrkVerify.cs` (root, Sentinel, extracted\Sentinel — three
  byte-identical copies, md5 `b70082958c…`) is a separate ATR-verifier
  strategy. It does NOT contain band logic.
- `extracted\PRJ_7_NoiseBRK_TrendPullback*\PRJ_7_*Backtest.cs` are
  second-engine BACKTEST verification code, not live.

### NT8 actually compiles from a different directory

The .cs files in this workspace are SOURCE files. NT8 itself compiles
whatever lives in `Documents\NinjaTrader 8\bin\Custom\Strategies\` (and
`…\AddOns\`) on the machine running the strategy. To change live
behavior, an edit to the canonical workspace .cs is necessary but NOT
sufficient: the edited file must be copied to NT8's compile directory,
NT8 must recompile, and the strategy must be re-loaded on charts. The
extracted snapshot in `session_history\…` is a recovery / inspection
copy and does not deploy itself.

### Rule of thumb

**live folder beats extracted folder** for Python (Sentinel\ wins),
**but extracted beats live folder for the PRJ_6 .cs bundle** because
that's where the deployment-version-stamped files live. **Root beats
backup**, **no-suffix beats .bak / .pybak / -ORG / numbered
duplicates**. When unsure, this AGENTS.md is the authority.
