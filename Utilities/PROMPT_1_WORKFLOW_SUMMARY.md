# PROMPT_1.md Workflow Summary

**Last Updated:** 2025-11-03

---

## Complete Analysis Workflow (10 Steps)

### Step 1: Execute Query and Save Full Results
- Run `execute_kusto_query_to_csv.py` against Kusto cluster
- Save complete dataset: `{month}_{year}_ttm_full_month.csv`
- Verify incident count, column count (~375), column names preserved

### Step 2: Identify and Document Exclusions 🆕
- **Create `exclusions.md`** with detailed documentation
- **Exclusion Criteria:**
  * BCDR related incidents (planned drills)
  * EUAP region incidents (pre-production environment)
- Search keywords across: Symptoms, RootCauses, Impacts, ImpactedRegion, etc.
- Document each excluded incident with:
  * OutageID, Service, TTM, Severity
  * Title/Symptoms, Root Cause, Resolution
  * Exclusion Reason, Notes
- Generate summary statistics (exclusion rate, TTM impact)
- **Create `{month}_{year}_ttm_filtered.csv`** for downstream analysis
- Provide filter code (KQL and Python)

### Step 3: Generate Summary Statistics
**Uses FILTERED dataset (excludes BCDR/EUAP)**
- Total incidents (after exclusions)
- TTM P75/P50/P90 percentiles
- Severity distribution
- Top 5 services
- Auto-detection rate
- Geographic distribution
- Reference exclusions.md

### Step 4: Calculate Key Metrics
**Uses FILTERED dataset**
- P75 TTM, TTD, TTO, TTN
- S400/F500 customer impact
- CritSit cases
- PIR completion rate

### Step 5: Compare to Previous Month
**Uses FILTERED dataset**
- Load previous month's CSV
- Calculate month-over-month deltas
- Service pattern shifts
- Severity mix changes

### Step 6: Create Narrative File
**Uses FILTERED dataset**
- Tell the "story" of the month
- Connect incidents with proof (OutageIncidentIds)
- No hallucination - grounded in data
- Save as `{Month}_Narrative.md`

### Step 7: Create Analysis Documents
**Uses FILTERED dataset**
- `{Month}_TTM_Analysis_Summary.md`
- `{Month}_Incident_Breakdown.md`
- `{Month}_Comparison_Report.md`
- `{Month}_Narrative.md`
- Visualizations (4 PNG files)

### Step 8: Generate What-If Analysis
**Uses FILTERED dataset**
- Event system identification (RootResponsibleIncidentId)
- `WhatIf.md` with individual and cumulative impacts
- Visualizations:
  * `WhatIf_Cumulative_Impact.png` (2-panel)
  * `WhatIf_Cumulative_Marginal.png` (dual-axis)
- Answers: "What if we prevented top N events?"

### Step 9: Generate Narrative Insights Analysis 🆕
**Uses FILTERED dataset**
- **References:** `Utilities/NARRATIVE_INSIGHTS_PROMPT.md`
- **Create `NarrativeInsights/` folder:**
  * `check_columns.py` - Verify narrative column availability
  * `get_narratives.py` - Extract top 20 high TTM incidents
  * `analyze_narratives.py` - 9-dimension text mining
  * `create_narrative_report.py` - Generate report & JSON
  * `top_20_high_ttm_incidents.csv` - Top incidents export
  * `NarrativeInsight.md` - Executive report (8 sections)
  * `narrative_analysis_data.json` - Structured data
- **Analysis Dimensions:**
  1. Detection Patterns
  2. Resolution Methods (Ad-hoc vs TSG vs Automation)
  3. Mitigation Types
  4. Root Cause Themes
  5. Symptom Patterns
  6. Service Patterns
  7. Geographic Concentration
  8. Temporal Patterns
  9. Key Incidents Deep Dive
- **Answers:** "WHY did high TTM incidents take so long?"
- **Complements Step 8:** What-If = WHAT, Narrative = WHY

### Step 10: Generate PowerPoint Presentation 🆕
**Uses ALL previous outputs**
- **Create:** `{Month}_{Year}_TTM_Analysis.pptx`
- **Script:** `create_presentation_v2.py`
- **20-Slide Structure:**
  1. Title Slide
  2. Executive Summary (metrics, exclusions, key findings)
  3-7. Visualizations (distribution, services, timeline, severity, statistics)
  8. Month-over-Month Comparison (two-column layout)
  9-11. What-If Analysis (cumulative impact, marginal returns, findings)
  12. Exclusions (BCDR/EUAP documentation)
  13-15. Narrative Insights (resolution gap, service patterns, root causes)
  16. Recommendations (4 priority actions)
  17. Key Takeaways
  18-20. Appendix (title, data sources, definitions)
- **Design:**
  * Professional 16:9 widescreen format (13.333" × 7.5")
  * Microsoft blue color scheme (RGB 0, 120, 215)
  * Blue title bars with white text
  * Auto-scaled images (fit within bounds, maintain aspect ratio)
  * Proper text sizing (no overflow)
- **Dependencies:** python-pptx, pillow
- **Purpose:** Executive-ready presentation synthesizing all quantitative + qualitative findings

---

## Critical Workflow Rules

### 🚨 Exclusions Must Be Applied First
- **Step 2 creates filtered dataset**
- **Steps 3-9 MUST use filtered data**
- **Step 10 synthesizes all outputs**
- Exclusions prevent BCDR/EUAP from skewing production metrics

