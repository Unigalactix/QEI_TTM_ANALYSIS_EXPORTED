import pandas as pd
import numpy as np
from datetime import datetime

df = pd.read_csv("october_2025_ttm_full_month.csv")
severity_col = 'OutageIncidentSeverity'
total = len(df)
mean_ttm = df['TTM'].mean()
median_ttm = df['TTM'].median()
p75_ttm = df['TTM'].quantile(0.75)
p90_ttm = df['TTM'].quantile(0.90)

auto_detected = len(df[df['OutageDetectedBy'] == 'AUTOMATED']) if 'OutageDetectedBy' in df.columns else 0
auto_rate = (auto_detected / total * 100) if total > 0 else 0
multi_region = len(df[df['IsMultiRegion'] == True]) if 'IsMultiRegion' in df.columns else 0
change_related = len(df[df['IsCausedBy'] == True]) if 'IsCausedBy' in df.columns else 0

output = f"""# October 2025 TTM Analysis - Summary Statistics

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

- **Total Incidents:** {total}
- **Auto-Detection Rate:** {auto_rate:.1f}%
- **Multi-Region Incidents:** {multi_region} ({multi_region/total*100:.1f}%)
- **Change-Related Incidents:** {change_related} ({change_related/total*100:.1f}%)

## TTM Metrics

- **Mean TTM:** {mean_ttm:.0f} minutes
- **Median (P50):** {median_ttm:.0f} minutes
- **P75:** {p75_ttm:.0f} minutes
- **P90:** {p90_ttm:.0f} minutes
- **Range:** {df['TTM'].min():.0f} - {df['TTM'].max():.0f} minutes

## Severity Distribution

"""

for sev, count in df[severity_col].value_counts().sort_index().items():
    output += f"- **Severity {sev}:** {count} incidents ({count/total*100:.1f}%)\n"

output += "\n## Top 10 Affected Services\n\n"

for service, count in df['ServiceName'].value_counts().head(10).items():
    avg_ttm = df[df['ServiceName'] == service]['TTM'].mean()
    output += f"- **{service}:** {count} incidents (Avg TTM: {avg_ttm:.0f} min)\n"

with open("October_Summary_Statistics.md", "w", encoding="utf-8") as f:
    f.write(output)

print("Created October_Summary_Statistics.md")
