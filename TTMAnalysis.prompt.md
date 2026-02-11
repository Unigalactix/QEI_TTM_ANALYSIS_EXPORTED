---
mode: agent
---
You are an agent. Keep your temperature low. You have full permission to run any python or powershell scripts you want within this QEI_TTM_Analysis directory. Please complete the steps listed in this file. Be sure you copy reference scripts from C:\Users\nigopal\OneDrive - Microsoft\Documents\QEI_TTM_Analysis\Utilities into any new folders you create if you need to edit them.
**NOTE:** Use the filtered dataset (with exclusions removed) for narrative.

## Folder Structure

All monthly analysis folders (e.g., OctTTM, NovTTM, DecTTM) must follow this organized structure:

```
{MonthTTM}/
├── data/              # All CSV and data files
│   ├── {month}_{year}_ttm_full_month.csv
│   ├── {month}_{year}_ttm_filtered.csv
│   └── mitigation_time_cohorts.csv
├── reports/           # All markdown documentation files
│   ├── exclusions.md
│   ├── {Month}_TTM_Analysis_Summary.md
│   ├── {Month}_Incident_Breakdown.md
│   ├── {Month}_Comparison_Report.md
│   ├── {Month}_Narrative.md
│   ├── Executive_Summary_Blurb.md
│   ├── PRIMO_Pulse.md
│   ├── Detailed_Mitigation_Actions_Summary.md
│   ├── WhatIf.md
│   ├── Quality_Verification_Summary.md
│   └── QUESTIONS_7_8_9_COMPLETE.md
├── visualizations/    # All PNG/image files
│   ├── {Month}_TTM_Distribution.png
│   ├── {Month}_Top_Services.png
│   ├── {Month}_Daily_Timeline.png
│   ├── {Month}_Severity_Distribution.png
│   ├── WhatIf_Cumulative_Impact.png
│   ├── WhatIf_Cumulative_Marginal.png
│   ├── TTM_HowFixed_Visualization.png
│   └── mitigation_time_regression_model.png
├── scripts/           # All Python scripts
│   ├── execute_kusto_query_to_csv.py
│   ├── identify_exclusions.py
│   ├── create_analysis_documents.py
│   ├── create_whatif.py
│   ├── create_narrative.py
│   ├── create_presentation_v2.py
│   ├── ttm_dashboard.py
│   ├── detailed_executive_analysis.py
│   └── create_mitigation_regression_model.py
├── models/            # Machine learning models and predictions
│   ├── mitigation_time_model.pkl
│   └── model_predictions.csv
├── presentations/     # PowerPoint and presentation files
│   └── {month}_{year}_TTM_Analysis.pptx
└── verification/      # Verification reports
    ├── Executive_Summary_Blurb_Verification.md
    ├── PRIMO_Pulse_Verification.md
    ├── Detailed_Mitigation_Actions_Summary_Verification.md
    └── [other verification reports]
```

**Important:** All scripts must be updated to use these folder paths. When creating files:
- Save all CSVs to `data/`
- Save all markdown reports to `reports/`
- Save all images to `visualizations/`
- Save all scripts to `scripts/`
- Save presentations to `presentations/`
- Save verification reports to `verification/`
- Save trained models to `models/`

**Script Management:** After creating or modifying any analysis scripts, copy them to `Utilities/CreateScripts/` for reuse in future months:
```powershell
# Example: Copy new or modified scripts to Utilities
Copy-Item 'OctTTM/scripts/create_mitigation_regression_model.py' -Destination 'Utilities/CreateScripts/'
Copy-Item 'OctTTM/scripts/create_analysis_documents.py' -Destination 'Utilities/CreateScripts/'
```

This ensures all improvements are captured in the central script repository.

## Step 1: Execute Query and Save Full Results
1. Use the reusable script: `QEI_TTM_Analysis\Utilities\execute_kusto_query_to_csv.py`
2. Copy script to `{MonthTTM}/scripts/` and update configuration for the target month:
   - `OUTPUT_FOLDER` = Path to data folder (e.g., `OctTTM/data/`)
   - `OUTPUT_CSV` = `{month}_{year}_ttm_full_month.csv`
   - `START_DATE` = First day of target month (e.g., `2025-10-01`)
   - `END_DATE` = Last day of target month (e.g., `2025-10-30`)
3. Execute the script from scripts folder: `python scripts/execute_kusto_query_to_csv.py`
   - Script will authenticate via interactive browser
   - Reads `ttm_query.csl`, updates date range automatically
   - Executes query against icmdataro-mcp Kusto cluster
   - Converts ALL incidents to DataFrame with proper column names
   - Saves complete dataset to `data/{month}_{year}_ttm_full_month.csv` with UTF-8-sig encoding
4. Verify the output in `data/` folder:
   - Check incident count is reasonable (September: 116, October: 109)
   - Verify ~375 columns are present
   - Confirm column names are preserved (not numbered)

## Step 2: Identify and Document Exclusions
Create an `reports/exclusions.md` file that identifies incidents to exclude from all downstream analysis:


### 2.1: Define Exclusion Criteria
Document the following exclusion criteria at the top of the file:
1. **BCDR Related Incidents**
   - Rationale: Planned disaster recovery drills and business continuity tests artificially inflate TTM
   - Keywords to search: BCDR, disaster recovery drill, DR drill, business continuity
   
2. **EUAP Region Incidents**
   - Rationale: Early Adoption Program (EUAP) environments are pre-production with different operational characteristics
   - Keywords to search: EUAP, East US 2 EUAP, euap

### 2.2: Identify Excluded Incidents
Search the following columns for exclusion keywords:
- `Symptoms`, `RootCauses`, `Impacts`, `HowFixed`
- `MitigationDescription`, `ImpactStartDescription`, `TTUpdateSummary`
- `ServiceName`, `ImpactedRegion`

For each excluded incident, document:
- **Outage ID** (OutageIncidentId)
- **Service Name** (ServiceName)
- **TTM** (minutes and hours)
- **Severity** (Severity)
- **Title/Symptoms** (first 200 chars)
- **Root Cause** (first 200 chars if available)
- **Impact** (subscriber/service counts, regions)
- **Resolution** (HowFixed)
- **Exclusion Reason** (which criteria matched)
- **Notes** (additional context, e.g., "Highest TTM incident", "Planned drill")

### 2.3: Generate Summary Statistics
Include at the top of reports/exclusions.md:
- Total incidents before exclusions
- Number of incidents excluded
- Exclusion rate (%)
- Remaining incidents for analysis
- Total TTM excluded (minutes and hours)
- Average TTM of excluded incidents
- Average TTM before and after exclusions
- Impact assessment (% reduction in average TTM)

### 2.4: Provide Filter Code
Include ready-to-use filter expressions:
```kql
| where OutageIncidentId !in (ID1, ID2, ID3, ...)
```
```python
df_filtered = df[~df['OutageIncidentId'].isin([ID1, ID2, ID3, ...])]
```

### 2.5: Apply Exclusions to Remaining Steps
**CRITICAL:** After creating `reports/exclusions.md`, apply the exclusion filter to the dataset before proceeding to Step 3. All subsequent analysis (Steps 3-8) must use the **filtered dataset** with exclusions removed.

Create a filtered CSV in data folder: `data/{month}_{year}_ttm_filtered.csv` for use in all downstream steps.

## Step 3: Generate Summary Statistics
**NOTE:** Use the filtered dataset (with exclusions removed) for all statistics.

Create a summary document with:
- Total incident count
- TTM P75, P50, P90 percentiles
- Severity distribution (Sev 1 vs Sev 2)
- Top 5 impacted services
- Auto-detection rate (%)
- Geographic distribution by region
- Date range coverage verification
- IsCausedByChange distribution

## Step 3: Calculate Key Metrics
Compute and document:
- P75 TTM, TTD, TTO, TTN
- S400/F500 customer impact counts (AcMSubCount)
- CritSit cases (TotalCritsit)
- PIR completion rate

## Checkpoint 1: 
Use "chain of verification" (aka plan verification questions for steps 1-3, answer those questions independently, tell me your findings about what is correct and incorrect, then proceed to step 4).

## Step 4: Compare to Previous Month
If previous month data exists (e.g., SeptTTM folder):
- Load previous month's CSV
- Calculate month-over-month changes:
  * Incident volume delta (absolute and %)
  * TTM P75 change (minutes and %)
  * Service pattern shifts
  * Severity mix changes
- Generate comparison table


## Step 5: Create Analysis Documents
Generate the following markdown files:
1. `{Month}_TTM_Analysis_Summary.md` - Executive summary with key findings
2. `{Month}_Incident_Breakdown.md` - Detailed incident list with key metrics
3. `{Month}_Comparison_Report.md` - Month-over-month comparison (if applicable)
4. `{Month}_Narrative.md` - Story of the month so far

Include visualizations where helpful:
- TTM distribution histogram
- Top services bar chart
- Timeline of incidents
- Severity pie chart

## Step 6: Create Analysis Documents
**NOTE:** Use the filtered dataset (with exclusions removed) for all documents.e to Previous Month
**NOTE:** Use the filtered dataset (with exclusions removed) for comparison.

If previous month data exists (e.g., SeptTTM folder):s
**NOTE:** Use the filtered dataset (with exclusions removed) for all statistics.

Create a summary document with:
- Total incident count (after exclusions)
- TTM P75, P50, P90 percentiles
- Severity distribution (Sev 1 vs Sev 2)
- Top 5 impacted services
- Auto-detection rate (%)
- Geographic distribution by region
- Date range coverage verification
- IsCausedByChange distribution
- Reference to exclusions.md for excluded incidents

## Step 7: Generate What-If Analysis
**NOTE:** Use the filtered dataset (with exclusions removed) for What-If analysis.

Create a comprehensive What-If scenario analysis to quantify the impact of preventing high-impact event systems:

### 7.1: Event System Identification
- Use **RootResponsibleIncidentId** to identify complete event systems
- Events are root incidents where RootResponsibleIncidentId == OutageIncidentId
- Outages are cascading impacts where RootResponsibleIncidentId points to the parent event
- Group all incidents with the same RootResponsibleIncidentId (regardless of Level) as a single event system

### 7.2: Generate WhatIf.md
Create `reports/WhatIf.md` with two main sections:

**Part 1: Individual Event System Impacts (Ranked by P75 Impact)**
- Calculate the P75 TTM impact if each event system (root + all cascades) were prevented
- Rank all event systems from highest to lowest P75 impact
- For each event system, include:
  * Root Event ID, Service, Severity, TTM
  * Number of cascading outages
  * Total system TTM
  * List of cascading outages (with OutageIncidentId, Service, TTM, Level)
  * Impact metrics: P75 without this system, P75 delta (minutes and %), Mean/Median changes
  * Root cause category
  * Flag high-impact events (≥2% P75 change) and high-cascade events (≥3 outages)

**Part 2: Cumulative Removal Impact Analysis**
- Show cumulative impact of removing event systems in rank order
- For each step (removing top 1, top 2, top 3, etc. event systems):
  * List which event was added at this step
  * Total event systems removed
  * Total incidents removed (count and % of all incidents)
  * Remaining incident count
  * Cumulative P75 TTM, delta from baseline (minutes and %)
  * Cumulative Mean and Median TTM
- Include summary insights for key milestones (Top 1, 3, 5, 10 events)
- Generate summary comparison table
- Add executive insights section with:
  * Impact concentration analysis
  * Cascading impact analysis
  * Prevention priorities
  * Interpretation guidance for leadership

### 7.3: Generate What-If Visualizations
Create two visualization files in the visualizations/ folder:

**visualizations/WhatIf_Cumulative_Impact.png** (2-panel figure):
- Left panel: Line plot showing P75 TTM (y-axis) vs Number of Events Removed (x-axis)
  * Include baseline reference line at 190 min
  * Highlight key milestones (1, 5, 10, 15 events)
  * Add insight text box with reduction percentages
- Right panel: Bar chart showing % Reduction in P75 TTM vs Events Removed
  * Highlight key milestones with value labels
  * Add reference line for top 5 events impact

**visualizations/WhatIf_Cumulative_Marginal.png** (dual-axis figure):
- Primary y-axis (left): Cumulative P75 TTM line plot
- Secondary y-axis (right): Marginal impact bars (P75 reduction per event)
- Annotate steep decline region (top 5 events) and diminishing returns region
- Show how incremental benefit decreases after top events

### 7.4: Key Metrics to Calculate
- Total incidents and event systems (after exclusions)
- Root events vs cascading outages counts
- Events with cascades (count and %)
- Average cascades per event
- Baseline P75, Mean, Median TTM
- Top 1/5/10 event system impacts (% of P75)
- Marginal impact analysis: average reduction for events 1-5, 6-10, 11-15
- Demonstrate diminishing returns effect

## Step 8: Generate Narrative Insights Analysis
**NOTE:** Use the filtered dataset (with exclusions removed) for Narrative Insights.

Create a comprehensive qualitative text-mining analysis to complement the quantitative What-If analysis. This step answers "WHY did high TTM incidents take so long?" by analyzing actual incident narratives.

Tell me the "story" of the month so far. Read through all incidents, and tell me what kind of issues happened from the start of the month until now, week by week. Bonus points for cohesively and logically interconnecting them with proof (outageincidentid with references). It is imperative that you do not take creative liberties or hallucinate when doing this, and that you cite references. Results should be saved in a `reports/{month}_Narrative.md` file

### 8.1: Reference NARRATIVE_INSIGHTS_PROMPT.md
Follow the detailed instructions in `Utilities/NARRATIVE_INSIGHTS_PROMPT.md` which provides:
- Complete workflow for narrative text mining
- 9 analysis dimensions (Detection, Resolution, Mitigation, Root Cause, Symptoms, Geographic, Service, Temporal)
- Script templates and output structure
- Expected insights and patterns

### 8.2: Create NarrativeInsights Folder
Create `{MonthFolder}/NarrativeInsights/` subdirectory containing:

**Analysis Scripts (place in scripts/ folder):**
1. `check_columns.py` - Verify availability of narrative text columns (Symptoms, RootCauses, HowFixed, etc.)
2. `get_narratives.py` - Extract top 20 highest TTM incidents with full narrative text
3. `analyze_narratives.py` - Comprehensive text mining across 9 dimensions
4. `create_narrative_report.py` - Generate final markdown report and JSON export

