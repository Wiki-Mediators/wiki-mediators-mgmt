---
artifact_type: "architecture-note"
name: "Candidate Support Stack"
status: "living-architecture"
created: 2026-06-02
updated: 2026-06-02
source: "Operator architecture discussion: applying daily bias, liquidity zones, target/invalidation packets, and session routers to candidate evaluation."
scope: "How composition nodes attach to candidate strategies without reopening undisciplined entry-search."
---

# Candidate Support Stack

## 1. Purpose

This note defines how composition nodes support candidate strategies.

The project is moving from:

```text
candidate = standalone entry rule
```

to:

```text
candidate = entry rule + declared overlay contract + management context
```

That is an architectural change. It is allowed only if the discipline is
explicit: overlays are gates and context layers, not a way to rescue weak
or closed candidates after the fact.

## 2. Gate, Not Rescue

The support stack is a **gate**, not a **rescue machine**.

Allowed use:

- A candidate already has admissible evidence or is being tested under a
  pre-committed overlay contract.
- The overlay blocks, reduces, sizes, or manages trades with bad context.
- The overlay is scored against baseline honestly.

Not allowed:

- Taking a closed or weak candidate and searching overlays until a green
  cell appears.
- Retrofitting a router after seeing which trades won or lost.
- Calling a candidate "rescued" because one overlay slice looked good
  without counting the search surface.

The H4 retrospective lesson still applies: the graveyard did not hide a
large population of easy regime-conditioned survivors. Overlay work must
not become a more sophisticated way to mine rejected candidates.

## 3. Declare Before Testing

Overlay contracts must be declared at candidate-spec time or before the
overlay experiment begins.

Example:

```yaml
composition_overlay_contract:
  daily_bias_packet:
    status: required
    rule: with_bias_or_neutral_only
  liquidity_zone_prior_router:
    status: forward_looking
    use: target_context
  intraday_target_invalidation_packet:
    status: forward_looking
    min_r_to_target: 1.5
  opening_momentum_acceptance_router:
    status: optional
    rule: reduce_against_bearish_acceptance
  opening_range_rejection_state_router:
    status: optional
    rule: reduce_on_fast_failed_break
```

After-the-fact overlay selection is curve-fitting. A future session may
propose a new overlay contract, but it must be logged as a new trial
before results are inspected.

## 4. Trial-Budget Rule

Overlay search multiplies the trial surface.

```text
5 candidates x 4 overlay policies = 20 tested cells
```

Do not report that as "five tests." Each overlay policy tested against a
candidate counts as part of the chance-expectation / trial-budget
accounting unless it was purely descriptive and not used for a verdict.

This is especially important for routers with multiple possible policy
maps:

- allow / reduce / block
- with-bias only / neutral allowed / against-bias reduced
- target R threshold variants
- acceptance versus rejection state variants

The more overlays the project adds, the more disciplined the accounting
must become.

## 5. Current Stack

### Currently Consumable Or Near-Consumable

These are usable as architecture today, though some still need overlay
validation before they can gate live or final candidate results.

| Node | Status | Current Use |
|---|---|---|
| `opening_range_rejection_state_router` | note-only | ORWS-derived failed-break / acceptance state; candidate gate or management context once implemented |
| `opening_momentum_acceptance_router` | implemented-untested | First-30m / first-hour momentum acceptance state; script scaffold exists, but first scoring is blocked in current Codex runtime by missing DBN reader package |
| `liquidity_zone_prior_router` | descriptive-diagnostic-v1-complete | Observer context for zone sweep/rejection/acceptance. v1 confirms OR_H/OR_L/PDH/PDL rejection-after-sweep behavior and PDC through-prone behavior; v2 bug fixes pending before target/invalidation packet implementation |
| daily-bias packet fields in observer docs | design-banked | Bias phase, target context, invalidation condition; not yet a standalone implemented node |

### Forward-Looking Dependencies

These are not ready to gate candidates yet.

| Node | Status | Dependency |
|---|---|---|
| `intraday_target_invalidation_packet` | note-only-pending-liquidity-router-v2 | Depends on a patched liquidity-zone router with clean target-vs-sweep distinction, round-number emission, and distance-matched controls |

Forward-looking overlays may be declared in a candidate spec as intended
future consumers, but they cannot be used to score candidate viability
until implemented and validated.

