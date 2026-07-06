# Under-Explored, Evidence-Grounded Sources of Intraday Daily Directional Bias for MNQ/NQ

## TL;DR
- The single best-supported, genuinely under-explored direction is the **overnight/intraday cross-period structure** (Lou-Polk-Skouras tug-of-war; Boyarchenko-Larsen-Whelan overnight drift; Hendershott-Livdan-Rösch night/day beta): these are knowable at the open, peer-reviewed in top journals, and grounded in inventory/clientele mechanisms — but most documented effects are *overnight* phenomena, so the trader's edge is in conditioning RTH bias on overnight sign/magnitude/open-location, not in trading the overnight return itself.
- Rank for probing next: (1) overnight-structure conditioning, (2) dealer-gamma/GEX regime as a *volatility-and-persistence* filter (not a direction oracle), (3) cross-asset/options-flow imbalance (OVI) as an early bias, (4) opening-return/initial-balance persistence — with VWAP-positioning and Market-Profile "day-type" taxonomies graded LOW because they are largely execution-benchmark or folklore with no rigorous directional validation.
- Under a trailing-drawdown constraint, the binding risk is that **multiple entries on a wrong daily bias multiply cluster-losses**; every candidate below has documented negative-skew or regime-dependence (especially short-gamma days and large-gap days), so position-multiplication should be gated on regime, not applied uniformly.

## Key Findings

**Distinguish what is knowable early from what is merely real.** Many famous "overnight" results (the equity premium accruing overnight; the 2–3am drift) are not directly tradable by an RTH-flat-by-close trader. Their value is as *conditioning variables*: the sign and size of the close-to-open move, where price opens in the overnight range, and the dealer-gamma regime are all observable by 9:30 ET and can bias the rest of the session.

**Grade summary (directional, RTH-actionable, under-explored):**
- Overnight-structure conditioning — **Moderate** (strong underlying research, but most effects are overnight-located; RTH-direction mapping is weaker and decaying).
- Dealer gamma / GEX regime — **Moderate for volatility/persistence, Weak for direction**; best academic anchors are Baltussen-Da-Lammers-Martens (JFE 2021) and Barbon-Buraschi (working paper).
- Options-flow imbalance (OVI) / Pan-Poteshman option signals — **Moderate**, but evidence is mostly overnight and cross-sectional.
- Opening-return / initial-balance persistence — **Moderate** (Gao-Han-Li-Zhou JFE 2018 momentum; concentrated on high-vol/news days) but overlaps the trader's already-explored ORB.
- Cross-asset/breadth (ES-NQ lead-lag, TICK, A/D) — **Weak-to-Moderate**; lead-lag is at the seconds scale, breadth is largely contemporaneous, not predictive.
- Prior-day structure beyond H/L (close location, inside/outside day) — **Weak**; mostly folklore, thin peer-reviewed support.
- VWAP-relative positioning — **Weak**; rigorous literature treats VWAP as an execution benchmark, not a directional signal.
- Market Profile open-type/day-type taxonomy — **Weak/none**; confirmed no peer-reviewed validation.
- Pre-FOMC drift — **Decayed**; documented but essentially gone post-2015.

## Details

### 1. Overnight / Globex session structure as a predictor of RTH direction — RANK #1
**What it is.** Using the sign and magnitude of the close-to-open (overnight) return, the overnight gap, the overnight high/low/range, and where the cash open sits relative to the overnight range and prior close, as a conditioning variable for RTH directional bias.

**Mechanism.** Three competing, well-developed mechanisms exist. (a) *Inventory/liquidity provision* — Boyarchenko, Larsen & Whelan ("The Overnight Drift," NY Fed Staff Report 917; CEPR DP14462; JFE 2023) show dealers absorb end-of-day order imbalances and are compensated via overnight returns, with a strong negative relationship between end-of-day sell imbalances and subsequent overnight reversals. The drift is concentrated in a 2–3am ET window so robust that the "2:00–3:00 return is statistically significant on every day of the week, and in 9 out of 12 months of the year," and overnight drift returns were "positive in 20 out of 23 years since 1998 and statistically significant in 17 of these." (b) *Clientele tug-of-war* — Lou, Polk & Skouras ("A Tug of War," JFE 2019, 134(1):192–213) document that overnight returns continue overnight and intraday returns continue intraday, with a cross-period reversal: overnight returns negatively predict subsequent intraday returns. (c) *Beta/illiquidity* — Hendershott, Livdan & Rösch ("Asset pricing: A tale of night and day," JFE 2020, 138(3):635–662) find beta is positively priced overnight (+14 bps per unit beta) and negatively priced intraday (−15 bps); the highest-beta decile has the lowest day return (−8 bps) and highest night return (+20 bps), so high-beta names (Nasdaq is high-beta) tend to give back overnight gains during the day. Their beta-sorted decile regressions fit R²=92.2% for day returns and 96.2% for night returns.

