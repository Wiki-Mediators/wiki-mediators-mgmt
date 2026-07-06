# The "No Target, No Trade" Gate: A Look-Ahead-Free Targetability Filter for MNQ Intraday

## TL;DR
- A "targetability" gate that requires (a) a structurally valid target in the trade direction, (b) reward:risk ≥ a minimum multiple, and (c) the target reachable within current volatility, is a legitimate, backtestable *filter* — but the weight of rigorous evidence (Carver, *Systematic Trading* 2015 p.213; EdgeTools' first-passage analysis; Polakow's 2-million-backtest study) says it removes bad trades from a positive-expectancy entry rather than creating edge.
- Build it look-ahead-free by using ONLY prior-session and confirmed-as-of-entry-bar structure: floor-trader pivots from the prior RTH OHLC, prior-day/overnight/opening-range highs and lows, session-anchored VWAP ± σ bands, round numbers, and the prior-session value area — never an unconfirmed swing point or the in-progress bar's high/low.
- For MNQ ($2 × Nasdaq-100; 0.25-pt tick = $0.50/tick; all-in round-trip cost ≈ 1.25–2 points ≈ $2.50–4/contract at discount/prop brokers), a sensible default is min R:R ≈ 1.5–2.0 with target distance ≤ ~0.75–1.0× a time-of-day-adjusted remaining-session range (or ≤ ~1.5–2× the entry-timeframe ATR), validated strictly out-of-sample.

## Key Findings
1. **A target must be defined from information available at or before the entry bar.** Pivots and prior-day/overnight/opening-range levels are naturally look-ahead-free because they are fixed before the bar. Swing highs/lows are the classic trap: a fractal swing high needs N bars to its *right* to confirm, so it is only known N bars later — you must lag confirmation by N bars and never reference the in-progress bar's extreme.
2. **Reachability is a volatility question.** A target many ATRs away, or beyond the range the session can still produce given the time of day, is statistically unlikely to be hit before the close. ATR-distance ratios and time-of-day-adjusted remaining-range expectations make this testable.
3. **The R:R gate is just rearranged expectancy math.** Break-even win rate = 1/(1+R). At 2:1 you need >33.3%, at 3:1 >25%, at 1:1 you need >50%. Transaction costs raise the required win rate; setting R too high collapses trade frequency.
4. **The gate cannot create edge.** It is a filter over entries. Under a random walk, the chosen R:R mechanically sets the win rate and leaves expected value at zero — so the gate only helps if the underlying entry already has positive expectancy, and it must be validated out-of-sample to avoid in-sample hindsight fitting.
5. **Evidence vs convention.** The "always require 1:2/1:3" rule is largely convention (canonically Van Tharp). Rigorous sources lean *against* fixed profit targets as an edge source, especially for trend strategies with positive skew.

## Details

### 1. Defining the target objectively (no look-ahead)

The principle: at the moment of entry on bar *t*, the only legitimate target levels are those computable from data fully known at the close of bar *t* (or earlier). Anything that requires future bars to "confirm" introduces look-ahead bias — the single most dangerous backtesting error, because it produces beautiful equity curves that collapse live. (A canonical illustration: a momentum strategy that "enters at the previous day's close" — something impossible in real life — produced a near-22% unleveraged annual return with a 1.81 Sharpe and a suspiciously smooth equity curve; the curve was an artifact of the leak.)

**Floor-trader (classic) pivots.** Computed from the PRIOR session's high (H), low (L), close (C):
- P = (H + L + C) / 3
- R1 = 2P − L; S1 = 2P − H
- R2 = P + (H − L); S2 = P − (H − L)
- R3 = H + 2(P − L); S3 = L − 2(H − P)

These are fixed before the current session opens, so they are inherently look-ahead-free **provided you use the prior completed RTH session's OHLC**, not the still-forming session. Pitfall: using the current day's developing high/low, or recomputing P intraday. Pivots are most useful intraday on liquid index futures (ES/NQ) because heavy algo participation makes them partially self-reinforcing. R1/S1 are the most-touched; R2/S2 require above-average momentum; R3/S3 mark exceptional moves. (Practitioner/vendor sources claim "~70% of range-bound activity stays between S1 and R1" and pivot "reactions in ~64% of sessions" — treat these as indicative, not peer-reviewed.)

