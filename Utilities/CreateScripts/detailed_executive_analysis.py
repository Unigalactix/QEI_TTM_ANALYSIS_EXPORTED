"""
Enhanced Executive Summary Analysis for October 2025
Provides detailed counts, percentages, and incident citations
"""

import pandas as pd
import numpy as np

# Read data
df = pd.read_csv('october_2025_ttm_filtered.csv', encoding='utf-8-sig')

print("="*80)
print("OCTOBER 2025 TTM ANALYSIS - DETAILED EXECUTIVE SUMMARY")
print("="*80)

# Question 1: How many outages met the north star of "less than 60 min TTM"?
north_star = df[df['TTM'] < 60]
north_star_count = len(north_star)
north_star_pct = north_star_count / len(df) * 100

print(f"\n1. NORTH STAR PERFORMANCE (<60 min TTM)")
print(f"   Met target: {north_star_count}/{len(df)} incidents ({north_star_pct:.1f}%)")
print(f"   Missed target: {len(df) - north_star_count}/{len(df)} incidents ({100-north_star_pct:.1f}%)")

# Question 2: Exclusions
total_raw = 129
excluded = 3
print(f"\n2. EXCLUSIONS FROM ANALYSIS")
print(f"   Excluded: {excluded}/{total_raw} incidents ({excluded/total_raw*100:.1f}%)")
print(f"   Analyzed: {len(df)}/{total_raw} incidents")

# Question 3: Top 3 LONGEST TTM OUTAGE EVENTS and P75 impact
print(f"\n3. TOP 3 LONGEST TTM OUTAGE EVENTS")
print(f"   NOTE: Looking for unique event systems (root events)")
print()

# Get unique root events by RootResponsibleIncidentId
if 'RootResponsibleIncidentId' in df.columns:
    # Group by root event to find event systems
    df['EventSystem'] = df['RootResponsibleIncidentId'].fillna(df['OutageIncidentId'])
    
    # Calculate total TTM per event system
    event_systems = df.groupby('EventSystem').agg({
        'TTM': 'sum',
        'OutageIncidentId': lambda x: list(x),
        'ServiceName': 'first',
        'Severity': 'first'
    }).reset_index()
    event_systems.columns = ['EventSystem', 'TotalTTM', 'Incidents', 'ServiceName', 'Severity']
    event_systems['IncidentCount'] = event_systems['Incidents'].apply(len)
    
    # Sort by total TTM
    top_events = event_systems.nlargest(3, 'TotalTTM')
else:
    # Fallback: just use individual incidents
    top_events = df.nlargest(3, 'TTM')[['OutageIncidentId', 'ServiceName', 'TTM', 'Severity']].copy()
    top_events['EventSystem'] = top_events['OutageIncidentId']
    top_events['TotalTTM'] = top_events['TTM']
    top_events['Incidents'] = top_events['OutageIncidentId'].apply(lambda x: [x])
    top_events['IncidentCount'] = 1

original_p75 = df['TTM'].quantile(0.75)
print(f"   Baseline P75 TTM: {original_p75:.1f} minutes")
print()

for idx, (_, event) in enumerate(top_events.iterrows(), 1):
    # Get all incidents in this event system
    if 'RootResponsibleIncidentId' in df.columns:
        event_incidents = df[df['EventSystem'] == event['EventSystem']]
    else:
        event_incidents = df[df['OutageIncidentId'] == event['EventSystem']]
    
    # Calculate P75 without this entire event system
    df_without = df[~df['OutageIncidentId'].isin(event['Incidents'])]
    new_p75 = df_without['TTM'].quantile(0.75)
    delta = original_p75 - new_p75
    pct_change = (delta / original_p75) * 100
    
    print(f"   Event #{idx}: Root Incident {int(event['EventSystem'])} - {event['ServiceName']}")
    print(f"   Total TTM: {int(event['TotalTTM'])} minutes ({int(event['TotalTTM']/60):.1f} hours)")
    print(f"   Incidents in event system: {event['IncidentCount']}")
    if event['IncidentCount'] > 1:
        print(f"   Incident IDs: {[int(x) for x in event['Incidents']]}")
    print(f"   Severity: {event['Severity']}")
    print(f"   P75 without this event: {new_p75:.1f} min")
    print(f"   Impact: Δ {delta:.1f} min ({pct_change:.1f}% reduction)")
    
    # Get narrative quotes for this event
    if len(event_incidents) > 0:
        root_incident = event_incidents.iloc[0]
        if pd.notna(root_incident.get('Symptoms')):
            print(f"   Symptoms: \"{root_incident['Symptoms'][:150]}...\"")
        if pd.notna(root_incident.get('RootCauses')):
            print(f"   Root Cause: \"{root_incident['RootCauses'][:150]}...\"")
    print()

