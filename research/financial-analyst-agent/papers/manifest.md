# Paper Manifest

All papers were accessed and reviewed in full on 2026-07-31. Findings below are
the authors' results, not promises of current profitability. `T`, `C`, `E`, and
`N` identify trading, company analysis, economic foundations, and financial-news
research. Page counts refer to the reviewed artifact and can differ from journal
pagination.

## Trading And Market Microstructure

### T1: Continuous Auctions and Insider Trading

- **Authors/year/venue:** Albert S. Kyle, 1985, *Econometrica* 53(6).
- **Source:** https://doi.org/10.2307/1913210; 22 pages; full text reviewed: yes.
- **Finding:** A strategic informed trader spreads orders while noise masks flow;
  Kyle lambda links order flow to price impact and market depth.
- **Limit:** A single risk-neutral insider, Gaussian flow, and stylized dealer
  market omit modern books, fragmentation, inventory, fees, and latency.
- **Agent impact:** Estimate conditional impact and distinguish informed flow
  from noise; use lambda as a regime benchmark, not a constant law.

### T2: Bid, Ask and Transaction Prices in a Specialist Market

- **Authors/year/venue:** Lawrence R. Glosten and Paul R. Milgrom, 1985,
  *Journal of Financial Economics* 14(1).
- **Source:** https://doi.org/10.1016/0304-405X(85)90044-3; 30 pages; full text
  reviewed: yes.
- **Finding:** Adverse selection alone creates a spread and each buy or sell
  updates the dealer's belief about value.
- **Limit:** Unit orders and a specialist abstraction omit inventory, queues,
  hidden orders, multiple venues, and modern latency.
- **Agent impact:** Separate quoted, effective, and realized spreads and inspect
  post-trade markouts before calling execution good.

### T3: Optimal Execution of Portfolio Transactions

- **Authors/year/venue:** Robert Almgren and Neil Chriss, 2001, *Journal of Risk*
  3(2).
- **Source:** https://doi.org/10.21314/JOR.2001.041; 42 pages; full text reviewed:
  yes.
- **Finding:** Execution has an impact-versus-timing-risk frontier; risk aversion
  selects a schedule and implementation shortfall supplies the cost objective.
- **Limit:** Linear impact, Gaussian independent returns, known parameters, and
  fixed targets omit stochastic liquidity, queues, venues, and partial fills.
- **Agent impact:** Produce calibrated pre-trade cost/risk frontiers and replan
  around events rather than treating a static schedule as an oracle.

### T4: Optimal Trading Strategy and Supply/Demand Dynamics

- **Authors/year/venue:** Anna A. Obizhaeva and Jiang Wang, 2013, *Journal of
  Financial Markets* 16(1).
- **Source:** https://doi.org/10.1016/j.finmar.2012.09.001; 32 pages; full text
  reviewed: yes.
- **Finding:** Order-book resilience and replenishment alter optimal timing and
  separate transient from permanent impact.
- **Limit:** The deterministic block book, exponential recovery, and known
  parameters omit queue priority, hidden liquidity, fragmentation, and strategy.
- **Agent impact:** Measure depth recovery after shocks and adapt participation
  to refill rather than rely on a single snapshot.

### T5: No-Dynamic-Arbitrage and Market Impact

- **Authors/year/venue:** Jim Gatheral, 2010, *Quantitative Finance* 10(7).
- **Source:** https://doi.org/10.1080/14697680903373692; 25 pages; full text
  reviewed: yes.
- **Finding:** Impact shape and decay cannot be calibrated independently if an
  impact model is to exclude profitable expected round trips.
- **Limit:** The propagator abstraction omits spread, stochastic liquidity,
  cross-impact, and many real frictions.
- **Agent impact:** Red-team every impact model for price manipulation before
  optimizing an execution strategy with it.

### T6: The Price Impact of Order Book Events

- **Authors/year/venue:** Rama Cont, Arseniy Kukanov, and Sasha Stoikov, 2014,
  *Journal of Financial Econometrics* 12(1).
- **Source:** https://arxiv.org/abs/1011.6402; 26 pages; full text reviewed: yes.
- **Finding:** Top-of-book order-flow imbalance including limits and cancels has
  a strong contemporaneous linear relation with short-horizon midprice moves;
  slope varies inversely with depth.
