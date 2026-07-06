# A Formula-Level Menu of Mathematical Tools for Intraday MNQ Momentum Research

## TL;DR
- **Your headline problem is statistical, not strategic:** 150 trades, PF 1.24, 39.3% win rate and a single month (Jan 2026, +$2,104.80) contributing >52% of the +$4,024.50 net P&L is a textbook "lucky-month / low-sample" signature. The right first move is to quantify concentration (HHI, top-k share, leave-one-month-out) and bootstrap confidence intervals on PF/Sharpe/expectancy — before touching the strategy logic.
- **Track 1 (robustness):** stationary/block bootstrap CIs, permutation/Monte-Carlo sign tests, White's Reality Check & Hansen's SPA for the search, Deflated/Probabilistic Sharpe + Minimum Track Record Length for multiple-testing deflation, PBO via CSCV for overfit probability, and FDR/Holm corrections — all implementable in NumPy and given below with formulas.
- **Track 2 (bracket math):** size stops/targets in ATR/σ units, standardize entries as VWAP z-scores, and use the two-barrier first-passage formulas for arithmetic Brownian motion (p = (1−e^(−2μb/σ²))/(1−e^(−2μ(a+b)/σ²))) to derive the win rate and expectancy a given stop:target/drift/vol *implies* — then size with fractional Kelly and check risk-of-ruin.

## Key Findings
1. With only 150 trades and a 39.3% win rate, the standard error on every statistic is large; the Jan-2026 concentration means the edge is likely **not yet distinguishable from a lucky run** until proven otherwise. Treat the burden of proof as "guilty until proven innocent."
2. The most decision-relevant tools are the **concentration metrics** and **leave-one-month-out** analysis (does the edge survive removing Jan 2026?), the **stationary bootstrap** CI on profit factor and expectancy, and a **permutation test** on trade signs/timing.
3. If multiple strategy variants were tried, the **Deflated Sharpe Ratio** and **PBO** are essential — they are the only tools here that explicitly penalize the number of configurations searched. Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns," *Review of Financial Studies* 29(1):5–68, catalogued 316 factors across 313 articles and concluded the conventional t>2.0 cutoff is too lenient: "a newly discovered factor today should have a t-ratio greater than 3.0."
4. For brackets, ATR/volatility scaling plus the **first-passage barrier formulas** give a principled, non-curve-fit way to choose stop:target ratios for a target win rate, and to sanity-check whether your realized win rate is even consistent with your bracket geometry.

## Details

### TRACK 1 — STATISTICAL ROBUSTNESS MATH

#### 1.1 Defining the statistics on a trade series
Let trade P&L be {x_1,…,x_n}, n=150.
- **Profit factor:** PF = Σ(x_i | x_i>0) / |Σ(x_i | x_i<0)|. Yours = 1.24.
- **Expectancy (per trade):** E = (1/n)Σ x_i = $4,024.50/150 = **$26.83/trade**.
- **Win rate:** w = #{x_i>0}/n = 0.393.
- **Payoff ratio:** b = (avg win)/(avg loss). PF = w·b/(1−w), so your implied b = PF·(1−w)/w = 1.24·0.607/0.393 ≈ **1.915**.
- **Per-trade Sharpe:** SR = mean(x)/std(x); annualize/aggregate carefully (see §1.6).

#### 1.2 Bootstrap methods for P&L statistics
**i.i.d. bootstrap (baseline):** Resample n trades with replacement B times (B≈10,000), recompute PF/SR/expectancy each time, and take the 2.5th/97.5th percentiles for a 95% CI. This is valid only if trades are independent — questionable for intraday trades clustered in the same session/regime.

**Block bootstrap (Künsch moving-block):** To preserve autocorrelation/clustering, resample contiguous blocks of length ℓ. Concatenate ⌈n/ℓ⌉ blocks. Drawback: pseudo-series are not stationary and the choice of ℓ matters.

