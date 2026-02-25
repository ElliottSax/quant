# User Experience: How Discoveries Appear to Users

This document shows **exactly what users see** when the discovery service finds hidden patterns.

---

## 📱 **Discovery Flow: Background → Frontend**

```
STEP 1: Discovery Service (Background - 2 AM)
┌────────────────────────────────────────────────────┐
│ Celery Worker: scan_all_politicians                │
│                                                     │
│ [Processing] Tommy Tuberville...                   │
│ • Loaded 347 trades                                │
│ • Testing parameter combinations...                │
│ • Found strong 87-day cycle!                       │
│   - Strength: 0.92                                 │
│   - Confidence: 0.89                               │
│   - Window: 30 days                                │
│                                                     │
│ [Writing to database]                              │
│ INSERT INTO pattern_discoveries (                  │
│   politician_id = 'abc-123',                       │
│   pattern_type = 'fourier_cycle',                  │
│   strength = 0.92,                                 │
│   confidence = 0.89,                               │
│   description = 'Strong 87-day trading cycle...'   │
│ )                                                   │
└────────────────────────────────────────────────────┘
                        ↓
STEP 2: Database (Shared between both services)
┌────────────────────────────────────────────────────┐
│ PostgreSQL: pattern_discoveries table              │
│                                                     │
│ id  | politician_name | pattern_type | strength    │
│ ────┼─────────────────┼──────────────┼─────────    │
│ 1   | T. Tuberville   | fourier_cycle| 0.92  ←NEW │
│ 2   | Nancy Pelosi    | correlation  | 0.87        │
│ 3   | Dan Crenshaw    | regime_trans | 0.84        │
└────────────────────────────────────────────────────┘
                        ↓
STEP 3: Main App API (User requests data)
┌────────────────────────────────────────────────────┐
│ GET /api/v1/discoveries/recent                     │
│                                                     │
│ SELECT * FROM pattern_discoveries                  │
│ WHERE strength > 0.8                               │
│ ORDER BY discovery_date DESC                       │
│                                                     │
│ Response: [                                         │
│   {                                                 │
│     politician_name: "Tommy Tuberville",           │
│     pattern_type: "fourier_cycle",                 │
│     strength: 0.92,                                │
│     description: "Strong 87-day cycle..."          │
│   },                                                │
│   ...                                               │
│ ]                                                   │
└────────────────────────────────────────────────────┘
                        ↓
STEP 4: Frontend (User sees it!)
┌────────────────────────────────────────────────────┐
│ USER SEES THIS:                                    │
│ (shown below in mockups)                           │
└────────────────────────────────────────────────────┘
```

---

## 🖼️ **UI Mockups: What Users Actually See**

### **1. Dashboard - Discovery Alert Badge**

When user visits their dashboard:

```
┌────────────────────────────────────────────────────────────┐
│ Quant Analytics Dashboard                                  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  🔍 3 NEW DISCOVERIES IN LAST 24H   [View All →]    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐│
│  │ Total Pols      │  │ Active Last 7d  │  │ Discoveries││
│  │   247           │  │   38            │  │   12 ⬆    ││
│  └─────────────────┘  └─────────────────┘  └────────────┘│
│                                                             │
│  Recent Discoveries:                                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 🔄 New Cyclical Pattern  [NEW]                       │  │
│  │ Tommy Tuberville • 87-day cycle • 92% strength       │  │
│  │ 2 hours ago                                          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 🚨 Critical Anomaly                                   │  │
│  │ Dan Crenshaw • No historical precedent • 94% severity│  │
│  │ 5 hours ago                              [Investigate]│  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

### **2. Discoveries Page - Full Feed**

When user clicks "View All Discoveries":

```
┌────────────────────────────────────────────────────────────┐
│ Pattern Discoveries                                         │
│ Hidden patterns found by AI analyzing Congressional trading│
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ 🚨 3 CRITICAL ANOMALIES DETECTED                       ││
│ │                                                          ││
│ │ ⚠️ Dan Crenshaw - Statistical Outlier (94% severity)   ││
│ │    No historical precedent • Off-cycle by 3.2σ          ││
│ │    [Investigate →]                                       ││
│ │                                                          ││
│ │ ⚠️ Tommy Tuberville - Volume Spike (87% severity)      ││
│ │    Trading 5x normal volume • Regime change detected    ││
│ │    [View Details →]                                      ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ Filters: [Last 24h ▼] [Min Strength: 80%  ━━━━━●━━━━]   │
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ 🔄 Cyclical Pattern                          [NEW]      ││
│ │ Tommy Tuberville                                        ││
│ │                                                          ││
│ │ Strong 87-day trading cycle detected with 92% strength │
│ │ Aligns with Defense Committee meeting schedule          ││
│ │                                                          ││
│ │ Pattern Strength  ████████████████████░░ 92%           ││
│ │ Confidence        ████████████████████░░ 89%           ││
│ │                                                          ││
│ │ Discovery Parameters ▼                                  ││
│ │ • Window: 30 days                                       ││
│ │ • Threshold: 0.8                                        ││
│ │ • Method: Fourier Transform                             ││
│ │                                                          ││
│ │ [View Politician →] [Full Analysis →]                  ││
│ │                                                          ││
│ │ Discovered 2 hours ago                                  ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ 🔗 Correlation Pattern                    [DEPLOYED]    ││
│ │ Nancy Pelosi & Paul Pelosi                              ││
│ │                                                          ││
│ │ Synchronized trading detected: 0.94 correlation with    ││
│ │ 24-hour lag. Statistically significant (p < 0.001)      ││
│ │                                                          ││
│ │ Pattern Strength  ████████████████████░░ 87%           ││
│ │ Confidence        ██████████████████████ 95%           ││
│ │                                                          ││
│ │ [View Network →] [Compare Trades →]                    ││
│ │                                                          ││
│ │ Discovered 1 day ago                                    ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ ✨ Novel Pattern                                        ││
│ │ Dan Crenshaw                                            ││
│ │                                                          ││
│ │ Previously unknown 73-day cycle discovered. No similar  ││
│ │ pattern in 5-year historical data. Further investigation││
│ │ recommended.                                             ││
│ │                                                          ││
│ │ Pattern Strength  ███████████████░░░░░░ 78%           ││
│ │ Confidence        ███████████████████░░ 91%           ││
│ │                                                          ││
│ │ [View Analysis →] [Mark as Reviewed]                   ││
│ │                                                          ││
│ │ Discovered 3 days ago                                   ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

### **3. Politician Detail Page - Discoveries Tab**

When viewing a specific politician:

```
┌────────────────────────────────────────────────────────────┐
│ Tommy Tuberville (R-AL) • Senate                           │
│                                                             │
│ [Overview] [Trades] [Analysis] [Discoveries] ← ACTIVE TAB │
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Discoveries for Tommy Tuberville                        ││
│ │                                                          ││
│ │ 🔄 Cyclical Pattern (92% strength)          2 hours ago ││
│ │ Strong 87-day trading cycle                             ││
│ │ Status: Under Review                      [Deploy →]   ││
│ │                                                          ││
│ │ ⚠️ Anomaly: Volume Spike (87% severity)    5 hours ago ││
│ │ Trading volume 5x above historical average              ││
│ │ Status: Pending Investigation        [Investigate →]   ││
│ │                                                          ││
│ │ 📊 Regime Transition (84% strength)         2 days ago  ││
│ │ Shifted from "Low Activity" to "Aggressive Buying"      ││
│ │ Status: Deployed                                        ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ Discovery Timeline:                                         │
│                                                             │
│ Nov 15 ●━━━━━━ 🔄 New 87-day cycle found                  │
│         │                                                   │
│ Nov 15 ●━━━━━━ ⚠️ Volume spike detected                   │
│         │                                                   │
│ Nov 13 ●━━━━━━ 📊 Regime change observed                  │
│         │                                                   │
│ Nov 10 ●━━━━━━ 🔗 Correlation with defense sector         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

### **4. Anomaly Investigation Page**

When user clicks "Investigate" on a critical anomaly:

```
┌────────────────────────────────────────────────────────────┐
│ Anomaly Investigation                                       │
│ Dan Crenshaw • Statistical Outlier                          │
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ 🚨 CRITICAL SEVERITY: 94%                               ││
│ │                                                          ││
│ │ Detected: 5 hours ago                                   ││
│ │ Type: No Historical Precedent                           ││
│ │ Status: Uninvestigated                                  ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ Evidence:                                                   │
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Model Disagreement                                      ││
│ │ • Fourier: Predicts +5 trades                          ││
│ │ • HMM: Predicts -3 trades                              ││
│ │ • DTW: No similar pattern (confidence < 30%)           ││
│ │ Agreement Score: 12% (very low!)                       ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Statistical Outliers                                    ││
│ │ • Z-score: 3.87 (exceeds 3σ threshold)                 ││
│ │ • Recent volume: 23 trades/week                        ││
│ │ • Historical avg: 4.2 trades/week                      ││
│ │ • Deviation: 5.5x normal                               ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Off-Cycle Trading                                       ││
│ │ • Dominant cycle: 45 days                              ││
│ │ • Expected next trade: Nov 20                          ││
│ │ • Actual trading: Nov 13 (7 days early)                ││
│ │ • Off-cycle deviation: 2.3σ                            ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌────────────────────────────────────────────────────────┐│
│ │ No Historical Precedent                                 ││
│ │ • DTW searched 1,250 historical windows                ││
│ │ • No patterns with >60% similarity found               ││
│ │ • This behavior is unprecedented in 5-year history     ││
│ └────────────────────────────────────────────────────────┘│
│                                                             │
│ Recent Trades:                                              │
│                                                             │
│ Nov 13  NVDA   Purchase  $500K-1M    [Unusual timing]     │
│ Nov 13  MSFT   Purchase  $250K-500K  [Unusual timing]     │
│ Nov 14  AAPL   Sale      $100K-250K  [Normal]             │
│                                                             │
│ Actions:                                                    │
│ [Mark as Investigated] [Flag for Compliance] [Not Anomaly]│
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

### **5. Mobile Experience**

On mobile devices:

```
┌─────────────────────┐
│ ≡  Discoveries   🔔3│
├─────────────────────┤
│                     │
│ 🚨 3 Critical      │
│    Anomalies        │
│    [View →]         │
│                     │
│ ───────────────────│
│                     │
│ 🔄 NEW DISCOVERY   │
│                     │
│ T. Tuberville      │
│ 87-day cycle       │
│ 92% strength       │
│                     │
│ Strength ████████  │
│          92%       │
│                     │
│ [Details →]        │
│                     │
│ 2 hours ago        │
│                     │
│ ───────────────────│
│                     │
│ ⚠️ ANOMALY         │
│                     │
│ Dan Crenshaw       │
│ No precedent       │
│ 94% severity       │
│                     │
│ [Investigate →]    │
│                     │
│ 5 hours ago        │
│                     │
│ ───────────────────│
│                     │
│ [Load More]        │
│                     │
└─────────────────────┘
```

---

## 🔔 **Notification Examples**

### **Push Notifications (Premium Users)**

```
┌────────────────────────────────────┐
│ 🚨 Quant Analytics                 │
│                                    │
│ Critical Anomaly Detected          │
│                                    │
│ Dan Crenshaw trading shows no      │
│ historical precedent (94% severity)│
│                                    │
│ Tap to investigate                 │
│                                    │
│ 5 minutes ago                      │
└────────────────────────────────────┘
```

### **Email Alert**

```
Subject: [CRITICAL] New Anomaly Detected - Dan Crenshaw

Hi User,

Our AI discovery service has detected a critical anomaly:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  CRITICAL ANOMALY (94% severity)

Politician: Dan Crenshaw
Type: No Historical Precedent
Detected: Nov 15, 2025 at 2:47 AM

Evidence:
• Model disagreement: 12% (very low)
• Statistical outlier: 3.87σ
• Off-cycle trading by 2.3σ
• No similar patterns in 5-year history

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Investigate Now →]

View all discoveries: https://app.quantanalytics.com/discoveries

This anomaly requires investigation. Please review within 24 hours.

---
Quant Analytics Platform
Automated Discovery Service
```

---

## 📊 **Stats Widget (Sidebar)**

Always visible on main pages:

```
┌─────────────────────────┐
│ Discovery Activity      │
├─────────────────────────┤
│                         │
│ Last 24 Hours:          │
│                         │
│ 🔍 12 Patterns Found   │
│ ⚠️ 3 Anomalies         │
│ 🧪 1 Model Ready       │
│                         │
│ ─────────────────────  │
│                         │
│ Top Discovery:          │
│                         │
│ 🔄 87-day cycle        │
│ T. Tuberville          │
│ 92% strength           │
│                         │
│ [View All →]           │
│                         │
└─────────────────────────┘
```

---

## 🎨 **Visual Design Elements**

### **Pattern Type Icons**

```
🔄 Cyclical Pattern     (Fourier)
📊 Regime Change        (HMM)
🔍 Pattern Match        (DTW)
🔗 Correlation          (Network)
🎯 Leading Indicator    (Predictive)
✨ Novel Pattern        (Unprecedented)
⚠️ Anomaly              (Unusual)
🚨 Critical Anomaly     (Severe)
```

### **Status Badges**

```
[NEW]              - Discovered < 24h ago
[DEPLOYED]         - Added to production models
[UNDER REVIEW]     - Being evaluated
[INVESTIGATED]     - Anomaly reviewed
[READY FOR A/B]    - Experiment ready to test
```

### **Severity Colors**

```
Critical (>90%):  🔴 Red
High (80-90%):    🟠 Amber
Medium (70-80%):  🟡 Yellow
Low (<70%):       🔵 Blue
```

---

## 🎯 **User Journeys**

### **Journey 1: Retail Investor**

```
1. User logs in → sees "3 NEW DISCOVERIES" badge
2. Clicks badge → lands on Discoveries page
3. Sees top discovery: "Strong 87-day cycle - Tommy Tuberville"
4. Clicks "View Politician" → sees full trading history
5. Sees discovery timeline showing when pattern emerged
6. Decision: "I'll monitor Tuberville's trades every 87 days"
```

### **Journey 2: Researcher**

```
1. User navigates to Discoveries > Pattern Library
2. Filters by "fourier_cycle" type
3. Downloads CSV of all cyclical patterns found
4. Analyzes in Jupyter notebook
5. Finds 15 politicians with quarterly (90-day) cycles
6. Publishes research paper with statistical evidence
```

### **Journey 3: Compliance Officer**

```
1. Receives email: "CRITICAL ANOMALY DETECTED"
2. Opens investigation page for Dan Crenshaw
3. Reviews evidence: model disagreement, no precedent, off-cycle
4. Checks recent trades: heavy NVDA purchases
5. Cross-references with committee assignments
6. Flags for SEC review
```

---

## 🔄 **Live Updates**

Discoveries update in real-time:

```javascript
// Frontend polls every 60 seconds for new discoveries
useInterval(() => {
  refetchDiscoveries()
}, 60000)

// When new discovery arrives:
showToast({
  title: "New Discovery",
  description: "87-day cycle found for Tommy Tuberville",
  action: <Link href="/discoveries">View</Link>
})
```

User sees toast notification:
```
┌────────────────────────────────┐
│ 🔍 New Discovery               │
│                                │
│ 87-day cycle found for         │
│ Tommy Tuberville               │
│                                │
│ [View] [Dismiss]               │
└────────────────────────────────┘
```

---

## 📈 **Before vs. After**

### **BEFORE (without discovery service):**

User experience:
1. Visit politician page
2. Click "Analyze Patterns"
3. Wait 5 seconds for analysis
4. See results for THAT politician only
5. No idea about other politicians
6. No automatic anomaly detection
7. Manual parameter tuning required

### **AFTER (with discovery service):**

User experience:
1. Log in → **immediately see discoveries feed**
2. **Critical anomalies flagged automatically**
3. **All politicians analyzed** (not just ones user checks)
4. **Optimal parameters** already found by sweep
5. **Novel patterns** discovered proactively
6. **Email alerts** for critical findings
7. **Timeline view** of when patterns emerged

---

**The key difference: Discovery service runs 24/7 finding patterns users would NEVER have looked for manually!**

---

Ready to see this in action? Just start the discovery service and within 24 hours, your users will have a feed of hidden patterns they never knew existed.