- **Limit:** One month of liquid U.S. large caps and consolidated top-of-book data
  do not establish causal predictive alpha.
- **Agent impact:** Include limits and cancels in liquidity analysis and never
  turn contemporaneous fit into a forecast without out-of-sample evidence.

### T7: High Frequency Trading and the New-Market Makers

- **Authors/year/venue:** Albert J. Menkveld, 2013, *Journal of Financial
  Markets* 16(4).
- **Source:** https://papers.tinbergen.nl/11076.pdf; 45 pages; full text reviewed:
  yes.
- **Finding:** One identified HFT earned gross spread capture but lost on longer
  inventory positioning; cross-market clearing and fees mattered.
- **Limit:** One anonymous trader, market, transition period, and gross-cost view
  have limited external validity.
- **Agent impact:** Attribute market-making P&L to spread, fees, inventory
  markouts, capital, and fixed costs across holding horizons.

### T8: The High-Frequency Trading Arms Race

- **Authors/year/venue:** Eric Budish, Peter Cramton, and John Shim, 2015,
  *Quarterly Journal of Economics* 130(4).
- **Source:** https://doi.org/10.1093/qje/qjv027; 76 pages; full text reviewed:
  yes.
- **Finding:** Continuous serial markets create stale-quote races and incentives
  for tiny speed advantages; frequent batch auctions can weaken the race.
- **Limit:** Evidence centers on one historical ES-SPY pair and a stylized market
  design; latency profits and optimal batch intervals are uncertain.
- **Agent impact:** Account for venue, feed, latency, fill, and sniping risk and
  never label public cross-market discrepancies riskless.

### T9: Trading Is Hazardous to Your Wealth

- **Authors/year/venue:** Brad M. Barber and Terrance Odean, 2000, *Journal of
  Finance* 55(2).
- **Source:** https://doi.org/10.1111/0022-1082.00226; 53 pages; full text
  reviewed: yes.
- **Finding:** In 66,465 discount-broker households, high turnover largely
  explained substantial net underperformance after commissions and spreads.
- **Limit:** One self-selected 1991-96 broker sample is observational and does not
  represent institutions, taxes, current costs, or total household wealth.
- **Agent impact:** Default to no trade unless the expected edge clears total
  costs and uncertainty; monitor turnover and churning.

### T10: The Probability of Backtest Overfitting

- **Authors/year/venue:** David H. Bailey, Jonathan M. Borwein, Marcos López de
  Prado, and Qiji Jim Zhu, 2017, *Journal of Computational Finance* 20(4).
- **Source:** https://doi.org/10.21314/JCF.2016.322; 34 pages; full text reviewed:
  yes.
- **Finding:** A single holdout is unreliable after broad strategy search;
  combinatorially symmetric cross-validation estimates selection overfit risk.
- **Limit:** Undisclosed trials, bad cost data, lookahead, regime breaks, and
  meta-overfitting remain possible.
- **Agent impact:** Require an immutable experiment registry, point-in-time data,
  PBO/CSCV, untouched walk-forward tests, costs, capacity, and shadow operation.

## Company And Fundamental Analysis

### C1: The Valuation of Cash Flow Forecasts

- **Authors/year/venue:** Steven N. Kaplan and Richard S. Ruback, 1995,
  *Journal of Finance* 50(4).
- **Source:** https://www.nber.org/papers/w4722; 37 pages; full text reviewed: yes.
- **Finding:** In 51 leveraged transactions, compressed-APV/DCF estimates were
  close to deal values and at least as accurate as selected comparable methods.
- **Limit:** Selected deals, endogenous management forecasts and prices, and
  terminal/risk-premium sensitivity limit generalization.
- **Agent impact:** Show forecast horizon, discount components, terminal
  cross-check, comparables, and sensitivities; report a range, not true value.

### C2: Financial Statement Analysis and Prediction of Stock Returns

- **Authors/year/venue:** Jane A. Ou and Stephen H. Penman, 1989, *Journal of
  Accounting and Economics* 11.
- **Source:** https://doi.org/10.1016/0165-4101(89)90017-7; 35 pages; full text
  reviewed: yes.
- **Finding:** A multivariate accounting score predicted future earnings
  direction and historical returns in the study sample.