**Evidence quality: Moderate-to-strong for the underlying phenomena, weaker for the specific RTH-direction mapping.** The tug-of-war reversal implies a *fade-the-overnight* intraday bias; the Hendershott beta result reinforces this for high-beta Nasdaq (the day "destroys the night"). But Lou-Polk-Skouras themselves note the effect requires extreme turnover and is concentrated in large stocks; the arxiv working paper "Does Overnight News Explain Overnight Returns?" (2025) notes the over-intra effect "falls short of being a viable trading strategy" on its own due to turnover. Cooper, Cliff & Gulen ("Like Night and Day," 2008) note the day-night effect "is driven in part by high opening prices which subsequently decline in the first hour of trading" — directly actionable: opening strength in a high-beta index has a documented tendency to fade in the first hour.

**How early knowable.** Fully at 9:30 ET (overnight return, gap, range, open location are all set).

**Transaction-cost realism.** The raw academic effects are small per day and turnover-heavy; an RTH trader is not trading them directly but using them as a free conditioning filter, so incremental cost is zero. MNQ round-trip costs are a few ticks; the bias must survive that on the *intraday* leg only.

**Multiple-entry combination.** Use overnight sign/open-location to set a directional tilt (e.g., fade an extended gap-up open in the first hour consistent with the documented first-hour give-back), and allow scaling/re-entry only while price respects the overnight range boundary that defines the thesis; abandon multiplication once the overnight high/low is decisively broken.

**Decay/risk flags.** The overnight effects are widely published (McLean-Pontiff would predict ~50% post-publication decay). Real-world capacity has already been tested and failed: NightShares launched the NightShares 500 ETF (NSPY) and NightShares 2000 ETF (NIWM) on June 28, 2022, explicitly citing "The Overnight Drift" (NY Fed); both were liquidated and ceased trading July 31, 2023 after returning −4.6% and −4.7% since launch while the S&P returned double digits — i.e., the packaged overnight-drift product was withdrawn, a cautionary datapoint on tradability net of costs. Gap days also carry negative skew: large news gaps tend to continue, small gaps tend to fade — multiplying entries on the wrong side of a continuing news gap is exactly the cluster-loss the trailing drawdown punishes.

### 2. Dealer gamma / GEX regime — RANK #2 (as a persistence/volatility filter, NOT a direction oracle)
**What it is.** Net dealer gamma exposure, estimated from the options chain pre-open, classifies the session into a positive-gamma (mean-reverting, range-bound, vol-suppressing) regime versus a negative-gamma (trend-amplifying, vol-expanding) regime, with a "gamma flip" level between them.

**Mechanism.** Hedging short gamma requires trading in the direction of price moves (buy higher, sell lower), amplifying trends; long gamma requires the opposite, suppressing moves. This is mechanical dealer delta-hedging.

**Evidence quality: Moderate for the volatility/persistence effect; Weak for standalone direction.** The rigorous anchors: Baltussen, Da, Lammers & Martens, "Hedging Demand and Market Intraday Momentum," JFE 2021, 142(1):377–403 — using 60+ futures 1974–2020, the last-30-minute return is positively predicted by the rest-of-day return, linked to gamma-hedging demand, with the effect reverting over subsequent days. Barbon & Buraschi, "Gamma Fragility" (Univ. St. Gallen School of Finance Research Paper 2020/05, SSRN 3725454, rev. 2021) — link aggregate dealer gamma imbalance to intraday momentum (negative gamma) versus reversal (positive gamma), conditional on illiquidity. Both are about *autocorrelation sign and volatility*, not a clean up/down call. The huge caveat: most public GEX is practitioner-driven (SpotGamma, etc.), naive models cannot see dealer-vs-customer sign, official open interest updates only overnight, and 0DTE options are missed by single-expiry models — and 0DTE now dominates: 0DTE SPX options averaged a record 2.3M contracts/day in 2025, 59% of total SPX volume per Cboe's "State of the Options Industry: 2025," with monthly share hitting a record 62.4% in August 2025. So the *sign* of net gamma is frequently mis-estimated without 0DTE-aware data.