**Stationary bootstrap (Politis & Romano 1994):** Resample blocks of *random* length L ~ Geometric(p), so E[L]=1/p. Start each block at a uniformly random index; when a block runs past the end, wrap around (circular). The resulting pseudo-series is stationary, and results are *less sensitive to misspecification of the mean block length* than the moving-block method. Algorithm:
1. Pick random start I_k ~ Uniform{1,…,n}.
2. Draw L_k ~ Geometric(p); copy x_{I_k}, x_{I_k+1}, …, (indices mod n).
3. Repeat until length ≥ n; truncate; recompute statistic.

**Choosing block length / p for autocorrelated returns:** Use the **Politis & White (2004)** automatic block-length selector (with the Patton, Politis & White 2009 correction). The optimal block length grows with the strength/persistence of autocorrelation; intuitively b_opt scales like n^(1/3) times a constant derived from the spectral density at zero frequency via flat-top lag windows. For the stationary bootstrap the relevant output is the optimal expected block length 1/p. Implementation: the `arch` Python package (`arch.bootstrap.StationaryBootstrap`, `optimal_block_length`) and the R `blocklength` package implement both PWSD and HHJ methods directly.

**Building CIs:** For each of B resamples compute θ*_(j) (θ = PF, SR, expectancy). Two standard CIs:
- **Percentile:** [θ*_(α/2), θ*_(1−α/2)].
- **Basic/empirical (pivotal):** [2θ̂ − θ*_(1−α/2), 2θ̂ − θ*_(α/2)].
- A **one-sided p-value** for "edge ≤ 0" is the fraction of resamples with the statistic ≤ its null value (e.g., expectancy ≤ 0, or PF ≤ 1).

#### 1.3 Permutation / Monte-Carlo tests for "is this distinguishable from random?"
- **Sign/label shuffle (Monte-Carlo permutation):** Under H0 of no edge with a symmetric payoff, randomly flip the sign of each trade's P&L (or randomly permute win/loss labels keeping the win/loss magnitude pools) and recompute total P&L/PF. The p-value is the fraction of shuffles whose statistic ≥ observed. Tests whether the *sequence* of outcomes is better than chance.
- **Randomized entry timing (the more honest test for a rule):** Re-run the exact bracket/exit logic but enter at random times within the RTH session (matching the number of trades and holding-time distribution). Build the null distribution of total P&L. If the real strategy's P&L is not in the top ~5% of the random-entry distribution, the entry signal adds little. This controls for the fact that *any* bracket on a drifting/volatile instrument generates P&L.
- **White's Reality Check (Bootstrap Reality Check, White 2000):** When you have searched over many rules, test H0: max_k E[f_k] ≤ 0 (best rule has no superior performance vs benchmark). Form the performance statistic for each rule, center it, and use the stationary bootstrap to build the distribution of max_k √T(f̄*_k − f̄_k); the RC p-value is the fraction of bootstrap maxima ≥ the observed max. Controls family-wise error across the rule universe.
- **Hansen's SPA test (2005):** Improves the RC by **studentizing** each rule's statistic (dividing by its bootstrap std error) and down-weighting clearly inferior rules, so power is not destroyed by adding many bad rules. Prefer SPA over RC when your search included many junk variants. Both are implemented in the `arch` package (`arch.bootstrap.SPA`).

#### 1.4 Deflated & Probabilistic Sharpe Ratio (Bailey & López de Prado)
**Variance of the Sharpe estimator with skew/kurtosis (Mertens/Lo, used by PSR):**

σ̂(SR̂) = √( [1 − γ̂₃·SR̂ + ((γ̂₄ − 1)/4)·SR̂²] / (T−1) )

where γ̂₃ = skewness, γ̂₄ = kurtosis (non-excess; γ₄=3 for normal). Note negative skew and high kurtosis *inflate* the standard error → reduce significance.

**Probabilistic Sharpe Ratio (PSR):** probability that true SR exceeds a benchmark SR*:

PSR̂(SR*) = Z( (SR̂ − SR*)·√(T−1) / √[1 − γ̂₃·SR̂ + ((γ̂₄−1)/4)·SR̂²] )

where Z is the standard-normal CDF. SR and SR* must be in the *same frequency* (do not annualize one only).

**Minimum Track Record Length (MinTRL):** number of observations needed for PSR(SR*) ≥ confidence 1−α:

MinTRL = 1 + [1 − γ̂₃·SR̂ + ((γ̂₄−1)/4)·SR̂²]·( Z_{1−α} / (SR̂ − SR*) )²