# Question 4: P75 TTM if we remove TTO
print(f"\n4. P75 TTM ANALYSIS: DETECTION vs MITIGATION")
df['Mitigation_Time'] = df['TTM'] - df['TTO']
mitigation_p75 = df['Mitigation_Time'].quantile(0.75)
tto_p75 = df['TTO'].quantile(0.75)
ttm_p75 = df['TTM'].quantile(0.75)

print(f"   P75 TTM (Total): {ttm_p75:.1f} minutes")
print(f"   P75 TTO (Detection/Diagnosis): {tto_p75:.1f} minutes ({tto_p75/ttm_p75*100:.1f}% of P75 TTM)")
print(f"   P75 Mitigation (TTM - TTO): {mitigation_p75:.1f} minutes ({mitigation_p75/ttm_p75*100:.1f}% of P75 TTM)")
print(f"\n   → Mitigation represents {mitigation_p75/ttm_p75*100:.1f}% of P75 TTM")
print(f"   → If we achieve zero detection time, P75 would be {mitigation_p75:.1f} minutes")

# Question 5: Factors causing high mitigation time
print(f"\n5. FACTORS DRIVING HIGH MITIGATION TIME (TTM - TTO > P80)")
print("="*80)

mitigation_p80 = df['Mitigation_Time'].quantile(0.80)
high_mit = df[df['Mitigation_Time'] >= mitigation_p80].copy()
normal_mit = df[df['Mitigation_Time'] < mitigation_p80].copy()

print(f"\nHigh Mitigation Threshold (P80): {mitigation_p80:.1f} minutes")
print(f"High Mitigation Incidents: {len(high_mit)}/{len(df)} ({len(high_mit)/len(df)*100:.1f}%)")
print(f"Normal Mitigation Incidents: {len(normal_mit)}/{len(df)} ({len(normal_mit)/len(df)*100:.1f}%)")

# Save detailed incident lists for appendix
high_mit_ids = high_mit['OutageIncidentId'].tolist()
normal_mit_ids = normal_mit['OutageIncidentId'].tolist()

print(f"\n{'='*80}")
print("A. AUTOMATION GAPS")
print(f"{'='*80}")

# Automation analysis
automation_high = high_mit[high_mit['HowFixed'].str.contains('Automation', na=False)]
automation_normal = normal_mit[normal_mit['HowFixed'].str.contains('Automation', na=False)]
adhoc_high = high_mit[high_mit['HowFixed'].str.contains('Ad-Hoc', case=False, na=False)]
adhoc_normal = normal_mit[normal_mit['HowFixed'].str.contains('Ad-Hoc', case=False, na=False)]

print(f"\nAutomation-Resolved Incidents:")
print(f"  High Mitigation: {len(automation_high)}/{len(high_mit)} ({len(automation_high)/len(high_mit)*100:.1f}%)")
print(f"  Normal Mitigation: {len(automation_normal)}/{len(normal_mit)} ({len(automation_normal)/len(normal_mit)*100:.1f}%)")
print(f"  Gap: {len(automation_normal)/len(normal_mit)*100 - len(automation_high)/len(high_mit)*100:.1f} percentage points")

if len(automation_high) > 0:
    print(f"\n  High Mitigation Automation-Resolved Incidents:")
    for _, inc in automation_high.iterrows():
        print(f"    - {int(inc['OutageIncidentId'])}: {inc['ServiceName']}, Mitigation: {int(inc['Mitigation_Time'])} min")