- **Limit:** Pooled old data, omitted sectors, missing-data selection, and later
  size/risk critiques make the score a hypothesis generator, not current alpha.
- **Agent impact:** Use point-in-time ratios and trends with modern independent
  replication and explicit sector normalization.

### C3: Value Investing and Historical Financial Statements

- **Authors/year/venue:** Joseph D. Piotroski, 2000, *Journal of Accounting
  Research* 38 Supplement.
- **Source:** https://doi.org/10.2307/2672906; 58 reviewed pages; full text
  reviewed: yes.
- **Finding:** Nine profitability, leverage/liquidity, and efficiency signals
  separated historical winners and losers inside a high-book-to-market universe.
- **Limit:** Ad hoc signals, a value-only universe, microcap concentration, and
  incomplete cost/capacity analysis limit live use.
- **Agent impact:** Use F-score transparently as triage with raw inputs, missing
  data, sector caveats, and no automatic recommendation.

### C4: Earnings Quality: Evidence from the Field

- **Authors/year/venue:** Ilia D. Dichev, John R. Graham, Campbell R. Harvey,
  and Shivaram Rajgopal, 2013, *Journal of Accounting and Economics* 56.
- **Source:** https://doi.org/10.1016/j.jacceco.2013.05.004; 33 pages; full text
  reviewed: yes.
- **Finding:** CFOs associate high-quality earnings with sustainability, cash
  backing, consistent policy, and few one-offs or long-estimation accruals.
- **Limit:** Self-report, selection, interpretation, and truthfulness risks make
  the survey evidence descriptive rather than causal.
- **Agent impact:** Review cash conversion, accrual reversals, one-offs, estimate
  sensitivity, policy consistency, peers, incentives, and management language.

### C5: The Other Side of Value: The Gross Profitability Premium

- **Authors/year/venue:** Robert Novy-Marx, 2013, *Journal of Financial
  Economics* 108(1).
- **Source:** https://www.nber.org/papers/w15940; 57 reviewed pages; full text
  reviewed: yes.
- **Finding:** Gross profit relative to assets predicted historical growth and
  returns and complemented value in U.S. and developed-market tests.
- **Limit:** Accounting classification, the asset denominator, excluded
  financials, old samples, and unresolved risk-versus-mispricing interpretation.
- **Agent impact:** Compare profitability, margins, and turnover within sector
  and pair business quality with price rather than use a universal cutoff.

### C6: Over-Investment of Free Cash Flow

- **Authors/year/venue:** Scott Richardson, 2006, *Review of Accounting Studies*
  11.
- **Source:** https://doi.org/10.1007/s11142-006-9012-1; 31 pages; full text
  reviewed: yes.
- **Finding:** Positive free cash flow was asymmetrically associated with a
  model-based residual interpreted as overinvestment; activist ownership reduced
  the association.
- **Limit:** Maintenance capex, R&D, persistence, discounting, model residuals,
  endogeneity, and excluded financials create large measurement risk.
- **Agent impact:** Score incremental ROIC, reinvestment, M&A, distributions,
  debt, cash, and governance; label residuals as risk indicators, not facts.

### C7: How Much Does Industry Matter, Really?

- **Authors/year/venue:** Anita M. McGahan and Michael E. Porter, 1997,
  *Strategic Management Journal* 18 Special Issue.
- **Source:** https://doi.org/10.1002/(SICI)1097-0266(199707)18:1%2B%3C15::AID-SMJ916%3E3.0.CO;2-1;
  17 pages; full text reviewed: yes.
- **Finding:** Industry, corporate parent, and business-specific components all
  contributed to profit variance, with large differences across sectors.
- **Limit:** Accounting ROA, segments, SIC assignment, residual variance, and
  descriptive historical decomposition do not establish causality.
- **Agent impact:** Combine industry structure/base rates, company capabilities,
  and parent capital allocation in every company review.

### C8: In Search of Distress Risk

- **Authors/year/venue:** John Y. Campbell, Jens Hilscher, and Jan Szilagyi,
  2008, *Journal of Finance* 63(6).
- **Source:** https://doi.org/10.1111/j.1540-6261.2008.01416.x; 41 pages; full
  text reviewed: yes.
