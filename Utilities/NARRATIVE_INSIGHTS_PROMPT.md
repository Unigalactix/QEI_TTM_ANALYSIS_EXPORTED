# Narrative Insights Analysis Prompt

## Overview
This prompt generates a comprehensive narrative analysis of TTM incident data by mining actual incident descriptions, symptoms, impacts, and resolution approaches to understand "what really happened" and why high TTM incidents took so long.

---

## Prompt for Agent

Please analyze the [MONTH] [YEAR] TTM data in `[MonthFolder]/[month]_[year]_ttm_full_month.csv` and create a comprehensive "NarrativeInsights" analysis.

### Directory Structure to Create:
```
[MonthFolder]/NarrativeInsights/
  ├── check_columns.py           (Verify available narrative columns)
  ├── get_narratives.py          (Extract top incidents with detailed narratives)
  ├── analyze_narratives.py      (Main analysis script)
  ├── top_20_high_ttm_incidents.csv (High TTM incident subset)
  ├── narrative_analysis_data.json (Structured output data)
  └── NarrativeInsight.md        (Final comprehensive report)
```

---

## Step 1: Column Verification (check_columns.py)

Create a script that:
- Loads the month's CSV file
- Checks availability of narrative columns:
  * `TTUpdateSummary`, `PublicSummary`, `ImpactStartDescription`
  * `Impacts`, `Symptoms`, `RootCauses`, `Mitigation`
  * `HowFixed`, `DetectionDescription`, `DiagnosisDescription`
  * `MitigationDescription`, `RecoveryDescription`
  * `OutageDeclaredDescription`
- Reports % non-null for each column
- Shows sample from highest TTM incident

**Example output:**
```
Column availability:
TTUpdateSummary: 153 non-null (100.0%)
Impacts: 149 non-null (97.4%)
Symptoms: 147 non-null (96.1%)
...
```

---

## Step 2: Extract Top Incidents (get_narratives.py)

Create a script that:
- Identifies top 20 highest TTM incidents
- Extracts and displays detailed narratives:
  * `IncidentId`, `ServiceName`, `TTM`, `TTO`, `TTD`, `TTN`
  * `Severity`, `HowFixed`, `RootCauseCategory`
  * `Symptoms` (first 400 chars)
  * `Impacts` (first 400 chars)
  * `RootCauses` (first 400 chars)
  * `MitigationDescription` (if available)
- Saves subset to `top_20_high_ttm_incidents.csv`

**Purpose:** Allows manual review of actual incident narratives

---

## Step 3: Comprehensive Analysis (analyze_narratives.py)

Create a script that performs text mining analysis across 9 dimensions:

### A. INCIDENT CLASSIFICATION
- Define High TTM threshold (P80 or P75)
- Split dataset into **High TTM** vs **Normal TTM** cohorts
- Report counts and percentages

### B. DETECTION PATTERNS
Analyze `OutageDeclaredDescription` and `DetectionDescription` to extract themes:
- Auto-detected by BRAIN
- Customer-reported
- Monitor-detected
- Severity escalations (Sev0→Sev1, Sev1→Sev2)
- Impact scope (Global, Multi-region, etc.)

**Compare:** High TTM vs Normal TTM detection patterns

### C. RESOLUTION METHODS
Analyze `HowFixed` column distribution and average TTM for:
- Fixed with Ad-Hoc steps
- Fixed with TSG
- Fixed by Automation
- Transient (self-healing)
- External dependencies
- By Design
- Other

**Key Metric:** Average TTM per resolution method  
**Compare:** High TTM vs Normal TTM resolution patterns  
**Look for:** Paradoxes (e.g., automation taking longer than expected)

### D. MITIGATION TYPES
Classify `MitigationDescription` into categories:
- Restart/Reboot
- Rollback
- Manual intervention
- Automated recovery
- Failover
- Configuration change
- Scaling/Capacity
- VM/Node healing
- Code fix deployed

**Calculate:** Average TTM per mitigation type  
**Identify:** Fastest vs slowest approaches

### E. ROOT CAUSE ANALYSIS
Extract patterns from `RootCauses` and `RootCauseCategory`:
- Service/Code issues
- Capacity/Resource constraints
- Network/Connectivity
- Deployment-related
- Configuration errors
- External/Dependency issues
- Hardware failures

**Compare:** Root cause prevalence in High vs Normal TTM  
**Identify:** Preventable vs external causes

### F. SYMPTOM PATTERNS
Mine `Symptoms` field for common keywords:
- Connectivity failures
- Timeout errors
- Service unavailable
- Degraded performance
- API failures
- Authentication issues
- Database errors

**Compare:** Symptom language in High vs Normal TTM

### G. GEOGRAPHIC/REGIONAL CONCENTRATION
- Identify regions with multiple high-TTM incidents
- Look for datacenter-specific patterns
- Detect cascading regional failures
- Flag potential infrastructure issues

**Example Finding:** "Norway East datacenter had 7 of top 10 highest TTM incidents"

### H. SERVICE PATTERNS
- Services with most high-TTM incidents
- Services with most ad-hoc resolutions
- Services with best automation coverage
- Services lacking TSGs

