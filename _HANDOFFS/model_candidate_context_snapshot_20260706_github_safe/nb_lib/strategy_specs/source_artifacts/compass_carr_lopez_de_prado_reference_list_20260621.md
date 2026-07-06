# Reference List: Carr–López de Prado "Optimal Trading Rules Without Backtesting" and Supporting Works

## TL;DR
- All ten requested sources are verified with stable identifiers; the primary method paper is **arXiv:1408.1159** (two SSRN twins: **2658641** under both authors, **2502613** under López de Prado solo), and the analytic sequel is **arXiv:2003.10502 / SSRN 3534445**, published in IJTAF vol. 23(8), article 2050056 (DOI 10.1142/S0219024920500569).
- Two long-standing community errors are corrected: the López de Prado Chapter 13 functions are named **`main()` (Snippet 13.1)** and **`batch()` (Snippet 13.2)** — **`processBatch` does not exist** in any official López de Prado code; and the Kaminski–Lo "50–100 bp/month" figure comes from the **2007/2008 working paper** (US equities, monthly), distinct from the published **2014 Journal of Financial Markets** futures version.
- For implementation, the faithful O-U/AR(1) calibration references are Dean Markwick's 2024 calibration post and Hudson & Thames' ArbitrageLab/MlFinLab docs; faithful Carr-LdP mesh reproductions include CanerIrfanoglu/advances_in_ml and coreych/optimal-trading-rules.

## Key Findings
- The primary paper exists in two arXiv versions (v1 Aug 6 2014; v2 Sep 28 2014) and two distinct SSRN postings with different titles ("Determining…" vs "Optimal…"). Both SSRN IDs are needed for complete citation.
- The official code (arXiv appendix "Snippet 1" and AFML Snippets 13.1/13.2) contains only `main()` and `batch()`. Verified verbatim from the arXiv PDF.
- The Lipton–LdP sequel has THREE citable forms: the SSRN/arXiv short note ("Mean-Reverting") and the full journal article ("Ornstein–Uhlenbeck Driven", IJTAF). Implementers should treat ArbitrageLab's heat-potentials module as the reference code.
- The "Probability of Backtest Overfitting" was definitively published in **Journal of Computational Finance, vol. 20, no. 4 (2017), pp. 39-69** — resolving the long-standing "forthcoming" ambiguity in older citations.

## Details (Organized for a Research Wiki)

### A. Primary-Method Sources

**1. Carr & López de Prado — "Determining Optimal Trading Rules Without Backtesting"**
- Authors: Peter P. Carr; Marcos López de Prado (author order: Carr, then López de Prado). Confidence: VERIFIED.
- arXiv: **1408.1159** [q-fin.PM]. Title on arXiv: "Determining Optimal Trading Rules without Backtesting." Version history: v1 (6 Aug 2014), v2 (28 Sep 2014). Canonical URL: https://arxiv.org/abs/1408.1159 (PDF: https://arxiv.org/pdf/1408.1159).
- SSRN: two abstract IDs. **2658641** (title "Determining Optimal Trading Rules Without Backtesting," both authors; DOI 10.2139/ssrn.2658641; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2658641). **2502613** (title "Optimal Trading Rules Without Backtesting," López de Prado solo, dated 28 Sep 2014; DOI 10.2139/ssrn.2502613; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2502613). Confidence: VERIFIED.
- Content: discrete Ornstein-Uhlenbeck model of trade mark-to-market P&L; Monte Carlo mesh over (profit-take, stop-loss) pairs maximizing Sharpe; conjectures (does not derive) a closed-form solution. The OLS linearization of the discrete O-U equation (Step 1) yields phi and a residual sigma; the mesh (Step 2) is built in multiples of sigma; Steps 5a/5b/5c give unconstrained / constrained-profit-take / constrained-stop-loss optima.

