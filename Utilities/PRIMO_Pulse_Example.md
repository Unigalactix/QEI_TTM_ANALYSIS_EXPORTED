## Primo Pulse Format Example

Please do the same 4 sections for the TTM analysis month and save as PRIMO_Pulse.md. Make the update short and more focused, 4 sentences max per section


# PRIMO Pulse - {Month & Year} TTM Analysis

**Analysis Period:** {Analysis Date Range}
**Report Date:** {Current Date}
**Focus Area:** Time to Mitigate (TTM) Performance & High Mitigation Drivers

---

## Situation/Summary

We completed October 2025 TTM analysis for 123 incidents, achieving 53.7% north star performance (<60 min TTM) with P75 at 133.0 minutes. High-mitigation incidents (25 of 123, 20.3%) are driven by lack of automation (0% adoption across all incidents) and ad-hoc resolution patterns (32% of high-mitigation incidents use ad-hoc steps vs 12.2% for normal incidents, taking 15.9x longer). New discovery: severity escalations, though rare (2.4%), showed 128% longer mitigation time. The top 3 events (incidents 694538461, 699333062, 693886253) were single-incident outages with minimal P75 impact.

---

## Highlights

Generated 22 deliverable files including Executive Summary, WhatIf analysis, PowerPoint presentation, and interactive dashboard. Identified service concentration: top 5 services (SQL Control Plane, Fabric Network Devices, SDN PubSub, Xstore, Service Bus) represent majority of high-mitigation time, providing clear automation investment targets. Discovered transitive severity escalations as potential early-warning signal for complex incidents (2.3x longer mitigation time, though based on only 3 incidents). Updated TTM Analysis workflow to include event cascades, geographic distribution, and severity escalation analysis for future monthly reports.

---

## Issues/Risks

Zero automation adoption across all 123 incidents (0% for both high and normal mitigation cohorts) represents a systemic gap. High-mitigation incidents show 32% ad-hoc resolution rate (8/25) vs 12.2% (12/98) for normal incidents, with ad-hoc approaches taking 542 min average (15.9x longer). Service concentration: 3 services (SQL Control Plane, Fabric Network Devices, SDN PubSub) account for 64.6% of high-mitigation time. Current systems lack early-warning mechanisms to identify incidents likely to require severity escalation (n=3 sample size limits predictive modeling).

---

## Next Steps

Develop TSGs and automation for top 5 services to address majority of high-mitigation time [Q1 2026, Owner: Service teams - requires resource commitment and prioritization]. Investigate early-warning system for severity escalations using predictive signals [Q1 2026, Owner: PRIMO Analytics - feasibility study needed given limited sample size]. Expand TSG coverage for top 10 high-mitigation root cause patterns to reduce ad-hoc resolution prevalence [Q1 2026, Owner: Service teams]. Execute November TTM analysis with enhanced workflow [Dec 2025, Owner: PRIMO Analytics].

---

## Appendix: Kusto Verification Queries

**Base Query Setup:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId;
```

---

### **Claim 1: 123 Incidents, 53.7% North Star, P75 = 133.0 min**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| summarize 
    TotalIncidents = count(),
    MetNorthStar = countif(TTM < 60),
    P75_TTM = percentile(TTM, 75)
| extend NorthStarPercentage = round(MetNorthStar * 100.0 / TotalIncidents, 1)
```

**Expected Output:** 123 total, 66 met north star (53.7%), P75 = 133.0 min

---

### **Claim 2: 25 of 123 (20.3%) High-Mitigation Incidents**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let p80Threshold = toscalar(ttmscope | summarize percentile(MitigationTime, 80));
ttmscope
| extend Cohort = iff(MitigationTime > p80Threshold, "High Mitigation", "Normal Mitigation")
| summarize 
    TotalIncidents = count(),
    HighMitigation = countif(Cohort == "High Mitigation"),
    P80_Threshold = p80Threshold