print(f"\nAd-Hoc Resolution Incidents:")
print(f"  High Mitigation: {len(adhoc_high)}/{len(high_mit)} ({len(adhoc_high)/len(high_mit)*100:.1f}%)")
print(f"  Normal Mitigation: {len(adhoc_normal)}/{len(normal_mit)} ({len(adhoc_normal)/len(normal_mit)*100:.1f}%)")
print(f"  Gap: {len(adhoc_high)/len(high_mit)*100 - len(adhoc_normal)/len(normal_mit)*100:.1f} percentage points")

avg_adhoc_high = adhoc_high['Mitigation_Time'].mean() if len(adhoc_high) > 0 else 0
avg_adhoc_normal = adhoc_normal['Mitigation_Time'].mean() if len(adhoc_normal) > 0 else 0
print(f"\n  Average Mitigation Time:")
print(f"    High Mitigation Ad-Hoc: {avg_adhoc_high:.0f} minutes")
print(f"    Normal Mitigation Ad-Hoc: {avg_adhoc_normal:.0f} minutes")
print(f"    Multiplier: {avg_adhoc_high/avg_adhoc_normal:.1f}x" if avg_adhoc_normal > 0 else "")

# Sample ad-hoc incidents with quotes
print(f"\n  Sample High Mitigation Ad-Hoc Incidents (with quotes):")
adhoc_sample = adhoc_high.nlargest(3, 'Mitigation_Time')
for _, inc in adhoc_sample.iterrows():
    print(f"\n    Incident {int(inc['OutageIncidentId'])} - {inc['ServiceName']}")
    print(f"    Mitigation Time: {int(inc['Mitigation_Time'])} min, Severity: {inc['Severity']}")
    if pd.notna(inc.get('HowFixed')):
        print(f"    How Fixed: \"{inc['HowFixed']}\"")
    if pd.notna(inc.get('MitigationDescription')):
        print(f"    Mitigation: \"{inc['MitigationDescription'][:200]}\"")

print(f"\n{'='*80}")
print("B. ROOT CAUSE PATTERNS")
print(f"{'='*80}")

if 'RootCauseCategory' in df.columns:
    high_causes = high_mit['RootCauseCategory'].value_counts()
    normal_causes = normal_mit['RootCauseCategory'].value_counts()
    
    print(f"\nHigh Mitigation Time Root Causes:")
    for cause, count in high_causes.head(5).items():
        if pd.notna(cause):
            pct = count / len(high_mit[high_mit['RootCauseCategory'].notna()]) * 100
            avg_mit = high_mit[high_mit['RootCauseCategory'] == cause]['Mitigation_Time'].mean()
            incidents = high_mit[high_mit['RootCauseCategory'] == cause]['OutageIncidentId'].tolist()
            print(f"\n  {cause}:")
            print(f"    Count: {count}/{len(high_mit[high_mit['RootCauseCategory'].notna()])} ({pct:.1f}%)")
            print(f"    Avg Mitigation: {avg_mit:.0f} minutes")
            print(f"    Incident IDs: {[int(x) for x in incidents]}")
            
            # Get a quote from one incident
            sample = high_mit[high_mit['RootCauseCategory'] == cause].iloc[0]
            if pd.notna(sample.get('RootCauses')):
                print(f"    Example Quote (Incident {int(sample['OutageIncidentId'])}):")
                print(f"    \"{sample['RootCauses'][:250]}...\"")

print(f"\n{'='*80}")
print("C. SERVICE-SPECIFIC PATTERNS")
print(f"{'='*80}")

service_high = high_mit.groupby('ServiceName').agg({
    'Mitigation_Time': ['count', 'mean', 'sum'],
    'OutageIncidentId': lambda x: list(x)
}).round(0)
service_high.columns = ['Count', 'Avg_Mitigation', 'Total_Mitigation', 'IncidentIDs']
service_high = service_high.sort_values('Total_Mitigation', ascending=False).head(5)

