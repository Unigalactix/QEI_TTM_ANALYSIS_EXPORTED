import pandas as pd
import numpy as np

# Read the CSV file
data = pd.read_csv('sept_base_data.csv')

# Convert TTM to numeric, handling any non-numeric values
data['TTM'] = pd.to_numeric(data['TTM'], errors='coerce')

# Filter out rows where TTM is NaN or empty
data_clean = data.dropna(subset=['TTM'])

# Sort by TTM in descending order to see highest TTM first
data_sorted = data_clean.sort_values('TTM', ascending=False)

# Select key columns for analysis
analysis_cols = ['OutageIncidentId', 'TTM', 'OutageCreateDate', 'ServiceName', 'Impacts', 'Symptoms', 
                'Severity', 'State', 'RootCauseCategory', 'HowFixed', 'IsMultiRegion', 'IsCausedBy']

top_incidents = data_sorted[analysis_cols].head(20)

print("=== TOP 20 HIGHEST TTM INCIDENTS IN SEPTEMBER 2025 ===")
print(top_incidents.to_string(index=False))

print(f"\n=== SUMMARY STATISTICS ===")
print(f"Total incidents: {len(data_clean)}")
print(f"Average TTM: {data_clean['TTM'].mean():.1f} minutes")
print(f"Median TTM: {data_clean['TTM'].median():.1f} minutes")
print(f"95th percentile TTM: {data_clean['TTM'].quantile(0.95):.1f} minutes")
print(f"Maximum TTM: {data_clean['TTM'].max():.1f} minutes")

print(f"\n=== TTM QUINTILE BREAKDOWN ===")
quintiles = pd.qcut(data_clean['TTM'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
quintile_counts = quintiles.value_counts().sort_index()
for q, count in quintile_counts.items():
    q_data = data_clean[quintiles == q]
    print(f"{q}: {count} incidents, TTM range {q_data['TTM'].min():.1f}-{q_data['TTM'].max():.1f} minutes")

print(f"\n=== ROOT CAUSE ANALYSIS ===")
root_causes = data_clean['RootCauseCategory'].value_counts(dropna=False)
print("Top root causes:")
for cause, count in root_causes.head(10).items():
    avg_ttm = data_clean[data_clean['RootCauseCategory'] == cause]['TTM'].mean()
    print(f"  {cause}: {count} incidents, avg TTM {avg_ttm:.1f} minutes")

print(f"\n=== CHANGE-RELATED INCIDENTS ===")
change_related = data_clean[data_clean['IsCausedBy'] == True]
non_change = data_clean[data_clean['IsCausedBy'] == False]
print(f"Change-related: {len(change_related)} incidents, avg TTM {change_related['TTM'].mean():.1f} minutes")
print(f"Non-change: {len(non_change)} incidents, avg TTM {non_change['TTM'].mean():.1f} minutes")

print(f"\n=== MULTI-REGION INCIDENTS ===")
multi_region = data_clean[data_clean['IsMultiRegion'] == True]
single_region = data_clean[data_clean['IsMultiRegion'] == False]
print(f"Multi-region: {len(multi_region)} incidents, avg TTM {multi_region['TTM'].mean():.1f} minutes")
print(f"Single-region: {len(single_region)} incidents, avg TTM {single_region['TTM'].mean():.1f} minutes")

# Analyze the highest TTM incidents more deeply
print(f"\n=== ANALYSIS OF HIGHEST TTM INCIDENTS ===")
extreme_incidents = data_sorted.head(10)
for idx, incident in extreme_incidents.iterrows():
    print(f"\nIncident {incident['OutageIncidentId']} (TTM: {incident['TTM']:.0f} minutes)")
    print(f"  Service: {incident['ServiceName']}")
    print(f"  Date: {incident['OutageCreateDate']}")
    if pd.notna(incident['Impacts']):
        print(f"  Impact: {str(incident['Impacts'])[:150]}...")
    if pd.notna(incident['Symptoms']):
        print(f"  Symptoms: {str(incident['Symptoms'])[:150]}...")
    print(f"  Root Cause: {incident['RootCauseCategory']}")
    print(f"  How Fixed: {incident['HowFixed']}")
    print(f"  Multi-Region: {incident['IsMultiRegion']}")
    print(f"  Change-Related: {incident['IsCausedBy']}")