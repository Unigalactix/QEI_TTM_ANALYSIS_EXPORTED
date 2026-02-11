import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data/october_2025_ttm_filtered.csv')

print('=' * 80)
print('FULL E2E AUTOMATION ANALYSIS (Detection + Mitigation)')
print('Using HowFixed and Is_IA_Mitigation fields')
print('=' * 80)

# Every incident in this dataset is auto-detected (confirmed in Executive Summary)
total_incidents = len(df)
print(f'\nTotal incidents in analysis: {total_incidents}')
print(f'Auto-detected incidents: {total_incidents} (100% - confirmed)')

# Check for Is_IA_Mitigation column (indicates actual mitigation automation)
if 'Is_IA_Mitigation' not in df.columns:
    print(f'\n⚠️  Column "Is_IA_Mitigation" not found in dataset.')
    exit(1)

if 'HowFixed' not in df.columns:
    print(f'\n⚠️  Column "HowFixed" not found in dataset.')
    exit(1)

# Count incidents with Is_IA_Mitigation = True (automatic mitigation actions)
ia_mitigation_true = df['Is_IA_Mitigation'].notna() & (df['Is_IA_Mitigation'] == True)
ia_mitigation_count = ia_mitigation_true.sum()

# Also count transient/false alarm incidents (auto-resolved without human mitigation)
transient_keywords = ['Transient', 'False Alarm', 'transient', 'false alarm']
is_transient = df['HowFixed'].notna() & df['HowFixed'].str.contains('|'.join(transient_keywords), case=False, na=False)
transient_count = is_transient.sum()

# Full E2E = IA Mitigation OR Transient/False Alarm
full_e2e_mask = ia_mitigation_true | is_transient
full_e2e_count = full_e2e_mask.sum()

print(f'\n' + '=' * 80)
print('AUTOMATIC MITIGATION:')
print('=' * 80)
print(f'  IA mitigation actions (Is_IA_Mitigation = True): {ia_mitigation_count} ({ia_mitigation_count/total_incidents*100:.1f}%)')
print(f'  Transient/False Alarm (auto-resolved): {transient_count} ({transient_count/total_incidents*100:.1f}%)')
print(f'  Total automatic mitigation: {full_e2e_count} ({full_e2e_count/total_incidents*100:.1f}%)')
print(f'  Manual mitigation required: {total_incidents - full_e2e_count} ({(total_incidents - full_e2e_count)/total_incidents*100:.1f}%)')

print(f'\n' + '=' * 80)
print('FULL E2E AUTOMATION (Auto-Detection + Auto-Mitigation):')
print('=' * 80)
print(f'  Full E2E automated incidents: {full_e2e_count} ({full_e2e_count/total_incidents*100:.1f}%)')
print(f'    - IA mitigation actions: {ia_mitigation_count}')
print(f'    - Transient/False Alarm: {transient_count}')
print(f'  Manual mitigation required: {total_incidents - full_e2e_count} ({(total_incidents - full_e2e_count)/total_incidents*100:.1f}%)')

# Analyze HowFixed field for all incidents
print(f'\n' + '=' * 80)
print('HOW INCIDENTS WERE FIXED (HowFixed field):')
print('=' * 80)

# Get unique HowFixed values
howfixed_counts = df['HowFixed'].value_counts()
print(f'Total incidents with HowFixed data: {df["HowFixed"].notna().sum()}/{total_incidents}')
print(f'\nHowFixed breakdown:')
for howfixed, count in howfixed_counts.items():
    pct = count / total_incidents * 100
    print(f'  {howfixed}: {count} ({pct:.1f}%)')

# Show correlation between HowFixed and Is_IA_Mitigation
print(f'\n' + '=' * 80)
print('HOWFIXED vs IS_IA_MITIGATION CORRELATION:')
print('=' * 80)