| extend HighMitigationPercentage = round(HighMitigation * 100.0 / TotalIncidents, 1)
```

**Expected Output:** 25 high-mitigation incidents (20.3%), P80 threshold = 108.6 min

---

### **Claim 3: 0% Automation Adoption (Both Cohorts)**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let p80Threshold = toscalar(ttmscope | summarize percentile(MitigationTime, 80));
ttmscope
| extend Cohort = iff(MitigationTime > p80Threshold, "High Mitigation", "Normal Mitigation")
| join kind=leftouter (cluster("icmdataro.centralus.kusto.windows.net").database("Reporting").Ingest_Report_TTTv1()) on $left.OutageIncidentId==$right.IncidentId
| summarize 
    HighMit_Total = countif(Cohort == "High Mitigation"),
    HighMit_Automation = countif(Cohort == "High Mitigation" and HowFixed == "Fixed with automation"),
    NormalMit_Total = countif(Cohort == "Normal Mitigation"),
    NormalMit_Automation = countif(Cohort == "Normal Mitigation" and HowFixed == "Fixed with automation"),
    AllIncidents_Total = count(),
    AllIncidents_Automation = countif(HowFixed == "Fixed with automation")
| extend 
    HighMit_AutomationPct = round(HighMit_Automation * 100.0 / HighMit_Total, 1),
    NormalMit_AutomationPct = round(NormalMit_Automation * 100.0 / NormalMit_Total, 1),
    AllIncidents_AutomationPct = round(AllIncidents_Automation * 100.0 / AllIncidents_Total, 1)
```

**Expected Output:** High: 0/25 (0%), Normal: 0/98 (0%), All: 0/123 (0%)

---

### **Claim 4: Ad-Hoc Resolution (32% vs 12.2%, 15.9x Slower)**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let p80Threshold = toscalar(ttmscope | summarize percentile(MitigationTime, 80));
ttmscope
| extend Cohort = iff(MitigationTime > p80Threshold, "High Mitigation", "Normal Mitigation")
| join kind=leftouter (cluster("icmdataro.centralus.kusto.windows.net").database("Reporting").Ingest_Report_TTTv1()) on $left.OutageIncidentId==$right.IncidentId
| summarize 
    HighMit_Total = countif(Cohort == "High Mitigation"),
    HighMit_AdHoc = countif(Cohort == "High Mitigation" and HowFixed == "Fixed with Ad-Hoc steps"),
    HighMit_AdHoc_AvgMit = avgif(MitigationTime, Cohort == "High Mitigation" and HowFixed == "Fixed with Ad-Hoc steps"),
    NormalMit_Total = countif(Cohort == "Normal Mitigation"),
    NormalMit_AdHoc = countif(Cohort == "Normal Mitigation" and HowFixed == "Fixed with Ad-Hoc steps"),
    NormalMit_AdHoc_AvgMit = avgif(MitigationTime, Cohort == "Normal Mitigation" and HowFixed == "Fixed with Ad-Hoc steps")
| extend 
    HighMit_AdHocPct = round(HighMit_AdHoc * 100.0 / HighMit_Total, 1),
    NormalMit_AdHocPct = round(NormalMit_AdHoc * 100.0 / NormalMit_Total, 1),
    Gap = HighMit_AdHocPct - NormalMit_AdHocPct,
    Multiplier = round(HighMit_AdHoc_AvgMit / NormalMit_AdHoc_AvgMit, 1)
```

**Expected Output:** High: 8/25 (32%), Normal: 12/98 (12.2%), Ad-hoc avg: 542 min vs 34 min (15.9x)

---

### **Claim 5: Severity Escalations (2.4%, 128% Longer Mitigation)**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let transitiveseverity = database("IcmDatawarehouse").IncidentHistory
| where ChangeDate >= startDate and ChangeDate <= endDate
| where ChangedBy == "CN=icmclient.v3workflow.icm.msftcloudes.com"
| mv-expand todynamic(ChangeCategories)
| where ChangeCategories in ("SeverityUpgrade", "OutageDeclared") or IsOutage == true
| join kind=inner database("IcmDatawarehouse").IncidentDescriptions on HistoryId, IncidentId
| where Text has "Transitive Severity"
| summarize by IncidentId;
ttmscope
| extend HasSeverityChange = iff(OutageIncidentId in (transitiveseverity), "Yes", "No")
| summarize 
    Count = count(),
    AvgTTM = avg(TTM),
    AvgMitigation = avg(MitigationTime)
    by HasSeverityChange
| extend 
    Percentage = round(Count * 100.0 / toscalar(ttmscope | count), 1)
| order by HasSeverityChange desc
```

**Expected Output:** 3 incidents (2.4%) with severity changes, 187.3 avg mitigation vs 82.1 (128% longer)

---