**Purpose:** Identify where to invest in automation/TSGs

### I. TEMPORAL PATTERNS
- High TTM incidents by day of week
- High TTM incidents by hour of day (if timestamps available)
- Clustering of related incidents in time
- Weekend vs weekday patterns

---

## Step 4: Generate NarrativeInsight.md

Create a comprehensive markdown report with the following structure:

### Executive Summary
- Total incidents analyzed
- High TTM threshold (P75/P80) and incident count
- **Key Finding Headline** (e.g., "Ad-Hoc Recovery Dominates High TTM Incidents")
- Average TTM/TTO/TTD/TTN for dataset
- Month-specific context

### Section 1: Resolution Method Analysis
**High TTM Incidents - Resolution Methods:**
- List each method with:
  * Count and percentage
  * Average TTM and TTO
  * Example incident IDs
  * **Critical insights** (flag methods taking >10x longer)

**Normal TTM Incidents - Resolution Methods:**
- Same structure as above
- **Contrast and compare** with High TTM

**Key Insights:**
- Highlight resolution method effectiveness gaps
- Identify paradoxes and unexpected patterns
- Calculate effectiveness ratios (e.g., "Ad-hoc for high TTM is 15x slower than normal")

### Section 2: Regional/Geographic Analysis
- **Top N Regional Impacts** with incident counts
- For each region:
  * List high-TTM incidents with IDs
  * Describe pattern (e.g., cascading failures, infrastructure issue)
  * Extract common themes
- **Identify datacenter crisis patterns** (like Norway East thermal runaway)
- Note cross-region cascading failures

### Section 3: Service-Specific Patterns
- **Services Dominating High TTM:**
  * Count, avg TTM, common failure modes
- **Services with Effective Automation:**
  * Low TTM, high automation success rate
- **Services Needing Improvement:**
  * High ad-hoc rate, missing TSGs
- **Service failure mode patterns:**
  * Network services → connectivity
  * Storage services → capacity
  * Control planes → cascading impacts

### Section 4: Detection & Diagnosis Insights
- **Detection Method Effectiveness:**
  * BRAIN auto-detection vs customer reports
  * Time-to-Detect (TTD) patterns for high TTM
  * Late detection correlations
- **Diagnosis Patterns:**
  * Complex diagnosis → high TTM
  * Well-instrumented services → fast diagnosis
- **Detection Gaps:**
  * Where incidents were customer-reported instead of auto-detected

### Section 5: Root Cause Themes
- **Dominant Root Causes in High TTM:**
  * Frequency, avg TTM, examples
- **Root Cause Categories by Impact:**
  * Table showing category, count, avg TTM, % of total
- **Preventable vs External Causes:**
  * Code/config/deployment (preventable) vs natural disasters/external deps
- **Cascading Root Causes:**
  * Identify chains of causation

### Section 6: Mitigation Strategies
- **Fastest Mitigation Approaches:**
  * Methods with lowest avg TTM
  * When they're effective
- **Slowest Mitigation Approaches:**
  * Methods with highest avg TTM
  * Why they take longer
- **TSG Effectiveness:**
  * Where TSGs work well
  * Where TSGs are missing or inadequate
- **Automation Gaps:**
  * Manual interventions that should be automated
  * Automation that failed to work

### Section 7: Key Incidents Deep Dive
For top 5-10 highest TTM incidents, provide:
- **Incident ID & Service**
- **TTM / TTO / TTD / TTN**
- **Region & Severity**
- **What Happened:** Extract from Symptoms/Impacts (use direct quotes)
- **How It Was Fixed:** Extract from Mitigation/HowFixed
- **Why It Took So Long:** Analyze TTM drivers from narrative
- **Preventability:** Could this have been avoided?

**Example:**
> **Incident 695596942 - SQL Control Plane**  
> TTM: 3,035 minutes (50.6 hours) | TTO: 2,986 min | Severity: 1  
> **What Happened:** "Control plane operations failing across multiple regions..."  
> **How Fixed:** Fixed with Ad-Hoc steps after extensive troubleshooting  
> **Why So Long:** Complex dependency chain, required coordination across 4 teams...

### Section 8: Actionable Recommendations

Based on narrative analysis, provide specific recommendations:

1. **Where to Add/Improve Automation:**
   - Services with high ad-hoc rates
   - Repetitive manual mitigation patterns
   - Specific automation opportunities

2. **Where TSGs Are Missing or Ineffective:**
   - Services without TSGs experiencing high TTM
   - Outdated TSGs not covering observed scenarios

3. **Services Needing Better Instrumentation:**
   - High TTD services
   - Customer-reported instead of auto-detected

4. **Regional Infrastructure Issues:**
   - Datacenter patterns requiring attention
   - Network/power/cooling concerns

5. **Dependency Management Improvements:**
   - External dependency patterns
   - Cascading failure prevention

6. **Training Gaps:**
   - Where ad-hoc dominates (lack of runbooks/TSGs)
   - Complex scenarios needing expert knowledge

**Format recommendations as actionable bullets with specific examples**

---