- **Finding:** A dynamic model combining accounting and market inputs predicted
  failure at different horizons; historically distressed equities had low returns.
- **Limit:** Rare events, regime and legal drift, market reflexivity, pre-2004
  U.S. data, liquidity, and shortability weaken direct reuse.
- **Agent impact:** Produce horizon-specific distress ranges and refinancing,
  liquidity, and recovery scenarios separately from expected equity return.

### C9: Corporate Governance and Equity Prices

- **Authors/year/venue:** Paul A. Gompers, Joy L. Ishii, and Andrew Metrick,
  2003, *Quarterly Journal of Economics* 118(1).
- **Source:** https://www.nber.org/papers/w8449; 70 pages; full text reviewed: yes.
- **Finding:** A 24-provision shareholder-rights index correlated with historical
  valuation, operating outcomes, and returns in 1990s U.S. firms.
- **Limit:** Equal weighting, endogenous governance, historical large-firm data,
  and later disappearance of the return association reject causal alpha claims.
- **Agent impact:** Review current board/control, voting, pay, ownership,
  takeover defenses, and related-party risks in jurisdictional context.

### C10: Analysts' Conflicts and Biases in Earnings Forecasts

- **Authors/year/venue:** Louis K. C. Chan, Jason Karceski, and Josef Lakonishok,
  2007, *Journal of Financial and Quantitative Analysis* 42(4).
- **Source:** https://doi.org/10.3386/w9544; 49 reviewed pages; full text reviewed:
  yes.
- **Finding:** Positive surprises became more frequent, especially for growth
  firms, consistent with strategic forecast walk-down and conflicts.
- **Limit:** Pre-Reg-FD/Global-Settlement data and observational evidence cannot
  isolate analysts from guidance, earnings management, and sample selection.
- **Agent impact:** Preserve forecast vintages, age, dispersion, revisions,
  source and conflicts and compare consensus with independent base-rate cases.

## Economic Foundations

### E1: Forecasting Inflation

- **Authors/year/venue:** James H. Stock and Mark W. Watson, 1999, NBER 7023;
  later *Journal of Monetary Economics* 44(2).
- **Source:** https://www.nber.org/papers/w7023; 46 pages; full text reviewed: yes.
- **Finding:** A factor from many real-activity indicators outperformed a
  conventional unemployment Phillips curve at a one-year horizon in recursive
  historical tests.
- **Limit:** Old U.S. data, linear models, horizon dependence, candidate search,
  instability, and data revisions matter.
- **Agent impact:** Use real-time vintages, simple benchmarks, multiple activity
  measures, recursive tests, error intervals, and instability warnings.

### E2: A New Measure of Monetary Shocks

- **Authors/year/venue:** Christina D. Romer and David H. Romer, 2004,
  *American Economic Review* 94(4).
- **Source:** https://www.nber.org/papers/w9866; 75 pages; full text reviewed: yes.
- **Finding:** Removing intended rate changes explained by decision-time
  forecasts yields contractionary shocks with delayed output and price effects.
- **Limit:** 1969-96 scheduled U.S. meetings, narrative choices, Volcker-period
  measurement, nonrandom residuals, and later policy regimes limit transfer.
- **Agent impact:** Separate expected decisions from shocks, keep forecast
  vintages, model lags, and grade causal confidence.

### E3: Predicting U.S. Recessions With Financial Variables

- **Authors/year/venue:** Arturo Estrella and Frederic S. Mishkin, 1998, *Review
  of Economics and Statistics* 80(1).
- **Source:** https://www.nber.org/papers/w5379; 53 pages; full text reviewed: yes.
- **Finding:** The 10-year/3-month Treasury spread was a strong parsimonious
  historical out-of-sample recession indicator at two-to-six-quarter horizons.
- **Limit:** Few episodes, ex-post labels, term-premium/regime change, old data,
  and horizon sensitivity preclude a binary rule.
- **Agent impact:** Report calibrated horizon-specific probabilities and use the
  curve as one cross-check with regime and term-premium analysis.

### E4: Dynamic Effects of Government Spending and Taxes

- **Authors/year/venue:** Olivier Blanchard and Roberto Perotti, 2002,
  *Quarterly Journal of Economics* 117(4).
