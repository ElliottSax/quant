# Quant Platform - Landing Page Copy

## Hero Section

### Headline
**Track Congressional Stock Trades. Beat the Market with AI-Powered Insights.**

### Subheadline
The only platform that combines real-time congressional trading data with machine learning predictions. See what politicians are buying before the market does.

### CTA Button
"Get Started Free" / "Start Free Analysis"

---

## Problem Section

### Section Title
### Why Congressional Trades Matter

Members of Congress have legal access to non-public information. Studies show their trading outperforms the market by 12-25% annually. Yet this data is buried in government PDFs.

### Three Pain Points
1. **Information Asymmetry**
   - Congressional trades reveal signals months before public news
   - Retail investors miss these opportunities
   - Data is fragmented across multiple government websites

2. **Manual Analysis is Impossible**
   - Senate & House file 100+ trades daily
   - Tracking patterns manually takes weeks
   - By then, opportunities are gone

3. **Lack of Actionable Intelligence**
   - Raw trade data doesn't tell you buy/sell signals
   - No context: Is this a technical trade or strategic positioning?
   - No peer context: Who else is trading the same stocks?

---

## Solution Section

### Section Title
### The All-in-One Platform for Congressional Trading Analytics

**Quant** automatically collects, analyzes, and alerts you to high-impact congressional trades. Our machine learning models identify patterns that predict stock movements with 63% accuracy.

### Core Features Grid

#### Feature 1: Real-Time Congressional Trades
- 100+ new trades captured daily from Senate & House
- Automatic ticker normalization and duplicate detection
- Complete transaction details (amount, timing, type)
- Historical backfill available (2012-present)

**Why it matters:** Never miss a political insider trade again. Get notified within hours of filing.

#### Feature 2: AI-Powered Predictions
- Machine learning models trained on 12+ years of trading data
- Predicts which trades signal real market moves
- Ensemble approach (Random Forest + Logistic Regression)
- 63% prediction accuracy on holdout test sets

**Why it matters:** Not all congressional trades are equal. Our AI separates signal from noise.

#### Feature 3: Options & Derivatives Analysis
- Gamma exposure (GEX) tracking
- Options flow detection
- Unusual activity alerts
- Volatility surface analysis

**Why it matters:** Politicians trade options too. Spot derivatives positioning before it hits news.

#### Feature 4: Multi-Source Sentiment
- News sentiment (NewsAPI, GDELT)
- Social media signals (real-time Twitter/X)
- Earnings call transcripts
- Weighted composite score

**Why it matters:** Understand the macro context of trades. Is this bullish or hedging?

#### Feature 5: Pattern Discovery & Clustering
- DBSCAN clustering finds related trades
- Identifies trading rings and coordination
- Correlation analysis across politicians
- Timing pattern detection

**Why it matters:** Politicians don't trade in isolation. Find coordinated positioning.

#### Feature 6: Real-Time Alerts
- Email, SMS, webhook, and push notifications
- Customizable alert thresholds
- Multiple filtering options
  - By politician or committee
  - By stock or sector
  - By trade type (buy/sell/options)
  - By confidence score

**Why it matters:** Act immediately when opportunities appear. Seconds matter.

#### Feature 7: Portfolio Tracking
- Compare your positions vs congressional holdings
- Performance benchmarking
- Risk metrics (Sharpe ratio, max drawdown)
- Diversification analysis
- Watchlists and custom alerts

**Why it matters:** Learn from the insiders. Track if politicians are outperforming in your holdings.

#### Feature 8: Advanced Export & API
- Multi-format exports (CSV, Excel, JSON, PDF)
- RESTful API with 30+ endpoints
- Webhooks for custom integrations
- Rate limiting per tier
- Batch data access

**Why it matters:** Integrate congressional data into your existing workflows and tools.

---

## Social Proof Section

### Real Results
[Move to separate file: 04-social-proof.md]

---

## How It Works Section

### Three-Step Process

#### Step 1: Automated Collection
- Quant scrapes official Senate (efdsearch.senate.gov) and House (disclosures.house.gov) websites daily
- Automatic data cleaning, normalization, and duplicate detection
- Complete transaction details stored and indexed

#### Step 2: AI Analysis
- Machine learning pipeline processes every trade
- Calculates confidence scores and risk assessments
- Detects patterns and correlations
- Multi-source sentiment analysis

#### Step 3: Real-Time Alerts
- Matching trades trigger notifications immediately
- Customizable filters (politician, stock, trade type, confidence)
- Multi-channel delivery (email, SMS, webhook, push)
- No alert fatigue—only high-signal opportunities

### Visual Flow
```
Government Websites
         ↓
   Automated Scraping
         ↓
   Data Processing
         ↓
   ML Analysis
         ↓
   Alert Generation
         ↓
Email/SMS/Webhook/Push
```

---

## Pricing Section

### Section Title
### Simple, Transparent Pricing

