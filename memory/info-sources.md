# Info Sources — Sig Botti 🦊

Curated RSS feeds, APIs, and data sources beyond what's already in `scanner/news_sources.py`.

**Already running in scanner:**
- Finviz, Benzinga, StockTwits, Google News RSS, Reddit WSB, Seeking Alpha (all via `news_sources.py`)
- Yahoo Finance news via yfinance (in `news_scanner.py`)

---

## AI/ML News

### [Hugging Face Blog](https://huggingface.co/blog/feed.xml)
- What: Official blog feed for the leading open-source ML platform — model releases, research, industry deployments
- Update frequency: Weekly (varies)
- Quality: 5/5
- Already in blogwatcher: no

### [arXiv cs.AI](https://export.arxiv.org/rss/cs.AI)
- What: Pre-print papers on artificial intelligence — cutting-edge research before peer review
- Update frequency: Daily (papers posted as submitted)
- Quality: 5/5
- Already in blogwatcher: no

### [AI News (artificialintelligence-news.com)](https://www.artificialintelligence-news.com/feed/)
- What: Aggregated daily AI news — covers OpenAI, Google DeepMind, Anthropic, policy, tools, and industry moves
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

### [The Verge AI](https://www.theverge.com/rss/ai-artificial-intelligence/index.xml)
- What: The Verge's AI section — accessible, mainstream coverage of AI products, regulation, and companies
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

### [VentureBeat AI](https://venturebeat.com/ai/feed/)
- What: In-depth coverage of enterprise AI, startups, and research breakthroughs
- Update frequency: Multiple times per week
- Quality: 4/5
- Already in blogwatcher: no

### [MIT Technology Review — AI](https://www.technologyreview.com/feed/)
- What: Longer-form investigative pieces on AI — policy, ethics, research, societal impact
- Update frequency: Weekly
- Quality: 5/5
- Already in blogwatcher: no

---

## Stock Market / Trading Signals

### [Alpha Vantage API](https://www.alphavantage.co/)
- What: Free REST API for real-time stock quotes, intraday data, forex, crypto, and technical indicators (SMA, RSI, MACD). Free tier: 25 requests/day, 5 req/min.
- Update frequency: Real-time (delay varies by tier)
- Quality: 4/5
- Already in blogwatcher: no

### [FRED (Federal Reserve Economic Data)](https://fred.stlouisfed.org/docs/api/fred/)
- What: Massive free economic dataset — interest rates, GDP, CPI, unemployment, housing starts, consumer sentiment. Great for macro signals.
- Update frequency: Varies by series (daily to monthly)
- Quality: 5/5
- Already in blogwatcher: no

### [Trading Economics](https://tradingeconomics.com/rss/news.aspx)
- What: Real-time economic indicators + market data — currencies, commodities, bonds, global indices
- Update frequency: Real-time
- Quality: 4/5
- Already in blogwatcher: no

### [Investopedia Market Dictionary RSS](https://www.investopedia.com/feedbuilder/feed/getfeed?feedId=rss2&format=txt)
- What: Educational financial content + market news — good for signals explained with context
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

### [MarketWatch Markets RSS](https://feeds.marketwatch.com/marketwatch/topstories/)
- What: Broad market coverage — breaking news, movers, analyst upgrades/downgrades
- Update frequency: Multiple times per day
- Quality: 4/5
- Already in blogwatcher: no

---

## Real Estate Market Data

### [Zillow Research Data](https://www.zillow.com/research/data/)
- What: Free downloadable datasets — home values, rents, inventory, prices by metro area. Philadelphia metro included.
- Update frequency: Monthly
- Quality: 5/5
- Already in blogwatcher: no

### [NAR (National Association of Realtors) Research](https://www.nar.realtor/research-and-statistics)
- What: Industry-defining statistics — existing home sales, pending sales, affordability indices, regional reports
- Update frequency: Monthly
- Quality: 5/5
- Already in blogwatcher: no