**How early knowable.** Pre-open from prior-day OI; intraday refinement requires real-time flow models. The regime classification is knowable at 9:30.

**Transaction-cost realism.** As a filter (not a traded signal) cost is negligible; data costs for quality, 0DTE-aware GEX are non-trivial.

**Multiple-entry combination.** This is the most natural fit for the trader's constraint: **gate the multiple-entry scheme on regime.** Negative-gamma (trend) days justify re-entry/scaling in the trend direction; positive-gamma (range) days argue for *single* fade entries and against trend-multiplication. This directly addresses cluster-loss risk because the regime that punishes trend-multiplication (positive gamma → failed breakouts) is identifiable in advance.

**Decay/risk flags.** Negative-gamma days are precisely the high-tail-risk, large-range days; mis-signing the regime and multiplying entries is catastrophic under trailing drawdown. Treat GEX as one input among several, not a price target.

### 3. Options-flow imbalance (OVI) and option-volume signals — RANK #3
**What it is.** Normalized imbalance between bullish-view and bearish-view option volumes, observable from early-session order flow, as a predictor of underlying direction.

**Mechanism.** Informed traders prefer the leveraged options market; their net positioning leaks directional information.

**Evidence quality: Moderate.** Michael, Cucuringu & Howison, "Option Volume Imbalance as a Predictor for Equity Returns" (SSRN 4019647, 2022) find strong predictability of *excess overnight returns*, strongest from market-maker volumes and high-implied-vol contracts, with put volume more informative than calls (some annualized Sharpe figures up to 4.5 in a frictionless betting scheme — explicitly before transaction costs). Pan & Poteshman, "The Information in Option Volume for Future Stock Prices" (RFS 2006) — low put-call-ratio stocks outperform high by 40+ bps next day, driven by nonpublic information. Hu (JFE 2014) on option-to-stock volume imbalance. Caveat: predictability is mostly *overnight* and cross-sectional (single stocks), not index-RTH; the index application is less established.

**How early knowable.** Early session, as opening option flow accumulates.

**Transaction-cost realism.** The headline Sharpes ignore costs; the authors flag this. Index-level, the realistic edge is much smaller.

**Multiple-entry combination.** Use as a tilt confirmer alongside overnight structure; do not scale on OVI alone given the overnight/cross-sectional provenance.

**Decay/risk flags.** Data-snooping risk is real in the nonlinear OVI study (many participant-class cuts). Treat as exploratory.

### 4. Opening-return / initial-balance persistence — RANK #4 (partially overlaps already-explored ORB)
**What it is.** The first 30–60 minute return (or initial-balance range) as a predictor of the rest-of-session direction and of trend-vs-range day character.

**Mechanism.** Infrequent rebalancing (Bogousslavsky, JF 2016, 71(6):2967–3006) and late-informed traders trading near the close in the open's direction; gamma-hedging (Baltussen et al.).

**Evidence quality: Moderate but caveated.** Gao, Han, Li & Zhou, "Market Intraday Momentum," JFE 2018, 129(2):394–414 — first half-hour return predicts last half-hour (scaled slope ~6.94, significant at 1%, R²~1.6%, rising to 2.6% adding the 12th half-hour), stronger on high-vol, high-volume, recession, and macro-news days; present in 11 liquid ETFs but *absent in FX and commodity futures*. A Taiwan index-futures study (Int. Rev. Econ. Finance, 2012) finds opening return predicts the day's return net of costs. ORB: Holmberg, Lönnbark & Lundström (Finance Research Letters 2013, 10(1):27–33) find ORB beats a fair game; Lundström (2017) finds profitability concentrated in high-volatility states. First-hour realized volatility also explains a large share (studies report up to ~68%) of daily volatility — so the early session strongly predicts the day's *range/magnitude* even where direction is harder. Important: this substantially overlaps the trader's already-explored ORB and Gao first-half-hour momentum — the *under-explored* twist is conditioning it on the gamma regime and on whether first-hour volatility signals a wide/trend day.