**2. López de Prado — "Advances in Financial Machine Learning" (Wiley, 2018)**
- ISBN-13: 978-1-119-48208-6; ISBN-10: 1119482089. Publisher: John Wiley & Sons, Hoboken, NJ. Publication date: 21 February 2018. Hardcover, 400 pp. (per Wiley/ACM Digital Library). Confidence: VERIFIED.
- Relevant chapter: **Chapter 13, "Backtesting on Synthetic Data."** Section structure: 13.1 Motivation; 13.2 Trading Rules; 13.3 The Problem; 13.4 Our Framework; 13.5 Numerical Determination of Optimal Trading Rules (13.5.1 The Algorithm, 13.5.2 Implementation); 13.6 Experimental Results; 13.7 Conclusion. The code lives in §13.5.2. Confidence: VERIFIED.
- Code snippets: **Snippet 13.1 = `main()`** (driver: builds `rPT=rSLm=np.linspace(0,10,21)` grids, iterates over the Cartesian product of forecasts `[10,5,0,-5,-10]` and half-lives `[5,10,25,50,100]`, packs `coeffs={'forecast','hl','sigma'}`, calls `batch()`); **Snippet 13.2 = `batch()`** (worker: `phi=2**(-1./hl)`, generates O-U paths with default `nIter=1e5`, `maxHP=100`, applies the profit-take/stop-loss/max-holding exit logic, returns `(PT, SL, mean, std, Sharpe=mean/std)` per mesh node). Confidence: function names VERIFIED (read verbatim from the identical arXiv twin code); literal "SNIPPET 13.1/13.2" label numbering is very-high-confidence inference (matches the arXiv code and AFML's chapter.number convention; the copyrighted Wiley/O'Reilly pages were not directly viewable).
- **DISCREPANCY FLAG — "processBatch" does not exist** in López de Prado's official code (neither the arXiv:1408.1159 appendix nor AFML Chapter 13). The arXiv appendix "Snippet 1" defines only `main()` and `batch()`; the book splits this single listing into Snippets 13.1 and 13.2. "processBatch" is a community/third-party renaming, not an original López de Prado function name.
- Faithful GitHub reproductions: `hudson-and-thames/mlfinlab` (library); `CanerIrfanoglu/advances_in_ml` (chapter13_synthetic_data folder, chapter summaries + exercises); `boyboi86/AFML` ("AFML 13.1.ipynb"); `charlesrambo/advances_in_financial_ML`. `coreych/optimal-trading-rules` reproduces the Carr-LdP paper code directly using yfinance + O-U.

**3. Lipton & López de Prado — analytic / heat-potentials sequel (solves the Carr-LdP conjecture)**
- Authors: Alexander Lipton; Marcos López de Prado. Confidence: VERIFIED.
- Short note: "A Closed-Form Solution for Optimal Mean-Reverting Trading Strategies." arXiv: **2003.10502**; SSRN: **3534445** (dated 8 Feb 2020). URLs: https://arxiv.org/abs/2003.10502 , https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3534445 . A short summary version also appeared in Risk/Wilmott.
- Full journal article: "A Closed-Form Solution for Optimal Ornstein–Uhlenbeck Driven Trading Strategies." International Journal of Theoretical and Applied Finance (IJTAF), World Scientific, vol. 23, issue 8 (December 2020), article **2050056**, pp. 1-34. DOI: **10.1142/S0219024920500569**. Confidence: VERIFIED.
- Content: Solves the open problem López de Prado identified at AFML p. 192 (existence of an analytical solution) using the method of heat potentials, deriving the optimal exit corridor (take-profit/stop-loss) that maximizes Sharpe for O-U-driven strategies. Builds on Lipton & Kaushansky's first-hitting-time work (arXiv:1810.02390; Quantitative Finance DOI 10.1080/14697688.2020.1713394).
- Library implementation: Hudson & Thames **ArbitrageLab**, `optimal_mean_reversion` module, heat_potentials documentation (https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/optimal_mean_reversion/heat_potentials.html).

### B. Supporting-Theory Sources

**4. Kaminski & Lo — "When Do Stop-Loss Rules Stop Losses?"**
- Authors: Kathryn M. Kaminski; Andrew W. Lo. Confidence: VERIFIED.
- Published version: Journal of Financial Markets, vol. 18 (March 2014), pp. 234-254. DOI: **10.1016/j.finmar.2013.07.001**. This version uses **daily futures price data** (index futures and Treasury note futures); finds that at longer sampling frequencies certain stop-loss policies can increase expected return while substantially reducing volatility, but stops add no value at short-term sampling frequencies.
- Working-paper versions: SSRN **968338** (dated 3 Jan 2007, EFA 2007 Ljubljana Meetings Paper; DOI 10.2139/ssrn.968338); SIFR Research Report Series 63 (Institute for Financial Research, 2008; RePEc handle hhs:sifrwp:0063).
- **DISCREPANCY FLAG — the basis-point figure differs by version.** The widely-cited "**50 to 100 basis points per month**" stopping-premium figure is from the **earlier working paper** (US equities buy-and-hold, with US long-term government bonds as the stop-loss asset, monthly data Jan 1950–Dec 2004). Verbatim from SSRN 968338: *"Using monthly returns data from January 1950 to December 2004, we find that certain stop-loss rules add 50 to 100 basis points per month to the buy-and-hold portfolio during stop-out periods."* The **published 2014 futures version** does NOT carry this equities/bp figure; it instead reports volatility-reduction and return results on futures. Both versions share the core theoretical result: under the Random Walk Hypothesis simple 0/1 stop-loss rules always **decrease** expected return (negative "stopping premium"), but under momentum/positive serial correlation the stopping premium **can be positive and is directly proportional to the magnitude of return persistence**.

