# Futures Prop Firm Deployment Guide: MNQ "Let-It-Breathe" Strategy (June 2026 Snapshot)

## TL;DR
- **For a ~$2,538 drawdown-at-15-MNQ, let-it-breathe strategy, the cleanest funded-phase fits are TradeDay's "Fast Pass" (EOD that STAYS EOD when funded, no scaling) and Alpha Futures (EOD trailing on ALL stages, full contracts day one on Advanced/Standard).** Lucid (both Flex and Pro) and MyFundedFutures Pro are strong EOD-funded options but carry contract-scaling or buffer frictions.
- **AVOID for funded-phase intraday-trailing traps: Take Profit Trader PRO (eval EOD → funded INTRADAY), MyFundedFutures RAPID (funded intraday), Bulenox Option 1, FFN Express MAX, and TradeDay "Quick Pay" (passed EOD eval → funded INTRADAY).** Apex 4.0 EOD is structurally workable but contract scaling cuts you to half-size until you clear the safety net.
- **A $2,538 DD at 15 MNQ needs ~$3,000+ of room, so every 100K-tier account (≈$3,000 DD) leaves only ~$460 cushion — genuinely tight. Strongly consider a 150K tier (~$4,500 DD) or trading 12-13 MNQ instead of 15.** Critically, **15 MNQ = 150 micros, and NO 100K account in this list allows 150 micros** (they cap at 60–120) — so a 150K tier is effectively mandatory to trade 15 MNQ at all.

## Key Findings

### The structural problem with your numbers
Your max drawdown of $2,538 at 15 MNQ contracts is the binding constraint, and it fails on **two** independent axes at the 100K tier:

1. **Drawdown room.** On a 100K-tier account the funded drawdown is almost universally $3,000. That leaves roughly $462 of cushion between your strategy's natural drawdown and account death — about 2.3 MNQ points of extra room. Survivable but unforgiving for a "let-it-breathe" style. A 150K tier (typically $4,500 DD) gives ~$1,962 of cushion, which is far more appropriate.
2. **Contract caps.** 15 MNQ = 150 micros = 1.5 minis of exposure. Standard 100K accounts cap you at 60–120 micros (6–12 minis). 150 micros is only reliably available at the **150K tier** (15 minis / 150 micros). This alone forces the 150K decision if you genuinely want to deploy 15 contracts.

### The EOD-eval-but-funded-intraday trap (most important)
Several firms advertise a friendly EOD evaluation, then switch the FUNDED account to intraday trailing — fatal for a let-it-breathe style. Confirmed traps as of June 2026:
- **Take Profit Trader:** Test (eval) is EOD trailing; **PRO funded is INTRADAY trailing.** Only the live PRO+ tier (auto-promotion, not guaranteed) reverts to EOD.
- **MyFundedFutures RAPID:** funded sim uses intraday trailing.
- **TradeDay "Quick Pay":** all Quick Pay funded accounts use intraday trailing even if you passed an EOD evaluation. Only "Fast Pass" keeps EOD after funding.
- **Topstep:** Combine is intraday-trailing; XFA funded is EOD-trailing (so funded is actually fine), but contract/payout realities matter.

---

## Details by Firm (100K tier unless noted)

### 1. Apex Trader Funding — 100K EOD (PRIORITY)
Apex relaunched as "4.0" on **March 1, 2026**, a complete product replacement. Legacy accounts run old rules until closed; new accounts are 4.0 only. Two products: **EOD Trailing** and **Intraday Trailing**.

