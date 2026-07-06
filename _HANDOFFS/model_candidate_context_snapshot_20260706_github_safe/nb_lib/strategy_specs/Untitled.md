



# Test

```dataview
LIST
FROM "candidates"
```



**Fourth hypothesis — the regime-gating-is-the-whole-game hypothesis.** Your decomposition treats the regime node as one of four co-equal blocks. This hypothesis promotes it to primary: the reason every standalone candidate fails is that each one has a regime where it works and a regime where it bleeds, and tested across all regimes the bleed cancels the edge. Under this view, _every_ closed candidate might contain a positive edge that's hidden because it was tested unconditionally. The deliverable wouldn't be new strategies or an execution matrix — it'd be a regime classifier (the Markov node, matured) applied retroactively to the ~36 closed candidates to ask: "which of these was actually positive in its right regime and only failed because we tested it everywhere?" This could be better because it's the cheapest to test (you already have the closed candidates' trade data) and because it might _resurrect_ dead candidates rather than requiring new ones. The wide-state reversal that lost $14K — was it uniformly bad, or bad in trending regimes and fine in rotational ones? You don't currently know, because you tested it unconditionally. This hypothesis says the graveyard might be full of regime-conditional survivors. 

**Fourth hypothesis — the regime-gating-is-the-whole-game hypothesis.** Your decomposition treats the regime node as one of four co-equal blocks. This hypothesis promotes it to primary: the reason every standalone candidate fails is that each one has a regime where it works and a regime where it bleeds, and tested across all regimes the bleed cancels the edge. Under this view, _every_ closed candidate might contain a positive edge that's hidden because it was tested unconditionally. The deliverable wouldn't be new strategies or an execution matrix — it'd be a regime classifier (the Markov node, matured) applied retroactively to the ~36 closed candidates to ask: "which of these was actually positive in its right regime and only failed because we tested it everywhere?" This could be better because it's the cheapest to test (you already have the closed candidates' trade data) and because it might _resurrect_ dead candidates rather than requiring new ones. The wide-state reversal that lost $14K — was it uniformly bad, or bad in trending regimes and fine in rotational ones? You don't currently know, because you tested it unconditionally. This hypothesis says the graveyard might be full of regime-conditional survivors.

Yes. That fourth hypothesis is probably the most interesting one.

I’d phrase it like this:

**Maybe we have not been testing bad strategies. Maybe we have been testing conditional strategies unconditionally.**

That is a very different diagnosis.

If true, the project’s main missing artifact is not another entry idea. It is a **regime attribution layer**. Not necessarily a fancy HMM at first. Just a disciplined way to tag every historical trade with the market state it occurred in, then ask: “where does this thing actually work?”

The reason I like this hypothesis is that it explains several patterns at once:

- Why many candidates have plausible thesis but fail aggregate tests.
- Why direction asymmetry keeps showing up.
- Why fade strategies get destroyed in trend conditions.
- Why continuation strategies probably bleed in chop.
- Why extra filters often disappoint: they are weak substitutes for actual regime routing.
- Why the marginal registry matters: some “bad” strategies may be bad only because they were deployed in the wrong state.

The cheap first version would not be Markov yet. I’d start simpler:

`For every historical trade from every tested strategy: tag daily regime: - trend up / trend down / neutral - high volatility / low volatility - opening drive / rotational day - above/below daily VWAP or prior close tag intraday regime: - OR expansion - OR mean-reversion - high ATR percentile - range-bound aggregate P&L / PF / win rate by tag`

Then the output would look like:

`Strategy All PF Trend PF Chop PF Up-day PF Down-day PF wide_reversal_short 0.55 0.22 1.18 0.12 1.05 OR_width_switch_base_hit 1.35 1.12 1.58 1.40 1.20 VWAP_stretch_snapback 0.80 0.40 1.25 0.70 0.95 round_number_rejection 0.60 0.30 1.05 0.50 0.80`

That table would be huge. Because if even two or three “dead” candidates show PF > 1.2 in a definable regime, the graveyard becomes useful again.

The key discipline: don’t immediately resurrect them. First prove the regime tag is real and available before entry. Then test whether applying that tag as a gate improves the strategy on held-out in-sample data. Otherwise we just rediscover post-hoc slicing.

My honest ranking of hypotheses now:

1. **Regime-gating-is-the-whole-game**  
    Most interesting, cheapest, most aligned with composition.
    
2. **Execution-structure dominates signal**  
    Already has evidence from base-hit survival.
    
3. **Tiny-edge composition**  
    Likely true long-term, but needs regime and execution nodes first.
    
4. **Find a new standalone entry**  
    Still possible, but increasingly the least likely path.