---
name: "Regime Attribution Panel"
tagline: "Retroactively tag closed candidate trades by causal day-state to test whether failed strategies were tested unconditionally in regimes where they should have been routed."
status: "implemented-panel-null"
created: 2026-07-06
updated: 2026-07-06
source: "Promoted from nb_lib/strategy_specs/Untitled.md scratch note after 2026-07-06 handoff cold review."

artifact_type: "composition_node"
node_type: "regime attribution diagnostic"
markets: ["MNQ"]
session: "RTH"
produces_trades: false
oos_status: "sealed; in-sample historical attribution only unless explicitly authorized"

tags:
  - composition-node
  - regime-attribution
  - graveyard-review
  - conditional-strategy
  - not-a-strategy
---

# Regime Attribution Panel

## 1. Hypothesis

Maybe we have not been testing bad strategies. Maybe we have been testing
conditional strategies unconditionally.

This node promotes regime state from a supporting context field to the
primary diagnostic question:

```text
Do some closed candidates contain positive edge in a causal, pre-entry
market state, while bleeding enough in other states to fail when tested
unconditionally?
```

This is not a strategy and not a resurrection pass. It is a panel
diagnostic over existing closed-candidate trade logs.

## 2. Why This Earns a Place

The candidate graveyard contains many ideas with plausible mechanisms
that failed aggregate tests. The useful question is no longer only
"which new standalone entry should be built?" It is also:

```text
Was the unconditional test the wrong object?
```

If the answer is yes, the graveyard may contain regime-conditional
components that should re-enter the pipeline as new pre-registered
conditional candidates. If the answer is no, the negative MNQ result
deepens and the project should stop spending effort on unconditional
entry variants.

## 3. Output Contract

The first implementation should emit a table with one row per historical
trade from each included closed candidate:

```text
strategy_id
trade_id
entry_time
direction
pnl
candidate_original_status
day_state_primary
trend_state
rotation_state
volatility_state
opening_drive_state
above_below_vwap_or_prior_close
data_available_before_entry
```

The panel report should then aggregate each strategy by state:

```text
strategy_id
state_definition
n
net_pnl
pf
win_rate
mean_trade
corrected_significance
interpretation
```

## 4. Causal Discipline

Every state tag must be knowable before the trade entry or explicitly
declared as a descriptive post-hoc label that cannot be used as a gate.

The initial version should prefer simple causal tags over a complex
model:

- prior-day / pre-entry trend state;
- opening-range expansion versus rotation state, only after the range is
  complete;
- volatility percentile computed from prior completed sessions or from
  completed intraday bars only;
- above/below VWAP or prior close as of the completed bar before entry.

No tag may use later session outcome to explain an earlier trade unless
it is clearly marked `descriptive_only`.

## 5. Panel Discipline

This diagnostic must inherit the directional-bias atlas discipline:

- report the whole panel;
- do not select the best cell as the finding;
- apply multiple-comparison correction such as FDR or a stricter
  family-wise rule;
- report sample size beside every cell;
- treat perfect-looking cells as suspicious until checked;
- any resurrected candidate becomes a new pre-registered conditional
  candidate, not a continuation of the old failed spec.

## 6. First Targets

Priority targets:

1. ORWS / opening-range-width-switch families, because prior notes
   describe path and variance sensitivity rather than uniform no-edge.
2. Level-response and liquidity-zone candidates, because the project has
   descriptive evidence that some zones behave differently from controls.
3. Management-policy result sets, to test whether v2a / V4 / G2
   divergence is regime composition rather than substrate magic.

## 7. Implementation Result

Implemented on 2026-07-06 as a pre-committed in-sample diagnostic:

- script: `nb_lib/scripts/regime_attribution_panel.py`
- report: `nb_lib/probe_results/regime_attribution_panel_report.md`
- tagged trades: `nb_lib/probe_results/regime_attribution_panel_tagged_trades.csv`
- scored cells: `nb_lib/probe_results/regime_attribution_panel_cells.csv`
- summary: `nb_lib/probe_results/regime_attribution_panel_summary.json`

Result: **mixed / panel-null**. Positive-looking cells exist, but no
strategy-state cell survived the pre-committed corrected panel screen
after Benjamini-Hochberg FDR across the declared panel. This run does
not validate, promote, or revive any candidate, and it does not provide a
regime-composition explanation for the v2a/V4/G2 management divergence.
OOS remained sealed.

Next valid action is not a rescue pass. Any future regime-conditional
candidate must be written as a fresh pre-registered spec with its own
reasoning, not selected from this panel by cherry-picking.
