---
name: "External Method References"
tagline: "Verified external references for management geometry, synthetic-path threshold work, stop policy evidence, and overfit discipline."
status: "reference-index"
created: 2026-06-21
source: "Operator-provided verified reference list on Carr-Lopez de Prado optimal trading rules and supporting works."
artifact_type: "external_references"
scope: "citation hygiene and hypothesis context only; not local validation"
tags:
  - references
  - methodology
  - management
  - synthetic-data
  - stop-loss
  - overfit
---

# External Method References

This file records external sources that are useful for future management
and validation research. It is a reference index, not a result. Nothing
in this file validates an `nb_lib` strategy, overrides local OOS
findings, or relaxes the project's pre-commitment and seal discipline.

Local MNQ evidence remains the authority for promotion decisions.

Raw operator-provided Compass source artifacts are archived here:

- `nb_lib/strategy_specs/source_artifacts/compass_carr_lopez_de_prado_reference_list_20260621.md`
- `nb_lib/strategy_specs/source_artifacts/compass_formula_level_menu_intraday_mnq_momentum_20260621.md`
- `nb_lib/strategy_specs/source_artifacts/compass_five_frequency_adequate_mnq_candidates_20260621.md`

## 1. Carr-Lopez de Prado Optimal Trading Rules

Primary method:

- Peter Carr and Marcos Lopez de Prado, "Determining Optimal Trading
  Rules without Backtesting."
- arXiv: `1408.1159`.
- SSRN: `2658641` for the dual-author posting and `2502613` for the
  Lopez de Prado solo posting under the shorter "Optimal Trading Rules
  Without Backtesting" title.

Project use:

- Treat as a possible framework for synthetic-path / OU-style
  profit-take and stop-loss threshold exploration.
- Use it only as hypothesis machinery. Any threshold it suggests still
  needs project-native validation on MNQ data.

Implementation hygiene:

- In the official paper / AFML code lineage, the driver and worker are
  named `main()` and `batch()`.
- Do not search for or cite `processBatch` as an original Lopez de Prado
  function name; that is a community / third-party rename.
- AFML Chapter 13 is the relevant book treatment:
  "Backtesting on Synthetic Data."

## 2. Analytic OU Exit Corridors

Analytic sequel:

- Alexander Lipton and Marcos Lopez de Prado, "A Closed-Form Solution
  for Optimal Mean-Reverting Trading Strategies."
- arXiv: `2003.10502`.
- SSRN: `3534445`.
- Full journal article: "A Closed-Form Solution for Optimal
  Ornstein-Uhlenbeck Driven Trading Strategies," International Journal
  of Theoretical and Applied Finance, volume 23, issue 8, article
  `2050056`, DOI `10.1142/S0219024920500569`.

Project use:

- Relevant if the project later builds an OU / mean-reversion
  corridor-sizing experiment.
- Keep separate from the Carr-Lopez de Prado mesh method: the Lipton
  sequel is the analytic corridor result, not another local backtest.
- Hudson & Thames ArbitrageLab `optimal_mean_reversion` /
  heat-potentials material is the most useful implementation pointer.

## 3. Stop-Loss And Volatility-Management Evidence

Stop-loss anchor:

- Kathryn Kaminski and Andrew Lo, "When Do Stop-Loss Rules Stop
  Losses?"
- Published futures version: Journal of Financial Markets, volume 18
  (2014), pages 234-254, DOI `10.1016/j.finmar.2013.07.001`.
- Working-paper versions: SSRN `968338`; SIFR Research Report Series
  63.

Citation hygiene:

- The often-cited "50 to 100 basis points per month" stopping-premium
  claim belongs to the 2007/2008 working-paper equities version, not to
  the 2014 published futures article.
- The shared lesson is conditional: simple stops are expected to hurt
  under random-walk assumptions, but may add value when returns have
  positive serial correlation / momentum.

Volatility-management anchors:

- Moreira and Muir, "Volatility-Managed Portfolios," Journal of
  Finance 72(4), 2017, DOI `10.1111/jofi.12513`.
- Cederburg, O'Doherty, Wang, and Yan, "On the Performance of
  Volatility-Managed Portfolios," Journal of Financial Economics
  138(1), 2020, DOI `10.1016/j.jfineco.2020.04.015`, SSRN `3357038`.

Project use:

- These sources support volatility / regime dependence as a serious
  hypothesis, but they do not prove intraday MNQ management edge.
- The Cederburg et al. challenge is important: volatility management can
  look good in spanning regressions while failing direct real-time
  comparisons. Future project tests should compare the managed and
  unmanaged policy directly, not rely on a synthetic alpha framing.

## 4. Backtest-Overfit And Validation Backbone

Useful references:

- Bailey, Borwein, Lopez de Prado, and Zhu, "Pseudo-Mathematics and
  Financial Charlatanism," Notices of the AMS 61(5), 2014, DOI
  `10.1090/noti1105`, SSRN `2308659`.
- Bailey and Lopez de Prado, "The Deflated Sharpe Ratio," Journal of
  Portfolio Management 40(5), 2014, SSRN `2460551`.
- Bailey, Borwein, Lopez de Prado, and Zhu, "The Probability of
  Backtest Overfitting," Journal of Computational Finance 20(4), 2017,
  pages 39-69, DOI `10.21314/JCF.2016.322`, SSRN `2326253`.

Discipline notes:

- PBO uses CSCV: combinatorially symmetric cross-validation.
- Do not conflate CSCV with CPCV: combinatorial purged
  cross-validation from AFML Chapter 12.
- These references support the project's existing trial-budget,
  pre-commitment, OOS-seal, and no-retuning-to-rescue rules. They do not
  replace those rules.

## 5. Implementation Pointers

OU / AR(1) calibration:

- Dean Markwick's 2024 OU calibration note is a useful implementation
  reference.
- Hudson & Thames ArbitrageLab half-life and mean-reversion materials
  are useful implementation references.
- Use the discrete AR(1) / OU relationship carefully: estimate the
  autoregressive coefficient and residual scale; do not mix half-life,
  sigma, and threshold units casually.

Carr-Lopez de Prado reproduction pointers:

- `coreych/optimal-trading-rules`.
- `CanerIrfanoglu/advances_in_ml`, `chapter13_synthetic_data`.
- Hudson & Thames MlFinLab / ArbitrageLab materials.

Repository-local rule:

- If any future implementation imports these ideas, add a local
  pre-commitment note before testing. The first local question is always
  "what exact observable is being added, and what simpler baseline must
  it beat?"

## 6. Project-Relevance Summary

The main useful ideas for NT8lab are:

1. Optimal stop / target geometry can be studied as a management
   problem without pretending entry prediction is the edge.
2. Synthetic-path or OU threshold methods may be useful for proposing
   candidates, but local replay and OOS discipline decide whether they
   matter.
3. Stop-loss value is conditional on the return process. This fits the
   project's current observation that early protection can clip noisy
   recoveries while later progress-conditioned protection may be useful.
4. Volatility scaling is plausible but must beat a direct unmanaged
   comparator in project-native replay.
5. Validation methodology matters as much as the idea. Do not use
   external citations to rescue a failed local result.