This directly answers "how many trades do I need for this Sharpe to be significant?"

**Deflated Sharpe Ratio (DSR):** a PSR whose benchmark SR* is set to the *expected maximum* Sharpe from N trials:

DSR̂ = Z( (SR̂ − SR₀)·√(T−1) / √[1 − γ̂₃·SR̂ + ((γ̂₄−1)/4)·SR̂²] )

with the deflated threshold derived from Extreme Value Theory:

SR₀ = √V·[ (1−γ)·Z⁻¹(1 − 1/N) + γ·Z⁻¹(1 − 1/(N·e)) ]

where V = Var({SR_n}) across the N trials, γ ≈ 0.5772 (Euler-Mascheroni), e = Euler's number, Z⁻¹ the inverse normal CDF. As N (number of configurations tried) grows, SR₀ rises and DSR falls. **This is the single most important correction for a strategy found by searching.** When trials are correlated, replace N by the *effective independent trials* N̂ via the average-correlation interpolation N̂ ≈ 1 + (M−1)(1−ρ̄), or via information-theoretic redundancy. López de Prado's published Python `getExpMaxSR` snippet computes SR₀ directly:
```python
def getExpMaxSR(mu, sigma, numTrials):
    emc = 0.5772156649  # Euler-Mascheroni constant
    maxZ = (1-emc)*ss.norm.ppf(1-1./numTrials) + emc*ss.norm.ppf(1-1./(numTrials*np.e))
    return mu + sigma*maxZ
```

#### 1.5 Probability of Backtest Overfitting (PBO) via CSCV
From Bailey, Borwein, López de Prado & Zhu (2017), *Journal of Computational Finance*. Procedure:
1. Build a T×N matrix M of per-period P&L for all N configurations tried (rows = time slices, must be equal-shaped).
2. Split rows into S equal disjoint submatrices (S even, e.g. 8–16).
3. Form all C(S, S/2) combinations that assign S/2 submatrices to **in-sample (IS)** and the complement to **out-of-sample (OOS)**. (This "combinatorially symmetric" design is what makes IS/OOS exchangeable.)
4. For each combination c: find n* = argmax over configs of the IS performance; record its OOS rank. Compute relative rank ω_c = (rank − 0.5)/N ∈ (0,1), then logit λ_c = ln(ω_c/(1−ω_c)).
5. **PBO = P(λ_c < 0)** = fraction of combinations (or KDE-integrated mass below 0) where the IS-best falls below the OOS median.

PBO near 0 = robust selection; PBO near 0.5 = IS rank is random OOS (pure overfit). Also report **performance degradation** (slope of OOS performance on IS performance) and the probability of OOS loss. Implemented in the R `pbo` package and reproducible in NumPy/SciPy.

#### 1.6 Sharpe significance, sample size and the √-time trap
- **Lo (2002) i.i.d. standard error:** SE(SR) ≈ √((1 + ½SR²)/T). A SR is ~2σ-significant when SR·√T ≳ 2, i.e. you need roughly T ≳ 4/SR² observations (before non-normal inflation). With negative skew and fat tails the requirement grows.
- **Autocorrelation correction (Lo 2002):** the naïve annualization SR_annual = √q · SR_period assumes i.i.d. The correct multiplier is q/√(q + 2·Σ_{k=1}^{q-1}(q−k)ρ_k), where ρ_k are return autocorrelations. Positive autocorrelation makes the naïve √q *overstate* the true annualized Sharpe. For intraday strategies with serially clustered trades this matters.

#### 1.7 Concentration metrics (directly targets your Jan-2026 problem)
Let monthly net P&L be {g_1,…,g_m}. To measure dependence on a few periods:
- **Herfindahl-Hirschman Index (HHI):** define positive-share weights p_i = g_i / Σg_j (over profitable months), then HHI = Σ p_i². Ranges from 1/m (perfectly even) to 1 (all profit in one month). López de Prado uses an adjusted, sample-debiased version normalized to [0,1]:

  HHI₊ = (Σ_i p_i² − 1/m) / (1 − 1/m)

  With Jan-2026 ≈ 52% of net profit, your top-share already implies a high HHI.