print(f"\nTop 5 Services by Total Mitigation Time (High Mitigation Cohort):")
for service, row in service_high.iterrows():
    pct = row['Total_Mitigation'] / high_mit['Mitigation_Time'].sum() * 100
    print(f"\n  {service}:")
    print(f"    Incidents: {int(row['Count'])}/{len(high_mit)} ({int(row['Count'])/len(high_mit)*100:.1f}% of high-mit incidents)")
    print(f"    Avg Mitigation: {int(row['Avg_Mitigation'])} minutes")
    print(f"    Total Mitigation: {int(row['Total_Mitigation'])} minutes ({pct:.1f}% of all high-mit time)")
    print(f"    Incident IDs: {[int(x) for x in row['IncidentIDs']]}")
    
    # Get sample quote
    service_incidents = high_mit[high_mit['ServiceName'] == service]
    sample = service_incidents.nlargest(1, 'Mitigation_Time').iloc[0]
    print(f"    Longest Incident Quote ({int(sample['OutageIncidentId'])}, {int(sample['Mitigation_Time'])} min):")
    if pd.notna(sample.get('Symptoms')):
        print(f"    Symptoms: \"{sample['Symptoms'][:200]}...\"")

print(f"\n{'='*80}")
print("D. SEVERITY ANALYSIS")
print(f"{'='*80}")

print(f"\nHigh Mitigation Time by Severity:")
for sev in sorted(high_mit['Severity'].unique()):
    sev_incidents = high_mit[high_mit['Severity'] == sev]
    count = len(sev_incidents)
    pct = count / len(high_mit) * 100
    avg_mit = sev_incidents['Mitigation_Time'].mean()
    ids = sev_incidents['OutageIncidentId'].tolist()
    
    print(f"\n  Severity {sev}:")
    print(f"    Count: {count}/{len(high_mit)} ({pct:.1f}%)")
    print(f"    Avg Mitigation: {avg_mit:.0f} minutes")
    print(f"    Incident IDs: {[int(x) for x in ids][:10]}{'...' if len(ids) > 10 else ''}")

print(f"\n{'='*80}")
print("E. PROCESS GAPS: TSG vs Ad-Hoc Resolution")
print(f"{'='*80}")

tsg_high = high_mit[high_mit['HowFixed'].str.contains('TSG', na=False)]
tsg_normal = normal_mit[normal_mit['HowFixed'].str.contains('TSG', na=False)]

print(f"\nTSG-Resolved Incidents:")
print(f"  High Mitigation: {len(tsg_high)}/{len(high_mit)} ({len(tsg_high)/len(high_mit)*100:.1f}%)")
print(f"  Normal Mitigation: {len(tsg_normal)}/{len(normal_mit)} ({len(tsg_normal)/len(normal_mit)*100:.1f}%)")

if len(tsg_high) > 0:
    avg_tsg_high = tsg_high['Mitigation_Time'].mean()
    print(f"  Avg Mitigation (High cohort, TSG): {avg_tsg_high:.0f} minutes")
    print(f"  TSG Incident IDs (High Mitigation): {[int(x) for x in tsg_high['OutageIncidentId'].tolist()]}")

# Compare TSG vs Ad-Hoc in high mitigation cohort
if len(tsg_high) > 0 and len(adhoc_high) > 0:
    print(f"\n  High Mitigation Cohort Comparison:")
    print(f"    TSG Resolution: {len(tsg_high)} incidents, {tsg_high['Mitigation_Time'].mean():.0f} min avg")
    print(f"    Ad-Hoc Resolution: {len(adhoc_high)} incidents, {adhoc_high['Mitigation_Time'].mean():.0f} min avg")
    print(f"    Multiplier: Ad-Hoc takes {adhoc_high['Mitigation_Time'].mean()/tsg_high['Mitigation_Time'].mean():.1f}x longer than TSG")

print(f"\n{'='*80}")
print("APPENDIX: INCIDENT CLASSIFICATIONS")
print(f"{'='*80}")

print(f"\nHigh Mitigation Time Incidents (n={len(high_mit)}):")
print(f"IDs: {[int(x) for x in sorted(high_mit_ids)]}")

print(f"\nNormal Mitigation Time Incidents (n={len(normal_mit)}):")
print(f"IDs (first 20): {[int(x) for x in sorted(normal_mit_ids)[:20]]}...")

# Save to CSV for reference
output_data = {
    'Cohort': ['High Mitigation'] * len(high_mit_ids) + ['Normal Mitigation'] * len(normal_mit_ids),
    'OutageIncidentId': high_mit_ids + normal_mit_ids
}
cohort_df = pd.DataFrame(output_data)
cohort_df.to_csv('mitigation_time_cohorts.csv', index=False, encoding='utf-8-sig')
print(f"\n✓ Cohort classifications saved to: mitigation_time_cohorts.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