for howfixed in howfixed_counts.index:
    howfixed_mask = df['HowFixed'] == howfixed
    howfixed_count = howfixed_mask.sum()
    howfixed_ia = (df[howfixed_mask]['Is_IA_Mitigation'] == True).sum()
    pct = howfixed_ia / howfixed_count * 100 if howfixed_count > 0 else 0
    print(f'\n{howfixed} ({howfixed_count} incidents):')
    print(f'  With IA mitigation: {howfixed_ia} ({pct:.1f}%)')
    print(f'  Without IA mitigation: {howfixed_count - howfixed_ia} ({(100-pct):.1f}%)')

# TTM performance comparison
if full_e2e_count > 0:
    e2e_df = df[full_e2e_mask]
    e2e_ttm_mean = e2e_df['TTM'].mean()
    e2e_ttm_p75 = e2e_df['TTM'].quantile(0.75)
    
    non_e2e_df = df[~full_e2e_mask]
    non_e2e_ttm_mean = non_e2e_df['TTM'].mean()
    non_e2e_ttm_p75 = non_e2e_df['TTM'].quantile(0.75)
    
    print(f'\n' + '=' * 80)
    print('TTM PERFORMANCE COMPARISON:')
    print('=' * 80)
    print(f'Full E2E Automation ({full_e2e_count} incidents):')
    print(f'  Mean TTM: {e2e_ttm_mean:.1f} minutes')
    print(f'  P75 TTM: {e2e_ttm_p75:.1f} minutes')
    
    print(f'\nManual Mitigation Required ({total_incidents - full_e2e_count} incidents):')
    print(f'  Mean TTM: {non_e2e_ttm_mean:.1f} minutes')
    print(f'  P75 TTM: {non_e2e_ttm_p75:.1f} minutes')
    
    diff_mean = non_e2e_ttm_mean - e2e_ttm_mean
    diff_pct = (diff_mean / non_e2e_ttm_mean * 100) if non_e2e_ttm_mean > 0 else 0
    print(f'\nPerformance Impact:')
    print(f'  Manual mitigation incidents have {diff_mean:.1f} min higher mean TTM ({diff_pct:.1f}%)')

# Examples of E2E automated incidents
if full_e2e_count > 0:
    print(f'\n' + '=' * 80)
    print('TOP 5 E2E AUTOMATED INCIDENTS (by TTM):')
    print('=' * 80)
    top_e2e = e2e_df.nlargest(5, 'TTM')[['OutageIncidentId', 'ServiceName', 'TTM', 'TTO', 'TTFix', 'HowFixed']]
    for idx, row in top_e2e.iterrows():
        incident_id = int(row['OutageIncidentId'])
        service = row['ServiceName']
        ttm = row['TTM']
        tto = row['TTO']
        ttfix = row['TTFix']
        howfixed = row['HowFixed']
        print(f'\nIncident {incident_id}:')
        print(f'  Service: {service}')
        print(f'  TTM: {ttm:.1f} min | TTO: {tto:.1f} min | TTFix: {ttfix:.1f} min')
        print(f'  HowFixed: {howfixed}')
    
    # Bottom 5 (fastest E2E automated incidents)
    print(f'\n' + '=' * 80)
    print('TOP 5 FASTEST E2E AUTOMATED INCIDENTS:')
    print('=' * 80)
    bottom_e2e = e2e_df.nsmallest(5, 'TTM')[['OutageIncidentId', 'ServiceName', 'TTM', 'TTO', 'TTFix', 'HowFixed']]
    for idx, row in bottom_e2e.iterrows():
        incident_id = int(row['OutageIncidentId'])
        service = row['ServiceName']
        ttm = row['TTM']
        tto = row['TTO']
        ttfix = row['TTFix']
        howfixed = row['HowFixed']
        print(f'\nIncident {incident_id}:')
        print(f'  Service: {service}')
        print(f'  TTM: {ttm:.1f} min | TTO: {tto:.1f} min | TTFix: {ttfix:.1f} min')
        print(f'  HowFixed: {howfixed}')
    
    # Breakdown by type
    print(f'\n' + '=' * 80)
    print('E2E AUTOMATION BREAKDOWN BY TYPE:')
    print('=' * 80)
    
    ia_only = df[ia_mitigation_true & ~is_transient]
    transient_only = df[is_transient & ~ia_mitigation_true]
    both = df[ia_mitigation_true & is_transient]
    
    print(f'  IA Mitigation only: {len(ia_only)} incidents')
    if len(ia_only) > 0:
        print(f'    Mean TTM: {ia_only["TTM"].mean():.1f} min')
    
    print(f'  Transient/False Alarm only: {len(transient_only)} incidents')
    if len(transient_only) > 0:
        print(f'    Mean TTM: {transient_only["TTM"].mean():.1f} min')
    
    print(f'  Both IA + Transient: {len(both)} incidents')
    if len(both) > 0:
        print(f'    Mean TTM: {both["TTM"].mean():.1f} min')