- **Top-k contribution share:** fraction of net P&L from the k most profitable months/trades. Report top-1 (≈0.52 for you), top-3, top-5.
- **Gini coefficient** of P&L contributions: G = (Σ_i Σ_j |g_i − g_j|)/(2m²·ḡ); higher = more concentrated.
- **Leave-one-month-out (LOMO):** recompute PF, expectancy, total P&L dropping each calendar month in turn. The decision rule: **if dropping Jan 2026 turns expectancy/PF non-significant or negative, the edge is month-dependent and not yet established.** Removing Jan 2026 leaves +$1,919.70 over the remaining months — recompute PF and the bootstrap CI on that subset.
- **Leave-one-out (LOO) per trade:** recompute statistics dropping each trade; flag if any single trade flips significance (extreme jackknife influence).

#### 1.8 Multiple-testing corrections for strategy search
Given p-values p_(1)≤…≤p_(m) from m tested variants:
- **Bonferroni (FWER):** reject if p_i ≤ α/m. Most conservative.
- **Holm step-down (FWER, uniformly more powerful than Bonferroni):** reject p_(k) for k=1,2,… while p_(k) ≤ α/(m−k+1); stop at first failure.
- **Benjamini-Hochberg (FDR):** find the largest k with p_(k) ≤ (k/m)·α; reject all p_(1..k). Controls expected false-discovery proportion; more powerful, allows some false positives. Under dependence use Benjamini-Yekutieli (divide α by Σ_{j=1}^m 1/j).
- **Harvey-Liu-Zhu "factor zoo" hurdle:** Harvey, Liu & Zhu (2016, *RFS* 29(1):5–68) catalogued 316 factors and recommend a **t-ratio > 3.0** (not 2.0) for a new strategy given how many have been tried. For your single strategy this means E·√n/std(x) should clear ~3.

