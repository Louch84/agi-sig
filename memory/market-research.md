# Market Research: Crashes, Cycles & Options Playbook

_Captured 2026-04-14 — Post-LCID lesson. For Lou's options trading._

---

## 1. Historical Crash Patterns

### The 5 Major Crashes

| Crash | Decline | Duration | Recovery | Speed |
|-------|---------|----------|---------|-------|
| 1929 Great Depression | -86% DJIA | 2.5 yrs | 25 years | Slow build → fast fall |
| 1987 Black Monday | -22.6% DJIA (1 day) | 2 days | 2 years | Instant |
| 2000 Dot-com | -78% Nasdaq | 2.5 yrs | 15 years | Slow burn |
| 2008 Financial Crisis | -57% S&P 500 | 17 months | 4-7 years | Fast fall |
| 2020 COVID | -34% S&P 500 | 23 days | 5 months | Fastest ever |

### The 2020 COVID Lesson (Most Relevant for Options)
- **Fastest crash ever**: 34% in 23 trading days
- **Fastest recovery ever**: All losses recovered in 5 months
- **Key insight**: Crashes caused by external shocks (not fundamental collapse) recover fast
- **VIX spiked to 82** — highest since 2008
- **Fed intervention + fiscal stimulus = explosive rebound**

### 1987 Black Monday (Most Relevant for Options Volatility)
- **22.6% in ONE DAY** — no fundamentals changed, purely technical cascade
- **Portfolio insurance** (automated selling) amplified the drop
- **Recovery in 2 years** despite the severity
- **Lesson**: IV explodes during crashes. Puts become extremely expensive but squeeze buyers out

### 2008 Volkswagen Squeeze (Most Relevant for Short Squeezes)
- **VW briefly became most valuable company in the world** (over $1T)
- Porsche announced it controlled 74% of VW float
- Short sellers were caught with 12.8% of float short — **20x available shares**
- **Price went from €210 to €1000 in 2 days**
- Short squeeze lesson: when short interest EXCEEDS available float, price can go infinite

### 2021 GameStop Squeeze (Most Relevant for Retail Squeeze Plays)
- SI was **140% of float** (shorters borrowing shares to short)
- Ryan Cohen / WSB turned it into a movement
- Price went from **$4 to $483 in 2 weeks**
- **Key metric for squeeze**: short interest + days-to-cover + cost-to-borrow
- **Options gamma squeeze**: Market makers hedged calls, creating buying pressure that drove price further up
- Robinhood restricted buying → SEC hearing → congressional testimony
- **Key lesson**: Retail coordination + high SI + options gamma = explosive squeeze

---

## 2. Short Squeeze Anatomy

### Requirements for a Squeeze:
1. **High SI** (>20% of float)
2. **Days to cover** (>5 days = hard to borrow)
3. **Cost to borrow** (high % = supply constrained)
4. **Catalyst** (news, earnings, WSB, or fundamental change)
5. **Available float** (when SI > float, squeeze magnifies)

### VW vs GME vs AMC:

| Factor | VW (2008) | GME (2021) | AMC (2021) |
|--------|-----------|-------------|-------------|
| Peak SI | 12.8% | 140% of float | 20% |
| Days to Cover | 4.4 | 15+ | 10+ |
| Float | Small (不足) | Very small | Moderate |
| Catalyst | Porsche takeover | Ryan Cohen + WSB | WSB + theater squeeze |
| Price move | +400% | +12,000% | +700% |
| Duration | 2 days | 2 weeks | Months |

---

## 3. Market Cycle Seasonality

### Monthly Patterns (Historical S&P 500):

| Month | Historical Return | Notes |
|-------|-----------------|-------|
| **January** | +1.0% avg | "First 5 days" predictor. New money flows. |
| **April** | +1.5% avg | Tax season — historically bullish |
| **May** | -0.5% avg | "Sell in May" — worst month historically |
| **October** | -0.3% avg | Crash month historically (1929, 1987) |
| **November** | +1.3% avg | Strongest months after October crash |
| **December** | +1.4% avg | Holiday rally, window dressing |

### Sell in May Effect:
- Historical data: November through April outperforms May through October
- **Implication**: Put spreads or bearish positions May-October
- **Long premium positions**: November through April

### Presidential Cycle:
- **Year 1-2**: Usually weakest (transition, midterm policies)
- **Year 3**: Usually strongest (pre-election year, fiscal injection)
- **Year 4**: Mixed, volatile (election uncertainty)
- 2026 = Year 2 of Trump presidency → historically weaker regime

### Options Implications:
- **Q4 earnings season** (Oct-Feb): Highest IV, best for selling premium
- **Earnings months**: Jan, Apr, Jul, Oct → IV crush after
- **Pre-election years (2024)**: More volatile. Post-election year (2025-2026) more stable

---

## 4. Options Strategies by Regime

### Regime 1: Bullish / Squeeze Play