**Output Files:**
1. `data/top_20_high_ttm_incidents.csv` - Top 20 incidents with detailed narrative fields
2. `reports/NarrativeInsight.md` - Executive report with 8 sections:
   - Executive Summary (key finding headline)
   - Resolution Method Analysis (High vs Normal TTM contrast)
   - Service-Specific Patterns (where impact lives)
   - Root Cause Category Analysis
   - Detection & Diagnosis Insights
   - Symptom Pattern Analysis
   - Geographic/Regional Patterns
   - Key Incidents Deep Dive (top 5-10 with direct quotes)
   - Actionable Recommendations (specific, not generic)
3. `reports/narrative_analysis_data.json` - Structured data export for programmatic access

### 8.3: Key Analysis Focus Areas

**Resolution Method Gap Analysis:**
- Compare "Ad-hoc/Manual" vs "TSG/Runbook" vs "Automation" resolution methods
- Calculate average TTM for each method in High TTM vs Normal TTM cohorts
- Identify the resolution method gap (e.g., "Ad-hoc 17x slower in High TTM")
- Flag services lacking TSG coverage

**Service Pattern Analysis:**
- Identify top 3-5 services by total TTM impact
- Extract common failure modes from narratives
- Identify automation gaps and TSG needs
- Calculate service-specific average TTM

**Root Cause Theme Extraction:**
- Mine RootCauses field for patterns: Software bugs, Capacity/Resource, Network, Hardware, Deployment/Config
- Compare High TTM vs Normal TTM root cause distributions
- Identify preventable vs external causes
- Calculate TTM multipliers by root cause type

