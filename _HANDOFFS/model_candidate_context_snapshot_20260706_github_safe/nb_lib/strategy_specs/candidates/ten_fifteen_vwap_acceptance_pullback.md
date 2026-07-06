---
name: "10:15 VWAP Acceptance Pullback"
tagline: "After the first 30-minute drive, wait for VWAP acceptance and the first pullback after 10:15."
status: "tested-informational-rejected"
created: 2026-06-21
updated: 2026-06-21
source: "Built after the fixed 10:15 opening-drive state router failed and the wiki resurfaced the older VWAP Acceptance First-Pullback Base Hit candidate."

markets: ["MNQ"]
session: "RTH"
time_of_day: "10:15-12:00 ET"
hold_duration: "intraday"

signal_type: "vwap-acceptance-continuation"
indicators: ["RTH VWAP", "ATR(14) 1-min", "EMA(8) 1-min", "opening-drive high/low"]
timeframes_used: ["1-second source", "1-minute derived"]

brackets: "structural stop, opening-drive extreme capped at 1R"
position_sizing: "fixed-risk-dollar"

implementation: "nb_lib/scripts/ten_fifteen_vwap_acceptance_pullback.py"
test_results:
  in_sample_n: 66
  in_sample_pnl_dollars: -1177.50
  in_sample_pf: 0.83
  in_sample_win_rate: 0.561
  in_sample_avg_trades_per_month: 3.9
  in_sample_max_drawdown_dollars: 1300.80
  out_of_sample_tested: false

related_candidates:
  - "ten_fifteen_opening_drive_state_router"
  - "vwap_acceptance_first_pullback_base_hit"
  - "vwap_zscore_mean_reversion_fade"
  - "vwap_stretch_snapback"

tags:
  - rth-only
  - intraday
  - vwap-based
  - opening-drive
  - pullback
  - base-hit
  - tested-informational
---

# 10:15 VWAP Acceptance Pullback

## Status

Tested-informational-rejected. OOS remained sealed.

This candidate was built as the more sophisticated version of the rough
"what happens around 10:00 / 10:15?" idea. The fixed 10:15 state router
was too blunt. The wiki already contained a more dynamic candidate,
`vwap_acceptance_first_pullback_base_hit`, but that older candidate was
closed at R1 with only a 53.1% target-first rate. This probe reused the
useful structure without relabeling the closed R1 candidate as fresh.

## Locked Test

- Window: 2024-08-01 through 2026-01-31.
- Hard OOS halt: 2026-02-01.
- Morning context: 09:30-10:00 RTH opening drive.
- No entries before 10:15 ET.
- Acceptance: at least two completed closes on one side of RTH VWAP and
  opening-drive distance at least `0.75 * ATR14`.
- Pullback: first VWAP touch within `0.20 * ATR14`, with close or
  next-bar confirmation around EMA8.
- Entry: stop-entry beyond the confirmation bar.
- Stop: structural pullback extreme, guarded to 6-28 points.
- Target: opening-drive extreme, capped at 1R.
- Max hold: 30 minutes.
- Size: $250 fixed-risk model, capped at 10 MNQ.

## Result

```text
n trades              = 66
n distinct days       = 66
Total P&L             = -$1,177.50
Profit factor         = 0.83
Win rate              = 56.1% (37W / 29L)
Mean P&L per trade    = -$17.84
Direction split       = 36 longs / 30 shorts
Best single day       = +$232.80
Worst single day      = -$272.00
Maximum drawdown      = $1,300.80
Exit reasons          = 37 tp / 28 full_stop / 1 time_exit
Average trades/month  = 3.9
```

Artifacts:

- Report: `nb_lib/probe_results/ten_fifteen_vwap_acceptance_pullback_report.md`
- Trades: `nb_lib/probe_results/ten_fifteen_vwap_acceptance_pullback_trades.csv`
- JSON: `nb_lib/probe_results/ten_fifteen_vwap_acceptance_pullback.json`
- Script: `nb_lib/scripts/ten_fifteen_vwap_acceptance_pullback.py`

## Read

The dynamic pullback construction produced a cleaner conceptual shape
than the fixed 10:15 router, but not an edge. It fired only 66 times
across the in-sample window, lost money after realistic friction, and
showed PF below 1.0.

This closes the current VWAP/opening-drive continuation branch as an
informational negative. The useful lesson is not that 10:15 is
irrelevant; it is that adding VWAP acceptance and first-pullback
structure did not rescue the opening-drive idea on MNQ under the locked
base-hit bracket.

Do not spend OOS on this branch without a new thesis.
