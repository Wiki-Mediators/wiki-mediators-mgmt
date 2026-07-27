# Household Inventory Tool Contracts

Status: operational contract. This format is intentionally reusable by other
tool families: invocation, inputs, durable outputs, summary projection, and
exit semantics are explicit and mechanically testable.

## Uniform CLI contract

| Field | Rule |
|---|---|
| Full output | JSON result on stdout for success; one diagnostic on stderr for failure. |
| `--summary` | At most six lines: `STATUS`, `COMMAND`, `DETAIL`, zero-to-two `METRIC` lines, and `ARTIFACT`. |
| Status authority | One `CommandOutcome` produces both the displayed status and process exit code. |
| Exit `0` | `OK`: requested operation completed and its declared artifact was written. |
| Exit `1` | `ERROR`: unexpected runtime or infrastructure failure. |
| Exit `2` | `REFUSED`: expected validation, policy, state, or input refusal. |
| Artifact rule | Success names the primary durable artifact; failure reports `ARTIFACT: NONE`. |

A summary is a projection, never a second verdict. It cannot say `OK` when
the process exits nonzero because both values are rendered from the same
immutable outcome object.

## Reporter contracts implemented in Phase 1 step 1

All household commands first resolve `python_executable` from the gitignored
local profile; scripts never hardcode a machine path. PowerShell invocation:

```powershell
$profile = Get-Content tools\household_inventory\local_profile.json -Raw | ConvertFrom-Json
& $profile.python_executable tools\household_inventory\environment_preflight.py
& $profile.python_executable <tool-and-arguments>
```

GPU cap tasks (names profile-owned): `HouseholdGPUCap-180` runs exactly `nvidia-smi -pl 180`; `HouseholdGPUCap-restore` runs exactly `nvidia-smi -pl 250` (booked but not operational until the ordinary-account round-trip verification passes).

All household commands first resolve `python_executable` from the gitignored
local profile; scripts never hardcode a machine path. PowerShell invocation:

```powershell
$profile = Get-Content tools\household_inventory\local_profile.json -Raw | ConvertFrom-Json
& $profile.python_executable tools\household_inventory\environment_preflight.py
& $profile.python_executable <tool-and-arguments>
```

| Tool / command | Invocation | Inputs | Durable outputs | Summary metrics |
|---|---|---|---|---|
| Video prepare | `household_video_pipeline.py prepare [options] --summary` | Stage-A session ID, known location prefix, FFmpeg path, local profile/config | Run directory, frame assessments, keeper manifest, quarantined transcript/alignment, state | candidates/keepers; unusable/near-duplicates |
| Video infer | `household_video_pipeline.py infer [options] --summary` | Prepared run ID, pinned local model directory, endpoint/config | Checkpoints, telemetry, raw/deduplicated proposals, merge report, updated state | raw/merged; quarantined |
| Video reconcile | `household_video_pipeline.py reconcile [options] --summary` | Inferred run ID, current confirmed local ledger | Three reconciliation buckets, local pilot report, updated state | corroborated/unseen; novel/coverage |
| Proposal merge | `proposal_merge.py --input ... --output-dir ... --summary` | One or more proposal JSONL files, config, optional answer key | `merged_queue.jsonl`, `merge_report.json`, optional scorecard | input/output; collapsed/priority |

## Existing command inventory (documented, not changed in this step)

| Tool | Invocation / purpose | Existing exits |
|---|---|---|
| Photo intake | `household_intake.py <photo>`: explicit Stage-A preservation and checks | `0` success, `1` unexpected error, `2` refusal |
| Video intake | `household_video_intake.py <video>`: explicit MP4 preservation | `0` success, `1` unexpected error, `2` refusal |
| Confirmed records | `household_records.py observe|correct|retract|move|recall` | `0` success, `1` unexpected error, `2` refusal |
| Pantry Picker | Interactive `HOME` consumables ledger plus read-only needs-to-flyer join; full contract below | Launchers use `0` normal stop / `1` startup or runtime error; one-shot join uses uniform `0/1/2`; HTTP bridge uses explicit success/refusal status |
| Pantry lexicon growth | `pantry_lexicon.py --learn-from-decisions <decisions.json> --session <confirmation_session.json>`: mandatory post-confirmation learner; appends only confirmed/corrected labels, deduplicated | `0` success; invalid input is an unexpected error until reporter-contract adoption |
| Florence / Qwen experiment runners | Local proposal and scoring experiments | `0` success, `2` expected refusal; unexpected exceptions remain exit `1` via Python |