- **Drawdown (100K EOD):** $3,000 EOD trailing. Recalculated at 4:59:59 PM ET on closing balance, enforced in real time the next session. **Stays EOD in the funded Performance Account (PA)** — no intraday switch. Trailing stops permanently once the EOD threshold reaches starting balance + $100 ($100,100). This is a clean EOD structure — good fit on the drawdown axis.
- **Contracts:** 100K allows roughly 14 contracts in eval but the **PA scales**: you start at HALF max until your balance clears the safety net (starting balance + drawdown + $100 = $103,100), then full size unlocks next session, with tier-based scaling thereafter. Practically, experienced traders describe operating at 2–6 contracts on the 100K due to the $1,500 DLL interaction. **15 MNQ would breach the early half-size cap; you cannot reliably trade 15 MNQ until you clear ~$103,100, and even then the 100K standard size sits well below 150 micros.**
- **Profit target / cost:** $6,000 target. EOD eval often ~$30 on promo (full retail $297). **PA activation fee $99 (EOD)** paid on passing. No monthly subscription on 4.0; promo codes do not discount the activation fee.
- **Payouts:** 100% profit split. 6-payout lifetime cap ladder on 100K EOD: $2,000 / $2,500 / $2,500 / $3,000 / $3,500 / $4,000 = $18,000 max, then account closes. 5 qualifying days ($300+ net each on 100K EOD), 50% consistency rule (funded only), $500 minimum, safety net $103,100 (must stay above after withdrawal — min request balance $103,600).
- **Daily loss limit:** $1,500 on 100K EOD. Hitting it pauses trading for the session; does not close account. (Intraday product has no DLL but real-time trailing.)
- **Min hold / anti-scalping:** As of March 2026, Rithmic/Tradovate reject orders without attached stop-loss and take-profit. No minimum hold time stated. Overnight banned (flat by 4:59 PM ET). Metals suspended since March 14, 2026.
- **Reputation:** Apex self-reports $750M+ paid since 2022 and 100,000+ funded traders, with a 4.4/5 Trustpilot rating from approximately 18,000 reviews as of April 2026. Automated payouts via Deel/Plane/ACH. The 2026 overhaul shows willingness to make sweeping changes (though legacy accounts were grandfathered).

### 2. Take Profit Trader — 100K (PRIORITY) — ⚠️ FUNDED INTRADAY TRAP
- **Drawdown (100K):** $4,000 trailing. **Test (eval) = EOD trailing; PRO (funded sim) = INTRADAY trailing** that tracks peak balance including unrealized gains. This is the single biggest disqualifier for a let-it-breathe style — your unrealized give-back permanently moves the floor. PRO+ (live, auto-promoted, not guaranteed) reverts to EOD with 90/10 split and no buffer.
- **Contracts:** 100K = up to 12 minis / 120 micros, same limit in Test and PRO. **120 micros < 150 micros (15 MNQ)** — you cannot trade 15 MNQ on the 100K; you'd need the 150K (15 minis / 150 micros).
- **Profit target / cost:** $6,000 target (6%). 100K Test = $330/month subscription. PRO activation $130 one-time (waived with NOFEE40 promo). No daily loss limit (removed Jan 2025).
- **Payouts:** PRO 80/20, PRO+ 90/10. Day-one withdrawals above the buffer (buffer = max drawdown = $4,000 on 100K, so withdraw above $104,000). No payout cap, no minimum days, no lifetime cap. Min payout $250 ($50 fee under $250). 50% consistency applies in Test only.
- **Min hold / anti-scalping:** No minimum hold time; scalping allowed. Counter-positions (e.g., simultaneous NQ/MNQ longs+shorts) prohibited. News-event flat rule on PRO/PRO+ (FOMC, NFP — flat 1 min before/after).
- **Reputation:** Founded 2021 (James Sixsmith, Orlando). Holds a 4.4/5 Trustpilot score from 8,979+ reviews (2,788 verified) — among the largest review bases in the futures prop category. Strong on-demand payout reputation, active Discord. Solid firm — but the PRO intraday drawdown makes it a poor structural fit for your style unless/until you reach PRO+.

### 3. Lucid Trading — LucidFlex & LucidPro 100K (PRIORITY)
Founded early 2025 by CEO AJ Campanella under Lucid Prop Ltd (registered 3500 S Dupont Hwy, Dover, DE 19901); $60M+ paid to 50,000+ traders per Propfirmsfinder, with LucidFlex launched late November 2025. Trustpilot 4.7/5 from 3,218 reviews (2,538 of which are from people invited by the firm), per PropFirm App (June 2026). Newer firm with frequent rule changes (restructured ~4× in 12 months) — counterparty/rule-churn risk is the main concern.

**Both LucidFlex 100K and LucidPro 100K:**
- **Drawdown:** $3,000 Max Loss Limit, **EOD trailing in BOTH eval AND funded** — no intraday switch. Locks at $100,100 once the account closes above $103,100 (Initial Trail Balance). For Flex, requesting a payout also locks the MLL. **This is exactly the EOD/locking structure your style wants.**
- **Profit target:** $6,000 on the 100K.
- **No activation fee** on either; one-time eval fee. LucidFlex 100K eval ~$225 list; LucidPro 100K ~$285 list (heavy promo discounts common, ~50% off). Reset fee on fail.
- **Profit split:** 90/10. (The "100% first $10K" perk is grandfathered to pre-Nov-28-2025 accounts only — do not count on it for new accounts.)
- **Min hold / anti-scalping:** No minimum hold time; scalping and news trading allowed. Anti-MICROscalping flag only if >50% of profits come from trades held ≤5 seconds. Flat by 4:45 PM EST.