**How early knowable.** By 10:00–10:30 ET.

**Transaction-cost realism.** Survives costs in the SPY/ETF studies; on MNQ the small R² means edge is thin and regime-dependent.

**Multiple-entry combination.** Best paired with the gamma filter: trend-multiplication only when first-hour range is wide AND regime is negative-gamma.

**Decay/risk flags.** Small R²; high false-discovery risk for short-horizon prediction (the authors explicitly guard against this, citing Harvey-Liu-Zhu). Decay likely given publication.

### 5. Cross-asset / breadth (ES-NQ lead-lag, TICK, A/D) — RANK #5
**What it is.** Using S&P/ES leadership, sector breadth, advance-decline, TICK, or the ES-NQ relationship at the open as an early NQ bias.

**Mechanism.** Index futures lead cash by seconds; breadth reveals participation behind a move.

**Evidence quality: Weak-to-Moderate, and mostly NOT predictive at a tradable horizon.** The rigorous lead-lag literature (Kawaller-Koch-Koch, JF 1987; Chan 1992; modern wavelet studies) finds futures lead cash by seconds to ~20 minutes — too fast to be a daily directional bias and already arbitraged. Breadth/TICK/A-D are heavily practitioner-driven with essentially no peer-reviewed evidence that they *predict* (rather than contemporaneously describe) index direction; the academic order-imbalance literature (Chordia-Roll-Subrahmanyam, JFE 2004) shows imbalance predicts returns but is a microstructure, not a breadth, result.

**How early knowable.** Real-time intraday.

**Transaction-cost realism.** ES-NQ lead-lag at seconds scale is a latency game, not viable for a discretionary RTH trader.

**Multiple-entry combination.** At most a confirmation overlay; not a primary bias.

**Decay/risk flags.** Largely folklore for the breadth/TICK claims; treat skeptically.

### 6. Order-flow / opening-imbalance bias — supporting evidence
**What it is.** Opening-auction imbalance and early-session cumulative delta as predictors of day direction.

**Evidence quality: Moderate microstructure foundation, but cross-sectional/equity-specific.** Chordia, Roll & Subrahmanyam ("Order imbalance and individual stock returns," JFE 2004) establish that order imbalances predict short-horizon returns. Brown ("The Quote Not Taken: Inefficient Price Discovery in Opening Auctions," SSRN 5498938) shows publicly observable retail order flow predicts short-term *reversals* at the open (an estimated $16bn retail-to-wholesaler transfer), with a difference-in-differences around the 2020 NYSE floor closure attributing much of the inefficiency to auction design. Caveat: these are stock-level NYSE-auction results; index futures (NQ) have no centralized opening auction, so the direct transfer to MNQ is conceptual, via the cumulative-delta proxy.

**How early knowable.** First minutes of RTH.

**Multiple-entry combination.** Early cumulative-delta sign can confirm or veto the overnight-structure tilt before committing multiple entries.

### 7. Other candidates
- **Prior-day structure beyond H/L (close location in range, inside/outside day, multi-day swing).** Weak peer-reviewed support; mostly trade folklore. The closest rigorous item is futures trend-strength work (arxiv "Trends, Reversion, and Critical Phenomena in Financial Markets") showing next-day return is a cubic function of trend strength (linear persistence at moderate strength, reversion at extremes) — aggregated across 24 markets/30 years, statistically significant but not strong at single-market daily scale. Grade: Weak-Moderate.
- **VWAP-relative positioning.** The rigorous VWAP literature is about *execution* (minimizing slippage vs. benchmark); there is no peer-reviewed evidence that price's position relative to VWAP predicts direction beyond what trend/momentum already capture. "VWAP magnet" and "above VWAP = bullish bias" are practitioner claims. Grade: Weak.
- **Market Profile open-type/day-type taxonomy (open-drive, open-test-drive, trend day vs. balanced day).** Confirmed via dedicated search: **no peer-reviewed validation exists.** The taxonomy originates with J. Peter Steidlmayer (CBOT, 1980s) and lives entirely in trade press and vendor materials. Vendor accuracy claims (e.g., "76% accuracy" for open vs. overnight midpoint) are uncited. The only academic-adjacent item is an unrefereed SSRN working paper whose own thesis is that the profile "reveals structure but not direction" — which argues *against* the open-type-predicts-direction folklore. Grade: Weak/none — explicitly de-prioritize.
- **Pre-FOMC drift.** Lucca & Moench (JF 2015, 70(1):329–371; FRB NY Staff Report 512) documented that the S&P 500 rose on average 49 basis points during the 24h before FOMC announcements, "a staggering 80% of the annual U.S. equity premium since 1994," with a pre-FOMC strategy yielding "an annualized Sharpe ratio of above 1.1." But the "disappearing pre-FOMC announcement drift" literature (Finance Research Letters 2020) finds it "essentially disappeared after 2015 in both announcements accompanied by press conferences and announcements not accompanied by press conferences." Knowable on the ~8 scheduled FOMC days/year. Grade: Decayed; only worth probing on FOMC days, and even then weak.

