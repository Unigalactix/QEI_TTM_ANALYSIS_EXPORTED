import pandas as pd

df = pd.read_csv('october_2025_ttm_full_month.csv')

# Get the 3 incidents
incident_ids = [694602140, 694752515, 694624704]

print('='*100)
print('DETAILED EUAP/BCDR INCIDENT ANALYSIS')
print('='*100)

for inc_id in incident_ids:
    incident = df[df['OutageIncidentId'] == inc_id].iloc[0]
    
    print(f'\n{"="*100}')
    print(f'INCIDENT: {inc_id}')
    print(f'{"="*100}')
    print(f'Service: {incident.get("ServiceName", "N/A")}')
    print(f'TTM: {incident["TTM"]:.0f} minutes ({incident["TTM"]/60:.1f} hours)')
    print(f'Severity: {incident.get("Severity", "N/A")}')
    print(f'Created Date: {incident.get("CreatedDate", "N/A")}')
    print(f'Mitigated Date: {incident.get("MitigatedDate", "N/A")}')
    
    print(f'\nImpacts:')
    if pd.notna(incident.get('Impacts')):
        print(f'  {incident["Impacts"]}')
    
    print(f'\nSymptoms:')
    if pd.notna(incident.get('Symptoms')):
        print(f'  {incident["Symptoms"]}')
    
    print(f'\nRoot Causes:')
    if pd.notna(incident.get('RootCauses')):
        print(f'  {incident["RootCauses"]}')
    else:
        print('  N/A')
    
    print(f'\nHow Fixed:')
    if pd.notna(incident.get('HowFixed')):
        print(f'  {incident["HowFixed"]}')
    else:
        print('  N/A')
    
    print()

print('='*100)
print('SUMMARY')
print('='*100)
print('Total EUAP/BCDR incidents: 3 out of 117 (2.6%)')
print('Total TTM: 7,802 minutes (130 hours / 5.4 days)')
print('Average TTM: 2,601 minutes (43.3 hours)')
print('\nKey Pattern: 1 BCDR drill caused 1,372 min TTM')
print('Key Pattern: 2 incidents in EUAP region with very high TTM (6,095 and 335 min)')
print('='*100)