**LucidFlex 100K specifics:**
- **No daily loss limit** (eval or funded).
- **Contracts:** 6 minis / 60 micros max, but **funded account SCALES from ~3 minis/30 micros** based on profit (tiers: $0–999 = 3 minis; $1,000–1,999 = 4; $2,000–2,999 = 5; $3,000+ = 6 minis/60 micros), updating at session close. **60 micros < 150 micros (15 MNQ)** — you cannot trade 15 MNQ on the Flex 100K at all.
- **Consistency:** 50% in eval, none when funded. 5 winning days @ ≥$200/day per payout cycle. No buffer required. Payout cap 50% of profit, max $2,500/request, 5 payouts then move to live.

**LucidPro 100K specifics:**
- **Daily loss limit:** $1,800 fixed (soft breach — pause, not account loss), replaced by LucidScale DLL (60% of peak EOD profit) once above the trail.
- **Contracts:** 6 minis / 60 micros, **full size immediately, no scaling.** Still **60 micros < 150 micros — cannot trade 15 MNQ.**
- **Consistency:** none in eval, **40% on funded payouts** (35% grandfathered for pre-Nov-28-2025 accounts). Buffer = $103,100 (MLL+$100) required to withdraw. Min profit goal $750/cycle. Payout caps $2,500 (1st), $3,000 (2nd+).

**Bottom line on Lucid:** drawdown structure is ideal (EOD funded, locks), but the **100K micro caps (60 micros) make 15 MNQ impossible** — you'd need a 150K-size Lucid account (verify its micro cap).

### 4. TradeDay — 100K (shortlist) — ⚠️ Quick Pay vs Fast Pass split
TradeDay (TradeDay LLC, founded 2020 by James Thorpe and Steve Miley, Chicago) relaunched as "TradeDay 2.0" on **May 29, 2026.** Old EOD/Intraday/Static lineup closed to new purchases. Two new routes: **Quick Pay** and **Fast Pass.** Static accounts discontinued.
- **Drawdown (100K):** $3,000 trailing, freezes at starting balance. **CRITICAL: all Quick Pay funded accounts use INTRADAY trailing even if you passed an EOD evaluation. Only Fast Pass keeps EOD drawdown after funding.** → **Choose Fast Pass for your style.**
- **Contracts:** 100K = 10 minis / 100 micros (per pre-2.0 specs; verify current). **100 micros < 150 micros — 15 MNQ not possible on 100K; need 150K (15 minis/150 micros).**
- **Profit target / cost:** $6,000 target on 100K. Activation fee now $0. ~$206 list (50% off with code).
- **Payouts:** Day-one payouts, no minimum trading days, processed <24h via Riseworks. Profit split 80% → 90% (after $50K cumulative) → 95% (after $100K). Buffer = starting + max drawdown ($103,000); withdrawing below buffer pays at 50/50. Consistency 30% (Quick Pay) / 45% (Fast Pass) on eval. Disclosed evaluation pass rate is 36% for January–June 2026, with Funded Live two cuts above that.
- **Daily loss limit:** none historically (only trailing/static drawdown).
- **Live progression:** consistent traders move to Funded Live (real capital) — reduces counterparty risk vs pure-sim firms.
- **Reputation:** 4.6/5 on Trustpilot from 1,348 reviews (363 invited), per PropFirm App; praised for payout speed.