- **Source:** https://www.nber.org/papers/w7269; 52 pages; full text reviewed: yes.
- **Finding:** A structural VAR using institutional elasticities found tax shocks
  reduce output and purchase shocks raise it, with magnitude sensitive to trends.
- **Limit:** Within-quarter identification, anticipation, elasticities, ordering,
  trends, and state dependence make multipliers conditional.
- **Agent impact:** Separate automatic stabilizers from discretionary news and
  report ranges by composition, financing, slack, and regime.

### E5: Macroeconomic Effects of Tax Changes

- **Authors/year/venue:** Christina D. Romer and David H. Romer, 2010,
  *American Economic Review* 100(3).
- **Source:** https://www.nber.org/papers/w13264; 71 pages; full text reviewed:
  yes.
- **Finding:** Narrative primary-source classification separated endogenous from
  exogenous U.S. tax changes and found large delayed output effects.
- **Limit:** Judgment, imprecision, anticipation, bundled policies, motivation,
  and regime differences prevent a universal tax multiplier.
- **Agent impact:** Read primary legislation, code motivation and dates, separate
  news from implementation, and preserve uncertainty and composition.

### E6: The Aggregate Matching Function

- **Authors/year/venue:** Olivier Jean Blanchard and Peter A. Diamond, 1989,
  NBER 3175; later MIT Press.
- **Source:** https://www.nber.org/papers/w3175; 56 pages; full text reviewed: yes.
- **Finding:** Hires relate to unemployment and vacancies; large worker/job flows
  and Beveridge-curve dynamics separate cyclical demand from matching change.
- **Limit:** Old aggregate data, adjusted vacancy proxies, classification error,
  and strong VAR restrictions limit current causal use.
- **Agent impact:** Combine unemployment, vacancies, hires, quits, participation,
  and curve shifts rather than read unemployment alone.

### E7: A Contribution to the Empirics of Economic Growth

- **Authors/year/venue:** N. Gregory Mankiw, David Romer, and David N. Weil,
  1992, *Quarterly Journal of Economics* 107(2).
- **Source:** https://www.nber.org/papers/w3541; 48 pages; full text reviewed: yes.
- **Finding:** An augmented Solow model with physical and human capital and
  population growth explained much historical cross-country income variation.
- **Limit:** Cross-country OLS, endogenous inputs, schooling proxies, restrictive
  technology, and old data do not establish short-run causal signals.
- **Agent impact:** Decompose long-run growth into productivity, capital, human
  capital, demographics, and institutions without turning it into market timing.

### E8: Empirical Exchange Rate Models Out Of Sample

- **Authors/year/venue:** Richard A. Meese and Kenneth Rogoff, 1983, *Journal of
  International Economics* 14.
- **Source:** https://www.federalreserve.gov/econres/ifdp/empirical-exchange-rate-models-of-the-seventies-are-any-fit-to-survive.htm;
  51 pages; full text reviewed: yes.
- **Finding:** A random walk beat several structural exchange-rate models even
  when those models received realized future fundamentals.
- **Limit:** A short turbulent 1970s sample, limited models, revised fundamentals,
  breaks, and point-error metrics leave room for later methods but set a hard
  benchmark.
- **Agent impact:** Require random-walk comparison, genuine rolling tests, and a
  clear distinction between economic explanation and forecast value.

### E9: Vulnerable Growth

- **Authors/year/venue:** Tobias Adrian, Nina Boyarchenko, and Domenico Giannone,
  2019, *American Economic Review* 109(4).
- **Source:** https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr794.pdf;
  56 pages; full text reviewed: yes.
- **Finding:** Tighter financial conditions shift the lower tail of future U.S.
  GDP growth much more than the upper tail.
- **Limit:** Signal-versus-cause ambiguity, sparse tails, index/model risk,
  revisions, and a U.S. quarterly sample limit precision.
- **Agent impact:** Forecast distributions, lower-tail quantiles, and expected
  shortfall and validate density calibration out of sample.

### E10: Evaluating Density Forecasts

- **Authors/year/venue:** Francis X. Diebold, Todd A. Gunther, and Anthony S.
  Tay, 1998, *International Economic Review* 39(4).