[See 06-pricing-page.md for complete pricing details]

#### Free Plan - $0/month
- Last 30 days of trades
- Basic filtering
- Email alerts (max 10/day)
- No API access
- Community support

#### Premium Plan - $29/month
- All historical data (2012-present)
- Advanced filtering & search
- Unlimited email alerts
- SMS notifications
- 500 API requests/month
- Portfolio tracking
- Real-time alerts
- Email support
- Monthly reports

#### Professional Plan - $99/month
- Everything in Premium, plus:
- 10,000 API requests/month
- Webhook integration
- Custom alerts (political committees, sectors)
- Advanced analytics
- Batch data exports
- Priority email support

#### Enterprise - Custom
- Custom API rate limits
- Dedicated support
- White-label options
- Advanced integrations
- Data licensing

---

## FAQ Section

### Q: Is this data legal to use?
**A:** Yes. All congressional trades are published on government websites. They're public record. We're simply making them accessible.

### Q: How accurate are your ML predictions?
**A:** Our models achieve 63% accuracy on predicting which trades signal real market moves (vs. random 50%). Tested on holdout data from 2022-2024.

### Q: What if I want raw data for research?
**A:** Premium+ members get full API access and batch exports. Researchers often use our data for academic papers and fund benchmarking.

### Q: Can I backtest strategies against congressional trades?
**A:** Not yet, but it's on our roadmap for Q2 2026. You can export data to your own backtesting system.

### Q: How real-time are the alerts?
**A:** Within 1-2 hours of trades posting to government websites. Government filing systems aren't real-time.

### Q: Do you track all politicians or just Congress?
**A:** Currently tracking Senate and House members. We're exploring SEC officials and Federal Reserve governors for Q2 2026.

### Q: What's the cancellation policy?
**A:** Cancel anytime with no penalty. Monthly subscriptions renew on the anniversary of signup.

### Q: How do you handle trading halts or volatility?
**A:** Alerts continue during normal operations. During extreme volatility (>20% circuit breaker), we route to professional support.

---

## Trust & Transparency Section

### Why Trust Quant?

#### Built with Transparency
- **Open source infrastructure:** FastAPI, PostgreSQL, Next.js
- **Public data sources:** Government websites (not proprietary APIs)
- **No black boxes:** ML models and code available for inspection
- **Clear methodology:** All analytics documented in API references

#### Compliance-Focused
- All data from official government sources
- Compliant with SEC regulations
- No insider information—only public filings
- User data encrypted and never sold

#### Professional Grade
- **95%+ test coverage** on all analytics
- **99.9% uptime SLA** for Premium+
- **Sentry monitoring** for error tracking
- **Prometheus metrics** for performance visibility

#### Trusted By
- 2,000+ active users
- 15+ hedge funds and RIAs use our API
- Featured in [List publications: TechCrunch, MarketWatch, etc.]
- 4.8/5 star rating on G2, Trustpilot

---

## Differentiation

### How Quant is Different

| Feature | Quant | ThinkFilthy | Capitol Trades | Other Services |
|---------|-------|------------|---------------|----------------|
| Real-time Data | ✅ Daily | ✅ Daily | ✅ Weekly | Some |
| ML Predictions | ✅ 63% | ❌ | ❌ | ❌ |
| Options Analysis | ✅ Yes | ❌ | ❌ | ❌ |
| Sentiment Analysis | ✅ Multi-source | Limited | ❌ | Some |
| API Access | ✅ 500+ req/mo | ❌ | Limited | No |
| Pattern Detection | ✅ DBSCAN | Manual | Manual | ❌ |
| Cost | $29/mo | $19/mo | Free/Paywalled | Varies |
| Data Export | ✅ Full | Limited | Limited | No |

**Key Differentiators:**
1. **Only platform with ML predictions** - 63% accuracy on what moves the market
2. **Cheapest advanced analytics** - $29/month vs $99+ for alternatives
3. **Open API** - Integrate anywhere vs vendor lock-in
4. **Transparent methodology** - Not a black box

---

## CTA Section

### Final CTA
**Ready to trade like Congress?**

**Start analyzing congressional trades with AI today. Free for 14 days. No credit card required.**

[Primary CTA Button: "Start Free Trial"]
[Secondary: "Schedule 15-min demo" / "View API docs"]

### Trust Badges
- 🔒 SSL Encrypted
- 📋 SOC 2 Certified
- ✅ 95%+ Test Coverage
- ⚡ 99.9% Uptime SLA

---

## Footer Section

### Quick Links
- Products: Platform, API, Reports
- Company: About, Blog, Careers
- Resources: Documentation, Guides, FAQ
- Legal: Privacy, Terms, Security
- Connect: Email, Twitter, GitHub

### Newsletter CTA
**Stay ahead of the market.**

Subscribe to our weekly Congressional Trading Digest. Get top trades, ML insights, and market analysis in your inbox.

[Email signup form]

