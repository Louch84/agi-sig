# 📈 The Stock Market Driver Playbook
*A comprehensive reference for everything that moves stock prices*

---

## 1. MACROECONOMIC FACTORS

These are the macro forces that set the overall market tone. They affect everything — every stock, every sector, every investor.

### Interest Rates (Fed Funds Rate)
- **What it is:** The rate at which banks lend to each other overnight, set by the Federal Reserve. The anchor for all borrowing costs in the economy.
- **Why it matters:** Higher rates → higher discount rates → lower present value of future earnings → lower stock valuations (especially tech/growth). Higher rates also draw capital into bonds, away from equities. Rate changes also affect mortgage rates, corporate debt costs, consumer spending, and credit card APRs.
- **How to track:**
  - FOMC meeting schedule & dot plot projections
  - Fed funds futures (CME FedWatch Tool)
  - Treasury yield curve (2Y, 10Y, 30Y)
- **Typical reaction:**
  - Rate **hike**: Equities sell off, especially rate-sensitive sectors (tech, REITs, utilities). Banking stocks may rise on NIM (net interest margin) expansion.
  - Rate **cut**: Equities rally, particularly growth stocks. Banks may face NIM compression. REITs and utilities outperform.
  - **Curve inversion/un-inversion**: Inverted curve often signals recession fear → defensive stocks favored. Un-inversion (2Y falls below 10Y) can signal market relief.

### Inflation (CPI & PPI)
- **What it is:**
  - **CPI** (Consumer Price Index): The cost of a basket of consumer goods. "Headline" includes food & energy; "Core" strips those out.
  - **PPI** (Producer Price Index): What producers pay for inputs. Considered a leading indicator of CPI.