### **Claim 6: Top 3 Events (Incidents 694538461, 699333062, 693886253)**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| top 3 by TTM
| project OutageIncidentId, TTM, ServiceOfficialName, Severity, OutageCreateDate
```

**Expected Output:** 
- Incident 694538461: TTM 3035, SQL Control Plane, Severity 1
- Incident 699333062: TTM 1584, Azure Resource Manager, Severity 2
- Incident 693886253: TTM 1458, SQL MI Prod Clusters, Severity 2

---

### **Claim 7: Top 5 Services (SQL Control Plane, Fabric Network Devices, SDN PubSub, Xstore, Service Bus)**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let p80Threshold = toscalar(ttmscope | summarize percentile(MitigationTime, 80));
let totalHighMitTime = toscalar(ttmscope | where MitigationTime > p80Threshold | summarize sum(MitigationTime));
ttmscope
| where MitigationTime > p80Threshold
| summarize 
    Incidents = count(),
    TotalMitigation = sum(MitigationTime),
    AvgMitigation = avg(MitigationTime)
    by ServiceOfficialName
| extend PercentageOfTotal = round(TotalMitigation * 100.0 / totalHighMitTime, 1)
| order by TotalMitigation desc
| take 5
```

**Expected Output:** 
- SQL Control Plane: 1 incident, 2,981 min (35.5%)
- Fabric Network Devices: 7 incidents, 1,487 min (17.7%)
- SDN PubSub: 3 incidents, 960 min (11.4%)
- Xstore: 3 incidents, 543 min (6.5%)
- Service Bus: 2 incidents, 512 min (6.1%)

---

### **Claim 8: Top 3 Services Account for 64.6% of High-Mitigation Time**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let p80Threshold = toscalar(ttmscope | summarize percentile(MitigationTime, 80));
let totalHighMitTime = toscalar(ttmscope | where MitigationTime > p80Threshold | summarize sum(MitigationTime));
let top3Services = ttmscope
| where MitigationTime > p80Threshold
| summarize TotalMitigation = sum(MitigationTime) by ServiceOfficialName
| order by TotalMitigation desc
| take 3
| summarize Top3Total = sum(TotalMitigation);
ttmscope
| where MitigationTime > p80Threshold
| summarize 
    AllHighMitTime = sum(MitigationTime)
| extend 
    Top3Total = toscalar(top3Services),
    Top3Percentage = round(toscalar(top3Services) * 100.0 / sum(MitigationTime), 1)
```

**Expected Output:** Top 3 services: 64.6% of high-mitigation time

---

### **Claim 9: Ad-Hoc Takes 542 Min Average (High Mitigation)**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let p80Threshold = toscalar(ttmscope | summarize percentile(MitigationTime, 80));
ttmscope
| where MitigationTime > p80Threshold
| join kind=leftouter (cluster("icmdataro.centralus.kusto.windows.net").database("Reporting").Ingest_Report_TTTv1()) on $left.OutageIncidentId==$right.IncidentId
| where HowFixed == "Fixed with Ad-Hoc steps"
| summarize 
    AdHoc_Count = count(),
    AdHoc_AvgMitigation = avg(MitigationTime),
    AdHoc_TotalMitigation = sum(MitigationTime)
```

**Expected Output:** 8 ad-hoc incidents, 542 min average mitigation

---

### **Claim 10: Transitive Severity 2.3x Longer Mitigation Time**

**Query:**
```kusto
let startDate = startofday(todatetime('10/01/2025'));
let endDate = endofday(todatetime('10/31/2025'));
let ttmscope = cluster("icmdataro.centralus.kusto.windows.net").database("Common").Get_Bowler_Outages()
| where OutageCreateDate between(startDate..endDate)
| where (IsQCS == True or IsTier0 == True) and IsAutoDetectedAllClouds == 1
| where DivisionName == "Cloud + AI Platform"
| join kind=leftouter (Get_Icm_Outages() | project OutageIncidentId, TTEng, TTFix, TTD) on OutageIncidentId
| extend MitigationTime = TTM - TTO;
let transitiveseverity = database("IcmDatawarehouse").IncidentHistory
| where ChangeDate >= startDate and ChangeDate <= endDate
| where ChangedBy == "CN=icmclient.v3workflow.icm.msftcloudes.com"
| mv-expand todynamic(ChangeCategories)
| where ChangeCategories in ("SeverityUpgrade", "OutageDeclared") or IsOutage == true
| join kind=inner database("IcmDatawarehouse").IncidentDescriptions on HistoryId, IncidentId
| where Text has "Transitive Severity"
| summarize by IncidentId;
ttmscope
| extend HasSeverityChange = iff(OutageIncidentId in (transitiveseverity), "Yes", "No")
| summarize 
    Count = count(),
    AvgMitigation = avg(MitigationTime)
    by HasSeverityChange
| extend Multiplier = round(maxif(AvgMitigation, HasSeverityChange == "Yes") / maxif(AvgMitigation, HasSeverityChange == "No"), 1)
| where HasSeverityChange == "Yes"
```

**Expected Output:** 187.3 min avg (with changes) vs 82.1 min (without), 2.3x multiplier (187.3 / 82.1 = 2.28)