- **Source:** https://www.nber.org/papers/t0215; 38 pages; full text reviewed: yes.
- **Finding:** Probability-integral transforms provide distribution and dynamic
  diagnostics for conditional density forecasts.
- **Limit:** Parameter uncertainty, finite-sample power, structural change, and
  user loss functions mean calibration is necessary but not economic proof.
- **Agent impact:** Store forecasts before outcomes, test calibration and serial
  dependence, score user-relevant losses, and retain failed histories.

## Financial News Research

### N1: Giving Content to Investor Sentiment

- **Authors/year/venue:** Paul C. Tetlock, 2007, *Journal of Finance* 62(3).
- **Source:** https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf;
  51 pages; full text reviewed: yes.
- **Finding:** Media pessimism predicted temporary downward pressure, reversal,
  and high volume in historical index data.
- **Limit:** One newspaper column, an old dictionary/sample, unclear causal
  direction, and trading costs/impact can erase the small signal.
- **Agent impact:** Treat tone as contextual sentiment, not fundamental truth or
  a standalone trading rule; validate timing and net economics.

### N2: More Than Words

- **Authors/year/venue:** Paul C. Tetlock, Maytal Saar-Tsechansky, and Sofus
  Macskassy, 2008, *Journal of Finance* 63(3).
- **Source:** https://www.columbia.edu/~pt2238/papers/TSM_More_Than_Words_02_07.pdf;
  47 pages; full text reviewed: yes.
- **Finding:** Negative language in firm-specific fundamental news forecast
  earnings and small delayed returns in the historical sample.
- **Limit:** Dictionary counts, S&P 500 news, and small underreaction do not
  survive reasonable costs automatically.
- **Agent impact:** First classify whether an article concerns fundamentals;
  separate same-day information from delayed reaction and costs.

### N3: The Causal Impact of Media in Financial Markets

- **Authors/year/venue:** Joseph E. Engelberg and Christopher A. Parsons, 2011,
  *Journal of Finance* 66(1).
- **Source:** https://conference.nber.org/confer/2009/BEF09/Engelberg_Parsons.pdf;
  44 pages; full text reviewed: yes.
- **Finding:** Geographic reporting variation and weather interruptions support
  a causal effect of local coverage on local trading after earnings news.
- **Limit:** Historical newspapers, U.S. retail brokerage data, local geography,
  and earnings events may not transfer to digital global media.
- **Agent impact:** Distinguish event content from dissemination and attention;
  coverage can change behavior without changing fundamentals.

### N4: Which News Moves Stock Prices?

- **Authors/year/venue:** Jacob Boudoukh, Ronen Feldman, Shimon Kogan, and
  Matthew Richardson, 2013, NBER 18725; later *Journal of Financial Economics*.
- **Source:** https://www.nber.org/papers/w18725; 44 pages; full text reviewed:
  yes.
- **Finding:** Event/topic identification and phrase-aware tone distinguish
  price-relevant news far better than treating every article or word equally.
- **Limit:** Proprietary rules/data, historical S&P 500 coverage, gross strategies,
  and contemporaneous associations constrain reproducibility and alpha claims.
- **Agent impact:** Resolve entity, event, topic, timestamp, and materiality
  before sentiment; require point-in-time and net out-of-sample validation.

### N5: News versus Sentiment

- **Authors/year/venue:** Steven L. Heston and Nitish R. Sinha, 2016, Federal
  Reserve FEDS 2016-048.
- **Source:** https://www.federalreserve.gov/econres/feds/news-versus-sentiment-predicting-stock-returns-from-news-stories.htm;
  36 pages; full text reviewed: yes.
- **Finding:** Daily news effects were short, while weekly aggregation predicted
  longer historical underreaction, especially for negative news around earnings.
- **Limit:** Proprietary classifier/news data, historical U.S. stocks, portfolio
  construction, shorting, capacity, and full costs constrain live use.
- **Agent impact:** Separate attention from tone and positive from negative
  timing; test every horizon independently.

### N6: Media Sentiment and International Asset Prices

- **Authors/year/venue:** Samuel P. Fraiberger, Do Lee, Damien Puy, and Romain
  Ranciere, 2021, *Journal of International Economics* 133.
- **Source:** https://www.nber.org/papers/w25353; 45 pages; full text reviewed:
  yes.