- **Why it matters:** Inflation erodes purchasing power and corporate profit margins. High inflation often forces the Fed to keep rates elevated. Unexpected inflation surprises are especially damaging — they create uncertainty about future earnings and multiple expansion.
- **How to track:**
  - BLS releases (CPI: ~monthly, mid-month; PPI: monthly)
  - Cleveland Fed Inflation Nowcasting
  - TIPS breakeven spreads (market's inflation expectation)
  - PPI components: energy, food, transportation
- **Typical reaction:**
  - **Hot CPI** (above expectations): Stocks fall. Bonds sell off. Gold and commodities rise. Fed rate cut expectations recede.
  - **Cooling CPI**: Stocks rally. Bonds rally. Rate cut hopes return.
  - **Transitory vs. persistent**: Markets care if inflation is stickier than expected.

### GDP (Gross Domestic Product)
- **What it is:** The total monetary value of all goods and services produced in the US. Reported quarterly (advance → revised → final).
- **Why it matters:** GDP growth drives corporate revenue and earnings. It's the broadest measure of economic health. Strong GDP = healthy corporate fundamentals; weak GDP = earnings recession risk.
- **How to track:**
  - BEA.gov quarterly releases
  - Nowcast (Atlanta Fed GDPNow, NY Fed Nowcast)
  - Leading Economic Indicators (LEI) from Conference Board
- **Typical reaction:**
  - **Strong GDP beat**: Bullish. Earnings growth expectations rise. Risk appetite increases.
  - **Weak GDP miss**: Bearish. Recession fears. Defensive sectors (utilities, healthcare, staples) outperform.
  - Negative GDP two consecutive quarters = technical recession definition.

### Employment / Jobs Report
- **What it is:** Monthly report from BLS covering Non-Farm Payrolls (NFP) and Unemployment Rate. Big focus on the first Friday of each month.
- **Why it matters:** Employment is a simultaneous indicator — strong employment drives consumer spending (70% of GDP) but can also signal overheating/inflation risk. The Fed watches this closely.
- **How to track:**
  - BLS Jobs Report (first Friday of month, 8:30am ET)
  - Initial Jobless Claims (weekly, Thursday) — more timely labor market signal
  - ADP Non-Farm Employment (private sector, released before BLS)
  - JOLTS (Job Openings and Labor Turnover Survey) — Vacancy rate signals labor tightness
- **Typical reaction:**
  - **Hot jobs** (big NFP beat): Bullish for economy, but raises inflation fears → rates may stay higher → mixed market reaction.
  - **Cold jobs** (NFP miss): Bearish. Recession risk. Fed rate cut expectations increase.
  - **Rising unemployment**: Often more bearish signal than weak NFP, as it signals labor market softening.

### Federal Reserve Policy
- **What it is:** The Fed's dual mandate is price stability (2% inflation) and maximum employment. Tools: Fed funds rate, quantitative tightening (QT), forward guidance, emergency facilities.
- **Why it matters:** The Fed is arguably the single most powerful entity influencing stock prices. Its actions shape the discount rate, liquidity conditions, and risk appetite.
- **How to track:**
  - FOMC meetings (8x/year, minutes released 3 weeks after)
  - Fed Chair speeches (Jerome Powell's tone, word choice, body language)
  - Balance sheet runoff (QT pace)
  - repo markets for liquidity stress signals
  - Dot plot (Summary of Economic Projections)
- **Typical reaction:**
  - **Dovish Fed** (rate cuts, dovish guidance): Risk-on. Stocks rally. Growth stocks outperform. Yields fall.
  - **Hawkish Fed** (rate hikes, tighten financial conditions): Risk-off. Stocks fall. Financials may outperform. Dollar strengthens.
  - **Uncertainty/volatility around Fed**: VIX elevates. Market oscillates.

### Treasury Yields
- **What it is:** The interest rate the US government pays to borrow money at different maturities. The 10Y is the most important for stocks — it's the benchmark for all risk asset valuations.
- **Why it matters:** The 10Y is the "risk-free rate." When it rises, future corporate earnings are worth less today → lower P/E multiples. It also competes with equities for capital. The yield curve (2Y vs 10Y spread) predicts recessions.
- **How to track:**
  - Treasury.gov or FRED (St. Louis Fed) for yield data
  - Daily yield curve shape
  - TIPS yields vs nominal yields for inflation expectations
  - Dollar Index (DXY) — dollar strength often correlates with rising yields
- **Typical reaction:**
  - **10Y rising rapidly**: Growth stocks, tech, high-P/E stocks get hit hardest. Banks may benefit.
  - **10Y falling**: Risk-on rally. High-growth, speculative assets outperform.
  - **Curve inversion**: Recession signal → defensive sectors, gold.

### Dollar Strength (DXY)
- **What it is:** The US Dollar Index measures the dollar vs. a basket of currencies (EUR, JPY, GBP, CAD, SEK, CHF). ~57% euro weight.
- **Why it matters:**
  - **Multinationals benefit** from weak dollar (earnings abroad convert to more dollars)
  - **Commodities priced in dollars** (oil, gold) become cheaper globally → demand rises
  - **Capital flows**: Strong dollar attracts capital into US assets; weak dollar pushes capital outflows
  - **Emerging markets** with dollar-denominated debt get crushed by strong dollar
- **How to track:**
  - DXY on any charting platform
  - Trade-weighted dollar index (more comprehensive, from the Fed)
- **Typical reaction:**
  - **Dollar strengthens**: Headwind for multinationals (AAPL, MSFT, etc.). Good for US domestic small caps. Emerging market stocks suffer.
  - **Dollar weakens**: Tailwind for multinationals. Commodity stocks rally. Emerging markets breathe.

---

## 2. COMPANY FUNDAMENTALS

These are the micro-level drivers specific to each company. They determine relative performance within sectors.

### Earnings & Revenue
- **What it is:**
  - **EPS (Earnings Per Share)**: Net income / shares outstanding. The core measure of profitability.
  - **Revenue**: Top-line sales. Growth without revenue growth is often margin expansion gimmicks.
  - Reported as **GAAP** (actual) vs. **Non-GAAP / Adjusted** (excludes one-time items, stock compensation, etc.)
- **Why it matters:** Earnings are the primary driver of long-term stock price. Price = earnings × P/E multiple. Beat or miss on earnings moves stocks immediately and persistently.
- **How to track:**
  - Earnings calendar (Yahoo Finance, Earnings Whispers, Tikr)
  - Company guidance (forward statements are forward-looking, more relevant than backward-looking GAAP)
  - Consensus estimates (FactSet, Bloomberg consensus)
  - whisper number (unofficial expected number circulated on trading desks)
- **Typical reaction:**
  - **Beat + raise guidance**: Strong rally, often gap up. Momentum continues.
  - **Beat + lower guidance**: "Buy the rumor, sell the news." Market focuses on future miss.
  - **Miss**: Gap down. Downgrades follow. Institutional selling begins.
  - **Small-cap beat on GAAP vs. non-GAAP**: Use GAAP for small caps; avoid manipulation.

### Earnings Per Share (EPS) — Deep Dive
- **What it is:** Net income divided by shares outstanding. Look at both reported (GAAP) and adjusted (non-GAAP).
- **Why it matters:** The "E" in P/E. The EPS trend over time matters more than any single quarter. Also watch EPS growth rate vs. revenue growth — expanding margins are healthy; revenue growth without EPS is a red flag.
- **How to track:**
  - Historical EPS table (5-10 years)
  - Forward EPS (analyst consensus for next 12 months)
  - Trailing 12-month (TTM) EPS
- **Typical reaction:**
  - **EPS growth accelerating**: P/E multiple can expand — "multiple on earnings" — stock compounds.
  - **EPS declining but stock up**: Market pricing in turnaround → fragile. One bad quarter can collapse it.
  - **Analyst downgrades before report**: Often a tell. Check the estimate trend over weeks before reporting.

### Guidance / Forward Statements
- **What it is:** What the company says about its own future — forward revenue, EPS guidance, EBITDA, operating margin targets. Management provides this on earnings calls.
- **Why it matters:** Markets price stocks on future expectations, not past earnings. Guidance beats are often more important than the actual earnings beat. Companies guide down before bad quarters (a form of expectations management).
- **How to track:**
  - Earnings call transcripts (Seeking Alpha, Alpha Street)
  - Guidance history (did they beat or miss their own guidance last quarter?)
  - Management tone on calls (cautious vs. confident)
- **Typical reaction:**
  - **Beat + raise guidance**: Strong buy signal. Momentum follows.
  - **Beat + maintain guidance** (refuse to raise): Market may sell the news as "disappointing"
  - **Guide down before report**: Expectations managed. Smaller beat may not help.
  - **Silent on guidance** (many recent quarters): Corporate risk aversion; adds uncertainty.

### Balance Sheet
- **What it is:** A snapshot of what a company owns (assets), what it owes (liabilities), and what belongs to shareholders (equity) at a point in time.
  - **Assets**: Cash, receivables, inventory, property, intangibles (goodwill, patents)
  - **Liabilities**: Debt, payables, deferred revenue
  - **Key ratios**: Current ratio (current assets / current liabilities), Debt-to-Equity, Debt-to-EBITDA
- **Why it matters:**
  - **Cash-rich companies** can weather downturns, buy back stock, acquire, pay dividends — signs of financial health.
  - **High debt** = leverage. Good in growth times, catastrophic in downturns. Watch Debt-to-EBITDA (healthy < 2-3x, distressed > 4-5x).
  - **Goodwill impairments** signal overpayment for acquisitions → stock price damage.
- **How to track:**
  - 10-K (annual), 10-Q (quarterly) filings via SEC EDGAR
  - Balance sheet quality scores (some data providers)
  - Cash burn rate (for unprofitable companies) — runway matters
- **Typical reaction:**
  - **Strong cash position**: Stock supports. Activist investors target these companies.
  - **Excessive debt + rising rates**: Stock underperforms. Refinancing risk is real.
  - **Goodwill impairment announcement**: Immediate, sharp sell-off.

### Cash Flow Statement
- **What it is:** Tracks actual cash moving in and out of the business — more difficult to manipulate than earnings (accrual accounting).
  - **Operating Cash Flow (OCF)**: Cash from core business. Should exceed net income.
  - **Free Cash Flow (FCF)**: OCF minus capital expenditures. The "real" earnings. FCF = cash available for buybacks, dividends, debt paydown, acquisitions.
  - **FCF Yield**: FCF / Market Cap. Higher = more undervalued.
- **Why it matters:** Earnings can be manipulated through accounting; cash flow is harder to fake. Companies that consistently generate strong FCF tend to be undervalued on FCF metrics vs. P/E metrics.
- **How to track:**
  - FCF history (5+ years)
  - FCF vs. net income divergence (red flag if earnings > cash flow consistently)
  - Capital expenditure trends (is the company investing in growth or milking the business?)
- **Typical reaction:**
  - **Strong and growing FCF**: Long-term outperformance. Stock buybacks fund shareholder returns.
  - **FCF negative + earnings positive**: Suspicious — accrual earnings may be inflated. Potential earnings restatement risk.
  - **Sudden FCF compression**: Often precedes earnings miss. Monitor working capital changes.

### Debt & Leverage
- **What it is:** Total debt (short-term + long-term), debt maturity schedule, interest coverage ratio (EBITDA / interest expense).
- **Why it matters:**
  - **Rising rates** make variable-rate debt more expensive → eats into earnings
  - **Debt maturities** require refinancing — if rates are higher when they mature, costs rise
  - **Debt covenants** can restrict shareholder returns if metrics deteriorate
  - **Credit ratings** (S&P, Moody's) affect borrowing costs and institutional ownership mandates
- **How to track:**
  - Debt schedule in 10-K / 10-Q
  - Interest coverage ratio trend
  - Credit default swaps (CDS) spreads — market's real-time default probability signal
  - Short interest relative to float (for highly leveraged short-squeeze candidates)
- **Typical reaction:**
  - **Downgrade by credit agency**: Stock sell-off, cost of debt rises.
  - **Debt refinancing at higher rates**: Guidance pressured. Market repricing.
  - **Leveraged company in recession fear**: Outperform on downside if they can weather it, but most suffer.

---

## 3. SECTOR & INDUSTRY DYNAMICS

Market-wide forces interact differently with each sector. Understanding these dynamics helps you know which stocks to own in any environment.

### Sector Rotation
- **What it is:** Capital flowing from one sector to another based on the macro environment, rate cycle, or risk appetite changes.
- **Why it matters:** You don't want to own the wrong sector at the wrong time. Cyclical sectors (consumer discretionary, industrials) outperform in growth; defensive sectors (utilities, staples, healthcare) outperform in recessions.
- **Typical rotation pattern by cycle phase:**
  - **Early cycle (recovery)**: Financials, Consumer Discretionary, Industrials, Materials
  - **Mid cycle (expansion)**: Technology, Communication Services, Materials
  - **Late cycle (overheating)**: Energy, Utilities (often rotates into defensive)
  - **Recession**: Utilities, Healthcare, Consumer Staples, Gold
- **How to track:**
  - Sector ETF relative performance (XLF vs. XLK vs. XLE vs. XLU over time)
  - Relative strength of sector vs. SPY
  - Rotation indicators (Bespoke, Morningstar sector dashboards)
  - Bull/bear market leadership differences

### Industry Trends
- **What it is:** Sector-specific secular (long-term) shifts — disruption, regulation, demographic changes, technology adoption curves.
- **Why it matters:** Even within a hot sector, weak industry trends can crush a stock (e.g., legacy retailers inside Consumer Discretionary during e-commerce disruption). Similarly, strong industry trends lift all boats (cloud computing 2012-2021).
- **Key current industry dynamics:**
  - **Tech**: AI/ML adoption, cloud migration, semiconductor cycles, developer velocity
  - **Healthcare**: Drug approval pipelines, patent cliffs, Medicare pricing pressure, GLP-1 market expansion
  - **Energy**: Energy transition, OPEC supply discipline, LNG export capacity, domestic production
  - **Financials**: Net interest margin direction, fee income trends, credit loss rates, Basel III capital requirements
  - **Consumer**: Discretionary vs. staples split, consumer credit health, household savings rate
  - **Industrials**: Infrastructure spending (U.S. CHIPS Act, IRA), defense budgets, shipping rates
- **How to track:**
  - Industry-specific news, earnings call language
  - Demand/supply balance for key inputs
  - Regulatory calendars
  - Adoption rate curves (e.g., EV market share, AI spending % of IT budgets)

### Supply Chain
- **What it is:** The flow of inputs from raw materials → components → finished goods → distribution.
- **Why it matters:** Supply chain disruptions cause input cost inflation (hurt margins) or shortages (lose sales). Bullwhip effects can cause inventory corrections years after demand shocks (see: semiconductor shortage → oversupply 2022-2023).
- **How to track:**
  - **Global supply chain pressure index** (NY Fed)
  - **PMI (Purchasing Managers' Index)** — new orders, supplier deliveries, inventories sub-indices
  - **Shipping rates** (Baltic Dry Index, FedEx shipping data)
  - **Company-specific disclosures** on earnings calls: management discussing "supply constraints" vs. "demand weakening"
- **Typical reaction:**
  - **Supply shortage**: Input costs spike → margins compress → guidance lowered. Companies with captive supply (vertical integration) outperform.
  - **Supply normalization**: Relief rally for dependent companies. Margins recover.
  - **Inventory glut**: Signals demand has cooled — companies cut production, workers laid off, guidance lowered.

---

## 4. TECHNICAL FACTORS

Technical analysis studies price/volume behavior to predict future moves. It's a debate about supply and demand, made visible.

### Support & Resistance
- **What it is:**
  - **Support**: A price level where buying pressure historically exceeds selling pressure. Buyers step in at this price.
  - **Resistance**: A price level where selling pressure exceeds buying. Sellers step out at this price.
  - **Breakout**: When price moves through a key level on volume — signals acceleration in that direction.
  - **Breakdown**: Opposite of breakout — signal of further decline.
- **Why it matters:** Key technical levels act as self-fulfilling prophecies. Large orders cluster at round numbers, moving averages, and prior highs/lows. Algorithms detect these levels and react.
- **How to track:**
  - Historical price pivots (swing highs/lows)
  - Volume profile (where most shares traded)
  - Fibonacci retracement levels (61.8%, 38.2%)
  - Horizontal support/resistance at round numbers and prior consolidation zones
- **Typical reaction:**
  - **Bounce from support**: Bulls defend it. Accumulation may be happening.
  - **Break below support**: Cascade sell-off. Stop losses trigger. Next support level further down.
  - **Breakout above resistance**: Trend accelerates. Next resistance is higher.
  - **False breakout** (breakout then reversal): Liquidity trap. Violent move against the breakout crowd.

### Moving Averages
- **What it is:** Smoothed average price over a rolling window.
  - **SMA**: Simple moving average (equal weight)
  - **EMA**: Exponential moving average (more weight on recent prices — faster response)
  - **Common periods**: 20 (short-term), 50 (medium-term), 200 (long-term trend)
  - **Golden Cross**: 50 SMA crosses above 200 SMA → historically bullish
  - **Death Cross**: 50 SMA crosses below 200 SMA → historically bearish
- **Why it matters:** Markets remember averages. Institutions use them for position sizing and stop-loss placement. EMAs are faster signals; SMAs are more significant structural levels.
- **How to track:**
  - Moving average slope direction (up = bullish trend, down = bearish)
  - Price relative to key MAs (above = bullish, below = bearish)
  - MA crossovers as entry/exit signals
- **Typical reaction:**
  - **Price above 50 SMA + 200 SMA both rising**: Strong uptrend. Buy pullbacks to 50 SMA.
  - **Price below 50 but above 200**: Mild weakness. Could be correction or reversal starting.
  - **Price below both**: Bear market. Resistance clusters at 50 and 200 SMAs.
  - **50/200 SMA crossover**: Often confirms major trend change. However — signals are lagged and widely known.

### RSI (Relative Strength Index)
- **What it is:** Momentum oscillator (0-100) measuring the magnitude of recent price changes. RSI > 70 = overbought (overextended upside); RSI < 30 = oversold.
- **Why it matters:** Identifies extremes where reversals are likely. Also monitors for divergence — when price makes a new high but RSI doesn't (bearish divergence) — often precedes reversals.
- **How to track:**
  - Standard 14-period RSI
  - **Overbought/oversold zones**: RSI > 70 = caution on longs; RSI < 30 = caution on shorts
  - **Hidden divergence**: Price makes higher low, RSI makes lower low = bearish continuation (not reversal)
  - RSI midline (50) crossing = trend momentum shift
- **Typical reaction:**
  - **RSI > 70**: Pullback risk. Stock overextended. Mean reversion likely.
  - **RSI < 30**: Bounce candidates. Oversold. Counter-trend buyers step in.
  - **RSI divergence**: Warns of momentum loss before price turns. Watch for this on tops.

### MACD (Moving Average Convergence Divergence)
- **What it is:** Trend-following momentum indicator.
  - **MACD line**: 12-period EMA − 26-period EMA
  - **Signal line**: 9-period EMA of MACD line
  - **Histogram**: MACD line − Signal line (shows momentum acceleration/deceleration)
  - Bullish signal: MACD crosses above signal line
  - Bearish signal: MACD crosses below signal line
- **Why it matters:** Catches trend changes earlier than MAs alone. Histogram narrows before crossover — gives early warning.
- **How to track:**
  - MACD crossover signals
  - MACD zero line (above = bullish momentum zone, below = bearish)
  - Histogram bars getting smaller = momentum weakening (even if price still rising)
- **Typical reaction:**
  - **MACD crosses above signal line**: Momentum shift to bullish. Confirm with price action.
  - **MACD crosses below signal line**: Momentum shift to bearish.
  - **Histogram contracting**: Speed of move is slowing. Consolidation or reversal incoming.
  - **MACD diverging from price**: Major warning signal.

### Volume
- **What it is:** The number of shares traded in a period. Confirms the strength of a price move.
- **Why it matters:** Price + volume = confirmation. A breakout on low volume is suspect; a breakout on high volume is a stronger signal. Volume precedes price — unusual volume spikes often precede big moves.
- **How to track:**
  - **On-balance volume (OBV)**: Cumulative volume adding on up days, subtracting on down days. Confirms trend.
  - **Volume spike**: 2x+ average volume day is a signal — something has changed
  - **Average volume by time of day** (intraday): Volume patterns differ by time of day
  - **Relative volume (RVol)**: Today's volume vs. the average for that time of day
- **Typical reaction:**
  - **Price up + volume up**: Strong, confirmed move. Bullish continuation likely.
  - **Price up + volume declining**: Weak move. May be a distribution top.
  - **Price down + heavy volume**: Distribution. Serious selling. Bottom may be near if volume spikes at support.
  - **Gap up on low volume**: Suspect. Likely to fill the gap.

### Chart Patterns
- **What it is:** Recurring, identifiable price formations that tend to predict future behavior.
- **Key patterns:**
  - **Cup and Handle**: Bullish continuation. Rounded base (cup) → consolidation (handle) → breakout higher.
  - **Head and Shoulders**: Bearish reversal. Three peaks: left shoulder, head (highest), right shoulder, then breakdown.
  - **Double Top/Bottom**: Two peaks at similar level = resistance; two troughs at similar level = support.
  - **Ascending/Descending Triangle**: Flat top (accumulation/distribution) with angled bottom. Breakout direction predicts next move.
  - **Flag/Pennant**: Short-term continuation after strong move. Parallelogram or small triangle consolidation.
  - **Dead Cat Bounce**: Strong downtrend → rally back to prior support (now resistance) → resumption of downtrend.
- **Why it matters:** Patterns represent supply/demand battles that have played out repeatedly. They have self-fulfilling properties because traders watch them.
- **Typical reaction:** Breakout direction usually confirmed by volume. Stop-loss placed just beyond pattern boundary.

### Market Cap & Float
- **What it is:**
  - **Market Cap** = Share price × Shares outstanding
  - **Float** = Shares available for trading (excludes insider/strategic holdings)
  - **Market cap categories**: Mega-cap ($200B+), Large-cap ($10B-$200B), Mid-cap ($2B-$10B), Small-cap ($250M-$2B), Micro-cap (<$250M)
- **Why it matters:**
  - **Large/mega-cap**: More liquid, more institutional ownership, less volatile day-to-day, more coverage
  - **Small/micro-cap**: Less liquid, more volatile, less analyst coverage = more inefficient = more alpha opportunity
  - **Float shrinkage**: As insiders lock up shares, float decreases → same dollar volume moves price more (float compression)
  - **Index inclusion/exclusion**: Being added to an index creates automatic buying from index funds
- **How to track:**
  - Market cap category classification
  - Shares outstanding vs. float (check for large insider/ESOP blocks)
  - Index weight (in SPY, QQQ, Russell indices)

---

## 5. SENTIMENT

Sentiment measures the collective psychological state of market participants. It can drive prices far from fundamentals in the short term.

### Fear & Greed Index (CNN Money)
- **What it is:** A composite index (0-100) measuring market sentiment across 7 indicators: put/call ratio, junk bond demand, stock price breadth, call options, market volatility (VIX), safe-haven demand, and momentum.
  - 0 = Extreme Fear
  - 50 = Neutral
  - 100 = Extreme Greed
- **Why it matters:** Sentiment is a contrarian indicator. Extreme fear often marks bottoms (buying opportunities). Extreme greed marks tops (dangerous to buy). It's a rough sentiment thermometer.
- **How to track:**
  - CNN Money Fear & Greed Index (free)
  - NDR Trading Sentiment (Ned Davis Research)
  - AAII Sentiment Survey (weekly, tracks individual investor bullishness/bearishness)
- **Typical reaction:**
  - **Extreme Fear (0-20)**: Market often bottoms within days to weeks. Contrarian buy signal.
  - **Extreme Greed (80-100)**: Market often tops within days to weeks. Caution warranted.
  - **Neutral (40-60)**: Sentiment provides no clear edge. Focus on fundamentals and technicals.

### Put/Call Ratio
- **What it is:** Ratio of put options volume (bets on decline) to call options volume (bets on rise). Can be measured on individual stocks, sectors, or the broad market.
  - **High PCR** (>1.0): More puts than calls = bearish positioning OR hedging activity (hard to distinguish)
  - **Low PCR** (<0.7): More calls than puts = bullish positioning, complacency
- **Why it matters:** Extreme readings (>1.3 or <0.5) tend to be contrarian. Also a gauge of hedging activity — when hedgers are loading up on puts, they may know something.
- **How to track:**
  - CBOE Total Put/Call Ratio (broad market)
  - Equity-only put/call ratio (more stock-specific signal)
  - 10-day moving average of PCR smooths noise
- **Typical reaction:**
  - **PCR spikes to extreme**: Often accompanies market bottoms (panic puts bought). Contrarian bullish signal.
  - **PCR drops to extremely low levels**: Complacency. Often accompanies market tops.

### Short Interest
- **What it is:** The number of shares sold short (borrowed shares sold with expectation of buying back cheaper) as a percentage of float.
  - **Short Interest Ratio (Days to Cover)**: Short interest / average daily volume. How many days it would take to cover all short positions if every short bought back at once.
  - **Short interest as % of float**: Higher = more bearish positioning, also more potential short squeeze fuel
- **Why it matters:**
  - **Short squeeze potential**: Stocks with very high short interest (20%+ of float) are prone to short squeezes — short sellers forced to buy to cover creates buying pressure that drives price up violently.
  - **Bearish signal of conviction**: Sophisticated short sellers research deeply before shorting. High short interest is a red flag.
  - **High days to cover**: A short squeeze in this stock could last weeks.
- **How to track:**
  - NYSE / NASDAQ short interest data (released bi-monthly, ~10 days after settlement)
  - Short squeeze candidates ( sites track this: SqueezeMetrics, iBorrowDesk for loan fees)
  - Failures to deliver (FTD) data — persistent FTDs signal potential manipulation or settlement issues
- **Typical reaction:**
  - **Short interest spike**: Stock faces headwinds. Hard for the stock to outperform.
  - **Short squeeze**: Sharp vertical rally as short sellers rush to cover. Often overshoots. Then collapses.
  - **Short covering**: In uptrends, short sellers covering adds fuel to rally.

### Social Media Sentiment
- **What it is:** Online chatter about stocks — Reddit (WSB), Twitter/X, StockTwits, TikTok, YouTube, Discord servers.
- **Why it matters:**
  - **Retail amplification**: Social media can cause retail stampedes into and out of stocks. WSB favorites (GME, AMC) showed how retail flow can move prices dramatically.
  - **Sentiment as leading indicator**: Rising mention volume + positive sentiment often precedes price rises.
  - **Narrative momentum**: The story matters as much as the numbers. A compelling narrative on social media attracts followers and money.
  - **Risks**: Pump-and-dump schemes, coordinated manipulation, viral but wrong analysis.
- **How to track:**
  - **StockTwits** — sentiment + trending
  - **Quiver Quant** — social media data, congressional trading, government contracts
  - **Alternative.me** — social sentiment data
  - **Trading volume anomalies** relative to social media mentions
  - Google Trends for stock search volume
- **Typical reaction:**
  - **Viral stock on WSB**: Buying frenzies. Extreme volatility. Can squeeze shorts.
  - **Trending on Twitter with negative sentiment**: Selling pressure. Narrative turns.
  - **Social sentiment precedes price**: Often but not always. Correlation ≠ causation.

### Analyst Ratings
- **What it is:** Wall Street analysts (sell-side) at major banks publish ratings (Buy/Hold/Sell) and price targets for covered stocks.
  - **Ratings**: Buy (strongest conviction), Outperform, Hold/Neutral, Underperform, Sell
  - **Price target**: 12-month target price. Average vs. consensus creates range.
  - **Revision direction**: Upgrades and downgrades matter more than the absolute rating — the trend in revisions is key.
- **Why it matters:**
  - **Institutional decision-making**: Many institutions require buy-side analyst coverage or cannot hold stocks without a buy rating from at least one major bank.
  - **Self-fulfilling prophecy**: Price targets create anchor points. Upgrades attract buying.
  - **Bias**: Analysts are often reluctant to issue sell ratings (conflicts of interest — companies are their clients via IPOs, underwriting). Ratings tend to be optimistic.
  - **Earnings estimate revisions**: More granular than ratings. Track the trend — are estimates going up or down?
- **How to track:**
  - Bloomberg consensus (most comprehensive, paywalled)
  - Yahoo Finance, TipRanks (free)
  - Zacks Investment Research
  - Watch for "Wall Street never saw it coming" — consensus estimate misses are the most damaging.
- **Typical reaction:**
  - **Analyst upgrade**: Immediate 1-3% pop on the day. Adds credibility for institutional buyers.
  - **Analyst initiation with Buy**: Particularly bullish — fresh coverage signals institutional eligibility.
  - **Multiple downgrades on same stock**: Serious warning sign. Sentiment deteriorates.
  - **Price target cuts**: Often more impactful than ratings — if the target goes down, institutions trim positions.

---

## 6. OPTIONS MARKET

The options market prices in a probability distribution of future outcomes. It is the most forward-looking data set available to traders.

### Open Interest (OI)
- **What it is:** The total number of outstanding (unclosed) option contracts at a given strike and expiration. Shows how much capital is deployed at each strike.
- **Why it matters:**
  - **OI + price rise** = new money flowing in (confirming move)
  - **OI + price fall** = longs selling (distribution)
  - High OI at a strike = "magnet zone" — that strike has lots of participants. Price often gets drawn toward high OI strikes.
  - **OI by strike** shows where the "big money" thinks price will be.
- **How to track:**
  - OI by strike (available on brokerage platforms)
  - OI concentration at specific strikes (very high OI relative to neighboring strikes)
  - OI change day-over-day
- **Typical reaction:**
  - **Rising OI + rising price**: Bullish confirmation. New positions being added.
  - **Rising OI + falling price**: More shorts being added. Bearish.
  - **OI collapsing at a strike**: Positions being closed. That strike loses significance.

### Gamma Squeeze Potential
- **What it is:** When market makers have sold options (collected premium), they are short gamma. As the stock moves, they must delta-hedge by buying more stock (if price rises) or selling (if price falls) — this buying amplifies the move.
  - **Gamma**: The rate of change of an option's delta. Higher gamma = more aggressive delta hedging by MMs.
  - **Gamma squeeze**: Self-reinforcing buying/selling by MMs trying to hedge, which accelerates the price move.
- **Why it matters:** Can produce violent, rapid price moves (10-100%+ in days) in stocks with high short interest + high OI in near-term options + high volatility (high IV = expensive options = more MM hedging needed).
- **How to track:**
  - **Gamma exposure (GEX)** — net gamma dealers hold (available from some data providers like Gme-squeeze.com, analytical platforms)
  - **Short interest + near-term OI**: High SI + near-term OI clusters = gamma squeeze potential
  - **Cost to borrow (CTB)** — if borrowing costs are high, short sellers are paying up = high conviction short position
  - Negative GEX (dealers short gamma) = potential for sharp moves in either direction
- **Typical reaction:**
  - Stock rises → MMs delta-hedge by buying more shares → stock rises more → repeat → violent short squeeze.
  - Sharp moves up or down can both trigger gamma squeeze dynamics.

### Options Flow
- **What it is:** The actual purchase or sale of options contracts — who is buying, what strikes, what expiration, and the dollar value.
- **Why it matters:** Unusual options activity in large dollar amounts often precedes significant moves. Watching flow from "smart money" (institutional) vs. retail is key.
- **How to track:**
  - **Unusual Whales** (unusualwhales.com) — free tier shows unusual options activity
  - **FlowAlgo** — paid, more comprehensive
  - **Dark pool / block prints**: Institutional orders that print after hours
  - Key difference: **Buying calls/puts (debit)** vs. **selling calls/puts (credit)**. Selling a put = taking bullish risk. Selling a call = taking bearish risk.
- **Typical reaction:**
  - **Large speculative call buying in near-term OTM strikes**: Bullish if stock moves; can be a sign of a squeeze building.
  - **Large put buying in a short squeeze stock**: Hedging. Protects longs.
  - **Sell-wall (large put sell orders)**: Institutional is selling puts at a strike = they think stock won't go below that level.
  - **Delta hedging by MMs**: This is not "smart money" — it's a mechanical response.

### ITM/OTM Dynamics
- **What it is:**
  - **ITM (In The Money)**: Call where strike < stock price, or Put where strike > stock price. ITM options have intrinsic value. Higher likelihood of expiring in the money.
  - **OTM (Out of The Money)**: Call where strike > stock price (or Put where strike < stock price). Purely speculative. No intrinsic value — only time value.
  - **Delta**: Probability proxy — an option's delta of 0.70 means ~70% chance of finishing ITM.
- **Why it matters:**
  - **High OI in near-term ITM options**: Large players hedging existing stock positions. If they're selling calls, they're reducing upside exposure to stock they already own (covered calls).
  - **High OI in near-term OTM options**: Pure speculative bets. These expire worthless most of the time, but occasional big winners.
  - **Max pain**: The strike where the most options expire worthless (max pain for option buyers = max profit for option sellers). Stock often gravitates toward max pain near expiration.
  - **OTM options expiring worthless**: Creates mechanical selling pressure at expiration (if shares need to be delivered for short calls).
- **How to track:**
  - **Max pain calculation**: Sum of all ITM strike × OI — find the strike where option buyers lose the most
  - **Put/call OI by strike**: See where large positions cluster
  - **Delta skew**: OTM puts often more expensive than OTM calls (fear > greed), especially in bearish environments

---

## 7. INSTITUTIONAL FACTORS

Institutions (mutual funds, hedge funds, pension funds, sovereign wealth funds) control the majority of equity capital. Their moves move markets.

### 13F Filings
- **What it is:** Quarterly reports (filed within 45 days of quarter-end) where institutional investment managers with $100M+ AUM disclose their long equity positions.
  - Shows what institutions owned at quarter-end — stale data (45+ day delay)
  - 13F-HR (holdings report) vs 13F-HR/A (amendment)
  - Lists: company name, class, value, shares, % of portfolio
- **Why it matters:**
  - **Track the whales**: See what Berkshire, Bridgewater, Renaissance, etc. are buying and selling
  - **Follow the leaders**: Institutions controlling billions must do extensive research before buying. Their moves are signals.
  - **Changes between quarters**: New purchases (new positions) are most interesting; fully exited positions (sold to zero) signal conviction
  - **Concentration**: Watch if a fund is building or reducing a position significantly (>50% change in shares)
- **How to track:**
  - **SEC EDGAR** (free, but raw data)
  - **WhaleWisdom.com** (free, parsed 13F data)
  - **Finra.org** (Form 13F filings)
  - **OpenEdge (AlphaArchitect)** — compares 13F filings across managers
  - **Sentiecon.com** — tracks fund sentiment and changes
- **Typical reaction:**
  - **Whale adds new position**: Often triggers momentum. Other investors follow.
  - **Whale sells entire position**: Negative signal. Other investors follow.
  - **13F beat (stock runs before filing)**: Sometimes happens — institutional buying ahead of filing.
  - **Note**: Many hedge funds file late or partially — data is an approximation, not complete.

### Insider Buying / Selling
- **What it is:** Corporate insiders (officers, directors, 10% owners) must report insider transactions to the SEC. These print on EDGAR within 2 business days ( Form 4 ).
  - **Open market purchase/sale**: Regular buying/selling
  - **10b5-1 plan**: Pre-set selling plan (allows insiders to sell on schedule, good for non-insider-trading-violation compliance)
  - **Gift**: No consideration — usually just a gift, but still reported
  - **Rule 10b5-1**: Pre-scheduled trading plans allow selling during blackout periods
- **Why it matters:** Insiders have the best view of their company's true health. They buy when they believe the stock is undervalued; they sell for many reasons (liquidity, diversification) — the absence of buying matters as much as the presence of selling.
- **How to track:**
  - **SEC EDGAR Form 4** (free)
  - **InsiderInsights.com** — parsed insider transactions
  - **OpenInsider.com** — free, useful scanner for insider buying
  - **FinViz.com** — insider trading tab
  - Look for **multiple insiders buying** vs. single transactions (larger pattern matters)
- **Typical reaction:**
  - **Heavy insider buying**: Bullish signal. Insiders have skin in the game and inside knowledge.
  - **Single insider selling**: Usually no signal — insiders sell for many personal reasons.
  - **Pattern of consistent selling via 10b5-1**: Insiders may be signaling they don't expect near-term performance.
  - **No insider buying during a stock decline**: Also a signal — even insiders won't buy = they may see deeper problems.

### ETF Flows
- **What it is:** Exchange-Traded Funds are baskets of securities. When money flows into or out of ETFs, the fund must buy or sell the underlying stocks to accommodate.
  - **Inflows**: Cash coming into ETFs → fund buys underlying stocks → stocks rise
  - **Outflows**: Cash leaving ETFs → fund sells underlying stocks → stocks fall
  - ETFs now account for ~50% of all equity trading volume in the US.
- **Why it matters:**
  - **ETFs create mechanical demand**: Index inclusion doesn't require judgment — the fund MUST buy when added.
  - **Sector/country ETFs**: Large flows into regional or sector ETFs can dramatically move those markets.
  - **Active ETFs** (semi-transparent structure becoming more common) still create flows but are less predictable than index ETFs.
  - **Authorized participant (AP) arbitrage**: Keeps ETF price close to NAV, but during extreme flows, ETF price can diverge from underlying.
- **How to track:**
  - **ETF.com** (flows data)
  - **Morningstar** (ETF flows, fund flows)
  - **Bloomberg** (comprehensive ETF flow data)
  - **FINRA Trace** (shows individual trades in ETFs vs. blocks)
  - **Large flows in small-cap ETFs** have more impact than same dollar flow in large-cap (liquidity mismatch)
- **Typical reaction:**
  - **Massive ETF inflow**: Mechanical buying across all holdings → broad-based support, especially for index constituents.
  - **ETF outflow**: Selling pressure on underlying stocks.
  - **New ETF launch**: The "ETF effect" — stocks added to new ETFs often see immediate buying.

### Index Rebalancing
- **What it is:** Index providers (S&P Dow Jones, MSCI, FTSE Russell) periodically rebalance their indices — adding new constituents, removing old ones, and reweighting based on market cap changes.
  - **S&P 500 additions/removals**: Most closely watched; affects the most AUM
  - **MSCI rebalancing**: Affects international and emerging market ETFs
  - **Russell reconstitution**: Complete annual rebuild of Russell 2000/3000 in late June
- **Why it matters:**
  - **Index inclusion** = automatic buying from all funds tracking that index. The fund managers don't have a choice — they must hold the new constituent.
  - **Index removal** = automatic selling.
  - The S&P 500 alone tracks ~$4.5T in assets (including ETFs and active funds). A single addition can move that stock significantly.
- **How to track:**
  - S&P Dow Jones announcements (s&P.com)
  - MSCI Market Cap Watch
  - Bloomberg ETF tracking calendars
  - **Announcement vs. effective date**: Stock may run up on announcement, sell off on removal.
- **Typical reaction:**
  - **Announced addition**: Stock often gaps up. Institutional accumulation begins. Runs ahead of effective date.
  - **Effective date**: Last wave of buying. Stock may pause or decline as passive buying is complete.
  - **Announced removal**: Immediate sell-off. Some funds must hold until removed; others sell immediately.

---

## 8. GEOPOLITICAL FACTORS

Events outside the economic calendar — political decisions, conflicts, international agreements — can move markets faster than any earnings report.

### Trade Policy
- **What it is:** Tariffs, trade agreements, export controls, sanctions, and the institutions that enforce them (WTO, US Trade Representative, export control regimes).
- **Why it matters:**
  - **Tariffs are a tax on imports** — raise costs for US importers → margin compression → consumer price increases.
  - **Trade wars**: Escalating tariffs between major economies cause uncertainty, corporate capex reductions (delay investments), and supply chain restructuring.
  - **Export controls** (e.g., US restricting semiconductor chip exports to China) can crush targeted companies' revenue and create supply chain disruptions.
  - **Currency effects**: Tariffs influence currency valuations — protectionist policy often weakens the dollar (makes exports cheaper).
- **How to track:**
  - USTR (ustr.gov) announcements
  - Bloomberg Trade Policy calendar
  - WTO dispute rulings
  - US Census Bureau trade data (monthly)
  - Geopolitical risk indices (Caldara-Iacono)
  - Key countries to watch: US-China, US-EU, US-Mexico, US-Taiwan
- **Typical reaction:**
  - **New tariff announcement**: Sector stocks in target region sell off immediately. Safe-haven assets (gold, yen, treasuries) rally.
  - **Trade deal signed**: Market rallies. Exporters benefit. Supply chain normalization.
  - **Escalation tweets**: VIX spikes. Market whipsaws. Uncertainty premium rises.

### Wars & Armed Conflicts
- **What it is:** Military conflicts that affect global supply chains, energy prices, immigration, defense spending, and investor risk appetite.
- **Why it matters:**
  - **Energy prices**: Conflicts in oil-producing regions (Middle East, Russia-Ukraine) spike oil and gas prices → inflation → rate concerns.
  - **Supply chain disruption**: Conflict near shipping lanes (Strait of Hormuz, Suez Canal, Black Sea) disrupts global trade.
  - **Defense stocks**: War benefits defense contractors (BA, LMT, RTX, NOC) as defense budgets expand.
  - **Safe-haven flows**: Conflict causes capital flight to US Treasuries, gold, Swiss Franc, US Dollar.
  - **Recession risk**: Sustained conflict drains economic resources.
- **How to track:**
  - RealGeoPal (real-time conflict mapping)
  - GlobalConflictTracker (Council on Foreign Relations)
  - Oil prices (WTI, Brent) — immediate proxy for conflict risk
  - Defense stock relative performance vs. market
- **Typical reaction:**
  - **Conflict erupts**: Immediate risk-off. Stocks fall. Gold and oil rise. VIX spikes.
  - **Conflict escalation**: Further risk-off. Energy spikes. Defense stocks outperform. Weak economic growth stocks underperform.
  - **Conflict de-escalation**: Risk-on. Energy prices normalize. Defense stocks give back gains. Broader market recovers.

### Sanctions
- **What it is:** Economic penalties imposed by one or more governments targeting countries, entities, or individuals.
- **Why it matters:**
  - **Sanctions on Russia**: Frozen sovereign assets, exclusion from SWIFT, oil price cap → dramatically reshaped global energy markets and commodity flows.
  - **Sanctions on Iran**: Contributed to oil price volatility, informal tanker networks.
  - **Secondary sanctions**: Threat to third countries doing business with sanctioned parties — extraterritorial reach.
  - **De-dollarization**: Sanctions accelerate efforts to reduce dollar dependency in bilateral trade.
- **How to track:**
  - OFAC (Treasury) sanctions lists
  - EU, UK, UN sanction frameworks
  - Bloomberg commodity flow data
  - Country-specific ETF performance (RSX for Russia, EWZ for Brazil, EWY for South Korea)
- **Typical reaction:**
  - **New sanctions announced**: Immediate impact on targeted country's assets. Ripple effects on allied/subsidiary companies.
  - **Sanctions on oil producers**: Oil price spike → inflation risk → rate concerns → broad market headwind.

### Elections
- **What it is:** Political cycles — presidential, congressional, midterms, primaries. US elections are the most market-moving globally due to US market weight.
- **Why it matters:**
  - **Presidential elections**: Party platforms differ on tax policy, regulation, trade, healthcare. Markets tend to price in expected policy outcomes.
  - **Congressional control**: Divided government vs. unified government produces very different policy outcomes. Unified Democrat government (2021-2023) → passed large stimulus, infrastructure bill, tax increases on wealthy → affected sector rotations.
  - **Lame duck periods**: Reduced legislative activity creates uncertainty.
  - **Election-year seasonality**: Historically, markets exhibit volatility patterns in election years.
- **How to track:**
  - PredictIt, Polymarket (prediction markets — prices reflect probabilities)
  - Intrade (now defunct but similar),Betfair
  - Polling averages (538, RCP)
  - Policy calendars (legislative deadlines)
- **Typical reaction:**
  - **Clear winner early**: Market prices in policy platform → rotation to preferred sectors.
  - **Contested/unclear result**: Uncertainty premium → VIX spikes, risk-off.
  - **Tax cut extension (Republican)** → Bullish for financials, energy, small caps.
  - **Increased regulation (Democrat)** → Headwind for healthcare, financials, energy; tailwind for renewables.

### Regulation
- **What it is:** Government rules affecting industries — FDA (drug approvals), FTC (antitrust), EPA (environmental), SEC (securities), DOJ (antitrust enforcement).
- **Why it matters:**
  - **Antitrust action against Big Tech** (Google, Meta, Amazon, Apple): Potential breakup, structural remedies, revenue restrictions — significant valuation headwinds.
  - **FDA drug approvals**: Biotech stocks often move 30-300% on FDA decisions.
  - **EPA environmental rules**: Affect energy sector compliance costs, could accelerate/delay energy transition.
  - **SEC crypto regulation**: Creates legal uncertainty for crypto companies.
  - **Banking regulation**: Basel III/IV capital requirements affect bank profitability.
- **How to track:**
  - FDA AdCom calendar (Advisory Committee meeting dates)
  - FTC/DOJ antitrust enforcement calendar
  - Congressional hearing schedules
  - Agency rulemaking in Federal Register
  - Policy & regulation news on specific sectors
- **Typical reaction:**
  - **Favorable regulation**: Stock pops. New market access created. Confidence restored.
  - **Unfavorable/restrictive regulation**: Stock sells off. Competitive landscape shifts. Compliance costs rise.
  - **FDA approval/rejection**: Biotech moves 30-300%+ on the day.

---

## 9. SECTOR-SPECIFIC DRIVERS

Each sector has unique drivers that aren't captured by broad market indicators.

### Technology Sector
- **Dev cycles / product cycles**: Apple (iPhone cycle), NVIDIA (GPU architecture cycles), Microsoft (Azure/AI cycles). Anticipating major product launches drives massive pre-positioning.
- **Chip shortages / oversupply**: Semiconductors are the oil of the modern economy. Supply/demand imbalances create massive price and margin swings across the entire tech food chain.
- **AI/Machine Learning cycle**: The 2023-2026 AI infrastructure buildout has created a multi-year demand cycle for GPUs (NVIDIA), networking (Marvell, Broadcom), power (Vistra, NextEra), and data centers.
- **Developer velocity**: How fast a company ships product. Metrics: app updates, feature releases, platform growth.
- **Cloud migration**: AWS, Azure, GCP growing. Enterprise software (CRM, ServiceNow, Workday) benefiting from shift to SaaS.
- **Key metrics**: ACV (annual contract value), NRR (net revenue retention), gross margin, churn rate.
- **Macro sensitivity**: High-growth tech is the most rate-sensitive sector. Rising rates compress P/E multiples on future earnings most dramatically.
- **Supply chain dependency**: TSMC (Taiwan) → any geopolitical tension around Taiwan moves global semis. ASML (Netherlands) EUV lithography monopoly.

### Energy Sector
- **OPEP+ supply discipline**: OPEC and allies (OPEC+) control ~40% of global oil production. Their decisions on output quotas directly set the floor for oil prices.
  - **OPEC+ meetings**: Occur bi-monthly. Key dates on the energy calendar.
  - **Spare capacity**: Low spare capacity = oil prices more volatile to shocks.
  - **Compliance rates**: If members cheat on quotas, effective supply increases without official announcement.
- **Global oil storage (DOE data)**: Weekly Wednesday EIA report on US petroleum inventories. Global storage tracked via Bloomberg/IEA.
  - **Crude oil inventories**: Higher than expected = bearish for oil price.
  - **Strategic Petroleum Reserve (SPR)**: US releases or purchases affect headline supply.
- **Natural gas / LNG**: US is now a major LNG exporter. Henry Hub natural gas price affects domestic energy companies; LNG spot prices affect global nat gas markets.
- **Refining capacity**: Refinery utilization rates — when refineries go offline (maintenance season: Spring/Fall), refined product prices spike separately from crude.
- **Energy transition risk**: The secular shift to renewables creates long-term headwinds for fossil fuel majors. How quickly?
- **Key metrics**: Production (barrels/day), breakeven cost, leverage, free cash flow yield, dividend yield.
- **Typical reaction**:
  - **Oil spikes (geopolitical/supply)**: Energy stocks rally. Airline stocks, chemical companies, transportation hurt.
  - **Oil collapses (demand destruction)**: Energy stocks collapse. Budget deficits of oil-dependent nations strain.

### Financials Sector
- **Net Interest Margin (NIM)**: The spread between what banks earn on loans/investments and what they pay on deposits. The key bank profitability metric.
  - **NIM expansion** → banks earn more per dollar loaned → higher bank earnings.
  - NIM direction follows the yield curve shape. Steeper curve = better NIM for most banks.
- **Rate sensitivity**: Banks benefit from rising rates (wider NIM) but face headwinds on the loan book if rates stay too high too long (credit losses rise).
  - **Duration mismatch**: Banks borrow short (deposits) and lend long (mortgages). A sudden rate spike hurts bond portfolios.
- **Credit loss rates**: Allowance for credit losses (ACL) in bank balance sheets. Rising ACL = bank bracing for recessions.
- **Basel III/IV capital requirements**: Require banks to hold more capital (Tier 1 capital) against risk-weighted assets. Higher capital = lower returns on equity, but more stability.
- **Fee income**: Investment banking fees (IPO, M&A advisory), trading revenues, asset management fees — volatile but not rate-sensitive.
- **Key metrics**: NIM, ROE (Return on Equity), CET1 ratio (capital ratio), NPL ratio (non-performing loans), efficiency ratio.
- **Typical reaction**:
  - **Steep yield curve**: Banks outperform. NIM expansion.
  - **Flat/inverted curve**: Banks underperform. NIM compression. Regional banks especially vulnerable.
  - **Credit stress**: Regional banks with commercial real estate exposure vulnerable (CRE loans 2024-present).

### Healthcare / Biotech Sector
- **FDA drug approval calendar**: Biotech's single most important event driver. FDA AdCom (Advisory Committee) votes are leading indicators of approval decisions.
  - **Clinical trial phases**: Phase I (safety), Phase II (dose-finding), Phase III (efficacy). Phase III failure = catastrophic stock collapse.
- **GLP-1 / obesity drug market**: The 2023-2025 revolution in obesity treatment (Eli Lilly, Novo Nordisk, others) created the largest pharmaceutical market expansion in decades.
- **Patent cliffs**: Drugs losing patent protection face generic competition (Authorized Generic) → revenue collapses rapidly.
- **Medicare drug pricing negotiation**: The Inflation Reduction Act (2022) allows Medicare to negotiate drug prices → revenue risk for pharma.
- **Pipelines**: A company's drug pipeline determines its long-term value. Track: IND filings, Phase I/II/III initiation, NDA/BLA submissions.
- **Key metrics**: Clinical trial readouts (event-driven), revenue growth, EPS, P&E ratio for biotech (use EV/EBITDA or cash runway instead).
- **Typical reaction**:
  - **FDA approval**: +30-300% on approval day, depending on drug market size.
  - **Complete Response Letter (CRL) / rejection**: -30-80% on rejection day.
  - **Phase III failure**: -80-95% in a single day.

### Consumer Sector
- **Consumer confidence (Conference Board, Michigan)**: Consumer spending drives 70% of GDP. Confidence levels predict spending behavior.
- **Household savings rate**: US personal savings rate (from 33% pandemic high to <3% in 2022-2023) affects future consumption capacity.
- **Consumer credit health**: Total revolving credit, delinquency rates, credit card APRs (now 20%+). Tightening credit = slowing consumer.
- **Same-store sales (SSS)**: Revenue growth from stores open at least one year. Strips out new store openings. Key metric for retailers.
- **Discretionary vs. Staples rotation**: Staples (PG, KO, WMT) hold up in recessions; Discretionary (AMZN, TSLA, NKE) fall.
- **Consumer Price Index components**: Food at home, new vehicles, apparel, recreation — sector-specific CPI components affect margins.
- **Key metrics**: SSS, average ticket, transaction count, e-commerce penetration %, gross margin.

### Industrials / Defense
- **Government defense budgets**: Defense spending is counter-cyclical (governments spend in recessions). Annual National Defense Authorization Act (NDAA) sets the budget.
- **Infrastructure spending**: U.S. infrastructure bill ($1.2T, 2021) created multi-year demand for construction, materials, machinery.
- **Commercial aerospace cycle**: Boeing deliveries, Airbus backlog, airline capacity. Airline profitability drives aircraft orders.
- **Supply chain normalization post-pandemic**: Reshoring / friend-shoring creating domestic industrial capex (semiconductors, pharmaceuticals, battery manufacturing).
- **Backlog / book-to-bill ratio**: Industrial companies report order backlogs. A high backlog provides earnings visibility for 1-2 years.
- **Key metrics**: Book-to-bill ratio (>1 = growing backlog), revenue per employee, backlog trend, margin expansion.

### Real Estate / REITs
- **Mortgage rates**: Directly affect real estate valuations and transaction volumes. Higher mortgage rates → lower home affordability → fewer transactions → lower realtor/builder revenue.
- **Cap rates**: Net operating income / property value. Cap rates rise when rates rise → property values fall.
- **REIT sector specifics**: REITs must distribute 90% of taxable income as dividends. Their NAV and dividend sustainability matter.
  - **Mortgage REITs (mREITs)**: Highly rate-sensitive — their leverage and spread make them volatile in rate cycles.
  - **Residential REITs**: Rent growth vs. rate environment.
  - **Commercial REITs**: Office (post-COVID structural headwinds), retail (recovery), industrial (e-commerce tailwind is slowing).

---

## 10. MARKET STRUCTURE

The underlying plumbing of how markets function. Understanding market structure helps you understand why strange things happen — halts, weird price action, sudden liquidity evaporation.

### Circuit Breakers
- **What it is:** Regulatory "circuit breakers" halt trading when markets move too far too fast.
  - **Level 1 (S&P 500 ± 7% from prior close)**: 15-minute halt (or resume if recovered before 3:25pm ET)
  - **Level 2 (S&P 500 ± 13%)**: Another 15-minute halt
  - **Level 3 (S&P 500 ± 20%)**: Market-wide circuit breaker — trading stops for remainder of day
  - Individual stock limit-up/limit-down rules: Different for each stock based on average price.
- **Why it matters:** Breakers exist to prevent cascading liquidations and panic. They also create "magnet days" — traders know breakers are at specific levels and position accordingly.
- **How to track:**
  - NYSE/TNASDAQ rules (Rule 7.12)
  - Halt codes on market data terminals
  - Level 1 / Level 2 data
- **Typical reaction:**
  - **Circuit breaker triggered**: VIX explodes. Bid/ask spreads widen. After-resumption trading is often chaotic.
  - **Breaker proximity**: Traders scalp around breaker levels. Know where breakers are — they are liquidity black holes.

### Halt Codes (TSEO Halt/Resume)
- **What it is:** Trading halts on individual securities (not market-wide) triggered by news, pending news, unusual price activity.
  - **T1 (News Pending)**: Halted while news is being disseminated
  - **T2 (News Disseminated)**: News has been released; trading may resume in minutes
  - **HALT**: Security halted for operational reasons
  - **LUDP**: Volatility halt (Limit Up-Limit Down)
- **Why it matters:** Halts create "information asymmetry" — some participants know the news, others don't. When trading resumes, price often gaps significantly.
- **How to track:**
  - FINRA OTC/UTP system
  - Exchange websites
  - Bloomberg Quote Status
- **Typical reaction:**
  - **Halt + positive news**: Resume → gap up. Momentum.
  - **Halt + negative news**: Resume → gap down. Stop losses triggered.

### Dark Pools
- **What it is:** Private exchanges or off-exchange venues where institutional investors trade large blocks without pre-hedge information leaking to lit markets.
  - **Alternative Trading Systems (ATS)**: Legally operated dark pools regulated by SEC.
  - **Types**: Broker-dealer dark pools (internalization), independent dark pools (Liquidnet, BIDS), crossing networks.
  - Dark pools account for ~40-45% of US equity volume.
- **Why it matters:**
  - **Price discovery**: Trades in dark pools don't contribute to NBBO (National Best Bid/Offer) → slower price discovery.
  - **Information advantage**: Large institutional orders can be worked without moving the market.
  - **Retail vs. institutional**: Retail orders rarely reach dark pools ( Payment for Order Flow (PFOF) sends retail to market makers); institutional orders can seek dark pool execution.
  - **Toxicity**: Some dark pools have been shown to favor high-frequency traders (HFT) over institutional investors.
- **How to track:**
  - FINRA ATS volume data (weekly)
  - Dark pool activity on Bloomberg
  - Execution quality analytics
- **Note**: Dark pools are legal. They provide liquidity for institutions but reduce transparency for retail investors.

### Payment for Order Flow (PFOF)
- **What it is:** Market makers pay brokerages (Charles Schwab, Robinhood, TD Ameritrade) for the right to execute retail orders. Robinhood pioneered the model.
  - The market maker pays the brokerage for the order flow; the brokerage routes the order to the market maker; the market maker makes a small spread on the execution.
  - The customer technically gets the NBBO (or better) but the PFOF model means retail is not necessarily getting the best possible execution.
- **Why it matters:**
  - **Conflict of interest**: Broker has incentive to route to a specific market maker regardless of best execution.
  - **Retail order execution quality**: Studies show retail orders in PFOF environments execute slightly worse than they would in auction markets.
  - **SEC proposed rule changes**: PFOF has been under regulatory scrutiny. Potential bans would reshape retail execution.
  - **Internalization**: Most PFOF orders are internalized (never touch the lit exchanges), removing retail from exchange price discovery.

### Market Maker Behavior
- **What it is:** Registered market makers (NYSE designated market makers, Nasdaq market makers) maintain bid/ask spreads and provide liquidity. Their hedging activities drive intraday price movements.
  - **Role**: Post both bid and offer, profit on the spread, and hedge their exposure via futures, ETFs, or correlated securities.
  - **MM delta hedging**: When options market makers sell options, they delta-hedge by trading the underlying. This creates systematic buying/selling pressure that can dominate intraday stock moves.
- **Why it matters:**
  - **Intraday volatility**: MM hedging amplifies large single orders into systematic buying/selling across correlated securities.
  - **Quote fade**: MMs will "fade" (not fill) large orders at the NBBO, widening spreads when information has leaked.
  - **Poison calls**: Requests for information about large order size to gauge market depth.
- **How to track:**
  - Level 2 order book
  - Time & sales data
  - Dark pool prints (institutional block prints show up after market close)
  - Short sale restrictions and locate availability (CTB = cost to borrow)

---

## 11. SEASONALITY

Markets have recurring patterns tied to calendar events, fiscal years, and behavioral cycles. These aren't guarantees — they're tendencies.

### Earnings Season (Quarterly)
- **What it is:** Most US companies report earnings on a quarterly calendar aligned with fiscal quarters ending ~December, March, June, September.
  - **Q4 reporting season**: January–February (largest, most market-moving)
  - **Q1**: April–May
  - **Q2**: July–August (smallest)
  - **Q3**: October–November
- **Why it matters:**
  - Earnings season creates the highest volatility period in the calendar. Individual stocks gap up/down 10-30% on reports.
  - Analysts revise estimates before and after the season — the revision trend (upgrades vs. downgrades) matters.
  - Market expectations (forward EPS) vs. actual results drives multiple re-rating.
- **How to track:**
  - Yahoo Finance Earnings Calendar
  - Earnings Whispers (consensus + whisper number)
  - Bloomberg Earnings Calendar
- **Typical reaction:**
  - **Good season overall**: Market rallies. Earnings growth validates valuations. Risk appetite expands.
  - **Bad season**: Market corrects. Multiple compression. Defensive sectors outperform.
  - **Forward guidance** from companies shapes QQQ direction more than the reported results.

### Tax Season (US)
- **What it is:** The US tax filing deadline is April 15. The period January–April has distinct characteristics.
  - **January**: Tax-loss selling wound up. Capital loss carryforwards reset. New money flows into markets.
  - **February–April**: Tax payments drain cash from some investors. Refunds inject cash back.
  - **Capital gains distributions**: Mutual funds distribute realized capital gains in October–December.
- **Why it matters:**
  - **Tax-loss selling**: December — investors sell stocks at a loss to offset gains. This creates December bottoms and January rebounds.
  - **Year-end distribution**: Mutual funds distributing capital gains in November–December — shareholders of funds who don't want to pay the tax sell their fund shares before the distribution date.
  - **Wash sale rule**: Investors cannot buy substantially identical securities 30 days before or after a sale at a loss. This creates artificial supply/demand patterns around December 31.

### Year-End Window Dressing
- **What it is:** Portfolio managers, at year-end, buy stocks that make their portfolio look good (high performers) and trim stocks that hurt performance attribution.
  - **"Window dressing"**: Buying stocks that outperformed in the year to show high weight in winners.
  - **"Best foot forward"**: Selling laggards so year-end report shows only strong positions.
  - Happens most aggressively in the last 2 weeks of December.
- **Why it matters:** Creates artificial buying pressure in high-performing stocks and selling pressure in laggards in late December. This can create profitable entry points in January when the artificial pressure lifts.
- **How to track:**
  - December ETF flows vs. other months
  - Small-cap vs. large-cap relative performance in late December
  - Laggard sector performance in December
- **Typical reaction:**
  - **Late December**: High-performing stocks get one more boost. Laggards underperform.
  - **January**: Reversal. Lagging stocks recover. Window dressing unwind begins.

### Sector Rotation by Month / Quarter
- **What it is:** Historical patterns show certain sectors perform better in certain months or quarters.
  - **January Effect**: Small-caps historically outperform in January. IPO activity resumes.
  - **February**: After January seasonality, market often consolidates.
  - **March**: Quarter-end rebalancing. Fiscal year-end for many countries.
  - **April**: Earnings season begins (Q4 results). Tax deadline effect fades.
  - **Q1**: Strongest quarter historically for equities (January–March).
  - **Q2**: Historically weakest for bonds. Strong for energy (pre-summer driving season).
  - **Summer (June–August)**: Historically weaker for equities. "Sell in May" strategy. Vacation season → lower volume, potentially more volatile.
  - **Fall**: Sector rotation. Back-to-school shopping (retail). Q3 earnings season (October–November).
  - **November–December**: Best months historically for equities. Santa Claus rally (last 2 weeks December). Strong Q4 seasonal tendency.
- **Why it matters:** Seasonality is a probabilistic framework, not a rule. It works most consistently on large-cap indices, less on individual stocks. The calendar is a tool, not a prediction engine.
- **How to track:**
  - "Sell in May" research (Halloween effect)
  - StockCharts.com monthly sector performance charts
  - Bespoke Investment Group seasonal charts
- **Typical reaction:**
  - **Historical pattern vs. current macro**: If macro conflicts with seasonality, seasonality loses. But knowing the tendency helps you set expectations and position sizing.
  - **Options expiration weeks**: Third Friday of each month (OPEX) creates intraday volatility around 4pm ET. Large put/call expiries create pin risk.

---

## 12. BLACK SWAN / TAIL RISK FACTORS

Tail risks are low-probability, high-impact events that can wipe out portfolios or trigger systemic crises. They are, by definition, difficult to predict — but their mechanics can be understood.

### What is a Black Swan?
- **Nassim Taleb's definition**: An event that is outlier (beyond normal expectations), has extreme impact, and is explainable only after the fact.
- Examples: 1987 crash (-22% in one day), 9/11, 2008 GFC, COVID-19 crash ( fastest bear market in history: -34% in 33 days, Feb-Mar 2020).

### Key Tail Risk Categories

#### Financial System Failures
- **What it is:** Systemically important institutions (SIFIs: JPMorgan, Goldman, BofA, Wells Fargo, etc.) failing or needing emergency bailouts.
- **Trigger**: Excessive leverage, concentrated toxic assets, liquidity crisis, runs on deposits.
- **Why it matters:** Too big to fail. Government backstops prevent domino effects but can cause moral hazard.
- **How to track:**
  - CDS spreads (credit default swaps) on major banks
  - SOFR (Secured Overnight Financing Rate) — spikes signal funding stress
  - Overnight repo market rates (Fed's Reverse Repo facility usage)
  - TED spread (3M LIBOR - 3M T-bill yield)
- **Typical reaction**: Risk-off shock. Financials crash. Fed出手 (intervention). Flight to safety (bonds, gold).

#### Pandemic / Public Health Crisis
- **What it is:** Global health event causing supply chain collapse, consumer pullback, mass mortality, and government-imposed restrictions.
- **COVID-19 example**: Global supply chains froze. Oil demand collapsed. Travel, leisure, retail crushed. Technology surged. Government stimulus created inflationary excess.
- **Why it matters:** Creates simultaneous supply and demand shock. Cannot be hedged with normal diversification.
- **How to track:**
  - WHO pandemic declarations
  - Global mobility data (Google, Apple)
  - PMI (Purchasing Managers' Index) — collapses in lockdowns
  - Equity sector performance (growth vs. value vs. cyclical)
- **Typical reaction**: Sharp initial crash (20-40%). Government/monetary stimulus counter. Asymmetric recovery based on digital adoption.

#### Geopolitical Black Swans
- **Taiwan conflict**: TSMC produces ~90% of advanced logic chips. A conflict scenario would create a global technology supply collapse — an existential risk for the global economy.
- **Nuclear escalation**: Any use of nuclear weapons would trigger extreme risk-off. Unprecedented. Uninsurable.
- **Suez Canal / Strait of Hormuz closure**: Chokepoints for global trade. Oil price spike + global trade disruption.
- **Cyberattack on financial infrastructure**: Attacks on SWIFT, DTCC, major exchanges or prime brokers. Market closure risk.
- **How to track:**
  - Geopolitical risk indices
  - Defense spending trends
  - Intelligence community public statements
  - Open-source intelligence (OSINT) monitoring

#### Climate / Natural Disaster Tail Risks
- **What it is:** Catastrophic climate events (hurricanes, floods, wildfires) or long-term climate tipping points.
- **Hurricane Katrina (2005)**: Oil spiked, regional GDP impact.
- **Texas freeze (2021)**: Electricity grid failure → chemical plant shutdowns → global resin shortage → packaging industry crisis.
- **Climate transition tail risk**: Sudden carbon tax or regulation → stranded assets for fossil fuel companies. Conversely: sudden policy reversal → stranded assets for green energy.
- **How to track:**
  - Catastrophe bond spreads
  - NOAA weather event tracking
  - Climate risk regulatory frameworks (SEC climate disclosure rules)
  - Swiss Re catastrophe loss data

#### Commodity Super-Cycle Spikes
- **What it is:** Sudden, sharp spikes in critical commodities (oil, natural gas, copper, food inputs) caused by supply disruptions or demand surges.
- **Oil embargo analogy (1973)**: Oil prices 4x in weeks. Stagflation. Bear market lasted years.
- **Why it matters:** Commodity price spikes create inflation, compress corporate margins, reduce consumer purchasing power, and force central banks to tighten even in the face of economic weakness.
- **How to track:**
  - Commodity super-cycle indicators
  - Copper (the " Dr. Copper" metal — tracks global growth)
  - Baltic Dry Index (shipping rates = global trade demand)
  - UN Food Price Index

#### Monetary System Crises
- **What it is:** A crisis of confidence in the US dollar as reserve currency, rapid de-dollarization, or loss of Treasury market functioning.
- **Why it matters:** US dollar dominance means the US can run persistent trade deficits and borrow in its own currency. If this changes: sudden stop, sharply higher US borrowing costs, inflationary spiral.
- **Trigger scenarios**: Sustained high fiscal deficits + debt ceiling crises + foreign central bank reserve diversification.
- **How to track:**
  - DXY (dollar index) long-term trend
  - US sovereign credit default swap (CDS)
  - Share of global central bank reserves held in USD (IMF COFER data)
  - Treasury auction bid-to-cover ratios

#### AI / Technology Systemic Risk (Emerging)
- **What it is:** AI-driven flash crashes, coordinated AI trading algorithm failures, or AI-enabled financial fraud at scale.
- **Flash crash scenario**: Multiple AI trading systems hit the same correlated stop-loss levels simultaneously → cascade selling → market microstructure fails.
- **How to track:**
  - Market volatility clustering (unusual correlated moves across unrelated securities)
  - Circuit breaker triggered outside normal macro events
  - SEC/FINRA pattern analysis for algorithmic trading anomalies

### How to Think About Tail Risk
- **Diversification**: Tail risks are often correlated — everything sells off simultaneously. Classic diversification helps less than expected in tail events.
- **Tail hedging**: Options (buying puts) are the most common hedge. OTM puts on SPY/QQQ are expensive but effective.
- **VIX**: Spikes to 30-80+ in crashes. VIX products (VXX, UVXY) allow betting on volatility, but decay is severe — these are not buy-and-hold instruments.
- **Cash as a hedge**: In black swan crashes, cash is the only truly uncorrelated asset at the moment of maximum fear.
- **Rules-based selling**: Stop-losses prevent catastrophic losses. Emotional holding through crashes amplifies losses.
- **Position sizing**: Small positions in many high-conviction ideas is safer than few large positions. Black swan risk is fundamentally about position concentration.

---

## HOW TO USE THIS PLAYBOOK

### Quick Reference by Situation

| Situation | What to Check |
|---|---|
| Macro uncertainty | Fed policy, CPI, Jobs Report, Treasury yields, DXY |
| Stock-specific decision | EPS vs. guidance, balance sheet, FCF, institutional holdings |
| Sector rotation | Rate environment, yield curve shape, sector ETF relative performance |
| Entry/exit timing | Support/resistance, RSI, MACD, volume confirmation |
| Sentiment gauge | Fear/Greed Index, Put/Call ratio, social media volume |
| Options-based signal | ITM/OTM skew, OI by strike, unusual options flow, GEX |
| Institutional follow | 13F filings, insider transactions, ETF flows, index inclusions |
| Geopolitical event | Oil price, gold, VIX, dollar, sector-specific impact analysis |
| Timing | Seasonality, earnings calendar, rebalancing schedule |

### Key Data Sources
- **FRED (St. Louis Fed)**: Free economic data — rates, yields, money supply, CPI, GDP, employment
- **BLS.gov**: Jobs Report, CPI, PPI
- **SEC EDGAR**: 10-K, 10-Q, 13F, Form 4
- **NYSE/NASDAQ**: Short interest data, halt codes
- **CBOE**: VIX, put/call ratios, open interest
- **BEA.gov**: GDP data
- **EIA.gov**: Weekly petroleum inventories (Wednesday)
- **Bespoke Investment Group**: Rotational charts, seasonal analysis
- **WhaleWisdom.com**: Parsed 13F filings
- **OpenInsider.com**: Insider trading
- **UnusualWhales.com**: Options flow data
- **FinViz.com**: Screening tools (free tier useful)
- **SqueezeMetrics / GEX**: Gamma exposure data
- **PredictIt / Polymarket**: Election/ geopolitical probability markets
- **Investopedia**: General financial education
- **CNN Fear & Greed Index**: Free sentiment gauge

### The Mental Model
> **Everything is a signal. Everything interacts. Markets are adaptive.**

The mistake most beginners make is treating these drivers as a checklist. In reality:
1. **Multiple factors move prices simultaneously** — a stock can beat earnings but fall because macro killed the sector.
2. **Signals conflict** — strong technical setup + terrible macro = macro wins. Understand which forces dominate in which timeframes.
3. **Markets are adaptive** — once a signal is widely known, it gets priced in quickly. The edge comes from: (a) understanding something before the crowd, or (b) understanding the interaction effects better than others.
4. **Timeframes matter** — macro sets the direction for months; fundamentals drive quarters; technicals dominate days and intraday; news flows move hours.

The goal is not to track everything. It's to know which category dominates at which time horizon, and have a framework for integrating signals when they conflict.

---

*Last updated: 2026-04-04. Built by Sig Botti 🤖 for the Louch.*