## Step 5: Export Structured Data (narrative_analysis_data.json)

Save key findings as JSON for programmatic access:

```json
{
  "analysis_date": "YYYY-MM-DD",
  "dataset": "month_year_ttm_full_month.csv",
  "total_incidents": 117,
  "high_ttm_threshold_minutes": 190.0,
  "high_ttm_count": 24,
  "normal_ttm_count": 93,
  "avg_ttm_all": 293.1,
  "avg_tto_all": 41.2,
  "resolution_methods": {
    "high_ttm": {
      "Ad-Hoc": {"count": 12, "avg_ttm": 2227.7, "pct": 38.7},
      "TSG": {"count": 4, "avg_ttm": 687.5, "pct": 12.9},
      ...
    },
    "normal_ttm": {...}
  },
  "top_incidents": [
    {
      "incident_id": 695596942,
      "service": "SQL Control Plane",
      "ttm": 3035,
      "severity": 1,
      "how_fixed": "Ad-Hoc",
      "root_cause": "Dependency - Internal",
      "key_finding": "Complex dependency chain..."
    },
    ...
  ],
  "regional_patterns": {
    "regions_with_high_ttm": ["Norway East", "Switzerland North"],
    "datacenter_issues": [...]
  },
  "service_patterns": {
    "highest_ttm_services": [...],
    "services_needing_automation": [...]
  },
  "recommendations": [
    "Automate SQL Control Plane recovery procedures",
    "Add TSG for Service Bus failover scenarios",
    ...
  ]
}
```

---

## Output Requirements

### Data Integrity
- ✅ All analysis grounded in actual incident data (no hallucination)
- ✅ Use direct quotes from narrative fields where compelling
- ✅ Show percentages and averages for all comparisons
- ✅ Verify findings against raw CSV data

### Analysis Quality
- ✅ Highlight paradoxes and unexpected patterns
- ✅ Focus on actionable insights for leadership
- ✅ Compare High TTM vs Normal TTM cohorts throughout
- ✅ Identify "smoking gun" patterns (e.g., ad-hoc taking 15x longer)
- ✅ Explain WHY high TTM incidents took so long (from narratives)

### Presentation
- ✅ Clear section headers and structure
- ✅ Use tables, bullets, and formatting for readability
- ✅ Include example incident IDs for all claims
- ✅ Make recommendations specific and actionable

---

## Execution Steps

1. **Create folder:** `[MonthFolder]/NarrativeInsights/`
2. **Run:** `check_columns.py` to verify data quality
3. **Run:** `get_narratives.py` to extract top incidents
4. **Run:** `analyze_narratives.py` (may take several minutes)
5. **Review:** Console output for patterns
6. **Generate:** `NarrativeInsight.md` with findings
7. **Export:** `narrative_analysis_data.json` for structured access
8. **Verify:** All insights are grounded in data

---

## Important Notes

### This is TEXT MINING Analysis
- Goal: Understand "what really happened" from incident owner's perspective
- Method: Extract themes and patterns from narrative text fields
- Focus: Why high TTM incidents took so long (root causes in narratives)

### Look for Patterns Not Visible in Quantitative Metrics
- Resolution method effectiveness by incident type
- Detection delays caused by poor instrumentation
- Manual intervention patterns that could be automated
- Training gaps revealed by ad-hoc resolutions
- Infrastructure issues revealed by regional clustering

### Leadership Value
This analysis answers:
- "Why did our P75 TTM increase this month?" → Narrative explains which incidents and why
- "Where should we invest in automation?" → Ad-hoc patterns reveal gaps
- "Do our TSGs work?" → Resolution method analysis shows effectiveness
- "Are we detecting incidents fast enough?" → Detection pattern analysis
- "What's causing our worst incidents?" → Deep dive into top TTM drivers

---

## Example Usage

```bash
# For October 2025 analysis:
cd QEI_TTM_Analysis/OctTTM
mkdir NarrativeInsights
cd NarrativeInsights

# Create and run analysis scripts
python check_columns.py
python get_narratives.py
python analyze_narratives.py

# Review generated insights
cat NarrativeInsight.md
```

---

## Tips for Effective Analysis

1. **Focus on Contrasts:** High TTM vs Normal TTM differences are most revealing
2. **Use Percentages:** Raw counts can be misleading; always show proportions
3. **Quote Directly:** Real incident language is more powerful than summaries
4. **Identify Outliers:** Extreme cases often reveal systemic issues
5. **Think in Themes:** Group similar patterns rather than listing individual incidents
6. **Be Specific:** "Service X needs automation" < "Service X manual restarts average 4hrs, automate with Watchdog"
7. **Validate Findings:** Cross-check narrative conclusions with quantitative metrics

---

## Related Artifacts

- **PROMPT_1.md:** Main TTM analysis workflow (Steps 1-7)
- **ttm_query.csl:** Kusto query for incident data extraction
- **WhatIf Analysis:** Quantifies impact of preventing top events
- **Narrative Insights:** Explains WHY those events took so long (this analysis)

Together, these provide complete TTM understanding: **What happened** (quantitative) + **Why it happened** (qualitative)