**5. Moreira & Muir — "Volatility-Managed Portfolios"**
- Authors: Alan Moreira; Tyler Muir. The Journal of Finance, vol. 72, issue 4 (August 2017), pp. 1611-1644. DOI: **10.1111/jofi.12513**. Confidence: VERIFIED. (Earlier: NBER Working Paper 22208, 2016, DOI 10.3386/w22208.)
- Per the JoF abstract: *"Managed portfolios that take less risk when volatility is high produce large alphas, increase Sharpe ratios, and produce large utility gains for mean-variance investors … for the market, value, momentum, profitability, return on equity, investment, and betting-against-beta factors, as well as the currency carry trade."*

**6. Cederburg, O'Doherty, Wang & Yan — "On the Performance of Volatility-Managed Portfolios"**
- Authors: Scott Cederburg; Michael S. O'Doherty; Feifei Wang; Xuemin (Sterling) Yan. Journal of Financial Economics, vol. 138, issue 1 (October 2020), pp. 95-117. DOI: **10.1016/j.jfineco.2020.04.015**. SSRN: **3357038** (dated 20 Mar 2019). Confidence: VERIFIED.
- The OOS challenge to Moreira-Muir. Per the abstract: *"Using a comprehensive set of 103 equity strategies, we analyze the value of volatility-managed portfolios for real-time investors. Volatility-managed portfolios do not systematically outperform their corresponding unmanaged portfolios in direct comparisons."* They confirm Moreira-Muir's positive in-sample spanning-regression alphas but show the implied combination strategies are not implementable in real time and typically underperform out of sample (managed versions win in only ~53 of 103 direct comparisons).

**7. Bailey, Borwein, López de Prado & Zhu — "Pseudo-Mathematics and Financial Charlatanism"**
- Full title: "Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance." Authors: David H. Bailey; Jonathan M. Borwein; Marcos López de Prado; Qiji Jim Zhu. Notices of the American Mathematical Society, vol. 61, no. 5 (May 2014), pp. 458-471. DOI: **10.1090/noti1105**. SSRN: **2308659** (DOI 10.2139/ssrn.2308659). Open PDF: https://www.ams.org/notices/201405/rnoti-p458.pdf . Confidence: VERIFIED.

**8. Bailey & López de Prado — "The Deflated Sharpe Ratio"**
- Full title: "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality." Authors: David H. Bailey; Marcos López de Prado. Journal of Portfolio Management, vol. 40, no. 5 (2014, 40th Anniversary Special Issue), pp. 94-107. SSRN: **2460551** (DOI 10.2139/ssrn.2460551; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551). Confidence: VERIFIED. (A related López de Prado solo note, "Deflating the Sharpe Ratio," is SSRN 2465675; the antecedent "The Sharpe Ratio Efficient Frontier," Journal of Risk 15(2):3-44, 2012, is SSRN 1821643.)

**9. Bailey, Borwein, López de Prado & Zhu — "The Probability of Backtest Overfitting" (PBO / CSCV)**
- Authors: David H. Bailey; Jonathan M. Borwein; Marcos López de Prado; Qiji Jim Zhu. **Journal of Computational Finance (Risk Journals), vol. 20, no. 4 (2017), pp. 39-69**; DOI: **10.21314/JCF.2016.322**. SSRN: **2326253** (DOI 10.2139/ssrn.2326253; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253). Mathematical Appendices: SSRN **2568435**. Confidence: VERIFIED (older citations list this as "forthcoming/2015"; the definitive published locus is JCF 20(4), 2017).
- Introduces Combinatorially Symmetric Cross-Validation (CSCV) to estimate the Probability of Backtest Overfitting (PBO). NOTE: distinguish from **CPCV** (Combinatorial Purged Cross-Validation), the related but distinct method in AFML Chapter 12 — the two are frequently conflated.