### 5. Alpha Futures — 100K / 150K (shortlist) — STRONG FIT
Alpha Futures Limited (UK Companies House #15655643, launched July 2024, part of Alpha Group). Plans: Premium (replaced Standard May 1 2026), Advanced, Zero.
- **Drawdown:** **EOD trailing on ALL accounts and ALL stages** (eval AND funded) — explicitly does not switch to intraday. Locks at starting balance once EOD balance clears the drawdown. 100K drawdowns: Zero/Standard $4,000 (4%), Advanced $3,500 (3.5%), Premium 3% (~$3,000). **This is a best-in-class EOD structure for let-it-breathe.**
- **Contracts (100K):** Standard/Advanced = 10 minis / 100 micros; Zero = 6 minis / 60 micros. **100 micros < 150 micros — 15 MNQ needs the 150K (15 minis / 150 micros).** Advanced/Premium = full contracts from day one (no scaling); Standard/Zero use a scaling plan.
- **Profit target / cost:** Zero/Standard 100K = $6,000 (6%); Advanced 100K = $8,000 (8%). Monthly subscription ($119–$279 depending on plan) + $149 activation (Advanced/Standard; Zero has none).
- **Payouts:** Up to 90% split (Advanced/Zero flat 90%; Standard tiered 70→80→90). 5 winning days @ $200+, up to 4 payouts/month, withdraw up to 50% of profit per request, processed ≤48h. **Withdrawals do NOT reduce the MLL** (rare, favorable). No consistency rule on Advanced Qualified accounts.
- **Daily loss limit:** "Daily Loss Guard" on Zero (and Standard Qualified); none on Advanced/Premium. Soft breach.
- **Min hold / anti-scalping:** No blanket minimum hold, but trades <10 ticks held <2 minutes are flagged if they form a profit pattern. Automated/bot trading prohibited (you hand-execute, so OK).
- **150K tier:** Advanced 150K = $12,000 target, $5,250 DD, 15 minis/150 micros, 90% — fits 15 MNQ with ~$2,700 cushion over your $2,538 DD.
- **Reputation:** Per alpha-futures.com (verbatim): "We hold a 4.9 / 5 rating on Trustpilot with over 17,000 reviews, and we have awarded $70M in performance fees to date." Live-capital progression via Alpha Prime.

### 6. MyFundedFutures (MFFU) — Pro / Core 100K (shortlist)
US futures-only (Fort Worth, founded 2023, Matt Leech). Trustpilot 4.9 (11,000+). No daily loss limit on any plan. Activation fees eliminated. Plan choice is everything — drawdown structure differs by plan.
- **Pro 100K:** **3% EOD trailing ($3,000), stays EOD in funded** — locks at starting balance + $100 after first payout. 80/20 split, bi-weekly payouts (14 calendar days), no per-cycle cap ($100K cumulative cap before live transition), no funded consistency rule, 60% pre-buffer withdrawal carve-out. **Contracts: 6 minis / 60 micros on 100K — 60 micros < 150, cannot trade 15 MNQ.** Good EOD structure, but contract cap is the blocker.
- **Core:** $50K only — not available at 100K.
- **Rapid 100K:** **4% intraday trailing ($3,000) — AVOID for your style.** 90/10, 10 minis/100 micros. (Intraday funded = wrong structure.)
- **Reputation:** Solid 3-year operator, building a brokerage division (Blue Row Capital live transition), clean payout cadence.

### 7. Topstep — 100K (shortlist)
12+ year track record (longest in the space). Trading Combine → Express Funded Account (XFA) → Live Funded.
- **Drawdown (100K):** $3,000 Maximum Loss Limit. **Combine = INTRADAY trailing (real-time unrealized P&L); XFA funded = EOD trailing.** So the FUNDED phase is EOD-friendly — but you must survive an intraday-trailing Combine first, which fights a let-it-breathe style during the evaluation. After first payout the MLL locks at $0 (zero buffer).
- **Contracts (100K):** 5 minis / 50 micros base (scales). **50 micros << 150 — 15 MNQ not possible on 100K.**
- **Payouts:** 90/10 from $1 (accounts after Jan 12 2026). Payout caps slashed late April 2026: 100K capped ~$3,000/request. 5 winning days ($150+) Standard path or 3 days + 40% consistency. Min $125.
- **Daily loss limit:** optional ($2,000 on 100K), soft breach, discount if added.
- **Reputation:** Most established firm; but intraday Combine + low contract caps + reduced payout caps make it a weaker fit.

### 8. Tradeify — 100K (shortlist)
- **Drawdown:** **ALL accounts use EOD trailing drawdown** (Growth, Select, Lightning). 100K = $3,000, locks at $100,100 ($100 above start) after EOD balance clears, or immediately on first payout request. Enforced real-time intraday (touching the limit fails you) but only UPDATES at EOD. **Stays EOD when funded — good structural fit.**
- **Contracts (100K):** full limits in eval (8 minis/80 micros on 100K Select); **funded SCALES** from lower tiers up to 8 minis/80 micros at $103,000 balance. **80 micros < 150 — cannot trade 15 MNQ on 100K.**
- **Cost/payouts:** Select 100K ~$259/mo (promo ~$181). No activation fee, no ongoing funded fees. 90/10. Select Daily payout caps $1,500/request; Select Flex caps $4,000 (50% of profit). Drawdown locks at $100,100. 40% consistency in eval only.
- **Reputation:** Static drawdown on Advanced/Growth historically; well-regarded, fast payouts.

### 9. Bulenox — 100K (shortlist)
Three-stage (Qualification → Master → Funded), Rithmic-based, six sizes.
- **Drawdown (100K):** $3,000. **Option 1 (No Scaling) = real-time INTRADAY trailing (full contracts day one). Option 2 (EOD) = EOD drawdown + scaling plan + daily loss limit.** → **Choose Option 2 for EOD.** On the Master account the trail locks at starting balance + $100 ($100,100).
- **Contracts (100K):** Option 1 = 12 minis/120 micros full from start (but intraday DD). Option 2 = scales: 3 contracts ($0–2,000 profit), 5 ($2,001–3,000), 8 ($3,001–5,000), 12 ($5,001+). **120 micros < 150 — 15 MNQ not possible on 100K; Option 1 gives 120 micros max.**
- **Daily loss limit (Option 2, 100K):** $2,200, soft breach (suspends day).
- **Payouts:** 100% first $10K, then 90/10. $1,000 min, weekly Wednesday payouts, 40% consistency, 10-trading-day Master minimum. First 3 payouts capped (~$1,750 on 100K), then uncapped.
- **Reputation:** ~4.7 Trustpilot, but criticized for eternal-sim (no live progression) and pricing the EOD option much higher than intraday. Payout-denial complaints center on the 40% consistency rule.

### 10. FundedFutures Network (FFN) — 100K (shortlist)
NY-based, founded 2022. 4.7/5 Trustpilot (~400 reviews, 94% 5-star). One-time fees (not subscription). Same-day payouts. Live onboarding calls.
- **Drawdown (100K):** **EOD trailing at 6%, converts to STATIC once funded** (per multiple reviews) — favorable. No daily loss limit on Standard. Buffer ~$3,600 on 100K (note: higher than the typical $3,000). Overnight positions NOT permitted. Tradovate only (no NinjaTrader).
- **Contracts:** fixed at purchased level (no scaling plan). Verify 100K micro cap — must be ≥150 micros for 15 MNQ.
- **Profit target / cost:** 6% target, min 3 trading days. Eval $149–$599 one-time. 80% → 90% after $5,000 cumulative.
- **Payouts:** same-day (live) / every 3 days (sim). $500 min, max $10,000/payout cumulative across accounts. MAX accounts: Standard MAX = 40% consistency + soft-breach DLL; Express MAX = 25% consistency + unrealized (intraday) trailing while building buffer (avoid Express).
- **Reputation:** Strong support reputation (10-second response claims), transparent; smaller/younger than Apex/Topstep.

---

## Comparison & Ranking (for $2,538 DD @ 15 MNQ, let-it-breathe, EOD/static preferred, manual execution)

**Tier A — Cleanest structural fit (EOD stays EOD when funded; pick a 150K size to fit 15 MNQ):**
1. **Alpha Futures Advanced 150K** — EOD on all stages, full contracts day one (15 minis/150 micros), $5,250 DD (~$2,700 cushion), withdrawals don't cut MLL, 90% split. Best overall fit.
2. **TradeDay Fast Pass 150K** — EOD stays EOD (Fast Pass only), $4,500 DD, 15 minis/150 micros, day-one payouts, live progression. Avoid Quick Pay.
3. **Lucid LucidPro 150K** — EOD funded + locks, full size immediately, 90/10 (verify 150K micro cap ≥150). LucidFlex 150K also EOD but funded scaling.

**Tier B — Good EOD structure but contract-capped at 100K / friction:**
4. **MyFundedFutures Pro 150K** — 3% EOD funded ($4,500), but 9 minis/90 micros on 150K still < 150 micros; Pro 100K = 60 micros. Contract cap is the blocker; otherwise clean EOD.
5. **Apex 100K/150K EOD** — clean EOD, but contract scaling (half-size until ~$103,100) and 6-payout/$18,000 lifetime cap. 150K EOD = $4,500 DD.
6. **Tradeify 150K** — EOD all accounts, but funded scaling delays full size; 150K = 12 minis/120 micros (still <150).
7. **Bulenox Option 2 150K** — EOD + scaling; 150K scales to 15 minis/150 micros at $12,001+ profit. Eternal sim (no live) is a drawback.
8. **FFN 100K/150K** — EOD→static when funded is excellent, but no overnight, Tradovate-only, verify micro cap.

**Tier C — AVOID for this strategy (funded intraday trailing or structural conflict):**
- **Take Profit Trader PRO** — funded INTRADAY trailing. Disqualifying unless you reach PRO+ (not guaranteed).
- **MyFundedFutures RAPID** — funded intraday.
- **TradeDay Quick Pay** — funded intraday despite EOD eval.
- **Bulenox Option 1** — real-time intraday trailing.
- **FFN Express MAX** — unrealized (intraday) trailing while building buffer.
- **Topstep** — funded XFA is EOD (OK), but intraday-trailing Combine + 50-micro 100K cap + reduced payout caps make it a poor fit.

**The contract-size reality:** 15 MNQ = 150 micros = 1.5 minis of exposure. **No standard 100K account in this list allows 150 micros** (they cap at 60–120 micros). To trade 15 MNQ you essentially MUST use a 150K-tier account (which also gives the ~$4,500 DD your $2,538 strategy really needs), OR reduce to 12–13 MNQ to fit a 100K account's contract cap and tighter $3,000 DD.

## Recommendations

**Stage 1 — Decide tier first (this week).** Your $2,538 DD at 15 MNQ effectively rules out 100K accounts on BOTH axes (only ~$460 DD cushion AND most 100K caps are 60–120 micros < 150). **Default to a 150K-tier account.** If you insist on 100K for cost reasons, cut size to ~12 MNQ (120 micros) and treat the ~$460 cushion as a hard discipline constraint.

**Stage 2 — Deploy on EOD-stays-EOD firms only.** Buy, in priority order: (1) **Alpha Futures Advanced 150K**, (2) **TradeDay Fast Pass 150K** (NOT Quick Pay), (3) **Lucid LucidPro 150K.** All keep EOD trailing in the funded phase and (Alpha/Pro) give full contracts immediately. Verify the exact 150K micro cap = 150 at checkout.

**Stage 3 — Diversify counterparty risk.** Given 2025–2026 rule churn and that all these are sim-funded, run 2–3 accounts across different firms rather than concentrating capital-at-risk in one. Favor firms with live-capital progression (TradeDay Funded Live, Alpha Prime) to reduce pure-sim solvency exposure.

**Benchmarks that change the plan:**
- If you can tighten your strategy's max DD below ~$2,400 AND accept 12 MNQ, a 100K EOD account (Alpha, Lucid Pro, Apex EOD) becomes viable and cheaper.
- If a firm you're holding announces a funded-phase switch from EOD to intraday (as TPT and TradeDay Quick Pay did), exit immediately — that single change breaks your edge.
- If contract scaling on Apex/Tradeify/Bulenox/Flex keeps you below your needed size for >2 weeks of trading, switch to a no-scaling firm (Alpha Advanced, Lucid Pro).

## Caveats
- **All figures are a June 2026 snapshot and MUST be re-verified on each firm's official help center / checkout before purchase.** These rules changed repeatedly through 2025–2026 (Apex 4.0 March 1; TradeDay 2.0 May 29; Alpha retired Standard May 1; Topstep payout caps cut April 28; Lucid restructured ~4×).
- Official sources used: Apex, Take Profit Trader, Lucid, Tradeify, Topstep, Alpha Futures, MyFundedFutures, Bulenox, and FFN help centers. Third-party review sites (DamnPropFirms, ProptradingVibes, QuantVPS, PipBack, PickMyTrade, TradeTanto, PropFirm App) corroborate but are secondary; where they conflict with official pages, trust the official page.
- **Contract micro caps at specific 150K tiers were not all directly confirmed** — verify each firm's 150K micro cap is ≥150 before assuming 15 MNQ fits. The LucidFlex funded scaling tier thresholds come from a third-party reading of Lucid's official scaling table; confirm on the live dashboard.
- All these accounts are **simulated/sim-funded**; "funded" means sim capital with real payouts. Counterparty solvency is a genuine deployment risk — none are CFTC-registered broker-dealers (standard for the category).
- The "100% first $10K" perks at Lucid and Bulenox have eligibility cutoffs/grandfathering — do not assume they apply to new accounts.