**Swing highs/lows (fractal/swing pivots).** A swing high is a bar whose high exceeds the highs of N bars on each side (commonly N=2, the Williams/Bill-Williams fractal). The look-ahead issue is fundamental: a swing high at bar *k* is only *confirmed* at bar *k+N*. If your backtest marks the swing at bar *k* and trades off it at bar *k+1*, you are peeking. The fix: only treat a swing as a usable level from bar *k+N* onward (lag the confirmation by N bars), and never use the current in-progress bar's extreme. This makes swings lag by N bars — acceptable for *targets* (you are pointing at an older, confirmed structural level) but you must encode the lag explicitly. Swings defined off wicks rather than bodies better capture true reach/liquidity.

**Prior-day high/low (PDH/PDL).** The completed prior RTH session's high and low. Fixed before the session; clean. Strong magnet levels intraday.

**Overnight high/low (ONH/ONL).** The high/low of the Globex/overnight session preceding the RTH open. Known at the RTH open; clean as long as you freeze it at the open and don't let it update into the level you are testing against after entry.

**Opening-range high/low (ORH/ORL).** High/low of the first N minutes (commonly 5/15/30). Look-ahead-safe ONLY for entries that occur AFTER the opening range completes. An entry at 9:40 cannot use a 30-minute (9:30–10:00) opening range — that range is not yet known. The 15-minute OR is the most common balance of signal and noise; note empirically that double-breaks of the opening range are frequent (one practitioner dataset reports ~71% double-break on the 5-min OR, ~56% on the 15-min, ~42% on the 30-min), which matters directly for stop and target placement and argues against assuming a single clean directional break.

**VWAP and VWAP σ bands.** Session-anchored VWAP = Σ(price×volume)/Σ(volume) cumulated from the session anchor; bands are ±k standard deviations of price about VWAP (population formula over bars since the anchor). VWAP and ±1σ/±2σ are computable in real time from data through bar *t*, so they are look-ahead-safe as targets *as of the entry bar* — but they move, so freeze the band value at entry for the R:R calculation. The 1σ band is a common first target; 2σ marks statistical over-extension. Bands behave most reliably as mean-reversion targets when VWAP is roughly horizontal (range/balance), less so on strong trend days.

**Round numbers.** Psychologically and algorithmically significant whole levels (e.g., MNQ 20,000; 19,950; quarter-thousands and hundreds). Trivially known in advance; useful as confluence.

**Prior value area (VAH/VAL) from volume profile.** Build a volume-at-price histogram for the prior completed session. The Point of Control (POC) is the highest-volume price; the Value Area is the contiguous range (default 70% of volume) around the POC, bounded by Value Area High (VAH) and Value Area Low (VAL), built by starting at the POC and adding the larger of the two adjacent rows until 70% of volume is captured. Look-ahead-safe if you use the PRIOR session's completed profile. Pitfall: using a developing/current-session profile (the "developing VA" shifts and will leak future information). Treat VAH/VAL/POC as zones, not exact lines.

**Confluence:** the most robust targets are where two or more independent sources stack (e.g., R1 ≈ PDH ≈ a round number). This is testable: define a "confluence target" as the nearest cluster of ≥2 levels within X ticks.

### 2. Measuring reachability under current volatility

The reachability test asks: *given how much this market is moving and how much session time remains, can price plausibly travel from entry to the target before I must exit (session close)?*