### 📊 Three Types of Analysis
**Quantitative (Steps 3-8):**
- Metrics, percentiles, counts
- What-If scenario modeling
- Answers: "What happened? How much impact?"

**Qualitative (Step 9):**
- Text mining of incident narratives
- Theme extraction, pattern identification
- Answers: "Why did it take so long? What's missing?"

**Synthesis (Step 10):**
- PowerPoint presentation
- Combines quantitative + qualitative insights
- Answers: "What's the complete story for leadership?"

### 🔗 Analysis Integration
1. **Exclusions (Step 2):** Clean the dataset
2. **What-If (Step 8):** Identify top impact events (quantitative)
3. **Narrative (Step 9):** Explain why those events took so long (qualitative)
4. **Presentation (Step 10):** Synthesize all findings for executive review

**Example:**
- What-If: "Top 5 events = 36% of P75 TTM"
- Narrative: "Because 46.7% used ad-hoc resolution vs 10% TSG"
- Presentation: Combines both insights with visualizations for leadership

---

## Expected Output Structure

```
{MonthFolder}/
├── {month}_{year}_ttm_full_month.csv      (Step 1: All incidents)
├── exclusions.md                           (Step 2: Documented exclusions)
├── {month}_{year}_ttm_filtered.csv        (Step 2: Clean dataset)
├── {Month}_Summary_Statistics.md          (Step 3)
├── {Month}_Key_Metrics.md                 (Step 4)
├── {Month}_vs_{PrevMonth}_Comparison.md   (Step 5)
├── {Month}_Narrative.md                   (Step 6)
├── {Month}_TTM_Analysis_Summary.md        (Step 7)
├── {Month}_Incident_Breakdown.md          (Step 7)
├── {Month}_TTM_Distribution.png           (Step 7)
├── {Month}_Top_Services.png               (Step 7)
├── {Month}_Daily_Timeline.png             (Step 7)
├── {Month}_Severity_Distribution.png      (Step 7)
├── WhatIf.md                              (Step 8)
├── WhatIf_Cumulative_Impact.png           (Step 8)
├── WhatIf_Cumulative_Marginal.png         (Step 8)
├── {Month}_{Year}_TTM_Analysis.pptx       (Step 10: PowerPoint)
├── create_presentation_v2.py              (Step 10: Generator script)
├── query_execution_log.json               (Step 1)
└── NarrativeInsights/                     (Step 9)
    ├── check_columns.py
    ├── get_narratives.py
    ├── analyze_narratives.py
    ├── create_narrative_report.py
    ├── top_20_high_ttm_incidents.csv
    ├── NarrativeInsight.md
    └── narrative_analysis_data.json
```

---

## Key Deliverables for Leadership

### Quantitative Insights (Steps 3-8)
- **P75 TTM trend** (are we improving?)
- **Top impact events** (where to focus prevention?)
- **Cascading impact** (how many outages per event?)
- **What-If scenarios** (if we fixed top 5, what's the gain?)

### Qualitative Insights (Step 9)
- **Resolution gaps** (ad-hoc vs TSG effectiveness)
- **Service automation needs** (which services lack TSGs?)
- **Detection gaps** (why aren't we auto-detecting?)
- **Root cause patterns** (preventable vs external)
- **Specific recommendations** (actionable next steps)

### Together They Answer:
- **What happened?** (Quantitative metrics)
- **How much impact?** (What-If analysis)
- **Why did it take so long?** (Narrative Insights)
- **What should we fix?** (Recommendations)

---

## Usage Example

```bash
# Run PROMPT_1.md.prompt.md in Copilot
# Agent will automatically execute all 10 steps

# Or run manually:
cd QEI_TTM_Analysis/OctTTM

# Step 1: Get data
python ../Utilities/execute_kusto_query_to_csv.py

# Step 2: Create exclusions
python create_exclusions.py  # (generates exclusions.md + filtered CSV)

# Steps 3-8: Use filtered CSV for all analysis
python create_summary_stats.py
python create_whatif.py
python create_whatif_plot.py

# Step 9: Generate Narrative Insights
cd NarrativeInsights
python check_columns.py
python get_narratives.py
python analyze_narratives.py
python create_narrative_report.py
cd ..

# Step 10: Generate PowerPoint Presentation
python create_presentation_v2.py
```

---

## Change Log

**2025-11-03:**
- ✅ Added Step 2: Exclusions (BCDR/EUAP filtering)
- ✅ Added Step 9: Narrative Insights (qualitative text mining)
- ✅ Added Step 10: PowerPoint Presentation (executive synthesis)
- ✅ Renumbered existing steps (old 2-7 → new 3-8)
- ✅ Added "Use filtered dataset" notes to all analysis steps
- ✅ Updated Expected Output Structure
- ✅ Created NARRATIVE_INSIGHTS_PROMPT.md reference
- ✅ Created create_presentation_v2.py with 16:9 format, auto-scaled images

**Previous versions:**
- Step 7 (What-If Analysis) added with event system cascade detection
- Event system definition updated to use RootResponsibleIncidentId
- Visualization requirements added (2 PNG files for What-If)

---

**For detailed Narrative Insights instructions, see:** `Utilities/NARRATIVE_INSIGHTS_PROMPT.md`