### [CoreLogic Home Price Index](https://www.corelogic.com/data-download.jsp)
- What: Loan-level property data + HPI — the most granular home price data in the industry
- Update frequency: Monthly
- Quality: 5/5
- Already in blogwatcher: no

### [Redfin Data Center](https://www.redfin.com/news/data-center/)
- What: Weekly housing market reports — median prices, sales volume, days on market by city/region
- Update frequency: Weekly
- Quality: 4/5
- Already in blogwatcher: no

### [Philadelphia Real Estate Journal (Philadelphia Business Journal)](https://www.bizjournals.com/philadelphia/real_estate/real_estate_news.rss)
- What: Local commercial and residential RE deals, development projects, CRE transactions in Philly region
- Update frequency: Weekly
- Quality: 4/5
- Already in blogwatcher: no

### [PlanPhilly](https://planphilly.com/rss.xml)
- What: Urban planning and development news for Philadelphia — zoning, development projects, city planning decisions
- Update frequency: Weekly
- Quality: 4/5
- Already in blogwatcher: no

---

## Philadelphia Local News

### [WHYY RSS](https://whyy.org/feed/)
- What: Philadelphia's public radio station — local politics, community, arts, education, breaking news
- Update frequency: Multiple times per day
- Quality: 5/5
- Already in blogwatcher: no

### [Billy Penn (Block Club Philadelphia)](https://billypenn.com/feed/)
- What: Nonprofit local Philly news — hyperlocal city hall, neighborhoods, housing, criminal justice
- Update frequency: Daily
- Quality: 5/5
- Already in blogwatcher: no

### [Philadelphia Inquirer — RSS](https://www.inquirer.com/phillynews/rss.xml)
- What: Philadelphia's main newspaper — breaking news, sports, business, local events
- Update frequency: Multiple times per day
- Quality: 4/5
- Already in blogwatcher: no

### [Philly.com RSS](https://www.philly.com/rss/)
- What: Front page of Philadelphia's major news — free tier, good for local market sentiment
- Update frequency: Multiple times per day
- Quality: 4/5
- Already in blogwatcher: no

### [Philadelphia Business Journal](https://www.bizjournals.com/philadelphia/rss.xml)
- What: Philly business and real estate deals — startups, M&A, commercial RE, tech scene
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

---

## Tech / Programming Feeds

### [Hacker News RSS](https://news.ycombinator.com/rss)
- What: The single best aggregator for startup/tech/engineering culture — ranked by reader votes, signals what the dev world cares about
- Update frequency: Multiple times per day
- Quality: 5/5
- Already in blogwatcher: no

### [GitHub Trending](https://github.com/trending.atom)
- What: Atom feed of repos gaining traction — shows what tools/languages/frameworks are hot right now
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

### [Lobsters](https://lobste.rs/rss)
- What: Like HN but smaller, more focused on technology and programming — less noise, higher signal
- Update frequency: Multiple times per day
- Quality: 5/5
- Already in blogwatcher: no

### [TechCrunch](https://techcrunch.com/feed/)
- What: Startup and tech industry news — funding rounds, product launches, big company moves
- Update frequency: Multiple times per day
- Quality: 4/5
- Already in blogwatcher: no

### [Dev.to RSS](https://dev.to/feed)
- What: Community blog for developers — tutorials, career advice, tool discussions, open source
- Update frequency: Multiple times per day
- Quality: 4/5
- Already in blogwatcher: no

### [The Register (tech news)](https://www.theregister.com/feeds/rss/)
- What: Enterprise tech news with a skeptical British tone — security, hardware, software, cloud. Good for systems-level news.
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

### [Product Hunt RSS](https://www.producthunt.com/feed)
- What: Daily new product launches — tracks what tools are launching and getting traction
- Update frequency: Daily
- Quality: 4/5
- Already in blogwatcher: no

---

*Last updated: 2026-04-11 by Sig Botti subagent*