**ATR-based reachability.** With ATR(n) on the entry timeframe (Wilder's True Range — the max of (H−L), |H−prevC|, |L−prevC| — averaged over n bars, e.g., 14):
- distance_to_target ≤ k × ATR(n_entry_timeframe), or
- distance_to_target ≤ k_day × ATR_daily (for the whole-session budget).

The "ATR distance to target" ratio = distance_to_target / ATR. A common practitioner heuristic: a target inside ~1× the relevant ATR is "relatively easy to achieve," and a target beyond the average range is "overly ambitious." Day-trading guidance (e.g., Optimus Futures, GFF Brokers, TradingWithRayner) repeatedly frames the daily ATR as the realistic per-session travel budget and recommends choosing the nearest *structural* level that sits *within* (not beyond) it — e.g., with a daily ATR of 300 points, a 250-point resistance is a reasonable target while a 400-point one is not.

**Expected move / remaining-session range.** Volatility scales with the square root of time, not linearly. The standard expected-move form:
- Expected move over horizon = Price × σ × √(t/252) (or √(t/365)), the 1σ (~68%) band.
- For Nasdaq index futures you can substitute VXN (Nasdaq vol index) for σ to get a session expected range (e.g., at VIX≈20 and NQ≈20,500, a 1σ daily move is on the order of ~258 points by the VIX formula, with NQ tending to overshoot its implied range by 10–20% due to momentum/gamma), or simply use the empirical average daily range (ADR).

**Time-of-day adjustment (the key intraday refinement).** Intraday volatility follows a well-documented U-shape — highest at the open and into the close, lowest midday — established academically (Biais, Hillion & Spatt 1995, *Journal of Finance* 50:1655–1689, the canonical limit-order-book/order-flow study; corroborated by Bouchaud et al. 2018 and fitted to a quadratic by Abergel et al. 2016). Practitioner data on NQ echoes this: the cash open accounts for ~25–35% of the day's total range, while the ~11:30–13:30 ET "dead zone" sees range/volume compress materially (one prop-firm dataset cites a ~40% midday volatility drop). So the range *already used* by a given time of day and the range *still available* are both time-dependent. A practical, backtestable estimate:

  remaining_expected_range(t) = ADR × [1 − cumulative_range_fraction(time_of_day)]

where cumulative_range_fraction is an empirically calibrated curve (e.g., a large share of the day's range is spent in the first hour; by early afternoon most of the typical range is gone). Then require:

  distance_to_target ≤ c × remaining_expected_range(t),  with c ≈ 0.5–1.0.

Intuition: entering long at 2 pm targeting a level a full ADR away is usually unreachable because most of the day's range is gone and the midday/early-afternoon hours produce little new range. The gate should tighten the reachable distance as the session ages.

### 3. The reward:risk gate and minimum multiple

Define distance_to_invalidation = |entry − stop| (the structural stop, just beyond the level that would prove the idea wrong), and distance_to_target = |target − entry|. The gate:

  R = distance_to_target / distance_to_invalidation ≥ min_R_multiple

**The break-even math.** With reward-to-risk ratio R and ignoring costs, the break-even win rate is:

  W_be = 1 / (1 + R)

- 1:1 → 50%
- 1.5:1 → 40%
- 2:1 → 33.3%
- 3:1 → 25%
- 5:1 → 16.7%

This is just the expectancy equation set to zero. Expectancy (Van Tharp) = (Win% × AvgWin) − (Loss% × AvgLoss); expressed in R-multiples, expectancy per trade = W×R − (1−W). Example: a 35% win rate at 3:1 → 0.35×3 − 0.65 = +0.40R per trade — solidly profitable despite being "wrong" 65% of the time. This is the heart of Van Tharp's framework (R = initial risk per trade; outcomes standardized as multiples of R; system expectancy = mean R-multiple), and an academic study he cites attributes ~91% of the variability in portfolio performance to position sizing rather than the entry itself.

**Costs shift the bar.** On MNQ, the all-in round-trip cost is roughly 1.25–2 index points (≈ $2.50–4/contract): commissions run ~$1.25–3.50 round-trip at discount/prop brokers (NinjaTrader ~$1.75, AMP ~$1.25, Tradovate Active ~$3.50; cross-broker average ~$4.70 per BrokerChooser, May 2026), plus ~$0.55/contract exchange+NFA fees, plus a typically 1-tick ($0.50) RTH spread. If your risk (1R) is 20 points ($40), costs are ~6–10% of R, raising the required win rate a few points above the frictionless W_be. The smaller your stop in points, the larger costs loom: a 5-point stop ($10) makes a 2-point cost 40% of R, which can swamp a thin edge. Practitioners commonly add a 5–10 percentage-point buffer above the theoretical break-even win rate to cover costs and slippage.

**Frequency collapse.** Pushing min_R_multiple very high (4:1–5:1) makes most setups fail the gate — few structural targets sit that far away while a tight, valid stop remains. You trade rarely, your sample shrinks, and statistical significance evaporates. There is a direct tradeoff: a stricter R:R gate raises per-trade expectancy *if* win rate holds, but cuts frequency and (because targets get farther) tends to lower the realized hit rate. The sweet spot for liquid intraday index futures is typically modest (1.5:1–2:1), not heroic.

### 4. Combining the pieces into a gate

Logical structure — enter only if ALL hold:
- (a) **Existence:** a valid target level exists in the trade's direction, strictly ahead of entry, computed look-ahead-free.
- (b) **Reward sufficiency:** distance_to_target ≥ min_R_multiple × distance_to_invalidation.
- (c) **Reachability:** distance_to_target ≤ reachability_limit = min(k×ATR_entry, c×remaining_expected_range(t)).

If (b) and (c) conflict (the nearest qualifying target is simultaneously too close for R:R and the only one within reach), the trade is correctly denied — there is no room. The gate returns allow/deny plus the chosen target and the computed R.

**Crucial conceptual point — this is a filter, not a signal generator.** It never tells you to buy or sell; it only vetoes entries with no realistic reward path. Therefore it *cannot manufacture edge*. It can only improve an already-positive-expectancy entry by stripping out trades that had no room to pay. Under a pure random walk, choosing an R:R simply trades win rate for payoff size at constant (zero) expected value — the gate does nothing for a zero-edge entry. The danger: filtering on targets in-sample almost always *looks* great by hindsight (you can always find a target rule that flatters the past). It must be validated out-of-sample / walk-forward, with realistic costs, before it is trusted. Stress-test it by deliberately delaying inputs (if performance collapses under a one-bar delay, the rule was leaking future data).

### 5. Evidence vs professional practice

**Convention.** The "always demand a minimum 1:2 or 1:3 reward:risk" rule is ubiquitous in educational and prop-firm material and is canonically traced to Van Tharp's R-multiple/expectancy framework (*Trade Your Way to Financial Freedom*, McGraw-Hill, 1998). The expectancy and break-even-win-rate formulas are sound algebra and genuinely useful for *evaluating* a system. The R-multiple language (think in R, standardize risk per trade, expectancy = mean R) is a real, widely adopted contribution. But repetition of "1:2 minimum" across vendor blogs is assertion, not proof that the gate *raises* expectancy.

**Rigorous evidence leans against fixed profit targets as an edge source.** Robert Carver (*Systematic Trading*, Harriman House, 2015, p.213): *"My research shows no evidence that systematic profit targets work consistently. Most markets exhibit trending behavior (with positive skew), and a profit target will get you out of trends too early."* Carver builds edge from signal quality + volatility-targeted position sizing + diversification, treats stops mainly as a turnover/cost lever (tight stops → high turnover, p.192), and lets R:R *emerge* rather than imposing it. He also stresses that you need on the order of a decade of data to judge a single rule — implying most retail "R:R works" claims are statistically underpowered.

The EdgeTools first-passage analysis (Monte Carlo of 500,000 trades per configuration + SPY 2000–2024 + EUR/USD) shows that under a random walk P(target first) = S/(S+T) = 1/(1+R), so the chosen R:R mechanically determines win rate and leaves expected value at zero; empirically SPY at 2:1 produced a ~34.8% win rate vs 33.3% theoretical (the small excess from positive drift), 3:1 → 26.3% vs 25%, and EUR/USD matched random-walk theory within ~1 point. Their conclusion: *"The risk-reward ratio does not create edge. It redistributes probability mass between win rate and payoff size while preserving expected value… No stop loss placement or profit target selection will transform random entries into a profitable system."* They further note (citing Siven 2009; Perelló 2011) that losses tend to arrive ~3× faster than gains, and that in positive-drift markets stops can *reduce* total returns. EdgeTools is a practitioner/vendor publication, not peer-reviewed, but its gambler's-ruin/first-passage math is standard and correct, and it references genuine literature (Carver 2015; Moskowitz-Ooi-Pedersen, "Time Series Momentum," *JFE* 2012; Hurst-Ooi-Pedersen, "A Century of Evidence on Trend-Following," *JPM* 2017).

The 2-million-backtest study (Oleg Polakow, "Stop Loss, Trailing Stop, or Take Profit? 2 Million Backtests Shed Light," DataDrivenInvestor/Medium, using vectorbt: 10 cryptocurrencies by market cap, daily data 2018-01-01→2021-01-01 split into 400 overlapping 6-month windows × 5 exit types × 100 stop values, with fees and slippage each set to 0.25% and pessimistic same-bar SL-before-TP assumptions) found that **no exit approach — stop-loss, trailing-stop, or take-profit — provided a significant advantage over a random exit** for the strategy tested. (A separate PyQuant momentum study on stocks found take-profit's mean total return ~12.3% vs <10% for SL/TS, but on a single strategy/universe and with the author's own warning against over-reading — not generalizable, and not from Polakow.)

Where R:R legitimately matters: as *position sizing* once a verified edge exists (Kelly f = (p·b − q)/b; e.g., 40% win at 2:1 → f = (0.40×2 − 0.60)/2 = 0.10). It is circular to use a min-R:R gate to *create* an edge.

**Net:** the targetability gate is best understood as risk-path *hygiene* — keeping you out of trades with no room and enforcing discipline — not as a source of alpha. Its honest value is (1) preventing structurally hopeless trades, (2) standardizing R for expectancy tracking, and (3) reducing overtrading in low-range conditions.

### 6. Implementation on MNQ specifically

**Contract facts.** MNQ = $2 × Nasdaq-100 index (CME Group); 1 tick = 0.25 index points = $0.50; 1 full point = 4 ticks = $2; cash-settled, quarterly (Mar/Jun/Sep/Dec). It is roughly 1.5–2× as volatile as ES in percentage terms; typical intraday stops run ~15–40 points. RTH bid-ask is typically 1 tick (occasionally 2 ticks overnight/low-volume) on daily volume of ~250k–500k contracts. Initial margin was ~$1,825 (maintenance ~$1,660) as of December 2025 — about 1/10th of full-size NQ — though intraday margins at some brokers are far lower and figures drift with volatility. Most reliable intraday target sources on MNQ (liquid, heavy algo participation): prior-day high/low, floor-trader pivots (R1/S1 first), session VWAP and ±1σ/±2σ bands, opening-range high/low, and round numbers; prior value area VAH/VAL/POC as secondary confluence.

**Parameter suggestions (starting points, to be validated OOS):**
- Entry timeframe: 5-min for active intraday; 15/30-min for fewer, cleaner signals.
- ATR: 14-period on the entry timeframe; also track daily ATR for the session budget.
- Reachability: distance_to_target ≤ 1.5–2.0 × ATR(14, entry TF), AND ≤ ~0.75× a time-of-day-adjusted remaining-session range; tighten the multiplier after midday (the dead-zone compression).
- min_R_multiple: 1.5 as a frequency-friendly floor; 2.0 if the entry's win rate comfortably clears ~40%. Avoid ≥3:1 as a hard gate intraday (frequency collapse).
- Cost handling: subtract ~1.25–2 pts from every modeled trade; require realized win rate ≥ W_be + ~5 pts.

**Look-ahead-safe pseudocode:**

```
function targetability_gate(entry_price, direction, t, structure, stop_price, params):
    # structure holds ONLY data known at/before bar t:
    #   prior-session OHLC -> pivots P,R1..R3,S1..S3
    #   PDH, PDL, ONH, ONL
    #   ORH, ORL   (only if opening range completed at/before t)
    #   VWAP_t, VWAP_upper1/2, VWAP_lower1/2 (cumulated through t, frozen)
    #   round_levels
    #   prior_session VAH, VAL, POC
    #   confirmed swings: only those confirmed at or before bar (t - N)
    #   ATR_entry = ATR(14) computed through CLOSED bar t-1
    #   ADR, time_of_day fraction curve (calibrated to MNQ RTH)

    # 1) candidate target levels strictly in trade direction
    if direction == LONG:
        candidates = [lvl in all_levels if lvl > entry_price]
    else:
        candidates = [lvl in all_levels if lvl < entry_price]
    if candidates is empty: return DENY

    # 2) invalidation distance from the structural stop
    risk = abs(entry_price - stop_price)
    if risk <= 0: return DENY

    # 3) reachability limit (freeze values as of bar t)
    rem_range   = ADR * (1 - cum_range_fraction(time_of_day(t)))
    reach_limit = min(params.k_atr  * ATR_entry,
                      params.c_range * rem_range)

    # 4) choose NEAREST target that clears BOTH R:R and reachability
    best = null
    for lvl in sort_by_distance(candidates, entry_price):
        dist = abs(lvl - entry_price)
        R    = dist / risk
        if R >= params.min_R and dist <= reach_limit:
            best = {target: lvl, R: R, dist: dist}
            break          # nearest qualifying = most reachable

    if best is null: return DENY
    return ALLOW with target=best.target, R=best.R
```

Key safeguards baked in: ATR and any swing levels use only closed bars / bars ≤ t−N; ORH/ORL only exist after the OR window; VWAP/σ frozen at entry; the nearest qualifying target is chosen (maximizing reachability while clearing the R:R floor). Position sizing then sits *outside* this gate: size so that 1R (risk in points × $2 × contracts) equals a fixed fraction of equity.

## Recommendations
1. **Build the gate as a pure veto on a separately validated entry.** First establish that your MNQ entry has positive expectancy with a fixed structural stop and a session-close exit, costs included. Only then bolt on the targetability gate and measure whether it *improves* net expectancy and Sharpe out-of-sample. If it doesn't, the entry — not the gate — is the problem. *Threshold to change course:* if the gate doesn't lift OOS expectancy after costs, drop or simplify it.
2. **Start with min_R = 1.5 and reach_limit = min(2×ATR14, 0.75×remaining-range); tighten after midday.** *Benchmarks to retune:* if filtered trade count falls below ~30–50 per OOS quarter (too thin to trust), loosen min_R or k; if realized win rate sits below W_be + 5 pts, the targets are too far — lower k or min_R.
3. **Use the most reliable, cleanly look-ahead-free sources first** — PDH/PDL, pivots R1/S1, VWAP ±1σ, ORH/ORL after the OR completes, round numbers. Add VAH/VAL/POC confluence only from the prior completed session. Avoid unconfirmed swing points entirely in the live path; if you use swings, lag them by N bars.
4. **Validate with walk-forward and realistic costs.** Subtract ~1.25–2 pts/round-trip, model the 1-tick spread, and confirm the gate's benefit persists across regimes (trend days vs midday chop). Treat any in-sample improvement as suspect until it survives OOS, and break the input pipeline on purpose (delay features) to detect leakage.
5. **Do not raise R:R to chase a prettier in-sample curve.** Frequency collapse and trend-truncation (Carver's warning) are real costs. Consider letting a portion of the position run past the first qualifying target (scale-out + ATR/Chandelier trailing stop) to recapture the positive-skew payoffs a hard target forfeits.

## Caveats
- The gate is a **filter, not an edge**. The strongest evidence (Carver 2015 p.213; first-passage math; Polakow's 2M backtests) says fixed targets/min-R:R do not create profitability and can hurt trend strategies by capping winners. Use the gate for risk-path discipline and expectancy bookkeeping, not as a source of alpha.
- Several cited figures — "~70% of activity between S1/R1," pivot "reaction in 64–89% of sessions," specific ORB win/double-break rates, the PyQuant "12.3%" take-profit result — come from practitioner/educational/vendor sources, not peer-reviewed studies; treat them as indicative, not established fact. The U-shape intraday volatility pattern, by contrast, is well-documented academically (Biais-Hillion-Spatt 1995).
- Reachability curves (cumulative range fraction by time of day) must be **empirically calibrated to MNQ's own RTH session** and re-checked as volatility regimes shift; a curve fit in a high-VXN period will misstate reachable distance in a quiet one.
- Look-ahead safety is fragile: the most common leaks are using the current session's developing high/low or value area, referencing a swing before its N-bar confirmation, and computing ATR/levels with the in-progress bar.
- MNQ specifics (margins, exact fees, typical ranges) drift over time and vary by broker; the cost (~1.25–2 pts round-trip), spread (~1 tick), and margin ($1,825 initial as of Dec 2025) figures here are reference values that should be re-pulled before live deployment.