**Detection & Diagnosis Patterns:**
- Extract detection methods: BRAIN/Auto-Detection, Customer-Reported, Internal-Monitoring
- Analyze detection coverage gaps (why aren't high TTM incidents auto-detected?)
- Correlate detection method with TTM outcomes

**Geographic Concentration:**
- Extract datacenter/region mentions from narratives
- Identify regional clustering of high TTM incidents
- Flag infrastructure issues (e.g., "7 incidents in Norway East datacenter")

**Symptom Keyword Analysis:**
- Mine Symptoms field for: Availability/Downtime, Performance/Latency, Connectivity, Reliability
- Compare symptom patterns in High vs Normal TTM
- Identify correlation between symptom type and resolution time

### 8.4: Critical Output Requirements

**Data Integrity:**
- All analysis must be grounded in actual incident data (no hallucination)
- Use direct quotes from narrative fields where compelling
- Show percentages and averages for all comparisons
- Include incident IDs for all claims

**Key Insights to Surface:**
- Primary TTM driver (e.g., "Ad-hoc resolution 17.0x slower")
- Top 3 services by impact with specific failure modes
- Resolution method effectiveness gaps
- Detection coverage gaps (% BRAIN vs customer-reported)
- Root cause patterns (software bugs X% more common in High TTM)
- Specific, actionable recommendations (not generic advice)

**Actionable Recommendations:**
Must include specific actions like:
- "Create TSG for SQL Control Plane Service Fabric Failover Manager scenarios"
- "Automate Xstore memory throttling detection and remediation"
- "Improve BRAIN monitors for capacity saturation patterns"

### 8.5: Integration with What-If Analysis

The Narrative Insights complement the What-If analysis:
- **What-If (Step 8):** Quantifies "WHAT" - Which events drive TTM? How much impact?
- **Narrative Insights (Step 9):** Explains "WHY" - Why did those events take so long?

Together they provide complete understanding:
- What-If: "Top 5 events = 36% of P75 TTM"
- Narrative: "Because they used ad-hoc resolution (46.7% of High TTM) vs TSG (10%)"

## Additional Requirements:
- Copy scripts from `Utilities/` to the `{MonthTTM}/scripts/` folder for customization
- Create the month folder structure if it doesn't exist (with data/, reports/, visualizations/, scripts/, presentations/ subfolders)
- The `execute_kusto_query_to_csv.py` script handles:
  - Interactive browser authentication (no need for az login)
  - Automatic date range substitution in query
  - Proper column name preservation from Kusto response
  - UTF-8-sig encoding for Excel compatibility
  - Validation and sample data display
  - Output saved to `data/` folder
- All scripts must reference the organized folder structure
- Handle edge cases: empty results, query timeouts, missing fields
- Validate data quality: check for duplicates, null critical fields, date range accuracy
- Log execution summary with timestamp and status

## Expected Output Structure:
```
{MonthFolder}/
  ├── data/
  │   ├── {month}_{year}_ttm_full_month.csv (ALL incidents)
  │   ├── {month}_{year}_ttm_filtered.csv (incidents after exclusions)
  │   └── mitigation_time_cohorts.csv (from executive analysis)
  ├── reports/
  │   ├── exclusions.md (documented excluded incidents)
  │   ├── {Month}_TTM_Analysis_Summary.md
  │   ├── {Month}_Incident_Breakdown.md
  │   ├── {Month}_Comparison_Report.md (if previous month exists)
  │   ├── {Month}_Narrative.md
  │   ├── Executive_Summary_Blurb.md
  │   ├── PRIMO_Pulse.md
  │   ├── Detailed_Mitigation_Actions_Summary.md
  │   └── WhatIf.md (event system scenario analysis)
  ├── visualizations/
  │   ├── {Month}_TTM_Distribution.png
  │   ├── {Month}_Top_Services.png
  │   ├── {Month}_Daily_Timeline.png
  │   ├── {Month}_Severity_Distribution.png
  │   ├── WhatIf_Cumulative_Impact.png (2-panel visualization)
  │   ├── WhatIf_Cumulative_Marginal.png (dual-axis visualization)
  │   └── TTM_HowFixed_Visualization.png
  ├── scripts/
  │   ├── ttm_query.csl (month-specific query)
  │   ├── execute_kusto_query_to_csv.py
  │   ├── identify_exclusions.py
  │   ├── create_analysis_documents.py
  │   ├── create_whatif.py
  │   ├── create_narrative.py
  │   ├── create_presentation_v2.py
  │   ├── ttm_dashboard.py
  │   └── detailed_executive_analysis.py
  ├── presentations/
  │   └── {month}_{year}_TTM_Analysis.pptx (20-slide deck)
  └── verification/
      ├── Executive_Summary_Blurb_Verification.md
      ├── PRIMO_Pulse_Verification.md
      └── Quality_Verification_Summary.md
  ├── {Month}_TTM_Distribution.png
  ├── {Month}_Top_Services.png
  ├── {Month}_Daily_Timeline.png
  ├── {Month}_Severity_Distribution.png
  ├── query_execution_log.json
  └── NarrativeInsights/
      ├── check_columns.py
      ├── get_narratives.py
      ├── analyze_narratives.py
      ├── create_narrative_report.py
      ├── top_20_high_ttm_incidents.csv
      ├── NarrativeInsight.md
      └── narrative_analysis_data.json
```

## Important Notes:

### Exclusion Workflow (Step 2):
- **Exclusions must be applied BEFORE any analysis steps (Steps 3-9)**
- Create `exclusions.md` to document all excluded incidents with rationale
- Generate `{month}_{year}_ttm_filtered.csv` with exclusions removed
- Use the filtered dataset for ALL subsequent analysis, metrics, and visualizations
- Excluded incidents should NOT appear in:
  * Summary statistics (Step 3)
  * Key metrics (Step 4)
  * Month-over-month comparisons (Step 5)
  * Narrative files (Step 6)
  * Analysis documents (Step 7)
  * What-If analysis (Step 8)
  * Narrative Insights (Step 9)
- Exclusion criteria:
  * BCDR related incidents (planned drills)
  * EUAP region incidents (pre-production environment)

### Event System Definition:
- **Event Systems** are identified by **RootResponsibleIncidentId**
- All incidents with the same RootResponsibleIncidentId (regardless of Level) are part of one event system
- When removing an event in What-If scenarios, ALL cascading outages with the same RootResponsibleIncidentId must be removed together
- This provides the true total impact of preventing that event

### What-If Analysis Purpose:
The What-If analysis answers the critical leadership question: "If we had prevented the top N most impactful events, what would our P75 TTM have been?" This helps:
- Identify highest-value prevention targets
- Quantify the impact concentration (Pareto effect)
- Demonstrate diminishing returns beyond top events
- Prioritize engineering investments for maximum TTM reduction## Step 10: Generate PowerPoint Presentation

**NOTE:** This step uses ALL previous outputs to create an executive-ready presentation.

### Checkpoint 2: 
Use "chain of verification" (aka plan verification questions for steps 4-8, answer those questions independently, tell me your findings about what is correct and incorrect, then proceed to step 9).

### 9.1: Create Presentation Script

Use the script `scripts/create_presentation_v2.py` (or create it if it doesn't exist) with the following specifications:

**Dependencies:**
- python-pptx (PowerPoint generation)
- pillow (Image processing)

Install if needed: `python -m pip install python-pptx pillow`

**Design Requirements:**
- **Format:** 16:9 widescreen (13.333" × 7.5")
- **Color Scheme:** Microsoft Blue (RGB 0, 120, 215) for title bars
- **Layout:** Blue title bar on each slide with white text
- **Images:** Auto-scaled to fit within slide bounds, maintain aspect ratio
- **Text:** Sized appropriately to prevent overflow (typically 16pt for content)

### 9.2: 20-Slide Structure

The presentation must include the following slides:

1. **Title Slide**
   - Title: "{Month} {Year} TTM Analysis"
   - Subtitle: "Quality Engineering Insights - Time to Mitigate Review"

2. **Executive Summary**
   - Total incidents (before and after exclusions)
   - P75 TTM baseline
   - Exclusion count and impact (TTM reduction %)
   - High TTM multiplier (e.g., 17.0x)
   - Resolution gap percentage
   - Top What-If finding (e.g., "Top 5 events = 36.3% of P75")

3-7. **Visualizations** (5 slides)
   - Slide 3: TTM Distribution chart
   - Slide 4: Summary Statistics
   - Slide 5: Top Services by TTM
   - Slide 6: Daily Timeline
   - Slide 7: Severity Distribution

8. **Month-over-Month Comparison**
   - Two-column layout comparing current month vs previous month
   - Include: Total incidents, P75, Mean, Median, P90

9-11. **What-If Analysis** (3 slides)
   - Slide 9: Cumulative Impact visualization (P75 reduction as events removed)
   - Slide 10: Marginal Returns visualization (diminishing returns)
   - Slide 11: Key Findings (event system count, top 5 impact %, diminishing returns data)

12. **Exclusions**
   - List all excluded incidents with OutageID, Service, TTM
   - Exclusion reasons (BCDR/EUAP)
   - Impact on average TTM

13-15. **Narrative Insights** (3 slides)
   - Slide 13: Resolution Gap Analysis (ad-hoc vs TSG, TTM multiplier)
   - Slide 14: Service Patterns (top services, specific failure modes)
   - Slide 15: Root Cause Patterns (bug rates, detection gaps)

16. **Recommendations**
   - 4 priority actions (specific, actionable)
   - Examples: Create TSGs, Improve BRAIN detection, Enhance code quality, Automate resolutions

17. **Key Takeaways**
   - 7 bullet points summarizing the month
   - Mix of quantitative and qualitative insights

18-20. **Appendix** (3 slides)
   - Slide 18: Appendix title slide
   - Slide 19: Data Sources and Methodology
   - Slide 20: Key Definitions (TTM, P75, Event System, High TTM, BCDR, EUAP, etc.)

### 9.3: Implementation Guidelines

**Image Embedding:**
- Load all PNG files from the visualizations/ folder
- Use intelligent scaling: calculate image dimensions, fit within available space
- Center images horizontally
- Never upscale (maintain quality)
- Include captions below images

**Text Content:**
- Read summary statistics from markdown files in reports/ folder
- Extract key metrics from analysis outputs
- Pull findings from reports/WhatIf.md
- Extract insights from reports/NarrativeInsight.md
- Ensure all content fits within slide bounds (no overflow)

**Layout Functions:**
- dd_title_slide(title, subtitle) - For title and appendix divider
- dd_content_slide(title, content_list) - For bullet point slides
- dd_image_slide(title, image_path, caption) - For visualization slides
- dd_two_column_slide(title, left_content, right_content) - For comparisons

### 9.4: Execute and Save

1. Run the script: `python scripts/create_presentation_v2.py`
2. Verify output: `presentations/{Month}_{Year}_TTM_Analysis.pptx`
3. Validate:
   - All 20 slides created
   - Images display correctly and fit within bounds
   - No text overflow
   - Professional appearance with consistent formatting

### 9.5: Purpose

This presentation synthesizes ALL analysis work (Steps 1-9) into an executive-ready format that answers:
- **What happened?** (Quantitative metrics)
- **How much impact?** (What-If analysis)
- **Why did it take so long?** (Narrative Insights)
- **What should we fix?** (Recommendations)

The presentation is suitable for leadership review, monthly QBRs, and stakeholder updates.

## Step 10: Generate Interactive TTM Dashboard

**NOTE:** This step creates a production-ready Dash web application for interactive TTM analysis with v2.0 features (interactive chart filtering, pre-computed performance optimization).

### 10.1: Dashboard Overview

Create `scripts/ttm_dashboard.py` - An interactive web dashboard built with Dash (Plotly) that provides:
- **12 Interactive Filters**: Date range, severity, service, TTM range, quintile, CritSit, P70-P80, event selection, cascade exclusion, BCDR/EUAP exclusion
- **5 Summary Cards**: Total incidents, P75 TTM, Mean TTM, P90 TTM, CritSit count
- **6 Charts**: TTM distribution, top services, timeline, severity pie, quintile bar, regional impact
- **🆕 Interactive Chart Filtering (v2.0)**: 5 clickable charts that filter the entire dashboard
- **Incident Details Table**: Full incident list with 14 high-value columns
- **Hierarchical Service Analysis**: Service → Team → Root Causes/Mitigations/Impacts
- **Pattern & Correlation Analysis**: 4 tables showing Root Cause × Mitigation combinations
- **📖 Data Dictionary**: Definitions for 7 root cause themes + 6 mitigation actions
- **🆕 Pre-Computed Performance (v2.0)**: 18 boolean columns for 100x faster filtering

### 10.2: Architecture Requirements

**Framework:**
- Dash 2.x with Flask backend
- Plotly Express for visualizations
- Pandas for data processing
- Port: 8050 (http://127.0.0.1:8050)

**Layout:**
- Flexbox design: 280px fixed sidebar + flex:1 main content
- Color scheme: BLUE=#0078D4, GRAY_BG=#F3F2F1, BORDER=#EDEBE9
- Responsive cards, charts, and tables
- Professional Microsoft aesthetic

**Data Source:**
- Read `{month}_{year}_ttm_full_month.csv` (UTF-8-sig encoding)
- Apply column mapping (OutageCreateDate→CreateDate, ServiceName→Service, etc.)
- Parse CreateDate as datetime with UTC timezone
- Calculate quintiles, P70-P80 range, event identification

### 10.3: 🆕 v2.0 Performance Optimization (Pre-Computed Columns)

**Pre-compute 18 Boolean Columns at Startup:**

The dashboard must create these columns once at data load to enable instant filtering:

```python
# Root Cause themes (7 columns)
df['has_connectivity'] = df['RootCauses'].str.lower().str.contains(
    'connectivity|connection|network|endpoint|unreachable', na=False)
df['has_configuration'] = df['RootCauses'].str.lower().str.contains(
    'configuration|config|misconfigur|setting|drift', na=False)
df['has_capacity'] = df['RootCauses'].str.lower().str.contains(
    'capacity|resource|memory|cpu|throttl|scaling|exhaust', na=False)
df['has_deployment'] = df['RootCauses'].str.lower().str.contains(
    'deployment|deploy|rollout|release|code change', na=False)
df['has_certificate'] = df['RootCauses'].str.lower().str.contains(
    'certificate|cert|ssl|tls|authentication', na=False)
df['has_timeout'] = df['RootCauses'].str.lower().str.contains(
    'timeout|latency|slow|performance', na=False)
df['has_dependency'] = df['RootCauses'].str.lower().str.contains(
    'dependency|dependent|downstream|upstream|cascading', na=False)

# Mitigation actions (6 columns)
df['has_restart'] = df['Mitigations'].str.lower().str.contains(
    'restart|reboot|recycle|bounce', na=False)
df['has_rollback'] = df['Mitigations'].str.lower().str.contains(
    'rollback|revert|roll back', na=False)
df['has_scaling'] = df['Mitigations'].str.lower().str.contains(
    'scal|add capacity|increase resource', na=False)
df['has_failover'] = df['Mitigations'].str.lower().str.contains(
    'failover|fail over|redirect|switch', na=False)
df['has_config_change'] = df['Mitigations'].str.lower().str.contains(
    'config|setting|parameter|adjust|modify', na=False)
df['has_traffic_mgmt'] = df['Mitigations'].str.lower().str.contains(
    'throttle|rate limit|block|traffic|load', na=False)

# Impact types (5 columns)
df['has_availability'] = df['Impacts'].str.lower().str.contains(
    'availability|unavailable|down|outage', na=False)
df['has_performance'] = df['Impacts'].str.lower().str.contains(
    'performance|slow|latency|delay', na=False)
df['has_functionality'] = df['Impacts'].str.lower().str.contains(
    'functionality|function|feature|capabilit', na=False)
df['has_data_issue'] = df['Impacts'].str.lower().str.contains(
    'data|corruption|loss|inconsisten', na=False)
df['has_authentication'] = df['Impacts'].str.lower().str.contains(
    'authentication|auth|login|access denied', na=False)

print(f"Pre-computed 18 keyword matching columns for performance optimization")
```

**Performance Gains:**
- Filter response: 0.3-0.5 seconds (75% faster than v1.0)
- Pattern Analysis: ~50ms (92% faster than v1.0)
- Initial load: 1.5-2 seconds
- No repeated string matching during filtering

### 10.4: 🆕 v2.0 Interactive Chart Filtering

**5 Clickable Charts:**

1. **Severity Pie Chart** (chart-severity):
   - Click action: Filter dashboard to selected severity
   - Use case: "Focus on Sev0 incidents only"

2. **Top Services Bar Chart** (chart-services):
   - Click action: Filter dashboard to selected service
   - Use case: "Deep-dive into ACS Communication Plane"

3. **Quintile Bar Chart** (chart-quintile):
   - Click action: Filter dashboard to selected quintile
   - Use case: "Analyze only Q5 (High TTM) incidents"

4. **Regional Impact Bar Chart** (chart-region):
   - Click action: Filter dashboard to selected region
   - Use case: "See incidents affecting West Europe"

5. **Timeline Bar Chart** (chart-timeline):
   - Click action: Filter dashboard to selected date
   - Use case: "Investigate October 15th incident spike"

**Chart Filter Implementation Pattern:**

The callback must detect which chart was clicked and extract the filter value:

```python
@app.callback(
    [Output('card-total', 'children'), Output('card-p75', 'children'),
     # ... 15 more outputs
     Output('chart-filter-banner', 'children'), Output('chart-click-store', 'data')],
    [Input('start-date-filter', 'date'), Input('end-date-filter', 'date'),
     # ... 10 more sidebar inputs
     Input('reset-btn', 'n_clicks'), Input('clear-chart-btn', 'n_clicks'),
     Input('chart-severity', 'clickData'), Input('chart-services', 'clickData'),
     Input('chart-quintile', 'clickData'), Input('chart-region', 'clickData'),
     Input('chart-timeline', 'clickData')],
    prevent_initial_call=False
)
def update_all(start_date, end_date, ..., severity_click, services_click, ...):
    # Determine which input triggered the callback
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Initialize chart filter storage
    chart_filters = {}
    chart_filter_labels = []
    
    # Handle "Clear Chart Filters" button
    if triggered_id == 'clear-chart-btn':
        severity_click = None
        services_click = None
        quintile_click = None
        region_click = None
        timeline_click = None
    
    # Process chart clicks to extract filter values
    if severity_click and triggered_id == 'chart-severity':
        clicked_severity = severity_click['points'][0]['label']
        chart_filters['severity'] = clicked_severity
        chart_filter_labels.append(f"📊 Severity: {clicked_severity}")
    
    if services_click and triggered_id == 'chart-services':
        clicked_service = services_click['points'][0]['label']
        chart_filters['service'] = clicked_service
        chart_filter_labels.append(f"📊 Service: {clicked_service}")
    
    # ... (repeat for quintile, region, timeline)
    
    # Apply CHART FILTERS FIRST (before sidebar filters)
    fdf = df.copy()
    
    if 'severity' in chart_filters and 'Severity' in fdf.columns:
        fdf = fdf[fdf['Severity'] == chart_filters['severity']]
    
    if 'service' in chart_filters and 'ServiceName' in fdf.columns:
        fdf = fdf[fdf['ServiceName'] == chart_filters['service']]
    
    # ... (apply other chart filters)
    
    # Then apply SIDEBAR FILTERS on top (AND logic)
    if severities:  # From sidebar dropdown
        fdf = fdf[fdf['Severity'].isin(severities)]
    
    # ... (apply other sidebar filters)
```

**Chart Filter Banner:**
- Display: Yellow background (#FFF4CE) with gold border (#FFD700)
- Content: "🎯 Active Chart Filters: 📊 Severity: Sev0 | 📊 Service: ACS"
- Visibility: Only when chart filters are active
- Helper text: "(Click 'Clear Chart Filters' to remove)"

**Clear Chart Filters Button:**
- Color: Gray (#666)
- Action: Removes chart filters but keeps sidebar filters
- Location: Sidebar below Reset Filters button

### 10.5: Dashboard Components (Complete Specification)

**Sidebar Filters (13 components):**
1. Start Date (DatePickerSingle) - `start-date-filter`
2. End Date (DatePickerSingle) - `end-date-filter`
3. Exclude Cascade (Checklist) - `exclude-cascade-filter`
4. Exclude BCDR/EUAP (Checklist) - `exclude-bcdr-filter`
5. Severity (Dropdown multi) - `severity-filter`
6. Service (Dropdown multi) - `service-filter`
7. TTM Range (RangeSlider) - `ttm-filter`
8. Quintile (Dropdown multi) - `quintile-filter`
9. CritSit (Dropdown single) - `critsit-filter`
10. P70-P80 Only (Dropdown single) - `p70p80-filter`
11. Event (Dropdown single) - `event-filter`
12. Reset Filters Button (Blue #0078D4) - `reset-btn`
13. 🆕 Clear Chart Filters Button (Gray #666) - `clear-chart-btn` (v2.0)

**Summary Cards (5 cards in flexbox row):**
- Total Incidents (Blue)
- P75 TTM (Blue)
- Mean TTM (Blue)
- P90 TTM (Blue)
- CritSits (Red #D13438)

**Charts (6 visualizations in 3 rows):**
1. TTM Distribution Histogram (50 bins, not clickable) - `chart-dist`
2. 🖱️ Top Services Bar Chart (clickable) - `chart-services`
3. 🖱️ Daily Timeline Bar Chart (clickable) - `chart-timeline`
4. 🖱️ Severity Pie Chart (clickable) - `chart-severity`
5. 🖱️ Quintile Bar Chart (clickable) - `chart-quintile`
6. 🖱️ Regional Impact Bar Chart (clickable) - `chart-region`

**Incident Details Table:**
- Columns: OutageIncidentId, ServiceName, Severity, TTM, IsCritSit, OwningTeamName, ImpactedRegion, OutageCreateDate, RootCauses, IncidentTitle, Mitigations, Impacts, OutageCorrelationId, EventSize
- Styling: Sticky header, scrollable (max 600px), truncated text (300px max width)
- Sorting: By TTM descending
- Component IDs: `table-incidents` (children), `table-count` (count text)

**Service Analysis Table (Hierarchical):**
- All-Up Summary: Root Causes, Mitigations, Impacts across all services
- Service Breakdown: For each service:
  - Service name, incident count, average TTM
  - Team Breakdown: For each team:
    - Team name, incident count, TTM stats
    - Root Cause themes (with emoji indicators: 🔗 cascading, 🔄 change-related)
    - Mitigation actions (with emoji indicators)
    - Impact types (with emoji indicators)
- Loading Indicator: Spinner during computation
- Component ID: `table-service-analysis`

**Pattern & Correlation Analysis (4 tables):**

1. **Combination Matrix** (Root Cause × Mitigation):
   - Uses pre-computed boolean columns: `fdf[fdf['has_connectivity'] & fdf['has_restart']]`
   - Columns: Root Cause, Mitigation, P75 TTM, Mean TTM, Count, Services
   - Sorted by P75 TTM descending (slowest combinations first)
   - Shows top 20 combinations with count ≥ 2

2. **Root Cause Table**:
   - Uses pre-computed boolean columns: `fdf[fdf['has_connectivity']]`
   - Columns: Root Cause, Count, % of Incidents, Avg TTM, P75 TTM
   - Sorted by P75 TTM descending

3. **Mitigation Table**:
   - Uses pre-computed boolean columns: `fdf[fdf['has_restart']]`
   - Columns: Mitigation, Count, % of Incidents, Avg TTM, P75 TTM
   - Sorted by Count descending

4. **Impact Table**:
   - Uses pre-computed boolean columns: `fdf[fdf['has_availability']]`
   - Columns: Impact, Count, % of Incidents, Avg TTM, P75 TTM
   - Sorted by Count descending

- Loading Indicator: Spinner during computation
- Component ID: `pattern-analysis`

**📖 Data Dictionary Section:**

Two tables with complete definitions (white background, bordered, bold labels):

**Root Cause Themes (7 rows):**
- **Connectivity**: "Issues related to network connections, endpoints becoming unreachable, connection timeouts, or network infrastructure failures"
- **Configuration**: "Problems caused by incorrect settings, misconfigurations, configuration drift, or missing configuration parameters"
- **Capacity**: "Resource exhaustion including memory limits, CPU constraints, throttling, or insufficient scaling to handle load"
- **Deployment**: "Issues introduced during software deployments, rollouts, releases, or code changes that caused service degradation"
- **Certificate**: "Certificate expiration, invalid certificates, SSL/TLS handshake failures, or authentication certificate issues"
- **Timeout**: "Request timeouts, operation timeouts, slow performance leading to timeout errors, or latency-related failures"
- **Dependency**: "Failures in dependent services, downstream/upstream service issues, or cascading failures from external dependencies"

**Mitigation Actions (6 rows):**
- **Restart/Reboot**: "Restarting services, rebooting servers, recycling application pools, or bouncing processes to clear state and recover"
- **Rollback**: "Reverting to a previous known-good version of code, configuration, or deployment to undo problematic changes"
- **Scaling**: "Adding more resources by scaling up (vertical) or scaling out (horizontal) to handle increased load or resource demands"
- **Failover**: "Switching to backup systems, redirecting traffic to healthy instances, or failing over to secondary regions/datacenters"
- **Config Change**: "Modifying configuration settings, updating parameters, adjusting thresholds, or reconfiguring services to resolve issues"
- **Traffic Mgmt**: "Throttling requests, implementing rate limits, blocking problematic traffic, or managing load distribution to protect services"

### 10.6: Callback Architecture (Complete)

**Single Callback Function:** `update_all()`

**Inputs (18 total):**
- 12 sidebar filter inputs (dates, checkboxes, dropdowns, slider)
- 1 reset button (n_clicks)
- 1 clear-chart button (n_clicks) - v2.0
- 5 chart clickData inputs (severity, services, quintile, region, timeline) - v2.0

**Outputs (17 total):**
- 5 summary cards (total, p75, mean, p90, critsits)
- 6 chart figures (dist, services, timeline, severity, quintile, region)
- 2 incident table outputs (children, count text)
- 1 service analysis table (children)
- 1 pattern analysis section (children)
- 1 chart-filter-banner (children) - v2.0
- 1 chart-click-store (data) - v2.0

**Filter Priority Logic:**
1. Apply CHART FILTERS FIRST (from chart clicks) - highest priority
2. Then apply SIDEBAR FILTERS on top (AND logic with chart filters)
3. Reset button clears ALL filters (chart + sidebar)
4. Clear Chart button clears ONLY chart filters (keeps sidebar filters)

### 10.7: Implementation Steps

1. **Create ttm_dashboard.py** in the month folder (e.g., `OctTTM/ttm_dashboard.py`)

2. **Import dependencies**:
   ```python
   import dash
   from dash import dcc, html, Input, Output
   import plotly.express as px
   import plotly.graph_objects as go
   import pandas as pd
   ```

3. **Load and prepare data**:
   - Read CSV with UTF-8-sig encoding
   - Apply column mapping (OutageCreateDate→CreateDate, etc.)
   - Parse CreateDate as datetime with UTC timezone
   - Calculate quintiles, P70-P80 range, identify events
   - **Pre-compute 18 boolean columns** (has_connectivity, has_restart, etc.)

4. **Define layout**:
   - Header with blue background
   - Flexbox container: 280px fixed sidebar + flex:1 main content
   - Hidden stores: `chart-click-store`, `chart-filter-banner`
   - All filters, cards, charts, tables, data dictionary

5. **Implement callback**:
   - 18 inputs → 17 outputs
   - Chart click detection with `dash.callback_context`
   - Chart filter extraction and application FIRST
   - Sidebar filter application SECOND
   - Generate all outputs (cards, charts, tables, banner)

6. **Add error handling**:
   - Graceful handling of missing columns
   - Empty dataset handling (show "No Data" in charts)
   - Try-except blocks around all chart generation
   - Date parsing with timezone awareness

7. **Test locally**:
   - Run: `python ttm_dashboard.py`
   - Open: http://127.0.0.1:8050
   - Verify all filters work
   - Test chart clicks
   - Check performance (<0.5s filter response)

8. **Validate features**:
   - ✅ All 12 sidebar filters function correctly
   - ✅ Chart clicks filter the entire dashboard
   - ✅ Chart filter banner displays when active
   - ✅ Clear Chart Filters button works
   - ✅ Reset Filters clears everything
   - ✅ Pattern Analysis uses pre-computed columns
   - ✅ Performance meets targets (<0.5s filtering)
   - ✅ Data dictionary renders correctly

### 10.8: Error Handling Requirements

**Missing Column Handling:**
```python
if 'ServiceName' in df.columns:
    # Use ServiceName
else:
    # Skip or use alternative
```

**Empty Dataset Handling:**
```python
if total > 0 and 'TTM' in fdf.columns:
    fig = px.histogram(fdf, x='TTM', nbins=50)
else:
    fig = go.Figure().update_layout(title='No Data')
```

**Date Timezone Handling:**
```python
if fdf['CreateDate'].dt.tz is not None:
    start_dt = start_dt.tz_localize('UTC')
```

### 10.9: Output Files

After running this step, the month folder should contain:

```
{MonthFolder}/
  └── ttm_dashboard.py (1665+ lines, production-ready)
```

### 10.10: Usage Instructions

**To run the dashboard:**
```powershell
cd {MonthFolder}
python scripts/ttm_dashboard.py
```

**Then open in browser:** http://127.0.0.1:8050

**Interactive features:**
- Use sidebar filters for broad filtering
- Click any chart segment to drill down instantly
- View active chart filters in yellow banner
- Clear chart filters while keeping sidebar filters
- Reset all filters to start fresh

### 10.11: Purpose and Benefits

This dashboard provides:

**For Executives:**
- Interactive exploration during QBRs and leadership reviews
- Click-to-filter for ad-hoc questions ("Show me only Sev0")
- Professional UI suitable for stakeholder demos
- Fast performance enables real-time discussion

**For Engineers:**
- Deep-dive into specific services and teams
- Pattern discovery through Root Cause × Mitigation analysis
- Hierarchical service analysis shows team-level details
- Pre-computed columns enable instant filtering

**For Analysis:**
- Comprehensive filtering: 12 filters × 5 clickable charts
- Pattern Analysis automatically identifies combinations
- Data dictionary provides self-documenting reference
- Export-ready insights for further investigation

**Integration with Other Outputs:**
- Complements PowerPoint with interactive exploration
- Validates findings from What-If and Narrative Insights analysis
- Enables team-specific drill-downs not possible in static reports
- Supports real-time hypothesis testing during meetings

The dashboard transforms static analysis into an interactive exploration tool, enabling stakeholders to answer their own questions and discover patterns in real-time.

---

## Step 11: Generate Regression Models for TTM Prediction

**NOTE:** This step creates machine learning models to predict mitigation time based on incident characteristics.

### 11.1: Model Overview

Create `scripts/create_mitigation_regression_model.py` to build predictive models that answer: "Given TTO, severity, and root cause, what is the expected mitigation time (TTM - TTO)?"

**Purpose:**
- Predict total TTM given incident characteristics
- Identify which factors (severity, root cause type) have strongest impact on mitigation time
- Quantify severity vs root cause importance
- Generate hypothetical scenario predictions

**Model Architecture:**
- **Target Variable:** Mitigation Time (TTM - TTO)
- **Features:**
  - TTO (detection/diagnosis time)
  - OutageIncidentSeverity (Sev0, Sev1, Sev2, etc.)
  - RootCause_Classified (8 categories extracted from PIR text)
- **Algorithms:** Linear Regression, Ridge Regression, Random Forest Regressor

### 11.2: Root Cause Classification

The model must classify root causes from PIR narrative text (`set_Whys` and `RootCauses` columns) into 8 categories:

1. **Hardware Failure** - Hardware errors, PSU, power loss, disk failure, ToR switch, memory failure
2. **Software Bug** - Code bugs, exceptions, crashes, memory leaks, deadlocks, race conditions
3. **Configuration Issue** - Misconfigurations, wrong settings, config changes, firewall rules, ACL
4. **Capacity/Resource** - Resource exhaustion, OOM, disk full, CPU high, throttling, scaling issues
5. **Network Issue** - Connectivity, packet loss, latency, BGP, routing, DNS, timeouts
6. **Deployment/Change** - Deployment rollout, releases, code push, updates, migrations, rollbacks
7. **External Dependency** - Third party, vendor dependencies, downstream/upstream services
8. **Transient** - Intermittent, temporary, self-healing, self-resolved issues

**Classification Function:**
```python
def classify_root_cause(row):
    """Classify root cause from narrative text using keyword matching"""
    text = ""
    if pd.notna(row.get('set_Whys')):
        text += str(row['set_Whys']).lower() + " "
    if pd.notna(row.get('RootCauses')):
        text += str(row['RootCauses']).lower() + " "
    
    if not text.strip():
        return "Unknown"
    
    # Priority-ordered keyword matching
    if any(kw in text for kw in ['hardware failure', 'psu', 'power loss', 'disk failure', 'tor switch']):
        return "Hardware Failure"
    elif any(kw in text for kw in ['software bug', 'exception', 'crash', 'memory leak', 'deadlock']):
        return "Software Bug"
    # ... [complete implementation in script]
    
    return "Unknown"
```

### 11.3: Model Training Requirements

**Data Preparation:**
1. Load filtered CSV from `data/{month}_{year}_ttm_filtered.csv`
2. Calculate `MitigationTime = TTM - TTO`
3. Apply root cause classification
4. Encode severity as numeric (Sev0=0, Sev1=1, Sev2=2, etc.)
5. Create one-hot encoding for root cause categories
6. Handle missing values (fillna for severity with median)

**Train Three Models:**
```python
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
}

X = df[['TTO', 'Severity_Numeric'] + root_cause_columns]
y = df['MitigationTime']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"{name}: R²={r2:.3f}, MAE={mae:.1f} min")
```

**Model Selection:**
- Choose model with highest R² score
- If R² is negative (high variance), still use best performer and document uncertainty
- Random Forest typically performs best for this use case

### 11.4: Model Output Requirements

**1. Visualization (`visualizations/mitigation_time_regression_model.png`):**

Create 4-panel figure:
- **Panel 1:** Actual vs Predicted scatter plot (with diagonal reference line)
- **Panel 2:** Residual plot (predicted vs error)
- **Panel 3:** Model comparison bar chart (R², MAE, RMSE for each model)
- **Panel 4:** Feature importance (for Random Forest) showing TTO, severity, and top root causes

**2. Saved Model (`models/mitigation_time_model.pkl`):**
```python
import pickle

model_data = {
    'model': best_model,
    'root_cause_categories': root_cause_categories,
    'severity_mapping': severity_map,
    'training_metrics': {
        'r2': r2_score,
        'mae': mae,
        'rmse': rmse,
        'cv_scores': cv_scores
    },
    'root_cause_stats': df.groupby('RootCause_Classified')['MitigationTime'].agg(['count', 'mean', 'std'])
}

with open('models/mitigation_time_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)
```

**3. Hypothetical Predictions:**

Generate predictions for common scenarios:
```python
# Example: Configuration issue with TTO=15 min across severities
scenarios = [
    {'Severity': 'Sev0', 'RootCause': 'Configuration Issue', 'TTO': 15},
    {'Severity': 'Sev1', 'RootCause': 'Configuration Issue', 'TTO': 15},
    {'Severity': 'Sev2', 'RootCause': 'Configuration Issue', 'TTO': 15},
    {'Severity': 'Sev0', 'RootCause': 'Software Bug', 'TTO': 10},
    {'Severity': 'Sev0', 'RootCause': 'Hardware Failure', 'TTO': 10},
]

for scenario in scenarios:
    # Create feature vector
    features = create_feature_vector(scenario)
    predicted_mitigation = model.predict([features])[0]
    predicted_ttm = scenario['TTO'] + predicted_mitigation
    print(f"{scenario['Severity']} + {scenario['RootCause']} + TTO={scenario['TTO']} → TTM={predicted_ttm:.1f} min")
```

### 11.5: Insights to Extract

The script must print and document:

1. **Root Cause Distribution:**
   - Count and percentage for each category
   - Average mitigation time per category
   - Identify slowest categories (e.g., "Software Bug = 994 min avg, 38x longer than Hardware")

2. **Feature Importance:**
   - Rank features by predictive power
   - Example: "TTO (48.8%), Software Bug (35.2%), Config (5.0%)"
   - Insight: "Root cause type matters more than severity"

3. **Model Performance:**
   - R² score interpretation (negative = high variance, positive = good fit)
   - MAE (mean absolute error in minutes)
   - Cross-validation scores (5-fold)

4. **Scenario Analysis:**
   - Compare Hardware Failure vs Software Bug mitigation times
   - Compare Sev0 vs Sev2 impact (often minimal difference)
   - Identify counterintuitive findings (e.g., "Severity has minimal impact")

### 11.6: Script Execution

**Run from OctTTM directory:**
```bash
cd OctTTM
python scripts/create_mitigation_regression_model.py
```

**Expected Output:**
```
================================================================================
MITIGATION TIME REGRESSION MODEL
================================================================================

Total Incidents: 122
Mitigation Time Stats:
  Mean: 84.8 minutes
  Median: 19.5 minutes
  Std: 281.7 minutes
  Min: -70.0 minutes
  Max: 2981.0 minutes

================================================================================
STEP 1: ROOT CAUSE CLASSIFICATION
================================================================================

Root Cause Classification Results:
  Hardware Failure: 41 incidents (33.6%), avg mitigation = 26.3 min
  Network Issue: 32 incidents (26.2%), avg mitigation = 64.7 min
  Unknown: 21 incidents (17.2%), avg mitigation = 111.0 min
  Software Bug: 3 incidents (2.5%), avg mitigation = 994.3 min ← CRITICAL
  Configuration Issue: 6 incidents (4.9%), avg mitigation = 202.5 min
  ...

================================================================================
STEP 2: MODEL TRAINING
================================================================================

Linear Regression: R²=-30.8, MAE=118.5 min
Ridge Regression: R²=-23.0, MAE=116.4 min
Random Forest: R²=-15.8, MAE=126.3 min ← Best Model

Random Forest selected (lowest negative R², best generalization)

Feature Importance:
  TTO: 48.8%
  Software Bug: 35.2%
  Configuration Issue: 5.0%
  Severity_Numeric: 2.1%
  ...

================================================================================
HYPOTHETICAL PREDICTIONS
================================================================================

Sev0 + Hardware Failure + TTO=10min → TTM=15.8 min
Sev0 + Software Bug + TTO=10min → TTM=676.8 min (11+ hours!)
Sev2 + Configuration Issue + TTO=15min → TTM=110.1 min (1.8 hours)
...

Model saved to: models/mitigation_time_model.pkl
Visualization saved to: visualizations/mitigation_time_regression_model.png
```

### 11.7: Integration with Other Outputs

- **Executive Summary:** Reference model insights in Question 5 (high mitigation factors)
- **Narrative Insights:** Cross-reference root cause themes with model predictions
- **PRIMO Pulse:** Use predictions for "what if" scenarios in stakeholder communication
- **Dashboard:** Potential future enhancement - real-time TTM prediction widget

### 11.8: Model Usage Example

**Interactive Prediction:**
```python
import pickle
import numpy as np

# Load model
with open('models/mitigation_time_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model']

# Predict for new incident
TTO = 15  # minutes
severity = 2  # Sev2
root_cause = 'Configuration Issue'  # one-hot encoded

features = np.array([[TTO, severity, 0, 0, 1, 0, 0, 0, 0, 0]])  # TTO, Sev, 8 root causes
predicted_mitigation = model.predict(features)[0]
predicted_ttm = TTO + predicted_mitigation

print(f"Predicted TTM: {predicted_ttm:.1f} minutes ({predicted_ttm/60:.1f} hours)")
```

---

## Step 12: Generate Executive Summary Blurb

Based on the analysis completed, write a comprehensive executive summary document (Executive_Summary_Blurb.md) that answers the following questions:

### 12.1: Questions to Answer

1. **How many outages met the north star of "less than 60 min TTM"?**
   - Provide exact count in "numerator/denominator (percentage%)" format
   - List incident IDs that met vs. missed the target

2. **How many outages were excluded from analysis?**
   - Provide exact count in "numerator/denominator (percentage%)" format
   - List excluded incident IDs and exclusion reasons

3. **What were the top 3 longest TTM outage events, and how would removing each one by one change our TTM P75 number?**
   - Identify top 3 event systems (using RootResponsibleIncidentId grouping)
   - Calculate P75 impact of removing each event (absolute and percentage change)
   - Include verbatim quotes from Symptoms and RootCauses fields
   - Cite specific incident IDs for each event

4. **What is our P75 TTM if we remove TTO (calculate P75 of TTM - TTO)?**
   - Calculate P75 TTO (detection/diagnosis time)
   - Calculate P75 Mitigation Time (TTM - TTO)
   - Show percentage breakdown of P75 TTM components
   - Explain implications for improvement focus

5. **What factors caused high TTM using mitigation time (TTM - TTO) data?**
   - Define high mitigation threshold (use P80 of mitigation time)
   - Analyze multiple dimensions:
     - **Automation Gaps**: Compare automation rates between high vs. normal mitigation cohorts
     - **Root Cause Patterns**: Top root causes in high mitigation cohort with counts
     - **Service-Specific Patterns**: Services with highest total mitigation time
     - **Severity Analysis**: Distribution across severity levels
     - **Process Gaps**: TSG vs. Ad-Hoc resolution comparison
   - For each dimension:
     - Provide exact counts with "numerator/denominator (percentage%)" format
     - Include verbatim quotes from incident narratives (Symptoms, RootCauses, MitigationDescription)
     - Cite specific incident IDs for all statistics
     - Provide sample incidents with full context

### 12.1.1: Enhanced Analysis for Question 3 (Top 3 Events)

**Additional Analysis Required:**
- For each of the top 3 events, add the following information:
  - **Total Incidents in Event:** Count of incidents within the event system
  - **Incident ID(s):** List specific OutageIncidentId values
  - Note whether the event has cascading outages or is a single-incident event
  - If using WhatIf.md for reference, cross-check event system details

**Data Source:** 
- Primary: `RootResponsibleIncidentId` grouping in filtered CSV
- Reference: `WhatIf.md` (if available) for event system analysis

**Example Enhancement:**
```markdown
#### Event #1: Incident 695596942 - SQL Control Plane
- **Total Incidents in Event:** 1 incident (no cascading outages)
- **Incident ID:** 694538461
- **Total TTM:** 3,035 minutes (50.6 hours)
```

### 12.1.2: Enhanced Analysis for Question 5 (High Mitigation Factors)

**Additional Geographic Region Analysis:**

After the main Section 5 header, add a **Geographic Region Distribution** subsection that analyzes where high-mitigation incidents occurred:

**Data Source:** Extract geographic regions from the `Impacts` column
- Pattern to search: "X region(s) <Region Name>" (e.g., "1 region East US", "2 regions UK South")
- Use regex pattern: `(\d+)\s+regions?\s+([A-Za-z0-9\s]+?)(?:\s+[a-z]{2,}[0-9]{2}|\s+\d+\s+services)`
- Common regions to look for: East US, West US, East US 2, West US 2, UK South, West Europe, North Europe, etc.
- Alternative: Check `IsMultiRegion` column for multi-region incidents

**Required Analysis:**
1. Extract geographic region for each high-mitigation incident
2. Count incidents per region
3. Calculate total mitigation time per region
4. Identify multi-region vs single-region incidents
5. Calculate percentage distribution

**Example Output:**
```markdown
**Geographic Region Distribution:**
- **East US & East US 2:** 7 incidents (28.0%), 7,312 min total mitigation
- **UK South:** 3 incidents (12.0%), 1,109 min total mitigation
- **West Europe:** 3 incidents (12.0%), 1,055 min total mitigation
- **West US:** 2 incidents (8.0%), 306 min total mitigation
- **Other regions:** 6 incidents (24.0%) across Germany North, Switzerland North, New Zealand North, South Central US, and Central India
- **Not specified/Global:** 4 incidents (16.0%), 1,134 min total mitigation
- **Multi-Region:** 1 incident (4.0%), 479 min mitigation (Incident 704144382 - Azure Frontdoor)

**Key Insight:** US and European regions account for 68% of high-mitigation incidents, with East US/East US 2 showing the highest concentration (28%) and longest total mitigation time (7,312 minutes).
```

### 12.1.3: New Question 6 - Transitive Severity Analysis

**Add a sixth question to the Executive Summary:**

6. **How did severity escalations (transitive severity) impact TTM?**

**Purpose:** Analyze incidents that experienced severity changes during their lifecycle to understand if severity escalations are markers for complex, high-impact incidents.

**Data Source:** 
- `set_ChangeCategories` column (look for values like `['SeverityUpgrade']`)
- `set_NewSeverity` column (new severity level after change)
- `Severity` column (original severity)

**Required Analysis:**
1. Identify incidents with severity changes:
   ```python
   df['HasSeverityChange'] = df['set_ChangeCategories'].notna() & (df['set_ChangeCategories'] != '')
   with_changes = df[df['HasSeverityChange']]
   without_changes = df[~df['HasSeverityChange']]
   ```

2. For each incident with severity changes, extract:
   - Incident ID and service name
   - Original and new severity
   - TTM, TTO, and mitigation time
   - Whether in high-mitigation cohort
   - Verbatim symptoms and root causes

3. Calculate comparative statistics:
   - Mean/Median TTM for incidents with vs without severity changes
   - Mean/Median mitigation time for incidents with vs without severity changes
   - P75 TTM comparison
   - High mitigation cohort overlap percentage

4. Calculate impact:
   - TTM difference (absolute and percentage)
   - Mitigation time difference (absolute and percentage)
   - Multiplier (e.g., "2.3x longer mitigation time")

**Section Structure:**
```markdown
### 6. Transitive Severity - How did severity escalations impact TTM?

**Answer:** Only 3 out of 123 incidents (2.4%) experienced severity changes during their lifecycle, but these incidents showed significantly higher TTM.

**Details:**
- **Incidents with Severity Changes:** 3/123 (2.4%)
- **Incidents without Severity Changes:** 120/123 (97.6%)

**Incidents with Severity Changes:**

1. **Incident 704389079 - SDN PubSub Service**
   - Original Severity → New Severity: Severity 1 (upgraded)
   - TTM: 373 minutes, TTO: 25 minutes, Mitigation: 348 minutes
   - High Mitigation Cohort: Yes
   - **Symptoms:** "Service experienced reduced publishing success rate and high CPU usage..."
   - **Root Cause:** "A platform update triggered a corner-case service bug..."

[Repeat for all incidents with severity changes]

**Impact Analysis:**

| Metric | With Severity Changes (n=3) | Without Severity Changes (n=120) | Difference |
|--------|----------------------------|----------------------------------|------------|
| Mean TTM | 215.7 minutes | 144.6 minutes | **+71.0 min (+49.1%)** |
| Median TTM | 183 minutes | 52 minutes | +131 minutes |
| P75 TTM | 278 minutes | 124 minutes | +154 minutes |
| Mean Mitigation Time | 187.3 minutes | 82.1 minutes | **+105.3 min (+128%)** |

**Key Findings:**

1. **Higher TTM:** Incidents with severity changes averaged 71.0 minutes longer TTM (+49.1%) than incidents without severity changes.

2. **Significantly Longer Mitigation:** Mitigation time was 105.3 minutes longer (+128%) for incidents with severity changes, suggesting that escalating severity correlates with more complex mitigation challenges.

3. **High Mitigation Cohort Overlap:** 2 out of 3 incidents with severity changes (66.7%) were in the High Mitigation cohort, compared to only 23 out of 120 (19.2%) for incidents without severity changes.

4. **Rare but Impactful:** While severity changes are rare (2.4%), they appear to be markers for incidents that require substantially more time to resolve.

**Conclusion:** Transitive severity escalations, though infrequent, are strong indicators of complex, high-impact incidents. These incidents require 2.3x longer mitigation time on average. Early identification of incidents likely to require severity escalation could enable faster escalation paths and resource allocation.
```

**Implementation Script:**
```python
# Transitive Severity Analysis
df['HasSeverityChange'] = df['set_ChangeCategories'].notna() & (df['set_ChangeCategories'] != '')
with_changes = df[df['HasSeverityChange']]
without_changes = df[~df['HasSeverityChange']]

print(f"\nTransitive Severity Changes: {len(with_changes)}/{len(df)} ({len(with_changes)/len(df)*100:.1f}%)")

# Detailed incident profiles
for idx, row in with_changes.iterrows():
    print(f"\nIncident {row['OutageIncidentId']} - {row['ServiceName']}")
    print(f"  Original Severity: {row['Severity']}, New: {row['set_NewSeverity']}")
    print(f"  TTM: {row['TTM']} min, TTO: {row['TTO']} min, Mitigation: {row['TTM']-row['TTO']} min")
    print(f"  Symptoms: {row['Symptoms'][:150]}...")
    print(f"  Root Cause: {row['RootCauses'][:150]}...")

# Comparative statistics
print(f"\nWith Changes: Mean TTM {with_changes['TTM'].mean():.1f}, Median {with_changes['TTM'].median():.0f}")
print(f"Without Changes: Mean TTM {without_changes['TTM'].mean():.1f}, Median {without_changes['TTM'].median():.0f}")
print(f"Difference: +{with_changes['TTM'].mean() - without_changes['TTM'].mean():.1f} min ({((with_changes['TTM'].mean() / without_changes['TTM'].mean() - 1) * 100):.1f}%)")
```

### 12.1.4: Questions 7, 8, and 9 - Extended Analysis

**CRITICAL:** After completing Questions 1-6, create a comprehensive analysis covering Questions 7, 8, and 9 and save to `reports/QUESTIONS_7_8_9_COMPLETE.md`.

These questions provide deeper insights into Incident Automation (IA) features, deployment safety (Red Thread), and E2E automation rates.

#### Question 7: Incident Automation Analysis

**Goal:** Analyze the relationship between IA features and TTM to identify which features reduce TTM most effectively.

**Data Source:**
- All columns starting with `Is_IA_` (12 features total)
- Examples: Is_IA_Edit, Is_IA_Mitigation, Is_IA_CustomRecommendation, Is_IA_CoreActions, etc.

**Required Analysis:**

1. **Individual IA Feature Performance:**
   - For each IA feature, calculate:
     - Adoption rate (% of incidents using the feature)
     - Average TTM with feature vs without feature
     - TTM reduction (absolute minutes)
     - North star achievement rate (% meeting <60 min TTM)
   - Rank features by TTM reduction effectiveness

2. **IA Feature Combinations:**
   - Calculate total IA features used per incident
   - Group incidents by feature count (0, 1, 2, 3, 4, 5, 6, 7, 8+ features)
   - For each group, calculate:
     - Average TTM
     - North star achievement rate
     - Incident count
   - Identify optimal feature count (lowest TTM, highest north star %)

3. **Concerning Patterns:**
   - Flag IA features with negative correlation (higher TTM when used)
   - Explain potential reasons (complexity markers vs actual effectiveness)

**Expected Insights:**
- "Best individual performer: Is_IA_Edit (64% adoption, 21.8 min TTM reduction, 61.5% north star)"
- "Optimal combination: Exactly 2 IA features = 51 min avg TTM, 80% north star"
- "Non-linear relationship: More features ≠ better outcomes (diminishing returns after 2 features)"

**Implementation:**
```python
# Identify all Is_IA_ columns
ia_columns = [col for col in df.columns if col.startswith('Is_IA_')]

# Individual feature analysis
for col in ia_columns:
    with_feature = df[df[col] == True]
    without_feature = df[df[col] == False]
    
    adoption = len(with_feature) / len(df) * 100
    ttm_with = with_feature['TTM'].mean()
    ttm_without = without_feature['TTM'].mean()
    reduction = ttm_without - ttm_with
    north_star_with = len(with_feature[with_feature['TTM'] < 60]) / len(with_feature) * 100
    
    print(f"{col}: {adoption:.1f}% adoption, {reduction:.1f} min reduction, {north_star_with:.1f}% north star")

# Feature count analysis
df['IA_Feature_Count'] = df[ia_columns].sum(axis=1)
for count in sorted(df['IA_Feature_Count'].unique()):
    subset = df[df['IA_Feature_Count'] == count]
    avg_ttm = subset['TTM'].mean()
    north_star = len(subset[subset['TTM'] < 60]) / len(subset) * 100
    print(f"{count} features: {len(subset)} incidents, {avg_ttm:.1f} min avg, {north_star:.1f}% north star")
```

#### Question 8: Red Thread Analysis

**Goal:** Analyze deployment safety indicators and regional impact patterns to identify correlation with TTM.

**Data Source:**
- `AutoStopHealthCheck` column (safety gate pass/fail indicator)
- `ChangeSafetyLearnings` column (deployment safety insights)
- `DeploymentMethod` column (e.g., Ev2)
- `DeclarationType` column (Brain Declared vs Manual)
- `ImpactedRegion` column (geographic scope)
- `IsMultiRegion` column (single vs multi-region)

**Required Analysis:**

1. **Deployment Safety Coverage:**
   - Calculate coverage rates for AutoStopHealthCheck, ChangeSafetyLearnings, DeploymentMethod
   - Identify data quality gaps

2. **AutoStopHealthCheck Impact:**
   - Compare TTM for value "0.0" (safety gate failed) vs "1.0" (passed)
   - Calculate multiplier effect
   - Example: "0.0 correlates with 5x higher TTM (551 min vs 110 min)"

3. **Regional Distribution:**
   - Extract top 5-10 impacted regions
   - Calculate average TTM per region
   - Identify regional concentration patterns
   - Flag "unknown" region incidents

4. **Regional Scope:**
   - Compare single-region vs global incidents
   - Analyze TTM differences

**Expected Insights:**
- "Extremely low Red Thread adoption (<10%)"
- "AutoStopHealthCheck = '0.0' correlates with 5x higher TTM"
- "15.6% of incidents have 'unknown' region (data quality issue)"
- "East US 2 has highest avg TTM (343.7 min)"

**Implementation:**
```python
# Coverage analysis
coverage = {
    'AutoStopHealthCheck': df['AutoStopHealthCheck'].notna().sum() / len(df) * 100,
    'ChangeSafetyLearnings': df['ChangeSafetyLearnings'].notna().sum() / len(df) * 100,
    'DeploymentMethod': df['DeploymentMethod'].notna().sum() / len(df) * 100
}
print(f"Red Thread Coverage: {coverage}")

# AutoStopHealthCheck impact
if 'AutoStopHealthCheck' in df.columns:
    failed = df[df['AutoStopHealthCheck'] == '0.0']
    passed = df[df['AutoStopHealthCheck'] == '1.0']
    print(f"Failed safety gate (0.0): {failed['TTM'].mean():.1f} min avg")
    print(f"Passed safety gate (1.0): {passed['TTM'].mean():.1f} min avg")
    print(f"Multiplier: {failed['TTM'].mean() / passed['TTM'].mean():.1f}x")

# Regional distribution
region_stats = df.groupby('ImpactedRegion').agg({
    'OutageIncidentId': 'count',
    'TTM': 'mean'
}).sort_values('OutageIncidentId', ascending=False).head(10)
print(region_stats)
```

#### Question 9: E2E Automation & Manual Touch

**Goal:** Quantify true E2E automation rate (detection + mitigation) and analyze manual touch patterns in high TTM incidents.

**Data Source:**
- `IsAutoDetectedAllClouds` column (detection automation)
- `Is_IA_Mitigation` column (mitigation automation)
- `HowFixed` column (resolution method - narrative text)
- `MitigationDescription` column (mitigation actions - narrative text)

**Required Analysis:**

1. **E2E Automation Rate:**
   - Detection automation: % with IsAutoDetectedAllClouds = True
   - Mitigation automation: % with Is_IA_Mitigation = True
   - E2E automation: % with BOTH detection AND mitigation automated
   - Example: "≤1.6% E2E automated (only 2/122 have Is_IA_Mitigation)"

2. **Manual Touch in High Mitigation Cohort:**
   - Define high mitigation cohort (P80 threshold)
   - For each incident in high cohort, classify resolution method:
     - **Ad-hoc steps:** Manual investigation, trial-and-error, custom fixes
     - **TSG-based:** Following documented runbooks/procedures
     - **Mixed/Unclear:** Combination or insufficient information
   - Calculate average mitigation time for each method

3. **Common Manual Touch Types:**
   - Mine HowFixed and MitigationDescription fields for patterns
   - Categories: Configuration changes, Investigation, Resource scaling, Code rollback, etc.
   - Provide incident counts per category

4. **IA Gap Analysis:**
   - Identify IA features with low adoption but high potential impact
   - Set target adoption rates based on proven effectiveness
   - Prioritize improvements (immediate, medium-term, long-term)

**Expected Insights:**
- "E2E Automation: ≤1.6% (only 2/122 incidents)"
- "Ad-hoc resolution: 8 incidents, 542 min avg (2.3x slower than TSG-based)"
- "Top IA gaps: Is_IA_Edit (current 64%, target 85%), Is_IA_Mitigation (current 1.6%, target 25%)"

**Implementation:**
```python
# E2E automation rate
detection_auto = df['IsAutoDetectedAllClouds'].sum()
mitigation_auto = df['Is_IA_Mitigation'].sum()
e2e_auto = df[(df['IsAutoDetectedAllClouds'] == True) & (df['Is_IA_Mitigation'] == True)]
print(f"Detection: {detection_auto}/{len(df)} ({detection_auto/len(df)*100:.1f}%)")
print(f"Mitigation: {mitigation_auto}/{len(df)} ({mitigation_auto/len(df)*100:.1f}%)")
print(f"E2E: {len(e2e_auto)}/{len(df)} ({len(e2e_auto)/len(df)*100:.1f}%)")

# Manual touch classification
high_mit = df[df['MitigationTime'] > df['MitigationTime'].quantile(0.80)]

def classify_resolution(row):
    text = str(row['HowFixed']).lower() + " " + str(row['MitigationDescription']).lower()
    if any(kw in text for kw in ['runbook', 'tsg', 'documented procedure', 'standard operating']):
        return 'TSG-based'
    elif any(kw in text for kw in ['investigation', 'ad-hoc', 'manual', 'trial', 'custom']):
        return 'Ad-hoc'
    else:
        return 'Mixed/Unclear'

high_mit['ResolutionMethod'] = high_mit.apply(classify_resolution, axis=1)
for method in ['Ad-hoc', 'TSG-based', 'Mixed/Unclear']:
    subset = high_mit[high_mit['ResolutionMethod'] == method]
    print(f"{method}: {len(subset)} incidents, {subset['MitigationTime'].mean():.0f} min avg")
```

**Output Format:**
Create `reports/QUESTIONS_7_8_9_COMPLETE.md` with:
- Executive summary at top
- Three main sections (Questions 7, 8, 9)
- Detailed findings with statistics, quotes, and incident IDs
- Actionable recommendations based on insights
- Prioritization matrix (immediate, medium-term, long-term actions)

### 12.2: Required Format Elements

1. **Exact Counts**: All statistics must use "count/total (percentage%)" format
   - Example: "66/126 incidents (52.4%) met the north star"

2. **Verbatim Quotes**: Include direct quotes from incident fields where they add clarity
   - Cite incident ID with each quote
   - Example: *Incident 694538461: "Intermittent database unavailability..."*

3. **Appendix Section**: List all incidents used in analysis
   - **High Mitigation Time Incidents**: Complete list with IDs
   - **Normal Mitigation Time Incidents**: Complete list with IDs
   - Include resolution method breakdown for each cohort

4. **Context and Clarity**: For each finding:
   - Explain business implications
   - Provide actionable insights
   - Include comparative metrics (e.g., "31.1x longer than normal cohort")

### 12.3: Implementation Steps

1. **Create detailed analysis script** (detailed_executive_analysis.py):
   `python
   import pandas as pd
   import numpy as np
   
   # Read filtered dataset
   df = pd.read_csv('{month}_2025_ttm_filtered.csv', encoding='utf-8-sig')
   
   # Calculate TTM - TTO (mitigation time)
   df['MitigationTime'] = df['TTM'] - df['TTO']
   
   # Define high mitigation threshold (P80)
   p80_mitigation = df['MitigationTime'].quantile(0.80)
   
   # Classify incidents into cohorts
   df['Cohort'] = df['MitigationTime'].apply(
       lambda x: 'High Mitigation' if x > p80_mitigation else 'Normal Mitigation'
   )
   
   # Group by event systems using RootResponsibleIncidentId
   df['EventSystem'] = df['RootResponsibleIncidentId'].fillna(df['OutageIncidentId'])
   
   # Calculate all metrics with exact counts
   # Extract verbatim quotes from narrative fields
   # Generate comprehensive output
   `

2. **Key calculations to perform**:
   - North star: len(df[df['TTM'] < 60]) / len(df)
   - Exclusions: Read full month CSV and compare to filtered
   - Top 3 events: Sort by total TTM per EventSystem, calculate P75 without each
   - P75 breakdown: df['TTO'].quantile(0.75) and df['MitigationTime'].quantile(0.75)
   - High mitigation factors: Compare cohorts across all dimensions

3. **Quote extraction**:
   `python
   # Get first 150 characters of narrative field with incident ID
   if pd.notna(incident['Symptoms']):
       quote = f"Incident {incident['OutageIncidentId']}: \"{incident['Symptoms'][:150]}...\""
   `

4. **Generate Executive Summary document** (Executive_Summary_Blurb.md):
   - Professional business narrative format
   - 6 main sections answering each question (Questions 1-6)
   - Detailed subsections with counts, percentages, quotes, and incident IDs
   - Summary section with key drivers and recommendations
   - Comprehensive appendix with all incident classifications

### 12.4: Expected Output Structure

`markdown
# {Month} 2025 TTM Performance: Executive Summary

## Overview
[High-level summary with key metrics and main finding]

## 1. North Star Performance: X% Meeting <60 Minute Target
Met Target: X/Y incidents (Z%)
Missed Target: A/Y incidents (B%)
[Analysis with context]

## 2. Exclusions: X% EUAP/BCDR Incidents
Excluded: X/Y incidents (Z%)
Analyzed: A/Y incidents (B%)
[List of exclusions with reasons]

## 3. Top 3 Longest TTM Events: X% of P75 Driven by Three Event Systems

### Event #1: [Service] (Root Incident [ID])
- **Total TTM:** X minutes (Y hours) across Z cascading incidents
- **Incident IDs:** [comma-separated list]
- **Severity:** [0/1/2]
- **P75 Impact:** Removing this event reduces P75 by **X minutes (-Y%)**
- **Symptoms:** *"[Verbatim quote from incident...]"*
- **Root Cause:** *"[Verbatim quote from incident...]"*

[Repeat for Events #2 and #3]

**Key Insight:** [Analysis paragraph with business implications]

## 4. Detection vs. Mitigation: X% of P75 is Mitigation Time

**P75 TTM (Total):** X minutes
**P75 TTO (Detection/Diagnosis):** Y minutes (Z%)
**P75 Mitigation Time:** A minutes (B%)

**Critical Finding:** [Paragraph explaining implications]

## 5. Factors Driving High Mitigation Time: X% of Incidents Drive Y% of Total Mitigation Time

We identified **X/Y incidents (Z%)** with mitigation times exceeding the P80 threshold of A minutes.

### A. **Automation Gaps: X Percentage Point Difference**

**Automation-Resolved Incidents:**
- **High Mitigation Cohort:** X/Y (Z%)
- **Normal Mitigation Cohort:** A/B (C%)
- **Gap:** **D percentage points**

**Ad-Hoc Resolution Incidents:**
- **High Mitigation Cohort:** X/Y (Z%)
- **Normal Mitigation Cohort:** A/B (C%)
- **Gap:** **D percentage points**
- **Average Mitigation Time:**
  - High Mitigation Ad-Hoc: **X minutes**
  - Normal Mitigation Ad-Hoc: **Y minutes**
  - **Multiplier: Zx longer**

**Sample High Mitigation Ad-Hoc Incident:**
- **Incident [ID]** ([Service], Severity [N], X min mitigation)
  - **How Fixed:** *"[Quote]"*
  - **Mitigation Description:** *"[Quote]"*
  - **Context:** [Analysis paragraph]

**Key Insight:** [Summary with multipliers and business impact]

### B. **Root Cause Patterns: [Theme] Dominates**

**Top Root Causes in High Mitigation Cohort (n=X with documented causes):**

1. **[Root Cause Category]:** X/Y (Z%), Avg A min
   - **Incident IDs:** [comma-separated list]
   - **Example (Incident [ID]):** *"[Verbatim quote...]"*
   - **Context:** [Analysis paragraph]

[Repeat for top 5 root causes]

**Key Insight:** [Summary paragraph]

### C. **Service-Specific Patterns: [Service] Represents X% of High Mitigation Time**

**Top 5 Services by Total Mitigation Time (High Mitigation Cohort):**

1. **[Service Name]:** X/Y incidents (Z%), Avg A min
   - **Total Mitigation:** X minutes (**Y% of all high-mitigation time**)
   - **Incident IDs:** [comma-separated list]
   - **Longest Incident Quote ([ID], X min):**
     - *Symptoms:* *"[Quote]"*

[Repeat for top 5 services]

**Key Insight:** [Summary paragraph]

### D. **Severity Analysis: Severity [N] Incidents Average X Minutes Mitigation**

**High Mitigation Time by Severity:**

- **Severity 0:** X/Y (Z%), Avg A min
  - **Incident IDs:** [list]

- **Severity 1:** X/Y (Z%), Avg A min
  - **Incident IDs:** [list]

- **Severity 2:** X/Y (Z%), Avg A min
  - **Incident IDs:** [list]

**Key Insight:** [Comparison with multipliers]

### E. **Process Gaps: Ad-Hoc Takes Xx Longer Than TSG Resolution**

**TSG-Resolved Incidents:**
- **High Mitigation Cohort:** X/Y (Z%)
- **Normal Mitigation Cohort:** A/B (C%)
- **Avg Mitigation (High Cohort, TSG):** X minutes
- **TSG Incident IDs (High Mitigation):** [list]

**High Mitigation Cohort Comparison:**
- **TSG Resolution:** X incidents, Y min avg
- **Ad-Hoc Resolution:** A incidents, B min avg
- **Multiplier: Ad-Hoc takes Zx longer than TSG**

**Key Insight:** [Analysis of TSG value]

---

## 6. Transitive Severity - How did severity escalations impact TTM?

**Answer:** Only X out of Y incidents (Z%) experienced severity changes during their lifecycle, but these incidents showed significantly higher TTM.

**Details:**
- **Incidents with Severity Changes:** X/Y (Z%)
- **Incidents without Severity Changes:** A/Y (B%)

**Incidents with Severity Changes:**

1. **Incident [ID] - [Service Name]**
   - Original Severity → New Severity: Severity [N] (upgraded/downgraded)
   - TTM: X minutes, TTO: Y minutes, Mitigation: Z minutes
   - High Mitigation Cohort: Yes/No
   - **Symptoms:** "[Verbatim quote]"
   - **Root Cause:** "[Verbatim quote]"

[Repeat for all incidents with severity changes]

**Impact Analysis:**

| Metric | With Severity Changes (n=X) | Without Severity Changes (n=Y) | Difference |
|--------|----------------------------|----------------------------------|------------|
| Mean TTM | X minutes | Y minutes | **+Z min (+A%)** |
| Median TTM | X minutes | Y minutes | +Z minutes |
| P75 TTM | X minutes | Y minutes | +Z minutes |
| Mean Mitigation Time | X minutes | Y minutes | **+Z min (+A%)** |

**Key Findings:**

1. **Higher TTM:** Incidents with severity changes averaged X minutes longer TTM (+Y%) than incidents without severity changes.

2. **Significantly Longer Mitigation:** Mitigation time was X minutes longer (+Y%) for incidents with severity changes, suggesting that escalating severity correlates with more complex mitigation challenges.

3. **High Mitigation Cohort Overlap:** X out of Y incidents with severity changes (Z%) were in the High Mitigation cohort, compared to only A out of B (C%) for incidents without severity changes.

4. **Rare but Impactful:** While severity changes are rare (X%), they appear to be markers for incidents that require substantially more time to resolve.

**Conclusion:** Transitive severity escalations, though infrequent, are strong indicators of complex, high-impact incidents. These incidents require Xx longer mitigation time on average. Early identification of incidents likely to require severity escalation could enable faster escalation paths and resource allocation.

---

## Summary

[Month] 2025 showed Y analyzable incidents with a P75 TTM of X minutes. While Z% of incidents met the <60 minute north star, nearly half exceeded this target. The top 3 longest events were [isolated/cascading] incidents with [minimal/significant] P75 impact.

**Key Drivers of High Mitigation Time:**
1. **Automation gaps:** High-mitigation incidents use automation only X% of the time vs Y% for normal incidents
2. **Ad-hoc resolution:** Zx slower than normal mitigation when used
3. **Service concentration:** [Top 3 services] account for X% of high-mitigation time
4. **Process gaps:** TSG-based resolution is Xx faster than ad-hoc approaches
5. **Transitive severity:** Incidents with severity escalations show X% higher TTM and Y% longer mitigation time
6. **Geographic concentration:** US and European regions account for X% of high-mitigation incidents

**Primary Recommendation:** Invest in automation and TSG development for the top 5 services ([list]) to address X% of total high-mitigation time. Additionally, develop early-warning systems to identify incidents likely to require severity escalation, enabling faster resource allocation and reducing mitigation time.

---

## Recommendations

### Priority 1: [Action Title]
- **Impact:** [Quantified impact statement]
- **Action:** [Specific actionable step]
- **Expected Benefit:** [Measurable outcome]

[Repeat for Priorities 2-4]

---

## Appendix: Incident Classifications

### High Mitigation Time Incidents (n=X)
**Threshold:** Mitigation time > X minutes (P80)
**Total TTM Impact:** Y minutes (Z% from [top service] alone)

**Incident IDs:**
[Complete comma-separated list]

**Resolution Method Breakdown:**
- **Automation:** X/Y (Z%) - Incident IDs: [list]
- **TSG:** X/Y (Z%) - Incident IDs: [list]
- **Ad-Hoc:** X/Y (Z%) - Incident IDs: [list with key examples]
- **Other/Unknown:** X/Y (Z%)

### Normal Mitigation Time Incidents (n=X)
**Threshold:** Mitigation time ≤ Y minutes
**Total TTM Impact:** Z minutes

**Sample Incident IDs (first 20 of X):**
[List]

**Resolution Method Breakdown:**
- **Automation:** X/Y (Z%)
- **TSG:** X/Y (Z%)
- **Ad-Hoc:** X/Y (Z%)
- **Other/Unknown:** X/Y (Z%)

---

## Data Files
- **Cohort Classifications:** mitigation_time_cohorts.csv (complete list of all incidents with cohort assignments)
- **Detailed Analysis Output:** xecutive_detailed_output.txt (full console output with all statistics and quotes)
- **Source Dataset:** data/{month}_2025_ttm_filtered.csv (incidents after exclusions)

---

**Analysis Date:** [Current Date]
**Dataset:** {Month} 2025 (X incidents, Y exclusions)
**Metrics:** P75 TTM = X min, P75 TTO = Y min, P75 Mitigation = Z min
`

### 12.5: Output Files

After running this step, the month folder should contain:

`
{MonthFolder}/
  ├── scripts/
  │   └── detailed_executive_analysis.py (comprehensive analysis script)
  ├── reports/
  │   ├── Executive_Summary_Blurb.md (5-10 page executive summary)
  │   └── executive_detailed_output.txt (full console output)
  └── data/
      └── mitigation_time_cohorts.csv (incident classifications)
`

### 12.6: Quality Criteria

Before considering this step complete, verify:

✓ Every statistic includes exact numerator/denominator
✓ All claims cited to specific incident IDs
✓ Verbatim quotes included where they add clarity
✓ Complete incident lists in appendix
✓ Business-focused recommendations with expected benefits
✓ Actionable insights with quantified impact
✓ Professional narrative suitable for executive audience
✓ All 5 questions answered comprehensively

### 12.7: Reference Implementation

See Utilities/CreateScripts for a script:
- **Script**: detailed_executive_analysis.py (270+ lines)

### 12.8: Usage Tips

**For script execution:**
`powershell
cd {MonthFolder}
python scripts/detailed_executive_analysis.py > reports/executive_detailed_output.txt
`

**For review:**
- Console output shows all statistics with incident IDs
- reports/Executive_Summary_Blurb.md provides polished narrative
- data/mitigation_time_cohorts.csv enables incident-level validation

**For presentations:**
- Use reports/Executive_Summary_Blurb.md as speaking notes
- Quote specific incident IDs when stakeholders ask for examples
- Reference appendix for complete incident traceability
- Leverage recommendations for action planning discussions

This step transforms quantitative analysis into executive-ready insights with full citation support and actionable recommendations.

# Section 15.1: PRIMO Pulse
Please generate a PRIMO Pulse file saved as `reports/PRIMO_Pulse.md`. Example in 'Utilities/PRIMO_Pulse_Example.md'

### Checkpoint 3: 
Use "chain of verification" (aka plan verification questions for steps 9-15, answer those questions independently, tell me your findings about what is correct and incorrect, then proceed to step 16).

# Section 16: Verify Claims
For the claims, stats in `reports/Executive_Summary_Blurb.md` & `reports/PRIMO_Pulse.md`, write kusto queries (based on ttm_query.csl) that correspond to each claim so I can verify each.

Please put the queries in the appendix section ("Appendix B: Kusto Verification Queries") of the `reports/Executive_Summary_Blurb.md` file & `reports/PRIMO_Pulse.md` file.

---

# Section 17: Detailed Mitigation Actions Analysis

## DELIVERABLE: reports/Detailed_Mitigation_Actions_Summary.md

### 17.1: Objective
Analyze TTM incident data to understand **what specific technical actions teams actually took** to mitigate incidents, moving beyond generic labels like "ad-hoc" or "0% automation" to document detailed mitigation patterns.

### 17.2: Purpose
This deliverable provides stakeholders with:
- **Specific technical actions** teams performed (not generic "ad-hoc" labels)
- **Evidence-based challenge** to "0% automation" narrative
- **Actionable automation investment priorities** based on pattern frequency and ROI
- **Critical data quality assessment** of Post-Incident Review (PIR) completion rates

### 17.3: Data Sources
Use PIR-preferred methodology (especially the "Whys" column):
1. **PIR (Post-Incident Review) fields** - Written after incident closure (authoritative, prioritize when available)
2. **Real-time incident fields** - Written during active response (fallback when PIR missing)

Prioritize PIR data but intelligently fall back to real-time fields when PIR is empty/missing.

**Key Data Columns:**
  - `IncidentId` - Unique incident identifier
  - `TTM` - Time-to-Mitigate in minutes
  - `HowFixed` - Categorization (e.g., "Fixed with Ad-Hoc steps", "Fixed by Automation", "Fixed with TSG")
  - **PIR Fields (Preferred):**
    - `PIR_MitigationDescription` - Post-incident mitigation documentation
    - `PIR_DetectionDescription` - How incident was detected
    - `PIR_DiagnosisDescription` - Diagnostic process
    - `PIR_TriageDescription` - Triage process
    - `PIR_RecoveryDescription` - Recovery actions
    - `PIR_EngineerEngagedDescription` - Engineer engagement timeline
    - `PIR_PublicRootCause` - Public-facing root cause
    - `PIR_PublicSummary` - Public summary
  - **Fallback Fields:**
    - `Mitigations` - Real-time mitigation notes (array field)
    - `MitigationDescription` - Detailed mitigation text
    - `RootCauses` - Root cause analysis (array field)
  - `ServiceTreeName` - Service name
  - `MitigationDateTime`, `EngagementTime` - Timing fields

### 17.4: Analysis Instructions

#### 17.4.1: Data Quality Assessment
1. Load the CSV data
2. Calculate PIR field coverage rates:
   - For each PIR_ field, count non-empty/meaningful entries
   - Meaningful = not `['']`, `['', '']`, `NaN`, or empty string
3. Calculate fallback field coverage rates
4. Generate coverage comparison table showing:
   - Field name
   - Coverage percentage
   - Data quality rating (✅ Full, ⚠️ Limited, ❌ Rare)
5. Analyze PIR coverage by TTM ranges:
   - < 60 min (P25)
   - 60-133 min (P25-P75)
   - 133-500 min (P75-P95)
   - > 500 min (P95+)

#### 17.4.2: Create PIR-Preferred Analysis Script
Write a Python script that:

```python
def has_meaningful_data(value):
    """Check if PIR field has meaningful data (not empty/null)"""
    if pd.isna(value):
        return False
    if isinstance(value, str):
        if value.strip() == '' or value == "['']" or value == "['', '']":
            return False
    return len(str(value).strip()) > 5  # Require substantive content

def get_best_field(row, pir_field, fallback_field):
    """Get PIR field if available, otherwise fallback field"""
    pir_value = row.get(pir_field, '')
    if has_meaningful_data(pir_value):
        return f"[PIR] {pir_value}"
    
    fallback_value = row.get(fallback_field, '')
    if has_meaningful_data(fallback_value):
        return f"[Fallback] {fallback_value}"
    
    return "[No Data]"
```

Use this logic to:
- Extract mitigation actions with `get_best_field(row, 'PIR_MitigationDescription', 'Mitigations')`
- Extract root causes with `get_best_field(row, 'PIR_PublicRootCause', 'RootCauses')`
- Extract detection methods with `get_best_field(row, 'PIR_DetectionDescription', 'DetectionMethod')`
- Track whether each incident used PIR or fallback data

#### 17.4.3: Analyze Top Incidents
1. Sort incidents by TTM (descending)
2. For top 30 incidents:
   - Document incident ID, service, TTM, HowFixed
   - Extract mitigation actions (PIR-preferred)
   - Extract root cause (PIR-preferred)
   - Extract detection method (if available)
   - Extract triage/diagnosis/recovery/engineer engagement (if available)
   - Mark each incident: 🔵 HAS PIR DATA or ⚪ NO PIR DATA
3. Provide detailed write-up for top 20 incidents including:
   - All available PIR fields
   - Fallback data for comparison
   - "Why Ad-Hoc/TSG/Hotfix?" explanation
   - Note when PIR is minimal vs detailed

#### 17.4.4: Identify Common Action Patterns
From mitigation descriptions (prioritizing PIR data), categorize actions into:

1. **Infrastructure Evacuation & Migration**
   - Database migrations, VM redeployment, service instance relocation
   - Keywords: migrate, evacuate, redeploy, relocate

2. **Network Device Isolation**
   - ToR isolation, network link removal, device quarantine
   - Keywords: isolate, ToR, network device, remove from rotation

3. **Configuration Management**
   - Config rollback, deployment blocks, setting changes
   - Keywords: rollback, config, setting, parameter, suspend

4. **Hotfix Deployment**
   - Code patches, backend fixes
   - Keywords: hotfix, patch, code change, deploy fix

5. **Service Partition Management**
   - Job suspension, partition disabling, placement constraints
   - Keywords: partition, suspend job, disable, placement

6. **Traffic Rerouting & Failover**
   - Traffic shifting, forced failover, cross-AZ redirection
   - Keywords: reroute, failover, traffic, redirect, shift

7. **Self-Healing & Monitoring**
   - Automated remediation, transient recovery
   - Keywords: self-healing, automated, transient, monitor

For each category:
- Count incidents
- Calculate average TTM
- Provide 2-3 specific examples
- Explain why manual intervention was needed (if ad-hoc)
- Estimate ROI potential for automation

#### 17.4.5: Calculate Automation Statistics
1. Count incidents by HowFixed type
2. Specifically identify:
   - "Fixed by Automation" or "Transient" (self-healing)
   - "Fixed with TSG" (documented procedure)
   - "Fixed with Ad-Hoc steps" (manual coordination)
   - "Fixed with Hotfix" (code change)
   - "External" (another team)
3. Calculate true automation rate vs "0% automation" narrative
4. Explain nuance: automated components used in manual processes

#### 17.4.6: Generate Key Insights
Based on the analysis, document:

1. **"0% Automation" Reality Check**
   - What percentage actually used automation?
   - Why is "0% automation" misleading?
   - Better framing: "X% required manual coordination due to..."

2. **PIR Data Quality Assessment** (CRITICAL NEW FINDING)
   - PIR completion rate for current month
   - Which PIR fields are most/least complete?
   - PIR coverage by incident severity (TTM ranges)
   - Impact of poor PIR documentation on learning
   - Comparison: PIR quality vs real-time field quality

3. **Ad-Hoc ≠ Incompetence**
   - Sophistication of ad-hoc actions
   - Why complex incidents require manual coordination
   - Examples of multi-phase, cross-team mitigations

4. **High TTM Drivers**
   - Complexity factors (safety, coordination, validation, novel failures)
   - Why long TTM doesn't indicate poor response

5. **Automation Gaps**
   - Where are TSGs/automation missing?
   - Top 5 categories needing automation investment
   - Expected ROI for each category

#### 17.4.7: Generate Recommendations
Create actionable recommendations with priorities:

**CRITICAL Priority:**
1. **Fix PIR Data Quality Issue** (if completion rate is low)
   - Current PIR completion rate is unacceptable
   - Mandate PIR completion for incidents > P75 TTM
   - Investigate why PIR fields are empty (process failure vs data pipeline issue)
   - Redesign PIR capture to pre-populate from real-time data
   - Add quality gates: cannot close Sev1/Sev2 without complete PIR

**HIGH Priority:**
2. **Reframe "0% Automation" Narrative**
   - Update stakeholder communications
   - Emphasize nuanced reality

3. **Prioritize Automation Investment by Category**
   - High ROI: Network Device Isolation, Job Queue Suspension
   - Medium ROI: Multi-Service Failover Orchestration
   - Low ROI: Rare complex operations (keep manual with better TSG)

**MEDIUM Priority:**
4. **Create Semi-Automated Playbooks**
   - Automation assists, human approves critical steps
   - Example workflows

5. **Improve TSG Coverage for Known Issues**
   - Convert repeated ad-hoc patterns to TSGs

6. **Document "Ad-Hoc Patterns" for Future Automation**
   - Repository of ad-hoc actions
   - 5+ similar incidents → TSG candidate
   - 10+ similar incidents → Automation candidate

### 17.5: Output Format Structure

Structure the markdown document as follows:

```markdown
# Detailed Mitigation Actions Summary - [Month] [Year]
## PIR-Preferred Analysis

**Analysis Date:** [Date]
**Scope:** [N] incidents from [Month] [Year] TTM analysis
**Data Priority:** Post-Incident Review (PIR) fields preferred over real-time incident data
**Objective:** Understand specific actions teams took beyond "ad-hoc" or "0% automation" labels

---

## Executive Summary
[3-5 paragraphs summarizing the 7 action categories, key finding about misleading "0% automation", and overall insights]

---

## Data Quality Assessment
**PIR (Post-Incident Review) Data Priority:**
[Explanation of PIR preference and fallback strategy]

[Table: Coverage comparison showing PIR vs Fallback fields]

**Key Finding:** [PIR data quality assessment]

**PIR Data by TTM Range:**
[Breakdown of PIR coverage across TTM ranges]

**Observation:** [Insights about PIR coverage patterns]

---

## Top 30 Incidents by TTM - PIR-Preferred Analysis
**Data Source Summary for Top 30:**
- **X incidents (Y%)** have PIR data
- **X incidents (Y%)** rely on fallback data
- **X incidents (Y%)** have no data

---

## Top 20 Incidents by TTM - Detailed Actions Taken

### 1. Incident [ID] - [Service] ([TTM] min TTM) [🔵 HAS PIR DATA or ⚪ NO PIR DATA]
**HowFixed:** [Type]
**Mitigation Time:** [Time] minutes

**Actions Taken [PIR or Fallback]:**
[Bulleted list of specific actions]

**Root Cause [PIR or Fallback]:**
[Root cause explanation]

**Why Ad-Hoc/TSG/Hotfix?** [Explanation]

**PIR Note:** [Commentary on PIR data quality/availability]

[Repeat for top 20 incidents]

---

## Common Action Patterns - PIR vs Fallback Data

### Action Pattern Frequency from PIR Data (Limited Sample):
[Table showing action categories from PIR data with mentions and notes]

**PIR Data Limitation:** [Explanation of PIR data quality issues]

---

### Comprehensive Action Patterns from Fallback Data:

### Category 1: [Name] ([N] incidents, avg [X] min TTM)
**Actions:**
[Bulleted list]

**Examples:**
[2-3 specific examples]

**Why Manual?** [Explanation]

[Repeat for all 7 categories]

---

## Key Insights

### 1. "0% Automation" is Misleading
[Reality check with statistics and better framing]

### 2. PIR Data Quality Crisis (CRITICAL NEW FINDING - if applicable)
[Detailed PIR completion rates, impact, recommendations]

### 3. Ad-Hoc ≠ Lack of Expertise
[Sophistication of ad-hoc actions]

### 4. High TTM Driven by Complexity, Not Incompetence
[Explanation of complexity factors]

### 5. Automation Gaps - Where TSGs/Automation Are Missing
[Top 5 categories with details]

---

## Recommendations

### 1. Fix PIR Data Quality Issue (CRITICAL - if completion rate < 50%)
**Problem:** [Description]
**Impact:** [Consequences]
**Actions:**
1. Immediate: [Steps]
2. Short-term: [Steps]
3. Long-term: [Steps]
**Priority:** **CRITICAL** - [Justification]

### 2. Reframe "0% Automation" Narrative
[Old vs New narrative with action items]

### 3. Prioritize Automation Investment by Category
**High ROI (Low Hanging Fruit):**
[List with expected impact]

**Medium ROI (Requires Development):**
[List with expected impact]

**Low ROI (Complex/Rare):**
[List with rationale]

### 4. Create "Semi-Automated" Playbooks
[Concept explanation with example workflow]

### 5. Improve TSG Coverage for Known Issues
[Known issues needing TSGs]

### 6. Document "Ad-Hoc Patterns" for Future Automation
[Pattern repository concept with example]

---

## Conclusion
[3-5 paragraphs summarizing the reality vs "0% automation" narrative, critical findings (including PIR data quality if applicable), sophistication of ad-hoc actions, and actionable next steps with priority emphasis]

---

**Analysis Methodology:**
[Description of PIR-preferred approach, fallback strategy, and data sources used]
```

### 17.6: Quality Criteria

The analysis and document should:

1. **Prioritize PIR Data:** Use PIR fields when available, fallback to real-time fields only when necessary
2. **Track Data Sources:** Mark each incident/insight as [PIR] or [Fallback] for transparency
3. **Be Specific:** Avoid generic terms like "fixed issue" - use exact technical actions
4. **Be Evidence-Based:** Every claim backed by incident examples with IDs
5. **Challenge Narratives:** Question misleading statistics like "0% automation"
6. **Identify Systemic Issues:** Call out critical problems like PIR data quality crisis
7. **Be Actionable:** Every recommendation has clear priority, expected impact, and ROI estimate
8. **Acknowledge Limitations:** Document PIR data quality issues and their impact on analysis
9. **Provide Context:** Explain WHY actions were manual/ad-hoc, not just WHAT was done
10. **Be Comprehensive:** Cover all incidents, with detailed analysis of top 30

### 17.7: Success Metrics

The deliverable is successful if it:
- ✅ Documents specific technical actions for top 20+ incidents
- ✅ Categorizes all incidents into 7 action patterns
- ✅ Calculates true automation rate (challenges "0%" narrative if present)
- ✅ Identifies critical PIR data quality gap (if 50%+ missing)
- ✅ Provides ROI estimates for automation investments
- ✅ Challenges misleading narratives with evidence
- ✅ Ranks recommendations by priority (CRITICAL/HIGH/MEDIUM)
- ✅ Distinguishes PIR data from fallback data throughout
- ✅ Generates actionable insights for improving automation AND documentation

### 17.8: Implementation Notes

- PIR fields may contain arrays like `['']` or `['', '']` that appear non-null but are meaningless - filter these out
- Real-time "Mitigations" field often has better detail than PIR even when both exist
- Focus on HIGH TTM incidents (>P75) as these drive the most impact
- Be critical of data quality - if PIR completion is poor, call it out as a systemic issue
- The biggest insight may not be about automation gaps, but about documentation gaps blocking organizational learning

---

# Section 18: Quality Verification

## DELIVERABLE: Verification Reports for All Deliverables

### 18.1: Objective
Use the Evaluator.prompt.md to systematically verify the quality, accuracy, and completeness of all markdown deliverables generated in previous sections.

### 18.2: Evaluator Prompt Location
`C:\Users\nigopal\AppData\Roaming\Code\User\prompts\Evaluator.prompt.md`

### 18.3: Documents to Verify

Evaluate each of the following deliverables in order:

1. **reports/Executive_Summary_Blurb.md** (from Section 12)
2. **reports/PRIMO_Pulse.md** (from Section 15)
3. **reports/Detailed_Mitigation_Actions_Summary.md** (from Section 17)
4. **reports/{Month}_TTM_Analysis_Summary.md** (from Section 5/6)
5. **reports/{Month}_Narrative.md** (from Section 5/6)
6. **reports/WhatIf.md** (from Section 7)

### 18.4: Evaluation Process

For each document:

#### 18.4.1: Invoke Evaluator
Call the Evaluator.prompt.md with the document as context:
```
@Evaluator.prompt.md Review [DocumentName].md
```

#### 18.4.2: Evaluation Criteria
The Evaluator will assess:
- **Faithfulness to source logs:** All claims traceable to CSV data
- **Factual correctness:** Statistics, incident IDs, calculations accurate
- **Completeness:** All required sections present (trigger, failure mode, contributing factors, detection, timeline, TTM, blast radius, lessons)
- **Actionability:** Recommendations are specific, testable, measurable
- **Safety:** No misleading or risky advice
- **Clarity:** Executive-readable (VP-level comprehension)

#### 18.4.3: Expected Output Format
The Evaluator returns JSON:
```json
{
  "scores": {
    "faithfulness": 0–1,
    "completeness": 0–1,
    "actionability": 0–1,
    "safety": 0–1,
    "clarity": 0–1
  },
  "unverifiable_claims": [...],
  "missing_sections": [...],
  "risky_advice": [...],
  "rewrite_instructions": "specific bullet list"
}
```

#### 18.4.4: Create Verification Report
For each evaluated document, create a verification report file in the verification/ folder:

**Filename:** `verification/{DocumentName}_Verification.md`

**Structure:**
```markdown
# Verification Report: {DocumentName}
**Evaluation Date:** [Date]
**Evaluator:** Evaluator.prompt.md
**Source Document:** {DocumentName}.md

---

## Evaluation Scores

| Criterion | Score | Status |
|-----------|-------|--------|
| Faithfulness | X.XX | ✅ Pass / ⚠️ Review / ❌ Fail |
| Completeness | X.XX | ✅ Pass / ⚠️ Review / ❌ Fail |
| Actionability | X.XX | ✅ Pass / ⚠️ Review / ❌ Fail |
| Safety | X.XX | ✅ Pass / ⚠️ Review / ❌ Fail |
| Clarity | X.XX | ✅ Pass / ⚠️ Review / ❌ Fail |

**Overall Status:** ✅ APPROVED / ⚠️ NEEDS REVISION / ❌ REQUIRES MAJOR REWORK

**Scoring Key:**
- 0.8–1.0: ✅ Pass
- 0.6–0.79: ⚠️ Review needed
- <0.6: ❌ Fail

---

## Unverifiable Claims

[List of claims that cannot be traced to source data]

**Action Required:** Verify these claims against source CSV or remove/revise them.

---

## Missing Sections

[List of required sections that are absent or incomplete]

**Action Required:** Add or complete these sections.

---

## Risky Advice

[List of recommendations or statements that could be misleading or risky]

**Action Required:** Revise these statements to add appropriate context, caveats, or remove them.

---

## Rewrite Instructions

[Specific bullet-point instructions from Evaluator for improving the document]

---

## Verification Checklist

- [ ] All incident IDs referenced exist in source CSV
- [ ] All statistics have been verified with Kusto queries (if Appendix B exists)
- [ ] All claims are backed by data
- [ ] Recommendations are specific and actionable
- [ ] No misleading or unsupported statements
- [ ] Document structure is complete
- [ ] Executive summary is clear and VP-readable
- [ ] All percentages/calculations are correct

---

## Next Steps

**If Status = ✅ APPROVED:**
- Document is ready for stakeholder distribution
- No further action required

**If Status = ⚠️ NEEDS REVISION:**
- Address unverifiable claims
- Complete missing sections
- Revise risky advice
- Re-run Evaluator after changes

**If Status = ❌ REQUIRES MAJOR REWORK:**
- Follow rewrite instructions carefully
- Verify all data sources
- Rebuild sections as needed
- Re-run complete evaluation process
```

### 18.5: Summary Report

After evaluating all documents, create a master summary:

**Filename:** `Quality_Verification_Summary.md`

**Structure:**
```markdown
# Quality Verification Summary - {Month} {Year} TTM Analysis
**Verification Date:** [Date]
**Total Documents Evaluated:** X

---

## Overall Status

| Document | Faithfulness | Completeness | Actionability | Safety | Clarity | Status |
|----------|--------------|--------------|---------------|--------|---------|--------|
| Executive_Summary_Blurb.md | X.XX | X.XX | X.XX | X.XX | X.XX | ✅/⚠️/❌ |
| PRIMO_Pulse.md | X.XX | X.XX | X.XX | X.XX | X.XX | ✅/⚠️/❌ |
| Detailed_Mitigation_Actions_Summary.md | X.XX | X.XX | X.XX | X.XX | X.XX | ✅/⚠️/❌ |
| {Month}_TTM_Analysis_Summary.md | X.XX | X.XX | X.XX | X.XX | X.XX | ✅/⚠️/❌ |
| {Month}_Narrative.md | X.XX | X.XX | X.XX | X.XX | X.XX | ✅/⚠️/❌ |
| WhatIf.md | X.XX | X.XX | X.XX | X.XX | X.XX | ✅/⚠️/❌ |

---

## Distribution Readiness

**Ready for Distribution (✅ APPROVED):**
- [List documents that passed all criteria]

**Needs Minor Revisions (⚠️ NEEDS REVISION):**
- [List documents needing updates]
- Expected fix time: [X hours/days]

**Requires Major Rework (❌ REQUIRES MAJOR REWORK):**
- [List documents needing significant changes]
- Expected fix time: [X days]

---

## Common Issues Across Documents

[Identify patterns in evaluation feedback across multiple documents]

Examples:
- Missing Kusto verification queries in Appendix B
- Incident IDs not consistently cited
- Recommendations too vague (not SMART criteria)
- PIR data limitations not acknowledged

---

## Priority Actions

1. **IMMEDIATE (before distribution):**
   - [Critical fixes needed]

2. **HIGH (within 24 hours):**
   - [Important revisions]

3. **MEDIUM (before next analysis cycle):**
   - [Process improvements]

---

## Verification Statistics

- **Average Faithfulness Score:** X.XX
- **Average Completeness Score:** X.XX
- **Average Actionability Score:** X.XX
- **Average Safety Score:** X.XX
- **Average Clarity Score:** X.XX
- **Overall Pass Rate:** X% (Y of Z documents approved)

---

## Recommendations for Future Analyses

[Based on evaluation results, suggest process improvements for next month's analysis]

Examples:
- Add Kusto verification queries during initial analysis (not as afterthought)
- Cite incident IDs inline as claims are written
- Use SMART criteria template for all recommendations
- Document PIR data quality issues earlier in process
```

### 18.6: Remediation Process

If any document receives ⚠️ or ❌ status:

1. **Review Verification Report:** Understand specific issues
2. **Address Issues:** Follow rewrite instructions
3. **Re-run Evaluator:** Verify fixes resolved problems
4. **Update Verification Report:** Document improvements
5. **Repeat until ✅:** Continue until document passes

### 18.7: Quality Gates

**Do NOT distribute documents to stakeholders until:**
- [ ] All documents have been evaluated by Evaluator.prompt.md
- [ ] All documents achieve ✅ APPROVED status (scores ≥0.8)
- [ ] Quality_Verification_Summary.md shows 100% pass rate
- [ ] All unverifiable claims have been resolved or removed
- [ ] All Kusto verification queries (Appendix B) have been tested
- [ ] All incident IDs referenced exist in source CSV

### 18.8: Output Files

After completing this section, the month folder should contain:

```
{MonthFolder}/
  ├── reports/
  │   ├── Executive_Summary_Blurb.md
  │   ├── PRIMO_Pulse.md
  │   ├── Detailed_Mitigation_Actions_Summary.md
  │   ├── {Month}_TTM_Analysis_Summary.md
  │   ├── {Month}_Narrative.md
  │   └── WhatIf.md
  └── verification/
      ├── Executive_Summary_Blurb_Verification.md
      ├── PRIMO_Pulse_Verification.md
      ├── Detailed_Mitigation_Actions_Summary_Verification.md
      ├── {Month}_TTM_Analysis_Summary_Verification.md
      ├── {Month}_Narrative_Verification.md
      ├── WhatIf_Verification.md
      └── Quality_Verification_Summary.md
```

### 18.9: Success Criteria

This section is complete when:
- ✅ All 6+ deliverables have been evaluated
- ✅ Individual verification reports created for each document
- ✅ Quality_Verification_Summary.md created
- ✅ All documents achieve ✅ APPROVED status (or documented exceptions)
- ✅ Quality gates checklist is 100% complete
- ✅ Documents are ready for stakeholder distribution

### 18.10: Integration with Previous Sections

**Section 16 (Verify Claims)** generates Kusto queries for verification.  
**Section 18** validates the entire document meets quality standards using those queries as supporting evidence.

**Workflow:**
1. Generate documents (Sections 1-17)
2. Add Kusto verification queries (Section 16)
3. Run Evaluator on all documents (Section 18)
4. Remediate issues if needed
5. Distribute to stakeholders

This ensures a comprehensive quality assurance process before stakeholder distribution.