**When to use**: RSI <40, gap up + high SI, short squeeze building

**Strategies**:
- **Buy OTM calls** (higher risk/reward for squeezes)
- **Buy call spreads** (reduce cost, define max loss)
- **Avoid**: Selling premium during squeeze

**LCID lesson**: RSI 71 = overbought = squeeze had no fuel. Entry must be RSI < 60 ideally < 50.

### Regime 2: Bearish / Crash Hedge

**When to use**: VIX >30, market-wide fear, economic shock

**Strategies**:
- **Buy puts** (direct but expensive at high IV)
- **Buy put spreads** (cheaper, defined risk)
- **Buy VIX calls** (when you expect volatility to spike further)
- **Sell call spreads** (if bearish AND IV is elevated)

**Lesson from 2020**: When VIX spikes above 40, put buying is expensive but protective.

### Regime 3: High Vol / Range Bound

**When to use**: VIX 20-30, no clear direction, choppy market

**Strategies**:
- **Iron condors** (short premium, sell both sides)
- **Straddles / strangles** (if expecting breakout)
- **Sell premium** when IV is high (over 30)

### Regime 4: Low Vol / Bullish

**When to use**: VIX <15, RSI < 40, steady uptrend

**Strategies**:
- **Buy calls** (cheap when IV is low)
- **Sell puts** (collect premium in uptrend)
- **Debit spreads** (cost-effective directional bets)

---

## 5. Key Indicators for Reading Market Regime

### Volume Indicators
- **On-Balance Volume (OBV)**: Rising = accumulation, falling = distribution
- **VWAP**: Price above VWAP = bullish, below = bearish
- **Volume surge + RSI divergence** = potential reversal

### Volatility Indicators
- **VIX > 40**: Crash/fear regime — don't sell premium
- **VIX 20-30**: Normal chop — iron condors work
- **VIX < 15**: Complacent — buy calls cheap, sell puts

### Breadth Indicators  
- **Advance/Decline Line**: Breadth diverging from price = warning
- **New Highs/Lows**: Market making lower highs while price makes new highs = divergence

### RSI (14) Reference:
- **< 30**: Oversold — squeeze setup
- **40-50**: Neutral / early accumulation
- **50-60**: Healthy uptrend
- **> 70**: Overbought — squeeze has less fuel
- **> 80**: Extreme — mean reversion likely

### Short Interest Metrics:
- **SI > 20%**: Elevated — squeeze possible
- **SI > 40%**: Extreme — squeeze likely with catalyst
- **Days to Cover > 5**: Short sellers are trapped, forced covering = buying
- **Cost to Borrow > 50%**: Supply constrained, squeeze imminent

---

## 6. Practical Lessons for Lou's Trading

### What the LCID Trade Taught Us:
1. **RSI 71 at scan time** = scanner was correct to flag it but WE missed the overbought signal
2. **Gap-fill detection** = gap was already fading by the time alert fired
3. **SI 41.8% was real** but needed RSI < 60 to be a squeeze play

### Updated Scanner Rules (APPLIED 2026-04-14):
- RSI > 60 → penalty -15
- RSI > 70 → penalty -25
- Gap > 25% filled → penalty -10
- Gap > 50% filled → penalty -20
- **Best squeeze setups**: gap >5% + SI >15% + RSI < 50

### Crash Playbook:
1. **If market drops 10% in a week**: VIX will spike. Buy put spreads or VIX calls
2. **If VIX > 50**: Don't sell premium. Buy protection.
3. **If VIX > 80** (2020 levels): Historically a buying opportunity within weeks
4. **Post-crash recovery**: Fastest when caused by external shock (COVID) vs fundamental crisis (2008)

### Short Squeeze Playbook:
1. **SI > 20% + RSI < 50 + gap up** = squeeze setup
2. **Days to cover > 5** = trapped shorts
3. **Check cost-to-borrow** before entry (above 50% = squeeze imminent)
4. **Options gamma**: When OI on calls is high, market makers hedge by buying stock = self-reinforcing rise
5. **Exit when**: RSI crosses 80 (momentum reversal), gap-fill starts, or SI starts declining

### Seasonal Timing:
- **Best months for bullish options**: November through April
- **Best months for selling premium**: May through October (Sell in May effect)
- **Earnings season plays**: Buy straddles 2 weeks before, sell after
- **October = danger month**: Historically most crash-prone. Protective puts around Halloween.

---

## 7. What's Different About 2026

**Current regime (April 2026)**:
- S&P 500 in year 2 of Trump presidency → historically weaker
- Tariff uncertainty → elevated VIX
- AI sector froth → potential for sector rotation
- No clear crash on horizon but elevated uncertainty

**Watch for**:
- VIX spiking above 30 = fear regime
- Credit spreads widening = stress signal
- TINA trade ending = rotation out of stocks

---

_Last updated: 2026-04-14_