## 6. Candidate Flow

```text
candidate signal fires
  -> daily bias / invalidation context
  -> liquidity-zone context
  -> target / invalidation packet
  -> session routers
  -> allow / reduce / block / manage tighter
```

More formally:

```yaml
candidate_support_stack:
  input:
    candidate_signal: object
    candidate_entry_price: float
    candidate_direction: long | short

  context_layers:
    daily_bias_packet:
      output: with_bias | against_bias | neutral | invalidated
    liquidity_zone_prior_router:
      output: next_target | nearby_danger_zone | sweep_rejection_state
    intraday_target_invalidation_packet:
      output: r_to_target | invalidation_distance | geometry_decision
    opening_momentum_acceptance_router:
      output: continuation_acceptance | failed_momentum | no_momentum
    opening_range_rejection_state_router:
      output: accepted_break | failed_break | chop_reversion

  decision:
    pretrade: allow | reduce | block
    management: hold | tighten | take_partial | flatten | simulated_only
```

## 6A. Pre-Entry Targetability Criteria

The `intraday_target_invalidation_packet` now carries the project's
explicit **No Target, No Trade** pre-entry gate.

Use it as a management-system criterion, not as a new entry signal:

```text
strategy proposes entry
  -> identify structural invalidation
  -> identify nearest objective target in trade direction
  -> check net reward:risk and volatility reachability
  -> allow / reduce / block / label-only
```

Hard-gate candidates:

- pullback-continuation entries;
- sweep/reclaim and liquidity-reversal entries;
- opening-range response entries;
- VWAP/EMA structural entries;
- any strategy whose stop and target are supposed to come from market
  structure rather than from a published unconditional anomaly.

Label-only candidates:

- close-window market-intraday-momentum;
- other once-daily or anomaly-style tests where applying the gate would
  change the hypothesis and cut the trade count before the raw effect is
  measured.

Required pre-entry output fields:

```yaml
targetability:
  mode: hard_gate | label_only
  targetability_pass: bool
  target_price: float | null
  target_source: string | null
  invalidation_price: float | null
  risk_points: float | null
  reward_points: float | null
  r_to_target_net_of_cost: float | null
  target_reachable_by_volatility: bool
  no_target_reason: string | null
```

The pass/fail values must be computed with information known at or
before the entry decision. Any use of an unconfirmed swing, developing
current-session value area, or current in-progress bar extreme is a
lookahead bug.

Trial accounting: `hard_gate`, `label_only`, `allow_only`, and
`reduce_on_fail` are separate overlay policies. Do not test all four
and report them as one candidate.

## 7. Candidate Spec Template Addition

Future candidate specs should include:

```markdown
## Composition Overlay Hooks

Declared before test:

```yaml
composition_overlay_contract:
  daily_bias_packet:
    status: required | optional | not_used | forward_looking
    rule: <pre-committed rule>
  liquidity_zone_prior_router:
    status: required | optional | not_used | forward_looking
    rule: <pre-committed rule>
  intraday_target_invalidation_packet:
    status: required | optional | not_used | forward_looking
    rule: <pre-committed rule>
  opening_momentum_acceptance_router:
    status: required | optional | not_used | forward_looking
    rule: <pre-committed rule>
  opening_range_rejection_state_router:
    status: required | optional | not_used | forward_looking
    rule: <pre-committed rule>
```

Trial-budget note:

```text
Each overlay policy tested against this candidate counts as a separate
overlay trial unless explicitly descriptive and not used for a verdict.
```
```

## 8. First Proper Use

The first honest use of the stack should be an overlay on an existing
bridge substrate, not graveyard resurrection:

```text
G2 3c
v2a 15c
combined G2 3c + v2a 15c
```

Candidate questions:

- Does a pre-declared router improve existing trades?
- Does it reduce drawdown or loss clustering without destroying pass
  rate?
- Does it improve both discovery and holdout under day-level partition?
- Does it add information beyond cheap baselines?

If the stack helps existing viable substrates, it earns broader use. If
it only finds isolated green cells in rejected candidates, it has not
earned trust.

## 9. Standing Rule

The support stack exists to attach management intelligence to entries.
It does not weaken the methodology gates.

```text
Passing candidate + declared overlays = smarter candidate.
Failed candidate + searched overlays = graveyard mining.
```