## Recommendations
**Stage 1 (probe first, lowest cost):** On your own MNQ data, test **overnight-structure conditioning** as a directional filter — regress RTH (open-to-close) return sign on (i) overnight return sign/size, (ii) open location within the overnight range, (iii) gap size buckets, splitting news-gap vs. quiet-gap days. Benchmark against the documented first-hour give-back (Cooper-Cliff-Gulen) and the tug-of-war fade. Threshold to advance: a stable, out-of-sample hit-rate edge that survives 2–3 ticks MNQ cost on the intraday leg.

**Stage 2 (gate your multiple-entry scheme):** Build a **gamma-regime classifier** (even a crude positive/negative net-gamma proxy, ideally 0DTE-aware given 0DTE is ~60% of SPX volume) and condition entry-multiplication on it — allow scaling/re-entry on negative-gamma (trend) days, restrict to single fade entries on positive-gamma (range) days. This is the highest-leverage change for your trailing-drawdown constraint because it suppresses cluster-losses on the exact days (failed breakouts in positive gamma) where multiplication is most punishing. Threshold: demonstrate that loss-clustering (consecutive-stop frequency) falls in positive-gamma classification without killing trend-day capture.

**Stage 3 (confirmers, not primaries):** Layer **OVI/option-flow** and **early cumulative-delta** as tilt-confirmers that must agree with the Stage-1 bias before committing the 2nd/3rd entry. Treat ES-NQ lead-lag, TICK, A/D, VWAP position, and Market-Profile day-types as **non-primary** — do not allocate research budget to them until Stages 1–2 are exhausted.

**What would change these recommendations.** If your overnight-conditioning hit-rate edge is <2–3% over base after costs and unstable across years, drop it (consistent with McLean-Pontiff decay). If your gamma proxy cannot reliably sign net gamma (likely without paid 0DTE-aware data), demote GEX to a pure volatility-sizing input rather than a regime gate. If first-hour-range conditioning merely reproduces your existing ORB results, it is not additive.

## Caveats
- **Publication decay (McLean & Pontiff, Journal of Finance 2016, 71(1):5–32, 97 predictors):** "Portfolio returns are 26% lower out-of-sample and 58% lower post-publication... We estimate a 32% (58%–26%) lower return from publication-informed trading." Every named effect here is published, and some have already died (pre-FOMC drift) or failed in product form (the NightShares overnight-drift ETFs liquidated in 2023).
- **Most "overnight" research is not RTH-tradable.** The equity premium / 2–3am drift accrue when you are flat; their value is purely as conditioning information, and the RTH-direction mapping (the part you can trade) is the weakest-tested link.
- **Negative skew and cluster-loss under trailing drawdown:** negative-gamma days, large-news-gap days, and high-volatility states are where trends run — and also where multiplying entries on a wrong bias produces correlated, drawdown-ending losses. Position-multiplication must be regime-gated, never uniform.
- **Folklore contamination:** Market Profile day-types, VWAP magnets, "smart money," and most TICK/breadth directional claims have no rigorous support; the literature that exists (order imbalance, lead-lag) is either cross-sectional/equity-specific or operates at sub-minute horizons that a discretionary RTH MNQ trader cannot exploit.
- **Data quality for GEX/OVI:** public/naive models mis-sign dealer gamma and miss 0DTE; without dealer-vs-customer-aware data, these signals are noisy.
- The deliverable here is a ranked research agenda with graded evidence, not a finished strategy; all effect sizes must be re-validated on the trader's own MNQ data and execution assumptions.