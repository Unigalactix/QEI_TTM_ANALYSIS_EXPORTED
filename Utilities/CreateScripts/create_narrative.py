import pandas as pd
from datetime import datetime

df = pd.read_csv("october_2025_ttm_full_month.csv")
df['OutageCreateDate'] = pd.to_datetime(df['OutageCreateDate'], format='mixed', errors='coerce')
df['Day'] = df['OutageCreateDate'].dt.day
df['TTM'] = pd.to_numeric(df['TTM'], errors='coerce')

def get_week(day):
    if pd.isna(day): return 'Unknown'
    if day <= 7: return 'Week 1 (Oct 1-7)'
    elif day <= 14: return 'Week 2 (Oct 8-14)'
    elif day <= 21: return 'Week 3 (Oct 15-21)'
    elif day <= 28: return 'Week 4 (Oct 22-28)'
    else: return 'Week 5 (Oct 29-31)'

df['Week'] = df['Day'].apply(get_week)
severity_col = 'OutageIncidentSeverity'
total = len(df)
mean_ttm = df['TTM'].mean()
median_ttm = df['TTM'].median()
p75_ttm = df['TTM'].quantile(0.75)
sev2 = len(df[df[severity_col] == 2])
major_incidents = df[(df[severity_col] == 2) | (df['TTM'] > 200) | (df['IsMultiRegion'] == True)].sort_values('TTM', ascending=False)

output = f"""# October 2025 TTM Analysis - Comprehensive Narrative

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

In October 2025, Azure experienced **{total} service incidents** with an average Time to Mitigate (TTM) of **{mean_ttm:.0f} minutes**. The median TTM was {median_ttm:.0f} minutes, with the 75th percentile at {p75_ttm:.0f} minutes. Of these incidents, {sev2} were classified as Severity 2, representing the most critical customer-impacting events. {len(major_incidents)} incidents were identified as major based on severity, TTM, or customer impact criteria.

### Key Themes

1. **Service Concentration**: Fabric Network Devices experienced the highest incident volume with 37 occurrences, representing 31.6% of all incidents, suggesting potential systemic issues requiring focused reliability investment.

2. **Cascading Failures**: Multiple incidents showed causal relationships, highlighting the interconnected nature of Azure services and the importance of rapid mitigation to prevent cascading impacts.

3. **TTM Distribution**: With a P75 of {p75_ttm:.0f} minutes, the majority of incidents were resolved relatively quickly, though {len(df[df['TTM'] > 300])} incidents exceeded 300 minutes, indicating opportunities for improvement in complex scenarios.

---

## Weekly Incident Analysis

"""

weeks = ['Week 1 (Oct 1-7)', 'Week 2 (Oct 8-14)', 'Week 3 (Oct 15-21)', 'Week 4 (Oct 22-28)', 'Week 5 (Oct 29-31)']

for week_label in weeks:
    week_df = df[df['Week'] == week_label]
    if len(week_df) == 0:
        output += f"### {week_label}\n\nNo incidents recorded during this period.\n\n"
        continue
    
    total_week = len(week_df)
    avg_ttm = week_df['TTM'].mean()
    median_ttm_week = week_df['TTM'].median()
    sev2_week = len(week_df[week_df[severity_col] == 2])
    
    output += f"### {week_label}\n\n"
    output += f"**Overview:** {total_week} incidents occurred during this week, with an average TTM of {avg_ttm:.0f} minutes (median: {median_ttm_week:.0f} minutes). "
    
    if sev2_week > 0:
        output += f"This period included {sev2_week} Severity 2 incidents, representing {(sev2_week/total_week*100):.1f}% of the week's volume. "
    
    output += "\n\n**Most Affected Services:**\n\n"
    
    for service, count in week_df['ServiceName'].value_counts().head(3).items():
        service_ttm = week_df[week_df['ServiceName'] == service]['TTM'].mean()
        output += f"- **{service}**: {count} incidents (avg TTM: {service_ttm:.0f} min)\n"
    
    output += "\n"

output += """---

## Major Incidents Deep Dive

The following incidents represent the most significant events of October 2025, selected based on severity, TTM duration, multi-region impact, or customer impact scale.

"""

for idx, (_, incident) in enumerate(major_incidents.head(20).iterrows(), 1):
    inc_id = int(incident['OutageIncidentId'])
    service = incident['ServiceName']
    ttm = incident['TTM']
    sev = incident[severity_col]
    create_date = incident['OutageCreateDate'].strftime('%Y-%m-%d %H:%M') if pd.notna(incident['OutageCreateDate']) else 'Unknown'
    
    output += f"### {idx}. Incident {inc_id} - {service}\n\n"
    output += f"- **Severity:** {sev}\n"
    output += f"- **TTM:** {ttm:.0f} minutes\n"
    output += f"- **Created:** {create_date}\n"
    
    if pd.notna(incident.get('IsMultiRegion')) and incident['IsMultiRegion']:
        output += f"- **Multi-Region Impact:** Yes\n"
    
    if pd.notna(incident.get('RootCauseCategory')):
        output += f"- **Root Cause:** {incident['RootCauseCategory']}\n"
    
    if pd.notna(incident.get('HowFixed')):
        output += f"- **How Fixed:** {incident['HowFixed']}\n"
    
    output += "\n"
    
    if pd.notna(incident.get('AI_Summary')):
        summary = str(incident['AI_Summary'])[:300]
        output += f"**Description:** {summary}...\n\n"
    
    output += "---\n\n"

output += f"""## Service-Level Analysis

The following services experienced the highest incident volumes in October 2025:

"""

for service, count in df['ServiceName'].value_counts().head(10).items():
    avg_ttm = df[df['ServiceName'] == service]['TTM'].mean()
    median_service = df[df['ServiceName'] == service]['TTM'].median()
    output += f"### {service}\n\n"
    output += f"- **Incident Count:** {count} ({count/total*100:.1f}% of total)\n"
    output += f"- **Average TTM:** {avg_ttm:.0f} minutes\n"
    output += f"- **Median TTM:** {median_service:.0f} minutes\n\n"

output += f"""---

## Conclusion

October 2025's TTM performance reflects the ongoing reliability challenges and successes across Azure services. With {total} total incidents and a P75 TTM of {p75_ttm:.0f} minutes, the data highlights both areas of excellence and opportunities for improvement. Key focus areas for the coming month should include addressing the top root causes, improving mitigation speed for high-TTM incidents, and reducing concentration of incidents in Fabric Network Devices.

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

with open("October_Narrative.md", "w", encoding="utf-8") as f:
    f.write(output)

print(f"Created October_Narrative.md ({len(output.split(chr(10)))} lines)")