- **Finding:** Global and local news sentiment had different historical price and
  flow effects across 25 countries, with foreign investors important.
- **Limit:** Dictionary-based sentiment, 1991-2015 media, observational channels,
  and country/data heterogeneity limit causal current trading rules.
- **Agent impact:** Separate local from global narratives and map investor-flow
  transmission, country exposure, and reversibility.

### N7: FinBERT: Financial Sentiment Analysis

- **Authors/year/venue:** Dogu Araci, 2019, University of Amsterdam thesis/arXiv.
- **Source:** https://arxiv.org/abs/1908.10063; 10 PDF pages in paper version;
  full text reviewed: yes.
- **Finding:** A finance-adapted BERT improved small financial-sentiment benchmark
  results relative to prior models.
- **Limit:** Small imbalanced datasets, cross-validation differences, overfit,
  arithmetic/context errors, and classification-to-return gaps remain.
- **Agent impact:** Use domain NLP as an extraction aid with confidence and human
  checks; never equate label accuracy with economic value.

### N8: FinBERT: A Pretrained Model for Financial Communications

- **Authors/year/venue:** Yi Yang, Mark Christopher Siy Uy, and Allen Huang,
  2020, arXiv/FinNLP.
- **Source:** https://arxiv.org/abs/2006.08097; 6 pages; full text reviewed: yes.
- **Finding:** Pretraining on reports, calls, and analyst research improved three
  financial sentiment tasks over generic BERT.
- **Limit:** Benchmark classification, corpus licensing/bias, old model scale,
  and no direct trading-economics test constrain conclusions.
- **Agent impact:** Match model and corpus to the task and validate factual,
  temporal, and economic outcomes separately.

### N9: The Spread of True and False News Online

- **Authors/year/venue:** Soroush Vosoughi, Deb Roy, and Sinan Aral, 2018,
  *Science* 359.
- **Source:** https://doi.org/10.1126/science.aap9559; 7 pages plus supplement;
  full text reviewed: yes.
- **Finding:** In fact-checked Twitter cascades, false stories spread farther,
  faster, deeper, and more broadly, with novelty and human sharing important.
- **Limit:** Fact-check selection, Twitter-era behavior, category imbalance, and
  observational novelty measures do not prove every mechanism or source false.
- **Agent impact:** Verify claims before reacting to velocity, novelty, or reach;
  use independent primary sources and record contradictions.

### N10: The Spread of Low-Credibility Content by Social Bots

- **Authors/year/venue:** Chengcheng Shao, Giovanni Luca Ciampaglia, Onur Varol,
  Kaicheng Yang, Alessandro Flammini, and Filippo Menczer, 2018, *Nature
  Communications* 9.
- **Source:** https://doi.org/10.1038/s41467-018-06930-7; 18 pages including
  methods; full text reviewed: yes.
- **Finding:** A small set of likely bots amplified low-credibility sources early
  and targeted influential accounts.
- **Limit:** Source-level credibility labels, bot classifiers, one platform and
  period, and observational design create classification and generalization risk.
- **Agent impact:** Flag early amplification, coordinated activity, provenance,
  incentives, and source reputation without treating automation as proof.

### N11: Extracting Fine-Grained Economic Events from Business News

- **Authors/year/venue:** Gilles Jacobs and Veronique Hoste, 2020, Financial
  Narrative Processing Workshop at LREC.
- **Source:** https://aclanthology.org/2020.fnp-1.36/; 11 pages; full text
  reviewed: yes.
- **Finding:** A finance-specific event dataset and model exposed a large domain
  performance gap relative to generic event-extraction benchmarks.
- **Limit:** Small pilot corpus, supervised annotations, single-token trigger
  restrictions, ambiguity, and many missed predictions limit automation.
- **Agent impact:** Extract multi-token event, actors, arguments, time, and target
  explicitly and preserve uncertainty instead of relying on generic NLP output.

## Cross-Lane Conclusion

The papers support disciplined workflows, not guaranteed signals. Any strategy
or recommendation must use point-in-time and survivorship-safe inputs, simple
benchmarks, independent out-of-sample validation, realistic costs/capacity,
calibrated uncertainty, sector and regime context, source provenance, and clear
separation of fact, inference, scenario, and opinion.