#### 1.9 Regime / month-stability tests
- **Chow test:** if you can pre-specify a break date, test equality of regression coefficients (or mean P&L) before/after. F-statistic compares pooled vs split residual sums of squares.
- **CUSUM of recursive residuals:** plot the cumulative sum of standardized one-step residuals of the equity curve; a path that drifts outside the ±confidence band signals instability — useful as a visual, date-free regime check on the equity curve.
- **Bai-Perron multiple-break test:** estimates the number *and* location of unknown breaks by minimizing residual sum of squares across regimes (piecewise model y_t = x_t'β_j + u_t on segment j); the right tool if you suspect Jan-2026 is its own regime.
- **Regime concentration:** combine with HHI above; also bucket trades by VIX/realized-vol regime and test whether expectancy is confined to one volatility bucket.

### TRACK 2 — TRADE-STRUCTURE / BRACKET MATH

#### 2.1 ATR & volatility-scaled stops/targets
**True Range:** TR_t = max(H_t − L_t, |H_t − C_{t−1}|, |L_t − C_{t−1}|). **ATR (Wilder):** ATR_t = ((N−1)·ATR_{t−1} + TR_t)/N (Wilder's smoothing, N=14 typical).
- **Volatility-normalized stop/target:** Stop distance = k_s·ATR, Target distance = k_t·ATR. By expressing brackets as ATR multiples, the *risk in points adapts to regime* while the structural ratio k_t/k_s stays fixed (not curve-fit to point values).
- **Constant-risk position sizing:** Contracts = (Account × risk%)/(k_s·ATR × point-value). Per CME Group specs, the Micro E-mini Nasdaq-100 (MNQ) is **$2 × the Nasdaq-100 Index** with a 0.25-point minimum tick = **$0.50/tick** (launched May 2019 as 1/10th of the E-mini NQ, which has a $20 multiplier). This keeps dollar risk constant as volatility changes — the core benefit. A stop below ~1×ATR is dominated by intraday noise; common day-trading multiples are ~1.5–2.5×ATR.
- **Realized-volatility version:** replace ATR with σ_intraday·√h (h = holding horizon in bars) when you want a returns-based rather than range-based scale; normalize all thresholds by this σ so signals are unitless (z-scores).

#### 2.2 Opening-range & VWAP-distance models
- **Session VWAP:** VWAP_t = Σ(price_τ·vol_τ)/Σ vol_τ from RTH open to t, using typical price (H+L+C)/3 per bar. Reset each session.
- **VWAP z-score (standardized distance):** z_t = (P_t − VWAP_t)/σ_VWAP,t, where σ_VWAP,t is the volume-weighted standard deviation of price about VWAP. ±2 is the conventional "stretched" threshold. **Acceptance/continuation** for a momentum rule can be defined as price holding z_t > +z_threshold for a minimum number of bars (the opposite of the mean-reversion fade). This standardizes your "First Hour Momentum Acceptance" trigger so it is comparable across days/regimes.
- **Opening-range breakout (ORB) geometry:** Let OR = [OR_high, OR_low] over the first k minutes; range height ΔOR = OR_high − OR_low. Measured-move target = breakout level ± m·ΔOR (m≈1.0–1.5 common). Crabel's "stretch" sets the target as the trailing average of session breakout-to-extreme distances. Stop options: opposite range boundary (risk = ΔOR) or range midpoint (risk = ΔOR/2). The reward:risk is then fully determined by m and the stop choice — e.g., target 1.5·ΔOR with midpoint stop (0.5·ΔOR) ⇒ R = 3:1.

#### 2.3 First-passage / barrier-hitting theory (the analytical core)
Model intraday price (in points, post-entry) as arithmetic Brownian motion dX = μ·dt + σ·dB, X(0)=0, with **target** at +a and **stop** at −b (a,b>0). Let p = P(hit +a before −b).

**Exact two-barrier hitting probability** (scale-function method; Karlin & Taylor, *A First Course in Stochastic Processes* Ch. 15; Borodin & Salminen, *Handbook of Brownian Motion* p. 309):

p = (1 − e^(−2μb/σ²)) / (1 − e^(−2μ(a+b)/σ²))

Derivation: the hitting probability u(x) is the bounded harmonic function for the generator (σ²/2)u″ + μu′ = 0 with u(a)=1, u(−b)=0; solving gives scale function s(x)=e^(−2μx/σ²) and p = (s(0)−s(−b))/(s(a)−s(−b)).

**Driftless limit (μ→0):** p = b/(a+b). So with zero drift, a 1:2 stop:target (b=1,a=2) gives win rate p = 1/3 — exactly the breakeven rate, confirming no edge from geometry alone.

**Expected time to hit either barrier** (optional stopping on the martingale X_t − μt, since E[X_τ] = μ·E[τ] = (a+b)p − b):

E[τ] = ((a+b)·p − b) / μ,   driftless limit: E[τ] = a·b/σ².

**Discrete gambler's-ruin analogue** (biased random walk, win prob q, r=(1−q)/q, start b units above lower barrier, width a+b; Feller, *Probability Theory* Vol. 1 Ch. XIV):

p = (1 − r^b) / (1 − r^(a+b)),   E[τ] = ((a+b)p − b) / (2q−1).

(Unbiased q=½: p = b/(a+b), E[τ] = a·b. The random-walk → BM correspondence is μ ↔ (2q−1), σ² ↔ 4q(1−q).)

**Using this to design brackets:**
- **Implied win rate & expectancy:** Given an estimate of intraday drift μ and volatility σ (e.g., from RTH bar data over the first hour) and a chosen (a,b), compute p, then expectancy per trade E = p·a − (1−p)·b (minus costs). This tells you the win rate your bracket *should* produce — compare to your realized 39.3%. If realized ≪ implied, your entry timing is adverse or costs/slippage are eating the edge.
- **Choosing stop:target for a target win rate:** invert p = b/(a+b) (driftless) → a/b = (1−p)/p. For a desired 50% win rate, a=b (1:1); for 40%, a/b = 1.5; for 33%, a/b = 2. With positive drift μ>0 the achievable win rate at a given ratio rises above the driftless value — quantify the edge as the gap between the drift-p and the driftless-p.
- **Pitfall:** real fills are discrete and gappy; the continuous formula slightly *overstates* p when gaps overshoot the stop. Treat barrier-implied win rate as an upper bound.

#### 2.4 Expectancy & Kelly sizing
- **Expectancy (R-multiples):** E = w·b − (1−w). Yours: 0.393·1.915 − 0.607 ≈ **+0.146R per trade** (positive, modest).
- **Kelly fraction (Bernoulli/payoff form):** f* = (w·b − (1−w))/b = w − (1−w)/b. With w=0.393, b=1.915: f* = 0.393 − 0.607/1.915 ≈ **0.076**, i.e. full Kelly ≈ 7.6% of capital risked per trade.
- **Fractional Kelly:** use ½ or ¼ Kelly. Half Kelly retains ~75% of full Kelly's maximum compound growth rate while roughly halving variance — a derived mathematical property, not a rule of thumb (consistent with Thorp 2008's fractional-Kelly recommendation). Full Kelly produces roughly a **1-in-3 chance of a 50% drawdown** over a long trading horizon, and **Kelly is acutely sensitive to estimation error** — with only 150 trades your w and b are noisy, so quarter-Kelly is the defensible choice. The expected growth penalty for betting fraction c·f* of Kelly is a factor c(2−c) of the maximum log-growth.
- **Drawdown intuition:** a fraction-f strategy that loses k trades in a row draws down 1−(1−f)^k of capital; keep f small enough that a realistic losing streak (tail probability (1−w)^k) is survivable.

#### 2.5 Risk of ruin
- **Classic edge form (Kaufman, *Trading Systems and Methods*):** RoR = ((1 − Edge)/(1 + Edge))^U, where Edge = win-prob advantage and U = capital units = (ruin threshold $)/(risk-per-trade $).
- **Reward-aware form:** with Edge = (w·b − (1−w)) measured in risk units and U risk-units of cushion, RoR ≈ ((1−Edge)/(1+Edge))^U. A positive edge with small per-trade risk (large U) drives RoR toward zero; doubling risk-per-trade more-than-doubles RoR (it's exponential in U). Target RoR < 1–5%.
- **Better for asymmetric payoffs:** estimate RoR by Monte-Carlo — resample your trade distribution, run many equity paths, and count the fraction that breach a chosen drawdown threshold (e.g., 25–30%) before recovering. This respects your actual fat-tailed P&L better than the closed form.

#### 2.6 Breakeven win rate & execution frictions
- **No-cost breakeven:** w* = 1/(1+R) = L/(W+L), where R = target/stop. For R=1.915 (your payoff), w* = 1/2.915 ≈ **34.3%** — your 39.3% sits above it, the source of the +0.146R edge.
- **With per-trade cost c (slippage + commission), charged every trade:** EV = w(W−c) − (1−w)(L+c) = 0 ⇒

  w* = (L + c) / (W + L).

  The cost terms do **not** cancel; costs raise the required win rate by Δw* = (c/L)/(1+R) = (cost as fraction of stop)/(1+R).
- **Stop overshoot / slippage on the stop:** if adverse slippage makes the realized loss L+s and reduces the realized win to W−g, the *effective* reward:risk shrinks to R_eff = (W−g)/(L+s) < R, and w* = (L+s+c)/((W−g)+(L+s)). For MNQ, one tick = 0.25 index points = **$0.50 per contract** (CME Group); with round-turn commission plus ~1-tick slippage, a nominal 1:2 plan typically needs roughly 2–4 percentage points more win rate than the frictionless 33.3%. **Audit whether your 39.3% survives realistic fills** — this is where small intraday edges most often die.

#### 2.7 Optimal-stopping framing
- Where you control the exit (e.g., time-stop vs. let-it-run), the exit is an **optimal stopping problem**: maximize E[reward(X_τ) − cost·τ] over stopping times τ. For a drifted diffusion with a holding cost, the solution is a free-boundary problem yielding a threshold rule (exit when the value of continuing = value of stopping).
- The **secretary problem / 1/e rule** — Bruss (1984), "A Unified Approach to a Class of Best Choice Problems with an Unknown Number of Options," *Annals of Probability* 12(3):882–889, which generalizes the classical 1/e ≈ 37% threshold — is the relevant optimal-stopping result for the *research* side: from the set of theoretically-justified configurations, observe ~37% without committing, then pick the next one that beats all seen so far. This is a principled cap on how many variants to test before selection bias dominates (it directly limits the N feeding your DSR).

## Recommendations
**Stage 1 — Diagnose concentration & basic significance (do first, ~1 day of coding):**
1. Compute HHI₊, top-1/top-3 share, and Gini of monthly P&L.
2. Run **leave-one-month-out**: recompute PF, expectancy, and a stationary-bootstrap 95% CI excluding Jan 2026. **Decision threshold:** if PF drops below ~1.1 or the expectancy CI includes 0 without Jan 2026, treat the edge as month-dependent and do not scale it.
3. Stationary-bootstrap (10,000 resamples, Politis-White block length) CIs on PF, expectancy, per-trade Sharpe on the full sample and the ex-Jan sample.

**Stage 2 — Test against randomness & overfitting (~2–3 days):**
4. Permutation test on trade signs AND a **random-entry-timing Monte-Carlo** (matched trade count/holding times). Benchmark: real P&L must beat the 95th percentile of random entries.
5. If you tried multiple variants, compute the **Deflated Sharpe Ratio** with N = (effective) number of configurations, and **PBO via CSCV** (S=8–16). **Thresholds:** PBO > 0.5 ⇒ overfit, shelve it; DSR < 0.95 ⇒ not significant after deflation.
6. Compute **Minimum Track Record Length** for SR* = 0 at 95%; if MinTRL > 150, you simply need more trades — keep trading paper/small and re-test.

**Stage 3 — Structure brackets analytically (~2 days):**
7. Estimate first-hour μ and σ for MNQ; compute the **barrier-implied win rate** for your current (a,b) and compare to 39.3%. If realized ≪ implied, investigate entry timing and fills.
8. Convert stops/targets to **ATR multiples** for regime adaptivity; standardize the entry trigger as a **VWAP z-score**.
9. Compute the **friction-adjusted breakeven win rate** with realistic MNQ slippage+commission; confirm 39.3% clears it with margin.

**Stage 4 — Size conservatively:**
10. Use **quarter-Kelly** (f* ≈ 0.076 → bet ≈ 1.9% risk) at most, and verify **Monte-Carlo risk-of-ruin < 1–5%** at a 25–30% drawdown threshold. Re-estimate Kelly inputs as the sample grows.

**Benchmarks that would change the plan:** edge survives LOMO with PF≥1.2 and a bootstrap CI excluding 0 → proceed to Stage 3–4; DSR≥0.95 and PBO≤0.4 → treat as a genuine candidate; any of (ex-Jan PF<1.1, PBO>0.5, realized win rate below friction-adjusted breakeven) → shelve or redesign.

## Caveats
- **All bootstrap/permutation CIs assume the resampling scheme matches the dependence structure.** Intraday trades clustered in sessions/regimes violate i.i.d.; use the stationary bootstrap and report block length. Overlapping windows and autocorrelation **inflate** apparent significance and shrink the *effective* sample below 150.
- **150 trades is a small sample.** Every statistic here has wide error bars; treat point estimates skeptically and prefer the lower CI bound for decisions.
- **DSR/PBO require honest accounting of how many variants you tried** (including informal manual tweaks). Understating N defeats the entire deflation; survivorship in your own search is the dominant risk.
- **Barrier formulas assume continuous price and constant μ, σ.** Real markets gap, μ/σ vary intraday, and stop overshoot makes realized win rate ≤ the continuous-model value. Use barrier results as design guides and upper bounds, not promises.
- **Kelly is fragile to estimation error** at this sample size; full Kelly here is reckless. Fractional Kelly + Monte-Carlo RoR is the safer path.
- Several practitioner sources (trading-education sites) corroborate the trade-structure formulas, but the *authoritative* references are academic: Politis & Romano (1994) and Politis & White (2004) for bootstrap; White (2000) and Hansen (2005) for data-snooping tests; Bailey & López de Prado (2014) for DSR/PSR; Bailey, Borwein, López de Prado & Zhu (2017) for PBO; Lo (2002) for Sharpe statistics; Karlin & Taylor and Borodin & Salminen for first-passage; Feller Vol. 1 for gambler's ruin; Harvey, Liu & Zhu (2016) for the multiple-testing hurdle; Bruss (1984) for optimal-stopping the search.