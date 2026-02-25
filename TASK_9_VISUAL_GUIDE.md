# Frontend Visual Guide

A conceptual overview of what each page looks like.

## 🏠 Home Page (`/`)

```
┌─────────────────────────────────────────────────┐
│ QUANTENGINES TERMINAL              ● CONNECTED  │
│ Discovery: CONNECTED | Models: 247              │
├─────────────────────────────────────────────────┤
│                                                 │
│  QUANT Discovery Engine                         │
│  ML-powered analysis of congressional trading   │
│                                                 │
│  [Predictions: 20] [Discoveries: 15]            │
│  [Anomalies: 3] [Politicians: 500+]             │
│                                                 │
│                    ┌──────┐                     │
│         ML SENTIMENT│ 65% │ GAUGE               │
│                    └──────┘                     │
│         Bullish 65% | Bearish 35%               │
└─────────────────────────────────────────────────┘

┌────────────────────────┐  ┌──────────────────┐
│ ML STOCK PREDICTIONS   │  │ REGIME           │
│                        │  │ DISTRIBUTION     │
│ ↑ AAPL  UP  92%       │  │                  │
│   RF: 0.8 LR: 0.9     │  │   [PIE CHART]    │
│                        │  │                  │
│ ↓ TSLA  DOWN 78%      │  │  High Activity   │
│   RF: 0.7 LR: 0.8     │  │  Low Activity    │
│                        │  │  Medium Activity │
│ ↑ NVDA  UP  85%       │  │                  │
│   RF: 0.9 LR: 0.8     │  ├──────────────────┤
│                        │  │ PATTERN          │
│ [View All →]          │  │ DISCOVERIES      │
└────────────────────────┘  │                  │
                            │ John Smith 87%   │
                            │ Correlation      │
                            │                  │
                            │ [View All →]     │
                            └──────────────────┘

┌─────────────────────────────────────────────────┐
│ ⚠ TRADING ANOMALIES DETECTED       [View All →]│
├─────────────────────────────────────────────────┤
│ [Jane Doe 95%] [Bob Lee 82%] [Ann Fox 76%]     │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Landing Page (`/landing`)

```
┌─────────────────────────────────────────────────┐
│              [Track Congressional Trading]      │
│                                                 │
│            Follow the Money,                    │
│          Make Smarter Trades                    │
│                                                 │
│  Track real-time congressional stock trades     │
│  with institutional-grade analytics             │
│                                                 │
│  [Get Started Free] [View Politicians]          │
│                                                 │
│         No credit card required                 │
└─────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│              Powerful Features                  │
└────────────────────────────────────────────────┘

┌─────────┐ ┌─────────┐ ┌─────────┐
│ 📊      │ │ 🏛️      │ │ 📈      │
│ Real-   │ │ Politi- │ │ Advan-  │
│ Time    │ │ cian    │ │ ced     │
│ Trades  │ │ Boards  │ │ Analy.  │
└─────────┘ └─────────┘ └─────────┘

┌─────────┐ ┌─────────┐ ┌─────────┐
│ 🔔      │ │ 🕸️      │ │ 📱      │
│ Custom  │ │ Network │ │ Mobile  │
│ Alerts  │ │ Analy.  │ │ First   │
└─────────┘ └─────────┘ └─────────┘

┌────────────────────────────────────────────────┐
│  500+ Politicians | 10K+ Trades | $2.5B Value  │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│        Simple, Transparent Pricing              │
└────────────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐
│   FREE   │ │ PRO $29  │ │ENTERPRISE│
│          │ │ POPULAR  │ │  CUSTOM  │
│ 30 req/m │ │ 500 req/m│ │ Unlimit. │
│ Basic    │ │ Advanced │ │ Dedicat. │
│ 30 days  │ │ ML pred. │ │ SLA      │
│          │ │ Alerts   │ │ Support  │
│[Start]   │ │[Start]   │ │[Contact] │
└──────────┘ └──────────┘ └──────────┘
```

---

## 🏛️ Politician Profile (`/politicians/[id]`)

```
┌─────────────────────────────────────────────────┐
│  John Smith                                     │
│  [Republican] [Senate] [TX]                     │
└─────────────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 📊       │ │ 💰       │ │ 🎯 ↑     │ │ 📈 ↑     │
│ 247      │ │ $2.5M    │ │ 65.2%    │ │ +12.5%   │
│ TOTAL    │ │ TOTAL    │ │ WIN RATE │ │ AVG RET. │
│ TRADES   │ │ VALUE    │ │          │ │          │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

