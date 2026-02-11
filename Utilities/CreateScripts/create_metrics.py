import pandas as pd
from datetime import datetime
import os

df = pd.read_csv("october_2025_ttm_full_month.csv")
severity_col = 'OutageIncidentSeverity'
high_impact = df[(df[severity_col] == 2) | (df['IsMultiRegion'] == True)]

# Customer impact
total_customers = df['CustomerImpactedCount'].sum() if 'CustomerImpactedCount' in df.columns else 0

# PIR completion
pir_complete = 0
pir_rate = 0
if 'PIRRequired' in df.columns and 'PIRStatus' in df.columns:
    pir_required = df[df['PIRRequired'] == True]
    pir_complete = len(pir_required[pir_required['PIRStatus'].str.contains('Complete', case=False, na=False)])
    pir_rate = (pir_complete / len(pir_required) * 100) if len(pir_required) > 0 else 0

# Quintiles
df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]
quintiles = pd.qcut(df_ttm['TTM'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], duplicates='drop')

output = f"""# October 2025 TTM Analysis - Key Metrics

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## High-Impact Incidents

- **Count:** {len(high_impact)}
- **Average TTM:** {high_impact['TTM'].mean():.0f} minutes
- **Median TTM:** {high_impact['TTM'].median():.0f} minutes

## Customer Impact

- **Total Customers/Subscriptions Affected:** {int(total_customers):,}
- **Average per Incident:** {total_customers/len(df):.0f}

## PIR Completion

- **Completion Rate:** {pir_rate:.1f}%
- **Completed PIRs:** {pir_complete}

## TTM by Quintile

"""

for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
    if q in quintiles.values:
        q_data = df_ttm[quintiles == q]
        output += f"""### {q}
- Incidents: {len(q_data)}
- TTM Range: {q_data['TTM'].min():.0f} - {q_data['TTM'].max():.0f} minutes
- Average TTM: {q_data['TTM'].mean():.0f} minutes

"""

with open("October_Key_Metrics.md", "w", encoding="utf-8") as f:
    f.write(output)

print("Created October_Key_Metrics.md")
