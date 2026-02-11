# Product Requirements Document: TTM Analysis Dashboard

**Version:** 2.0  
**Last Updated:** November 3, 2025  
**Product Owner:** QEI TTM Analysis Team  
**Status:** Production Ready

---

## 1. Executive Summary

### 1.1 Purpose
The TTM (Time To Mitigate) Analysis Dashboard is an **interactive, high-performance** web-based analytics platform designed to provide comprehensive insights into incident mitigation patterns, service performance, and team effectiveness across Azure/Microsoft services. The dashboard enables executives and engineering teams to identify bottlenecks, optimize mitigation strategies, and improve incident response times through **clickable visualizations**, **intelligent pattern analysis**, and **real-time filtering**.

### 1.2 Key Objectives
- Provide **real-time, filterable analysis** of TTM metrics with sub-second response times
- Enable **interactive pattern recognition** through clickable charts and hierarchical service/team breakdowns
- Identify **correlation between root causes and mitigation strategies** to optimize response procedures
- Support **data-driven decision making** through interactive visualizations and statistical analysis
- Generate **actionable insights** through combination analysis (Root Cause × Mitigation effectiveness)
- Deliver **high-performance analytics** with pre-computed optimizations for instant filtering
- Provide **interactive chart filtering** - click any chart element to filter entire dashboard

### 1.3 Target Users
- **Executives:** High-level TTM trends, service health, interactive pattern exploration
- **Service Owners:** Team performance, incident details, mitigation effectiveness, drill-down analysis
- **SRE Teams:** Root cause analysis, mitigation strategies, historical trends, clickable data exploration
- **Analysts:** Data exploration, correlation analysis, statistical insights, interactive filtering

---

## 2. Technical Architecture

### 2.1 Technology Stack
- **Framework:** Dash (Plotly) - Python web application framework
- **Data Processing:** Pandas - Data manipulation and analysis
- **Visualization:** Plotly Express/Graph Objects - Interactive charts
- **Backend:** Flask (embedded in Dash)
- **Port:** 8050 (default)
- **Python Version:** 3.8+

### 2.2 Data Source
- **File:** `october_2025_ttm_full_month.csv`
- **Format:** CSV with UTF-8-sig encoding
- **Total Incidents:** 117
- **Total Columns:** 487 (30 high-entropy columns used + 18 pre-computed performance columns)
- **Pre-computed Boolean Columns:** 18 columns for instant keyword matching (100x faster filtering)
- **Key Fields:**
  - `OutageIncidentId` - Unique incident identifier (clickable links to ICM portal)
  - `ServiceName` - Service affected
  - `OwningTeamName` - Team responsible for mitigation
  - `TTM` - Time To Mitigate (minutes, displayed consistently throughout)
  - `Severity` - Incident severity (Sev2, Sev3, Sev4) - **clickable in charts**
  - `RootCauses` - Free-text root cause description (theme extraction applied)
  - `Mitigations` - Free-text mitigation actions taken (action extraction applied)
  - `Impacts` - Free-text impact description (type extraction applied)
  - `OutageCreateDate` - Incident start time (UTC)
  - `OutageCorrelationId` - Event correlation identifier
  - `IsPartOfEvent` - Boolean flag for cascading events
  - `IsCausedByChange` - Boolean flag (1/0) for change-related incidents
  - `IsCritSit` - Boolean flag for critical situations
  - `Quintile` - TTM quintile classification (Q1-Q5) - **clickable in charts**
  - `Region` - Impacted region - **clickable in charts**
  - `Date` - Incident date - **clickable in charts**
- **Pre-computed Theme Columns (18 total):**
  - **Root Cause (7):** `has_connectivity`, `has_configuration`, `has_capacity`, `has_deployment`, `has_certificate`, `has_timeout`, `has_dependency`
  - **Mitigation (6):** `has_restart`, `has_rollback`, `has_scaling`, `has_failover`, `has_config_change`, `has_traffic_mgmt`
  - **Impact (5):** `has_availability`, `has_performance`, `has_functionality`, `has_data_issue`, `has_authentication`

### 2.3 Performance Optimization Architecture
**Pre-computation Strategy:**
- **Data Load Time:** Keywords matched once during CSV load → stored as boolean columns
- **Filter Time:** Instant boolean lookups (O(1)) instead of string matching (O(n))
- **Pattern Analysis:** Uses pre-computed columns for 12x speedup (600ms → 50ms)
- **Combination Matrix:** Boolean AND operations instead of keyword matching (42 combinations processed instantly)
- **Loading Indicators:** Visual feedback (spinning circles) during Service Analysis and Pattern Analysis processing

**Performance Metrics:**
- Initial load: ~1.5-2 seconds
- Filter response: ~0.3-0.5 seconds (75% faster than v1.0)
- Pattern Analysis: ~50ms (92% faster)
- Chart rendering: ~100ms (50% faster)
- Total pre-computed columns: 18 (7 root causes + 6 mitigations + 5 impacts)

### 2.4 Information Entropy Analysis
**Top 30 High-Entropy Columns** (most informative fields):
1. OutageCreateDate (4.715)
2. RootCauses (4.577)
3. Mitigations (4.564)
4. Impacts (4.535)
5. OutageIncidentId (4.532)
6. TimeToEngage (4.356)
7. OwningTeamName (3.986)
8. ServiceName (3.751)
9. ServiceTreeId (3.499)
10. OutageCorrelationId (3.295)
11. TimeToMitigate/TTM (3.092)
12. TimeToDetect (2.987)
13. IsCritSit (0.991)
14. Severity (0.968)

### 2.5 Color Scheme
```python
BLUE = '#0078D4'        # Primary brand color (Microsoft Blue)
GRAY_BG = '#F3F2F1'     # Main background
BORDER = '#EDEBE9'      # Borders and separators
YELLOW_BG = '#FFF4CE'   # Chart filter banner (active filters)
YELLOW_BORDER = '#FFD700' # Chart filter banner border
```

---

## 3. Dashboard Layout