┌──────────────────────┐ ┌──────────────────────┐
│ TRADE DISTRIBUTION   │ │ TOP HOLDINGS         │
│                      │ │                      │
│   [PIE CHART]        │ │ AAPL    ↑ BUY       │
│                      │ │ MSFT    ↑ BUY       │
│   Purchases: 65%     │ │ TSLA    ↓ SELL      │
│   Sales: 35%         │ │ NVDA    ↑ BUY       │
│                      │ │ GOOGL   ↑ BUY       │
└──────────────────────┘ └──────────────────────┘

┌─────────────────────────────────────────────────┐
│ RECENT TRADES                                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ ↑ AAPL        PURCHASE      $15K - $50K        │
│   Jan 15, 2026                                  │
│                                                 │
│ ↓ TSLA        SALE          $50K - $100K       │
│   Jan 14, 2026                                  │
│                                                 │
│ ↑ NVDA        PURCHASE      $100K - $250K      │
│   Jan 12, 2026                                  │
│                                                 │
└─────────────────────────────────────────────────┘

← Back to All Politicians
```

---

## 💼 Trade Detail (`/trades/[id]`)

```
┌─────────────────────────────────────────────────┐
│  Trade Details                    [PURCHASE]    │
│  Transaction ID: abc-123-def-456                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ TRANSACTION INFORMATION                         │
├─────────────────────────────────────────────────┤
│                                                 │
│ Politician                  Stock Ticker        │
│ John Smith →                AAPL →              │
│ [Republican] [Senate]       Apple Inc.          │
│                                                 │
│ Transaction Date            Disclosure Date     │
│ Jan 15, 2026               Jan 17, 2026         │
│                                                 │
│ Amount Range               Transaction Type     │
│ $15,000 - $50,000          PURCHASE             │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ RELATED TRADES                                  │
├─────────────────────────────────────────────────┤
│ Similar trades from John Smith in AAPL          │
└─────────────────────────────────────────────────┘

← Back to Politicians | View Politician Profile →
```

---

## 🔐 Login Page (`/auth/login`)

```
          ┌────────────┐
          │     Q      │
          └────────────┘
        QUANTENGINES
    Sign in to access your dashboard


┌─────────────────────────────────────────────────┐
│ Welcome back                                    │
│ Enter your credentials to continue              │
├─────────────────────────────────────────────────┤
│                                                 │
│ Email                                           │
│ ┌─────────────────────────────────────────────┐ │
│ │ you@example.com                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Password                  Forgot password?      │
│ ┌─────────────────────────────────────────────┐ │
│ │ ••••••••                                    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │           Sign in                           │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│   Don't have an account? Sign up               │
│                                                 │
└─────────────────────────────────────────────────┘

By signing in, you agree to our Terms and Privacy
```

---

## ✍️ Register Page (`/auth/register`)

```
          ┌────────────┐
          │     Q      │
          └────────────┘
        QUANTENGINES
    Create your account to get started


┌─────────────────────────────────────────────────┐
│ Create an account                               │
│ Enter your information to sign up               │
├─────────────────────────────────────────────────┤
│                                                 │
│ Full Name                                       │
│ ┌─────────────────────────────────────────────┐ │
│ │ John Doe                                    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Email                                           │
│ ┌─────────────────────────────────────────────┐ │
│ │ you@example.com                             │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Password                                        │
│ ┌─────────────────────────────────────────────┐ │
│ │ ••••••••                                    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Confirm Password                                │
│ ┌─────────────────────────────────────────────┐ │
│ │ ••••••••                                    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │         Create account                      │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│   Already have an account? Sign in             │
│                                                 │
└─────────────────────────────────────────────────┘

By signing up, you agree to our Terms and Privacy
```

---

## 👤 Profile Page (`/auth/profile`)

```
┌─────────────────────────────────────────────────┐
│  Profile                              [Logout]  │
│  Manage your account settings                   │
└─────────────────────────────────────────────────┘

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Account Type │ │  API Calls   │ │ Member Since │
│              │ │              │ │              │
│ [FREE TIER]  │ │     247      │ │ Jan 1, 2026  │
│              │ │  This month  │ │              │
└──────────────┘ └──────────────┘ └──────────────┘