# Services with highest E2E automation rate
print(f'\n' + '=' * 80)
print('SERVICES WITH HIGHEST E2E AUTOMATION RATE (2+ incidents):')
print('=' * 80)

service_stats = df.groupby('ServiceName').agg({
    'OutageIncidentId': 'count',
}).rename(columns={'OutageIncidentId': 'Total'})
service_stats['E2E_Automated'] = df.groupby('ServiceName').apply(
    lambda x: ((x['Is_IA_Mitigation'] == True) | (x['HowFixed'].notna() & x['HowFixed'].str.contains('Transient|False Alarm', case=False, na=False))).sum()
)
service_stats['E2E_Rate'] = (service_stats['E2E_Automated'] / service_stats['Total'] * 100).round(1)
service_stats = service_stats[service_stats['Total'] >= 2]  # At least 2 incidents
service_stats = service_stats.sort_values('E2E_Rate', ascending=False).head(10)

for service, row in service_stats.iterrows():
    print(f'\n{service}:')
    print(f'  Total incidents: {int(row["Total"])}')
    print(f'  E2E automated: {int(row["E2E_Automated"])} ({row["E2E_Rate"]:.1f}%)')

# Examples of non-E2E incidents
if total_incidents - full_e2e_count > 0:
    print(f'\n' + '=' * 80)
    print(f'MANUAL MITIGATION REQUIRED - {total_incidents - full_e2e_count} incidents:')
    print('=' * 80)
    non_e2e_sample = non_e2e_df.nlargest(5, 'TTM')[['OutageIncidentId', 'ServiceName', 'TTM', 'TTO', 'TTFix', 'HowFixed']]
    for idx, row in non_e2e_sample.iterrows():
        incident_id = int(row['OutageIncidentId'])
        service = row['ServiceName']
        ttm = row['TTM']
        tto = row['TTO']
        ttfix = row['TTFix']
        howfixed = row['HowFixed']
        print(f'\nIncident {incident_id}:')
        print(f'  Service: {service}')
        print(f'  TTM: {ttm:.1f} min | TTO: {tto:.1f} min | TTFix: {ttfix:.1f} min')
        print(f'  HowFixed: {howfixed}')

print(f'\n' + '=' * 80)
print('SUMMARY:')
print('=' * 80)
print(f'✓ Full E2E Automation (Detection + Mitigation): {full_e2e_count}/{total_incidents} ({full_e2e_count/total_incidents*100:.1f}%)')
print(f'  - IA Mitigation: {ia_mitigation_count} incidents')
print(f'  - Transient/False Alarm: {transient_count} incidents')
print(f'✓ Manual Mitigation Required: {total_incidents - full_e2e_count}/{total_incidents} ({(total_incidents - full_e2e_count)/total_incidents*100:.1f}%)')
print(f'\n✓ Analysis based on:')
print(f'  - Detection: IsAutoDetectedAllClouds (100%)')
print(f'  - Mitigation: Is_IA_Mitigation + Transient/False Alarm in HowFixed')
print(f'  - Context: HowFixed field')