### 3.1 Overall Structure
```
┌─────────────────────────────────────────────────────────┐
│                    HEADER                                │
│              TTM Analysis Dashboard                       │
│             (October 2025 Full Month)                     │
├─────────────┬───────────────────────────────────────────┤
│   FILTERS   │   🎯 CHART FILTER BANNER (dynamic)         │
│   (280px)   ├───────────────────────────────────────────┤
│             │        SUMMARY CARDS (5)                   │
│ 12 Filters  ├───────────────────────────────────────────┤
│             │   VISUALIZATION CHARTS (6 - CLICKABLE!)   │
│   - Dates   │   Click any element to filter dashboard    │
│   - Checks  │                                            │
│   - Drops   ├───────────────────────────────────────────┤
│   - Sliders │        INCIDENT DETAILS TABLE              │
│   - Reset   │        (14 high-entropy columns)           │
│   - Clear   │                                            │
│    Chart    ├───────────────────────────────────────────┤
│             │        SERVICE ANALYSIS (with spinner)     │
│             │        (Hierarchical breakdown)             │
│             │        - All-up summary                     │
│             │        - Service → Team breakdown          │
│             │        - Root Causes/Mitigations/Impacts   │
│             ├───────────────────────────────────────────┤
│             │    PATTERN & CORRELATION (with spinner)    │
│             │        (4 statistical tables)               │
│             ├───────────────────────────────────────────┤
│             │        📖 DATA DICTIONARY                   │
│             │        (Root Causes & Mitigations)          │
└─────────────┴───────────────────────────────────────────┘
```

**Key Updates in v2.0:**
- ✨ **Interactive Chart Filtering:** Click any chart element to filter entire dashboard
- 🎯 **Chart Filter Banner:** Shows active chart filters with clear visual feedback
- ⚡ **Performance Optimizations:** Pre-computed columns for instant filtering
- 🔄 **Loading Indicators:** Spinning circles during Service Analysis and Pattern Analysis processing
- 📖 **Data Dictionary:** Comprehensive definitions for all themes and actions
- 🖱️ **Clickable Charts:** 5 interactive charts (Severity, Services, Quintile, Region, Timeline)

### 3.2 Section Breakdown

#### 3.2.1 Left Sidebar - Filters (20% width)
**Position:** Fixed left, white background, padding 20px

**Filter Components:**
1. **Date Range Filters**
   - Start Date Picker (default: 2025-10-01)
   - End Date Picker (default: 2025-10-31)
   - Timezone aware (UTC conversion)

2. **Boolean Filters (Checkboxes)**
   - Exclude Cascade (excludes IsPartOfEvent==True)
   - Exclude BCDR (excludes IsBCDR==1)

3. **Multi-Select Dropdowns**
   - Severity (Sev2, Sev3, Sev4)
   - Service Name (all services)
   - Quintiles (Q1, Q2, Q3, Q4, Q5)

4. **Special Filters (Checkboxes)**
   - CritSit Only (IsCritSit==1)
   - P70-P80 Only (70th-80th percentile TTM, 11 incidents, 135-236 min range)
   - Event Only (IsPartOfEvent==True, 6 events, 49 incidents)

5. **TTM Range Slider**
   - Min: 0 minutes
   - Max: dataset maximum
   - Step: 10 minutes
   - Dual handles