┌─────────────────────────────────────────────────┐
│ Personal Information                            │
│ Update your account details                     │
├─────────────────────────────────────────────────┤
│                                                 │
│ Full Name                                       │
│ ┌─────────────────────────────────────────────┐ │
│ │ John Doe                                    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Email Address                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ john@example.com                            │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [Edit Profile]                                  │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ API Access                                      │
│ Your API credentials                            │
├─────────────────────────────────────────────────┤
│                                                 │
│ API Key                                         │
│ ┌──────────────────────────────────┬─────────┐ │
│ │ •••••••••••••••••••••••••••••••• │ [Reveal]│ │
│ └──────────────────────────────────┴─────────┘ │
│                                                 │
│ Keep your API key secure. Do not share.        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Component Demo (`/components-demo`)

```
┌─────────────────────────────────────────────────┐
│  Component Showcase                             │
│  A demonstration of all components              │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Buttons                                         │
├─────────────────────────────────────────────────┤
│ Button Variants                                 │
│                                                 │
│ [Default] [Destructive] [Outline] [Secondary]  │
│ [Ghost] [Link]                                  │
│                                                 │
│ [Small] [Default] [Large]                       │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Cards                                           │
├─────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐                     │
│ │Simple│ │Footer│ │High- │                     │
│ │Card  │ │Card  │ │light │                     │
│ │      │ │      │ │Card  │                     │
│ └──────┘ └──────┘ └──────┘                     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Input Fields                                    │
├─────────────────────────────────────────────────┤
│ Default  │ [________________]                   │
│ Email    │ [________________]                   │
│ Password │ [••••••••••••••••]                   │
│ Disabled │ [________________]                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Badges                                          │
├─────────────────────────────────────────────────┤
│ [Default] [Secondary] [Destructive] [Outline]  │
│ [Success] [Warning] [Info] [Custom]             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Loading States                                  │
├─────────────────────────────────────────────────┤
│ ████████████████████████████                    │
│ ████████████████████                            │
│ ████████████                                    │
└─────────────────────────────────────────────────┘
```

---

## 📱 Mobile View

```
┌──────────────────┐
│ ☰  Q  [FREE]    │ ← Hamburger menu
├──────────────────┤
│                  │
│  ML PREDICTIONS  │
│                  │
│ ↑ AAPL  UP      │
│   92% conf.     │
│                  │
│ ↓ TSLA  DOWN    │
│   78% conf.     │
│                  │
├──────────────────┤
│                  │
│ [CHART]          │
│                  │
├──────────────────┤
│                  │
│ DISCOVERIES      │
│                  │
│ John Smith       │
│ 87% strength     │
│                  │
└──────────────────┘

Mobile menu expanded:
┌──────────────────┐
│ × MENU          │
├──────────────────┤
│ Dashboard        │
│ Politicians      │
│ Charts           │
│ About            │
├──────────────────┤
│ Login            │
│ [Sign Up]        │
└──────────────────┘
```

---

## 🎨 Color Theme

```
Primary Gold:    ████  hsl(45, 96%, 58%)
Background:      ████  hsl(220, 60%, 4%)
Card:            ████  hsl(220, 55%, 7%)
Border:          ████  hsl(215, 40%, 18%)
Success:         ████  #22c55e
Error:           ████  #ef4444
Info:            ████  hsl(210, 100%, 56%)
Warning:         ████  #eab308
```

---

## 📐 Layout Patterns

### Grid Layouts

**4 Columns (Desktop)**
```
┌────┐ ┌────┐ ┌────┐ ┌────┐
│ 1  │ │ 2  │ │ 3  │ │ 4  │
└────┘ └────┘ └────┘ └────┘
```

**2 Columns (Tablet)**
```
┌──────────┐ ┌──────────┐
│    1     │ │    2     │
└──────────┘ └──────────┘
┌──────────┐ ┌──────────┐
│    3     │ │    4     │
└──────────┘ └──────────┘
```

**1 Column (Mobile)**
```
┌────────────────────┐
│         1          │
└────────────────────┘
┌────────────────────┐
│         2          │
└────────────────────┘
┌────────────────────┐
│         3          │
└────────────────────┘
┌────────────────────┐
│         4          │
└────────────────────┘
```

---

## 🎯 Key Features Visualized

### Interactive Elements
- **Buttons**: Hover effects, click states
- **Links**: Underline on hover, color change
- **Cards**: Border highlight on hover
- **Charts**: Tooltips on hover

### Loading States
- **Skeleton**: Pulsing gray rectangles
- **Spinner**: Rotating circle
- **Disabled**: Reduced opacity

### Error States
- **Red border**: Invalid input
- **Red text**: Error message
- **Red card**: Critical error

---

This visual guide shows the conceptual layout and structure of each page. The actual implementation includes:
- Full color styling
- Animations and transitions
- Interactive elements
- Real data integration
- Responsive behavior
- Accessibility features

**All pages are production-ready and fully functional!**
