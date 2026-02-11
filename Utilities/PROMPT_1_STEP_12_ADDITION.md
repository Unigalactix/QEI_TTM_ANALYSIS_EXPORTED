# Step 12 Addition for PROMPT_1.md.prompt.md

## Instructions for Adding to PROMPT_1.md.prompt.md

Add this as **Step 12** at the end of the PROMPT_1.md.prompt.md file (after Step 11: Dashboard Generation):

---

## Step 12: Generate Executive Summary Blurb

Based on the analysis completed, write a comprehensive executive summary document (`Executive_Summary_Blurb.md`) that answers the following questions:

### Questions to Answer:

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

### Required Format Elements:

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

### Implementation Steps:

1. **Create detailed analysis script** (`detailed_executive_analysis.py`):
   - Read filtered dataset (e.g., `october_2025_ttm_filtered.csv`)
   - Calculate all required metrics with exact counts
   - Extract verbatim quotes from narrative fields
   - Identify event systems using RootResponsibleIncidentId
   - Classify incidents into high vs. normal mitigation cohorts
   - Generate comprehensive console output
   - Export cohort classifications to CSV

2. **Generate Executive Summary document** (`Executive_Summary_Blurb.md`):
   - Professional business narrative format
   - 5 main sections answering each question
   - Detailed subsections with counts, percentages, quotes, and incident IDs
   - Recommendations section with prioritized actions
   - Comprehensive appendix with all incident classifications

### Expected Outputs:

- **Executive_Summary_Blurb.md**: 5-10 page comprehensive executive summary
- **detailed_executive_analysis.py**: Python script for all calculations
- **mitigation_time_cohorts.csv**: Incident classifications (High vs. Normal mitigation)
- **executive_detailed_output.txt**: Full console output with all statistics

### Quality Criteria:

✓ Every statistic includes exact numerator/denominator  
✓ All claims cited to specific incident IDs  
✓ Verbatim quotes included where they add clarity  
✓ Complete incident lists in appendix  
✓ Business-focused recommendations  
✓ Actionable insights with expected benefits  

---

## Example Output Structure

```markdown
# [Month] 2025 TTM Performance: Executive Summary

## Overview
[High-level summary with key metrics and main finding]

## 1. North Star Performance
Met Target: X/Y incidents (Z%)
[Analysis with incident IDs and context]

## 2. Exclusions
Excluded: X/Y incidents (Z%)
[List of exclusions with reasons]

## 3. Top 3 Longest TTM Events
### Event #1: [Service] (Root Incident [ID])
- Total TTM: X minutes
- P75 Impact: Δ X min (Y% reduction)
- Symptoms: "[Verbatim quote...]"
- Root Cause: "[Verbatim quote...]"

## 4. Detection vs. Mitigation
P75 TTM: X min
P75 TTO: X min (Y%)
P75 Mitigation: X min (Y%)

## 5. Factors Driving High Mitigation Time
### A. Automation Gaps
[Analysis with counts, percentages, quotes, incident IDs]

### B. Root Cause Patterns
[Analysis with counts, percentages, quotes, incident IDs]

[Continue for all subsections...]

## Recommendations
[Priority 1-4 with impact, action, expected benefit]

## Appendix: Incident Classifications
### High Mitigation Time Incidents (n=X)
[Complete list of incident IDs]

### Normal Mitigation Time Incidents (n=Y)
[Complete list of incident IDs]
```

---

## Reference Implementation

See the October 2025 implementation in `OctTTM` folder:
- **Script**: `detailed_executive_analysis.py`
- **Output**: `Executive_Summary_Blurb.md`
- **Supporting**: `mitigation_time_cohorts.csv`