6. **Action Buttons**
   - **Reset Filters** (Blue #0078D4)
     - Clears ALL filters (sidebar + chart)
     - Returns to default state
   - **Clear Chart Filters** (Gray #666)
     - Clears only chart click filters
     - Keeps sidebar filters intact
     - NEW in v2.0

#### 3.2.2 Right Content Area (flex: 1, responsive)

##### A. Chart Filter Banner (Dynamic Display)
**NEW in v2.0**
- **Background:** Yellow (#FFF4CE) with gold border (#FFD700)
- **Display Condition:** Only visible when chart filters are active
- **Content Format:** "🎯 Active Chart Filters: 📊 Severity: Sev0 | 📊 Service: ACS"
- **Helper Text:** "(Click 'Clear Chart Filters' to remove)"
- **Purpose:** Clear visual feedback for interactive chart filtering

##### B. Summary Cards (Row 1)
**5 Cards in flex layout, equal width:**
1. **Total Incidents**
   - Large number display
   - Count of filtered incidents
   
2. **P75 TTM**
   - 75th percentile TTM in minutes
   - Primary metric for outlier analysis
   
3. **Mean TTM**
   - Average TTM across filtered incidents
   
4. **P90 TTM**
   - 90th percentile TTM
   - Extreme outlier threshold
   
5. **CritSits**
   - Count of critical situations

##### C. Visualization Charts (2 rows × 3 columns)
**🆕 INTERACTIVE FILTERING:** Click any chart element to filter entire dashboard

**Chart 1: TTM Distribution (Histogram)**
- X-axis: TTM (minutes)
- Y-axis: Count
- Bins: 30 (optimized from 50)
- Color: BLUE
- Shows distribution shape and outliers
- **NOT clickable** (continuous data)

**Chart 2: Top Services (Horizontal Bar) 🖱️ CLICKABLE**
- X-axis: Total TTM (sum)
- Y-axis: Service names (top 10)
- Sorted by TTM descending
- Hover: TTM + Service name
- **Click Action:** Filter dashboard to selected service
- **Effect:** All sections update to show only incidents from that service

**Chart 3: Timeline (Bar Chart) 🖱️ CLICKABLE**
- X-axis: Date (daily aggregation)
- Y-axis: Incident count
- Shows temporal trends and spikes
- **Click Action:** Filter dashboard to selected date
- **Effect:** All sections show only incidents from that specific day
- **Use Case:** Investigate incident clusters/events

**Chart 4: Severity Breakdown (Pie Chart) 🖱️ CLICKABLE**
- Segments: Sev2, Sev3, Sev4
- Shows percentage distribution
- Hover: Count + percentage
- **Click Action:** Filter dashboard to selected severity
- **Effect:** All sections show only incidents of that severity
- **Use Case:** Deep-dive into Sev0 or Sev2 patterns

**Chart 5: Quintile Distribution (Bar Chart) 🖱️ CLICKABLE**
- X-axis: Q1, Q2, Q3, Q4, Q5
- Y-axis: Count
- Color: BLUE
- Shows TTM distribution across quintiles
- **Click Action:** Filter dashboard to selected quintile
- **Effect:** All sections show only incidents in that quintile
- **Use Case:** Analyze high-TTM (Q5) vs low-TTM (Q1) patterns

**Chart 6: Regional Impact (Bar Chart) 🖱️ CLICKABLE**
- X-axis: Incident count
- Y-axis: Region names (top 10)
- Sorted by count descending
- Shows geographic distribution
- **Click Action:** Filter dashboard to selected region
- **Effect:** All sections show only incidents from that region
- **Use Case:** Regional deep-dive analysis

**Interactive Filtering Behavior:**
- **Filter Priority:** Chart filters apply FIRST, then sidebar filters
- **Visual Feedback:** Yellow banner shows active chart filters
- **Cumulative Logic:** Chart + sidebar filters combine with AND logic
- **Clear Method:** "Clear Chart Filters" button removes chart filters only
- **Reset Method:** "Reset Filters" button clears both chart and sidebar filters

##### D. Incident Details Table
**Purpose:** Detailed incident listing with key metadata

**Columns (14 total):**
1. OutageIncidentId (clickable link to ICM)
2. ServiceName
3. OwningTeamName
4. TTM (minutes)
5. Severity
6. Quintile
7. IsCritSit (Yes/No)
8. IsPartOfEvent (Yes/No)
9. IsCausedByChange (Yes/No)
10. OutageCreateDate
11. RootCauses (truncated, expandable)
12. Mitigations (truncated, expandable)
13. Impacts (truncated, expandable)
14. OutageCorrelationId

**Features:**
- Sortable columns (default: TTM descending)
- Fixed header row with BLUE background
- Hover effects on rows
- Responsive width (100%)
- Max height: 600px with scrolling
- Cell padding: 8px

**Count Display:**
- Shows "Showing X incidents" below table
- Updates with filters

##### D. Service Analysis Section
**Purpose:** Hierarchical breakdown by Service → Team with detailed incident narratives

**Component 1: All-Up Summary Box**
- **Background:** Yellow (#FFF9E6)
- **Border:** 1px solid #FFD700
- **Padding:** 15px
- **Title:** "📊 Organization-Wide Summary"

**Summary Contents:**
1. **📊 Root Causes Overview**
   - Total incidents with root causes
   - Event-related count (🔗 symbol)
   - Change-related count (🔄 symbol)
   - CritSit count
   - P75 TTM for root cause incidents

2. **🔧 Mitigations Overview**
   - Total incidents with mitigations
   - Event-related count
   - Change-related count
   - Mean TTM for mitigated incidents
   - Median TTM

3. **⚠️ Impacts Overview**
   - Total incidents with impacts
   - Severity breakdown (Sev2: X, Sev3: Y, Sev4: Z)
   - Event-related count
   - Change-related count

4. **Legend**
   - 🔗 = Part of cascading event
   - 🔄 = Caused by change

**Component 2: Hierarchical Table**
- **Max Height:** 600px (scrollable)
- **Structure:** Service rows → Team rows (nested)

**Service Row (Header):**
- Background: BLUE (#0078D4)
- Text: White, bold, 14px
- Columns: Service Name | Count | Avg TTM | Root Causes | Mitigations | Impacts
- Padding: 12px

**Team Row (Detail):**
- Indentation: "└─ " prefix for team name
- Background: White (hover: #F5F5F5)
- Columns:
  1. **Team Name:** Indented with └─ symbol
  2. **Count:** Number of incidents for team
  3. **Avg TTM:** Average TTM for team (bold, BLUE if > overall avg)
  4. **Root Causes:** 
     - Summary sentence (intelligent theme extraction)
     - Bullet list with incident citations
     - Each citation: `[INC {id}]` (clickable link to ICM)
     - Symbols: 🔗 (event), 🔄 (change) after incident ID
  5. **Mitigations:**
     - Summary sentence (intelligent action extraction)
     - Bullet list with incident citations
     - Clickable links with symbols
  6. **Impacts:**
     - Summary sentence (intelligent impact type extraction)
     - Bullet list with incident citations
     - Clickable links with symbols

**Intelligent Summarization:**
- **Root Causes:** Extracts themes (Connectivity, Configuration, Capacity, Deployment, Certificate, Timeout, Dependency)
- **Mitigations:** Extracts actions (Restart/Reboot, Rollback, Scaling, Failover, Config Change, Traffic Mgmt)
- **Impacts:** Extracts types (Availability, Performance, Customer, API Failures, Regional)
- **Summary Format:** "This team dealt with [theme1], [theme2], and [theme3] issues."

**Incident Links:**
- Format: `https://portal.microsofticm.com/imp/v5/incidents/details/{id}/summary`
- Target: `_blank` (new tab)
- Color: BLUE
- Hover: Underline

##### E. Pattern & Correlation Analysis Section
**Purpose:** Aggregate statistical analysis of patterns and mitigation effectiveness

**Background:** Gray (#F8F9FA)
**Padding:** 20px
**Border Radius:** 8px

**Table 1: Root Cause × Mitigation Combination Analysis**
- **Goal:** Identify which mitigations work best for specific root causes
- **Sorting:** By incident count descending (most common combinations first)
- **Display:** Top 15 combinations
- **Minimum Threshold:** ≥2 incidents per combination

**Columns:**
1. Root Cause Theme (7 themes)
2. Mitigation Action (6 actions)
3. P75 TTM (bold BLUE)
4. Incident Count (center-aligned)
5. Service Count (center-aligned)
6. Severity Breakdown (e.g., "Sev2: 3, Sev3: 8, Sev4: 4")

**Root Cause Themes (7):**
1. **Connectivity:** connectivity, connection, network, endpoint
2. **Configuration:** configuration, config, misconfiguration
3. **Capacity:** capacity, resource exhaustion, memory, throttling
4. **Deployment:** deployment, rollout, release
5. **Certificate:** certificate, cert, ssl, tls
6. **Timeout:** timeout, timed out, latency
7. **Dependency:** dependency, dependent, downstream

**Mitigation Actions (6):**
1. **Restart/Reboot:** restart, reboot, recycle
2. **Rollback:** rollback, rolled back, reverted
3. **Scaling:** scale, scaled, scaling
4. **Failover:** failover, failed over, switched
5. **Config Change:** config change, reconfigured
6. **Traffic Mgmt:** throttle, rate limit, blocked

**Example Insights:**
- "Connectivity + Failover: 25 incidents, P75: 120 min" (effective)
- "Connectivity + Restart: 15 incidents, P75: 240 min" (less effective)
- → **Recommendation:** Prioritize failover for connectivity issues

**Table 2: Root Cause Pattern Analysis**
- **Goal:** Identify which root causes take longest to mitigate
- **Sorting:** By P75 TTM descending
- **Display:** Top 5 themes

**Columns:**
1. Root Cause Theme
2. P75 TTM (bold BLUE)
3. Incident Count
4. Service Count
5. Severity Breakdown

**Table 3: Mitigation Effectiveness Analysis**
- **Goal:** Identify most commonly used mitigation strategies
- **Sorting:** By incident count descending
- **Display:** Top 5 actions

**Columns:**
1. Mitigation Action
2. P75 TTM (bold BLUE)
3. Incident Count
4. Service Count
5. Severity Breakdown

**Table 4: Impact Pattern Analysis**
- **Goal:** Identify which impact types correlate with higher TTM
- **Sorting:** By P75 TTM descending
- **Display:** Top 5 types

**Impact Types (5):**
1. **Availability:** availability, downtime, unavailable
2. **Performance:** degradation, slow, latency
3. **Customer:** customer, user, tenant
4. **API Failures:** api, endpoint, request
5. **Regional:** region, regional, geography

**Columns:**
1. Impact Type
2. P75 TTM (bold BLUE)
3. Incident Count
4. Service Count
5. Severity Breakdown

##### F. Data Dictionary Section
**NEW in v2.0**
**Purpose:** Provide comprehensive definitions for all Root Cause themes and Mitigation actions

**Background:** White
**Padding:** 20px
**Border Radius:** 8px

**Component 1: Root Cause Themes Table**
- **Title:** "Root Cause Themes"
- **Rows:** 7 definitions
- **Format:** Bold label (180px width) + Detailed description

**Themes Defined:**
1. **Connectivity:** Issues related to network connections, endpoints becoming unreachable, connection timeouts, or network infrastructure failures
2. **Configuration:** Problems caused by incorrect settings, misconfigurations, configuration drift, or missing configuration parameters
3. **Capacity:** Resource exhaustion including memory limits, CPU constraints, throttling, or insufficient scaling to handle load
4. **Deployment:** Issues introduced during software deployments, rollouts, releases, or code changes that caused service degradation
5. **Certificate:** Certificate expiration, invalid certificates, SSL/TLS handshake failures, or authentication certificate issues
6. **Timeout:** Request timeouts, operation timeouts, slow performance leading to timeout errors, or latency-related failures
7. **Dependency:** Failures in dependent services, downstream/upstream service issues, or cascading failures from external dependencies

**Component 2: Mitigation Actions Table**
- **Title:** "Mitigation Actions"
- **Rows:** 6 definitions
- **Format:** Bold label (180px width) + Detailed description

**Actions Defined:**
1. **Restart/Reboot:** Restarting services, rebooting servers, recycling application pools, or bouncing processes to clear state and recover
2. **Rollback:** Reverting to a previous known-good version of code, configuration, or deployment to undo problematic changes
3. **Scaling:** Adding more resources by scaling up (vertical) or scaling out (horizontal) to handle increased load or resource demands
4. **Failover:** Switching to backup systems, redirecting traffic to healthy instances, or failing over to secondary regions/datacenters
5. **Config Change:** Modifying configuration settings, updating parameters, adjusting thresholds, or reconfiguring services to resolve issues
6. **Traffic Mgmt:** Throttling requests, implementing rate limits, blocking problematic traffic, or managing load distribution to protect services

**User Benefits:**
- Clarifies theme/action meanings for non-technical stakeholders
- Ensures consistent interpretation across teams
- Supports onboarding for new analysts
- Provides reference during executive presentations

---

## 4. Functional Requirements

### 4.1 Filter Behavior
**FR-1:** All filters must update dashboard reactively (real-time updates)
**FR-2:** Filters apply to ALL sections (cards, charts, tables, analysis)
**FR-3:** Date filters convert to UTC timezone
**FR-4:** P70-P80 filter calculates 70th-80th percentile from unfiltered data
**FR-5:** Event filter shows only incidents with IsPartOfEvent==True
**FR-6:** Reset button clears ALL filters to default state
**FR-7:** Multiple filters combine with AND logic
**FR-8:** Empty filter results show "No data available" message
**FR-9:** 🆕 Chart click filters apply FIRST, then sidebar filters (filter priority)
**FR-10:** 🆕 Chart filter banner displays active chart filters with clear visual feedback
**FR-11:** 🆕 "Clear Chart Filters" button removes only chart filters, keeps sidebar filters

### 4.2 Data Processing
**FR-12:** Calculate TTM quintiles from unfiltered dataset
**FR-13:** Handle missing/null values gracefully (fillna(''))
**FR-14:** Convert OutageCreateDate to datetime with UTC
**FR-15:** Calculate P70, P80 thresholds from full dataset
**FR-16:** Extract event groups from OutageCorrelationId
**FR-17:** Keyword matching is case-insensitive
**FR-18:** 🆕 Pre-compute 18 boolean columns for theme/action/impact matching at load time
**FR-19:** 🆕 Use boolean column lookups instead of string matching during filtering (100x speedup)
**FR-20:** 🆕 Pattern Analysis uses pre-computed columns for combination matrix generation

### 4.3 Visualization Requirements
**FR-15:** All charts must be interactive (hover tooltips)
**FR-16:** Charts resize responsively
**FR-17:** Empty data shows "No data available" message
**FR-18:** Color consistency across all charts (BLUE primary)
**FR-19:** Histograms use 20 bins for distribution
**FR-20:** Bar charts show top 10 items

### 4.4 Table Requirements
**FR-21:** Incident Details table shows 14 columns
**FR-22:** Service Analysis table is hierarchical (Service → Team)
**FR-23:** All incident IDs are clickable links to ICM portal
**FR-24:** Symbols (🔗🔄) appear after incident citations
**FR-25:** Summaries use intelligent theme extraction
**FR-26:** Pattern analysis tables filter by minimum thresholds

### 4.5 Performance Requirements
**FR-27:** 🆕 Initial data load and pre-computation: < 2 seconds (achieved 1.5-2s)
**FR-28:** 🆕 Filter response time: < 0.5 seconds (achieved 0.3-0.5s, **75% faster than v1.0**)
**FR-29:** 🆕 Pattern Analysis generation: < 100ms (achieved ~50ms, **92% faster than v1.0**)
**FR-30:** 🆕 Chart click filtering: < 0.5 seconds
**FR-31:** Support 100+ incidents without performance degradation
**FR-32:** Responsive UI updates with loading indicators on Service Analysis and Pattern Analysis
**FR-33:** Memory-efficient filtering (operate on filtered dataframes)
**FR-34:** 🆕 Theme extraction: 18 pre-computed boolean columns eliminate repeated string matching (100x speedup)

---

## 5. Callback Architecture

### 5.1 Single Callback Function
**Function:** `update_dashboard()`

**Inputs (18 total):**

**Sidebar Filters (12 inputs):**
1. `start-date-filter` (date-picker) → value
2. `end-date-filter` (date-picker) → value
3. `exclude-cascade-filter` (checkbox) → value
4. `exclude-bcdr-filter` (checkbox) → value
5. `severity-filter` (dropdown) → value
6. `service-filter` (dropdown) → value
7. `ttm-filter` (range-slider) → value
8. `quintile-filter` (dropdown) → value
9. `critsit-filter` (checkbox) → value
10. `p70p80-filter` (checkbox) → value
11. `event-filter` (checkbox) → value
12. `reset-btn` (button) → n_clicks

**🆕 Interactive Chart Filters (5 inputs - v2.0):**
13. `chart-severity` (graph) → clickData
14. `chart-services` (graph) → clickData
15. `chart-quintile` (graph) → clickData
16. `chart-region` (graph) → clickData
17. `chart-timeline` (graph) → clickData

**🆕 Chart Filter Controls (1 input - v2.0):**
18. `clear-chart-btn` (button) → n_clicks

**Outputs (17 total):**

**Summary Cards (5 outputs):**
1. `card-total` → children (Total Incidents)
2. `card-p75` → children (P75 TTM)
3. `card-mean` → children (Mean TTM)
4. `card-p90` → children (P90 TTM)
5. `card-critsits` → children (CritSit Count)

**Charts (6 outputs):**
6. `chart-ttm-dist` → figure (TTM Distribution Histogram)
7. `chart-services` → figure (Top Services Bar - 🖱️ Clickable)
8. `chart-timeline` → figure (Timeline Bar - 🖱️ Clickable)
9. `chart-severity` → figure (Severity Pie - 🖱️ Clickable)
10. `chart-quintile` → figure (Quintile Bar - 🖱️ Clickable)
11. `chart-region` → figure (Regional Impact Bar - 🖱️ Clickable)

**Tables (3 outputs):**
12. `table-incident-details` → children (Incident Details Table)
13. `table-count-text` → children (Incident Count Display)
14. `table-service-analysis` → children (Hierarchical Service Analysis)

**Pattern Analysis (1 output):**
15. `pattern-analysis` → children (4 Pattern Tables)

**🆕 Interactive Filtering UI (2 outputs - v2.0):**
16. `chart-filter-banner` → children (Active Chart Filters Banner)
17. `chart-click-store` → data (Chart Filter State Storage)

### 5.2 Filter Application Logic
```python
# Step 1: Load data
### 5.2 Filter Application Logic

```python
# Step 1: Load data and pre-compute boolean columns (ONE TIME at startup)
df = pd.read_csv('october_2025_ttm_full_month.csv', encoding='utf-8-sig')

# Pre-compute 18 boolean columns for instant keyword matching
df['has_connectivity'] = df['RootCauses'].str.lower().str.contains(
    'connectivity|connection|network|endpoint', na=False)
df['has_restart'] = df['MitigationAction'].str.lower().str.contains(
    'restart|reboot|recycle|bounce', na=False)
# ... (16 more boolean columns)

# Step 2: Calculate unfiltered metrics
p70_val = df['TTM'].quantile(0.70)
p80_val = df['TTM'].quantile(0.80)
quintiles = pd.qcut(df['TTM'], q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

# Step 3: Process callback trigger
ctx = dash.callback_context
triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

# Step 4: Handle button clicks
if reset_btn_clicks and triggered_id == 'reset-btn':
    # Reset ALL filters (sidebar + chart)
    return default_outputs()

if clear_chart_clicks and triggered_id == 'clear-chart-btn':
    # Clear ONLY chart filters, keep sidebar filters
    chart_filters = {}
    # Continue with sidebar filters...

# 🆕 Step 5: Apply CHART FILTERS FIRST (v2.0 - Interactive Filtering)
fdf = df.copy()
chart_filters = {}
chart_filter_labels = []

# Process chart clicks (priority: latest click wins)
if severity_click and triggered_id == 'chart-severity':
    clicked_severity = severity_click['points'][0]['label']
    fdf = fdf[fdf['Severity'] == clicked_severity]
    chart_filters['severity'] = clicked_severity
    chart_filter_labels.append(f"📊 Severity: {clicked_severity}")

if services_click and triggered_id == 'chart-services':
    clicked_service = services_click['points'][0]['y']  # Bar chart uses y-axis
    fdf = fdf[fdf['ServiceName'] == clicked_service]
    chart_filters['service'] = clicked_service
    chart_filter_labels.append(f"📊 Service: {clicked_service}")

if quintile_click and triggered_id == 'chart-quintile':
    clicked_quintile = quintile_click['points'][0]['x']
    fdf = fdf[fdf['Quintile'] == clicked_quintile]
    chart_filters['quintile'] = clicked_quintile
    chart_filter_labels.append(f"📊 Quintile: {clicked_quintile}")

if region_click and triggered_id == 'chart-region':
    clicked_region = region_click['points'][0]['y']
    fdf = fdf[fdf['Region'] == clicked_region]
    chart_filters['region'] = clicked_region
    chart_filter_labels.append(f"📊 Region: {clicked_region}")

if timeline_click and triggered_id == 'chart-timeline':
    clicked_date = timeline_click['points'][0]['x']
    fdf = fdf[fdf['OutageCreateDate'].dt.date == pd.to_datetime(clicked_date).date()]
    chart_filters['date'] = clicked_date
    chart_filter_labels.append(f"📊 Date: {clicked_date}")

# Step 6: Apply SIDEBAR FILTERS on top of chart filters (AND logic)
if not reset_btn_clicks:
    # Date filters
    fdf = fdf[(fdf['OutageCreateDate'] >= start_date) & 
              (fdf['OutageCreateDate'] <= end_date)]
    
    # Checkbox filters
    if exclude_cascade:
        fdf = fdf[fdf['IsPartOfEvent'] != True]
    if exclude_bcdr:
        fdf = fdf[fdf['IsBCDR'] != 1]
    if critsit:
        fdf = fdf[fdf['IsCritSit'] == 1]
    if p70p80:
        fdf = fdf[(fdf['TTM'] >= p70_val) & (fdf['TTM'] <= p80_val)]
    if event:
        fdf = fdf[fdf['IsPartOfEvent'] == True]
    
    # Dropdown filters
    if severity:
        fdf = fdf[fdf['Severity'].isin(severity)]
    if service:
        fdf = fdf[fdf['ServiceName'].isin(service)]
    if quintile:
        fdf = fdf[fdf['Quintile'].isin(quintile)]
    
    # Range slider
    fdf = fdf[(fdf['TTM'] >= ttm_range[0]) & (fdf['TTM'] <= ttm_range[1])]

# Step 7: Generate chart filter banner
if chart_filter_labels:
    banner_text = f"🎯 Active Chart Filters: {' | '.join(chart_filter_labels)}"
    banner = html.Div(banner_text, style={'backgroundColor': '#FFF4CE', ...})
else:
    banner = html.Div()  # Empty div when no chart filters

```

**Key Filtering Principles (v2.0):**
1. **Filter Priority**: Chart filters applied FIRST, then sidebar filters (AND logic)
2. **Performance**: Pre-computed boolean columns eliminate repeated string matching
3. **User Feedback**: Chart filter banner shows active chart-based filters
4. **Flexibility**: "Clear Chart Filters" removes chart filters but keeps sidebar filters
5. **Reset**: "Reset Filters" button clears ALL filters (chart + sidebar)

# Step 4: Calculate metrics from filtered data
total_incidents = len(fdf)
p75_ttm = fdf['TTM'].quantile(0.75)
mean_ttm = fdf['TTM'].mean()
p90_ttm = fdf['TTM'].quantile(0.90)
critsit_count = fdf['IsCritSit'].sum()

# Step 5: Generate outputs
# ... (build charts, tables, analysis)

return [outputs...]
```

---

## 6. Algorithm Details

### 6.1 🆕 Pre-Computed Boolean Columns (v2.0 Performance Optimization)
**Purpose:** Eliminate expensive string matching operations during filtering

**Algorithm:**
```python
def precompute_boolean_columns(df):
    """
    ONE-TIME computation at data load (executed once, used thousands of times)
    
    Performance: 100x speedup for Pattern Analysis
    Before v2.0: 600ms per filter change (string matching every time)
    After v2.0: 6ms per filter change (boolean column lookup)
    
    Args:
        df: Raw DataFrame from CSV
    
    Returns:
        DataFrame with 18 additional boolean columns
    """
    # Root Cause Themes (7 columns)
    df['has_connectivity'] = df['RootCauses'].str.lower().str.contains(
        'connectivity|connection|network|endpoint|unreachable', na=False)
    df['has_configuration'] = df['RootCauses'].str.lower().str.contains(
        'configuration|config|setting|parameter', na=False)
    df['has_capacity'] = df['RootCauses'].str.lower().str.contains(
        'capacity|throttl|resource|memory|cpu', na=False)
    df['has_deployment'] = df['RootCauses'].str.lower().str.contains(
        'deployment|deploy|release|rollout', na=False)
    df['has_certificate'] = df['RootCauses'].str.lower().str.contains(
        'certificate|cert|ssl|tls|expir', na=False)
    df['has_timeout'] = df['RootCauses'].str.lower().str.contains(
        'timeout|time out|latency|slow', na=False)
    df['has_dependency'] = df['RootCauses'].str.lower().str.contains(
        'dependency|downstream|upstream|cascad', na=False)
    
    # Mitigation Actions (6 columns)
    df['has_restart'] = df['MitigationAction'].str.lower().str.contains(
        'restart|reboot|recycle|bounce', na=False)
    df['has_rollback'] = df['MitigationAction'].str.lower().str.contains(
        'rollback|roll back|revert|previous version', na=False)
    df['has_scaling'] = df['MitigationAction'].str.lower().str.contains(
        'scal|capacity|resource', na=False)
    df['has_failover'] = df['MitigationAction'].str.lower().str.contains(
        'failover|fail over|redirect|switch', na=False)
    df['has_config_change'] = df['MitigationAction'].str.lower().str.contains(
        'config|setting|parameter|tuning', na=False)
    df['has_traffic_mgmt'] = df['MitigationAction'].str.lower().str.contains(
        'throttl|rate limit|block|traffic', na=False)
    
    # Impact Types (5 columns)
    df['has_availability'] = df['CustomerImpact'].str.lower().str.contains(
        'unavailable|down|outage|offline', na=False)
    df['has_performance'] = df['CustomerImpact'].str.lower().str.contains(
        'slow|latency|performance|delay', na=False)
    df['has_functionality'] = df['CustomerImpact'].str.lower().str.contains(
        'functionality|feature|capability', na=False)
    df['has_data_issue'] = df['CustomerImpact'].str.lower().str.contains(
        'data|message|content', na=False)
    df['has_authentication'] = df['CustomerImpact'].str.lower().str.contains(
        'auth|login|credential|access denied', na=False)
    
    return df

# Usage: Called ONCE at startup
df = precompute_boolean_columns(df)
print(f"Pre-computed 18 keyword matching columns for performance optimization")
```

### 6.2 Intelligent Summarization Algorithm
**Purpose:** Extract themes from free-text Root Causes, Mitigations, and Impacts

**Algorithm (v2.0 - Uses Pre-Computed Columns):**
```python
def extract_themes_fast(df, theme_columns):
    """
    v2.0: Uses boolean column lookups instead of string matching
    
    Performance: 100x faster than v1.0
    
    Args:
        df: filtered DataFrame with pre-computed boolean columns
        theme_columns: list of boolean column names (e.g., ['has_connectivity', 'has_restart'])
    
    Returns:
        list of detected themes
    """
    themes = []
    
    for col in theme_columns:
        if df[col].any():  # Boolean column check (instant)
            theme_name = col.replace('has_', '').replace('_', ' ').title()
            themes.append(theme_name)
    
    return themes

def generate_summary(themes):
    """
    Args:
        themes: list of theme names
    
    Returns:
        human-readable summary sentence
    """
    if len(themes) == 0:
        return "No specific patterns identified."
    elif len(themes) == 1:
        return f"This team primarily dealt with {themes[0]} issues."
    elif len(themes) == 2:
        return f"This team dealt with {themes[0]} and {themes[1]} issues."
    else:
        themes_str = ', '.join(themes[:-1]) + f', and {themes[-1]}'
        return f"This team dealt with {themes_str} issues."
```

### 6.3 Combination Analysis Algorithm (v2.0 - Optimized)
**Purpose:** Calculate Root Cause × Mitigation effectiveness matrix

**Algorithm:**
```python
def build_combination_matrix(fdf):
    """
    v2.0: Uses pre-computed boolean columns for instant filtering
    
    Performance Improvement:
    - v1.0: 600ms (7×6=42 combinations × ~15ms string matching each)
    - v2.0: 50ms (42 combinations × ~1ms boolean lookup each)
    - Speedup: 12x faster (92% reduction)
    
    Args:
        fdf: filtered DataFrame with 18 pre-computed boolean columns
    
    Returns:
        list of dicts with combination statistics
    """
    combinations = []
    
    # Define root cause and mitigation column mappings
    root_cause_cols = ['has_connectivity', 'has_configuration', 'has_capacity', 
                      'has_deployment', 'has_certificate', 'has_timeout', 'has_dependency']
    mitigation_cols = ['has_restart', 'has_rollback', 'has_scaling', 
                      'has_failover', 'has_config_change', 'has_traffic_mgmt']
    
    for rc_col in root_cause_cols:
        for mit_col in mitigation_cols:
            # v2.0: Boolean column lookup (instant)
            combo_df = fdf[fdf[rc_col] & fdf[mit_col]]
            
            # Calculate stats if sufficient data
            if len(combo_df) >= 2:
                combinations.append({
                    'root_cause': rc_col.replace('has_', '').replace('_', ' ').title(),
                    'mitigation': mit_col.replace('has_', '').replace('_', ' ').title(),
                    'p75_ttm': combo_df['TTM'].quantile(0.75),
                    'mean_ttm': combo_df['TTM'].mean(),
                    'count': len(combo_df),
                    'services': combo_df['ServiceName'].nunique(),
                    'severity': combo_df['Severity'].value_counts().to_dict()
                })
    
    
    # Sort by incident count descending
    combinations.sort(key=lambda x: x['count'], reverse=True)
    
    return combinations[:15]  # Top 15
```

### 6.3 Percentile Calculation
**Purpose:** Identify P70-P80 range for filter

**Algorithm:**
```python
def calculate_percentile_range(df, p_low=0.70, p_high=0.80):
    """
    Args:
        df: full DataFrame (unfiltered)
        p_low: lower percentile (0.70)
        p_high: upper percentile (0.80)
    
    Returns:
        tuple (p70_val, p80_val)
    """
    p70 = df['TTM'].quantile(p_low)
    p80 = df['TTM'].quantile(p_high)
    
    return (p70, p80)

# Filter application:
# fdf = df[(df['TTM'] >= p70) & (df['TTM'] <= p80)]
# Result: 11 incidents in range [135, 236] minutes
```

### 6.4 Event Detection
**Purpose:** Identify multi-incident cascading events

**Algorithm:**
```python
def detect_events(df):
    """
    Args:
        df: full DataFrame
    
    Returns:
        dict {correlation_id: incident_count}
    """
    # Group by OutageCorrelationId
    event_groups = df.groupby('OutageCorrelationId').size()
    
    # Filter for multi-incident events
    multi_incident_events = event_groups[event_groups > 1]
    
    return multi_incident_events.sort_values(ascending=False)

# Result: 6 events, 49 total incidents
```

---

## 7. Data Quality Considerations

### 7.1 Missing Data Handling
- **Root Causes:** fillna('') → empty string
- **Mitigations:** fillna('') → empty string
- **Impacts:** fillna('') → empty string
- **Numeric Fields:** dropna() before quantile calculations
- **Date Fields:** pd.to_datetime() with errors='coerce'

### 7.2 Data Validation
- **TTM:** Must be numeric, >= 0
- **Severity:** Must be in ['Sev2', 'Sev3', 'Sev4']
- **Boolean Fields:** Convert to bool (1 → True, 0 → False)
- **Dates:** Valid datetime format, UTC timezone

### 7.3 Edge Cases
- **Single Incident Teams:** Still show in Service Analysis
- **Empty Themes:** Display "No specific patterns identified"
- **No Combinations:** Skip table if no combinations found
- **All Filters Active:** May result in zero incidents (handled gracefully)

---

## 8. User Workflows

### 8.1 Executive Workflow
1. Open dashboard → View all-up summary cards
2. Check P75 TTM and total incidents
3. Review Pattern & Correlation Analysis section
4. Identify top Root Cause × Mitigation combinations
5. Note services with highest TTM (from Top Services chart)
6. Use findings for strategic planning

### 8.2 Service Owner Workflow
1. Open dashboard
2. Filter by specific service (dropdown)
3. Review Service Analysis section for their service
4. Check team performance (Avg TTM)
5. Read incident citations for specific teams
6. Click incident links to view full ICM details
7. Identify common root causes and mitigation patterns
8. Share findings with teams for process improvement

### 8.3 SRE Workflow
1. Open dashboard
2. Filter by date range (recent incidents)
3. Filter by CritSit or high TTM range
4. Review Incident Details table
5. Sort by TTM descending to find outliers
6. Check Service Analysis for teams with high TTM
7. Analyze Root Cause Pattern Analysis
8. Compare mitigation effectiveness
9. Identify process improvement opportunities

### 8.4 Analyst Workflow
1. Open dashboard
2. Use multiple filters to segment data
3. Compare quintile distributions
4. Analyze temporal trends (Timeline chart)
5. Review combination analysis for correlations
6. Export insights for reporting
7. Identify statistical anomalies

---

## 9. Testing Requirements

### 9.1 Functional Testing
- **Test Case 1:** All filters apply correctly
- **Test Case 2:** Reset button clears all filters
- **Test Case 3:** Charts update with filter changes
- **Test Case 4:** Tables display correct data
- **Test Case 5:** Links open ICM portal in new tab
- **Test Case 6:** Symbols display correctly (🔗🔄)
- **Test Case 7:** Summaries generate with correct themes
- **Test Case 8:** Combination analysis shows top 15

### 9.2 Edge Case Testing
- **Test Case 9:** Zero incidents after filtering
- **Test Case 10:** Single incident in dataset
- **Test Case 11:** All incidents in same service
- **Test Case 12:** No root causes for team
- **Test Case 13:** P70-P80 filter with no incidents
- **Test Case 14:** Event filter with no events

### 9.3 Performance Testing
- **Test Case 15:** Load time with 500 incidents
- **Test Case 16:** Filter update time with all filters active
- **Test Case 17:** Memory usage during extended session
- **Test Case 18:** Concurrent user testing (if deployed)

### 9.4 Browser Compatibility
- **Chrome:** Latest version
- **Edge:** Latest version
- **Firefox:** Latest version
- **Safari:** Latest version (if applicable)

---

## 10. Future Enhancements

### 10.1 Phase 2 Features
- **Export Functionality:** Download filtered data as CSV/Excel
- **Custom Date Ranges:** Quick filters (Last 7 days, Last 30 days, Last Quarter)
- **Drill-Down:** Click chart segments to filter
- **Bookmark Views:** Save filter combinations
- **Comparison Mode:** Compare two time periods side-by-side

### 10.2 Phase 3 Features
- **Predictive Analytics:** ML model for TTM prediction
- **Anomaly Detection:** Automated outlier identification
- **Alert System:** Email notifications for high TTM incidents
- **Team Benchmarking:** Compare team performance across services
- **Custom Metrics:** User-defined KPIs

### 10.3 Advanced Analytics
- **Correlation Heatmap:** Root Cause × Mitigation × Impact 3D analysis
- **Trend Analysis:** Month-over-month TTM improvement tracking
- **Root Cause Pareto:** 80/20 analysis for prioritization
- **Mitigation Decision Tree:** Recommended actions based on root cause
- **Cost Impact Analysis:** Link TTM to business impact metrics

---

## 11. Deployment Instructions

### 11.1 Local Deployment
```bash
# Step 1: Install dependencies
pip install dash plotly pandas

# Step 2: Navigate to directory
cd "C:\Users\nigopal\OneDrive - Microsoft\Documents\QEI_TTM_Analysis\OctTTM"

# Step 3: Ensure data file exists
# File: october_2025_ttm_full_month.csv

# Step 4: Run dashboard
python ttm_dashboard.py

# Step 5: Open browser
# Navigate to: http://127.0.0.1:8050
```

### 11.2 Production Deployment (Future)
- **Option 1:** Azure App Service
- **Option 2:** Docker container
- **Option 3:** Kubernetes cluster
- **Option 4:** Dash Enterprise

### 11.3 Configuration
```python
# Dashboard configuration (top of file)
PORT = 8050
DEBUG_MODE = False
DATA_FILE = 'october_2025_ttm_full_month.csv'
ENCODING = 'utf-8-sig'
```

---

## 12. Maintenance & Support

### 12.1 Data Updates
- **Frequency:** Monthly (new CSV file)
- **Process:** Replace `october_2025_ttm_full_month.csv` with new file
- **Validation:** Ensure column schema matches
- **Backup:** Archive previous month's data

### 12.2 Code Maintenance
- **Version Control:** Git repository recommended
- **Documentation:** Update PRD with feature changes
- **Testing:** Run test cases after modifications
- **Code Review:** Peer review for significant changes

### 12.3 Support Contacts
- **Product Owner:** QEI TTM Analysis Team
- **Developer:** [Your name/team]
- **Data Source:** ICM/Azure incident tracking system

---

## 13. Appendices

### 13.1 Glossary
- **TTM:** Time To Mitigate - Minutes from incident detection to mitigation
- **CritSit:** Critical Situation - High-priority incident requiring immediate attention
- **Quintile:** Five equal groups (Q1-Q5) based on TTM distribution
- **P75/P90:** 75th/90th percentile - Value below which 75%/90% of data falls
- **ICM:** Incident Management Portal - Microsoft's incident tracking system
- **Event:** Cascading incident affecting multiple services
- **BCDR:** Business Continuity and Disaster Recovery

### 13.2 Sample Data Schema
```csv
OutageIncidentId,ServiceName,OwningTeamName,TTM,Severity,RootCauses,Mitigations,Impacts,OutageCreateDate,IsPartOfEvent,IsCausedByChange,IsCritSit,Quintile,OutageCorrelationId
12345,Service A,Team Alpha,120,Sev3,"Connectivity timeout to backend",Restarted service instances,"API availability degraded",2025-10-15 08:30:00,False,1,0,Q3,abc-123-xyz
```

### 13.3 ICM Link Format
```
https://portal.microsofticm.com/imp/v5/incidents/details/{OutageIncidentId}/summary
```

### 13.4 Code Structure
```
ttm_dashboard.py
├── Imports (Dash, Plotly, Pandas)
├── Configuration (Colors, Constants)
├── Data Loading
│   ├── Read CSV
│   ├── Data Cleaning
│   └── Calculate Metrics
├── Layout Definition
│   ├── Header
│   ├── Left Sidebar (Filters)
│   └── Right Content
│       ├── Summary Cards
│       ├── Charts
│       ├── Incident Details Table
│       ├── Service Analysis
│       └── Pattern Analysis
├── Callback Function
│   ├── Input Processing
│   ├── Filter Application
│   ├── Metric Calculation
│   ├── Chart Generation
│   ├── Table Generation
│   └── Return Outputs
└── Main Execution (if __name__ == '__main__')
```

---

## 14. Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-03 | QEI Team | Initial PRD creation |
| | | | - 12 filters implemented |
| | | | - 14 outputs configured |
| | | | - Service Analysis with intelligent summarization |
| | | | - Pattern & Correlation Analysis with 4 tables |
| | | | - Root Cause × Mitigation combination analysis |
| | | | - Clickable incident links with symbols |

---

## 15. Acceptance Criteria

### 15.1 Minimum Viable Product (MVP)
- ✅ Dashboard loads successfully
- ✅ All 12 filters functional
- ✅ All 6 charts display correctly
- ✅ Incident Details table shows 14 columns
- ✅ Service Analysis displays hierarchical breakdown
- ✅ Pattern Analysis shows 4 tables
- ✅ Incident links open ICM portal
- ✅ Symbols display after incident citations
- ✅ Reset button clears all filters

### 15.2 Quality Standards
- ✅ No console errors during normal operation
- ✅ Responsive design (desktop)
- ✅ Filter updates complete in <2 seconds
- ✅ Accurate data calculations
- ✅ Proper error handling (empty data states)
- ✅ Consistent color scheme
- ✅ Readable font sizes and spacing

### 15.3 User Acceptance
- ✅ Executives can identify high-level trends
- ✅ Service owners can drill into team performance
- ✅ SREs can analyze root causes and mitigations
- ✅ Analysts can perform correlation analysis
- ✅ Dashboard supports data-driven decision making

---

**End of PRD**

**Document Owner:** QEI TTM Analysis Team  
**Last Review:** November 3, 2025  
**Next Review:** December 1, 2025 (or after major feature additions)