### C. Implementation / Code Sources

**10a. Ornstein-Uhlenbeck / AR(1) parameter estimation in Python**
- Dean Markwick, "Calibrating an Ornstein–Uhlenbeck Process" (9 Mar 2024): https://dm13450.github.io/2024/03/09/Calibrating-an-Ornstein-Uhlenbeck-Process.html — covers the OU SDE, simulation, and parameter estimation (in Julia, but the method transfers directly to Python). Faithful and well-explained.
- Hudson & Thames ArbitrageLab, "Half-life of Mean-Reversion": https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/cointegration_approach/half_life.html — implements the half-life under the OU assumption.
- Discretization mapping (canonical and correct): the OU process is the continuous-time analogue of the discrete AR(1) process. Fit AR(1) by OLS of the change in the series on its lagged level; recover phi from the slope, the residual standard deviation gives sigma, and **half-life = -ln(2)/ln(phi)** (equivalently -ln(2)/lambda in continuous time). The widely reproduced OLS half-life idiom `half_life = -np.log(2)/res.params[1]` (statsmodels OLS) is faithful — see Letian Wang's "Mean Reversion" notes (https://letianquant.com/mean-reversion.html) and arXiv:1507.01610 §4 for the OU↔AR(1) MLE/OLS equivalence.

**10b. Carr-LdP mesh code reproductions**
- `coreych/optimal-trading-rules` (GitHub) — direct, faithful reproduction of the paper's O-U mesh (yfinance data, PT/SL Sharpe optimization).
- `CanerIrfanoglu/advances_in_ml` (GitHub), `chapter13_synthetic_data` — faithful chapter reproduction with summaries and the 5-step algorithm.
- Hudson & Thames **MlFinLab** library and the blog post "Optimal Trading Thresholds for the O-U Process" (https://hudsonthames.org/optimal-trading-thresholds-for-the-o-u-process/) — library-grade implementations.
- MQL5 article 22275 ("MetaTrader 5 Machine Learning Blueprint, Part 15") — reproduces the AFML Chapter 13 OTR algorithm faithfully (OLS fit of φ and residual σ, σ-scaled PT/SL mesh, 100k O-U paths) but renames internal variables for its own kernel and notes the book's 100k-path snippet is slow.

## Recommendations
1. **Primary method:** Cite arXiv:1408.1159 together with AFML Chapter 13. Use SSRN **2658641** for the dual-author posting and **2502613** for the López de Prado-solo posting; flag in any wiki that these are the same work under two titles.
2. **Code naming:** Implement the worker as `batch()` and the driver as `main()` to match the original; explicitly annotate that **`processBatch` is not an original López de Prado name** so future agents don't search for a non-existent function.
3. **Analytic exit corridors:** Use the IJTAF article (DOI 10.1142/S0219024920500569) as the authoritative full text, the SSRN 3534445 / arXiv 2003.10502 note for the abstract-level summary, and ArbitrageLab's `optimal_mean_reversion` heat-potentials module as the reference implementation.
4. **Kaminski-Lo:** Always specify which version when quoting numbers — the "50–100 bp/month" figure is the 2007/2008 equities working paper (SSRN 968338 / SIFR 63), not the 2014 JFM futures article.
5. **Overfitting trilogy:** Treat PBO (JCF 20(4), 2017, CSCV) and the Deflated Sharpe Ratio (JPM 40(5), 2014) as the validation backbone; do not conflate CSCV (PBO paper) with CPCV (AFML Ch. 12).

## Caveats
- Book snippet label numbering ("SNIPPET 13.1 / 13.2") is very-high-confidence inference, not a directly-quoted paywalled Wiley/O'Reilly page; the function names `main()` and `batch()` are verified verbatim from the identical arXiv appendix code.
- The Lipton-LdP work appears under two distinct titles ("Mean-Reverting" for the SSRN/arXiv note vs "Ornstein–Uhlenbeck Driven" for the IJTAF journal article); ensure both are cross-referenced so an implementer fetching one finds the other.
- The PBO paper is cited as "forthcoming" in many secondary sources predating 2017; the definitive published reference is Journal of Computational Finance 20(4):39-69 (2017), DOI 10.21314/JCF.2016.322.
- DOI 10.1090/noti1105 for the AMS Notices article is the publisher DOI; the freely available canonical PDF (ams.org/notices/201405/rnoti-p458.pdf) is the most stable open link.