The inventory table does not expand Phase 1 step 1: only the pipeline,
reconciliation, and merge reporter surfaces above gained `--summary` here.

## Pantry Picker operational contract

| Field | Contract |
|---|---|
| Local launcher | `tools\household_inventory\pantry_picker\Open Pantry Picker.cmd`; invokes `start_pantry_picker.ps1`, binds `127.0.0.1:8770`, and opens the app window. |
| Phone launcher | Run `Install Phone Access.cmd` once with the Administrator prompt, then run `Open Pantry Picker on Home Network.cmd`; the latter invokes `start_pantry_picker_home_lan.ps1`. |
| Direct bridge | `<profile python_executable> tools\household_inventory\pantry_picker\server.py [--host IP] [--port PORT] [--profile PATH] [--access-token TOKEN]`. A non-loopback bind is refused unless a token of at least 24 characters is supplied. |
| Needs/flyer join | `<profile python_executable> tools\household_inventory\pantry_picker\pantry_flyer_join.py run --site HOME --config tools\local_deals\local_deals.config.json [--summary]`. |
| Candidate acceptance | `<profile python_executable> tools\household_inventory\pantry_picker\pantry_flyer_join.py accept --candidate-file PATH --candidate-id ID [--summary]`; this is an explicit operator action and writes only the local-deals shopping-list event stream. |
| Inputs | Gitignored `tools\household_inventory\local_profile.json`; `pantry_catalog.json`; append-only pantry ledger projection; config-owned local-deals matching policy; operator-selected site; explicit browser actions. |
| Pantry output | `<artifact_root>\ledger\pantry_events.jsonl`, where `artifact_root` comes only from the local profile. Browser storage is a recoverable draft, not confirmed state. |
| Local-deals outputs | Dated needs, raw flyer snapshot, normalized offers, pending candidates, ambiguity-review queue, run manifest, and append-only accepted-shopping-list events under `C:\VMShare\local-deals\`. No local-deals artifact may be written inside the vault. |
| Pantry write boundary | Only `POST /api/events` after **Save to ledger** may append `pantry-ledger-v1` events. Needs derivation, flyer fetching, candidate creation, and candidate acceptance must not call the pantry append function or alter `pantry_events.jsonl`. |
| LAN boundary | Local mode needs no token because it binds loopback only. Phone mode binds the home LAN only for the launcher session, generates a random token placed in the URL fragment, requires the token in `X-Pantry-Token` for protected API calls, and stops when the launcher closes. |
| Firewall boundary | `Pantry Picker (Private Home LAN)` permits only the configured household Python executable, TCP 8770, Windows Private profile, and `LocalSubnet`. No router forwarding or internet exposure is part of the contract. |
| HTTP outcomes | `200` success; `400` validation refusal; `403` missing/invalid LAN token or origin; `404` unknown route; `413` oversized request. |
| Process exits | `0 OK`; `1 ERROR` for unexpected runtime/infrastructure failure; `2 REFUSED` for expected validation, policy, state, schema, or input refusal. Interactive launchers return `0` on normal operator stop and nonzero on startup/runtime failure. |
| `--summary` | One-shot join and acceptance commands emit at most six lines from the same immutable outcome that owns the process exit: `STATUS`, `COMMAND`, `DETAIL`, zero-to-two `METRIC` lines, and `ARTIFACT`. Interactive launchers are long-running and do not accept `--summary`; `/api/health` is their machine-readable readiness surface. |

Candidate acceptance is not pantry replenishment. An accepted flyer deal enters
only the append-only shopping-list event stream; the operator must still use
the existing Pantry Picker count controls and **Save to ledger** after a real
purchase is physically on site.
