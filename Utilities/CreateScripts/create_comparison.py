import pandas as pd
from datetime import datetime
import os

df_oct = pd.read_csv("october_2025_ttm_full_month.csv")
sept_path = "../SeptTTM/september_ttm_analysis.csv"

if os.path.exists(sept_path):
    df_sept = pd.read_csv(sept_path)
    
    oct_count = len(df_oct)
    sept_count = len(df_sept)
    count_delta = oct_count - sept_count
    count_pct = (count_delta / sept_count * 100) if sept_count > 0 else 0
    
    oct_ttm_p75 = df_oct['TTM'].quantile(0.75)
    sept_ttm_p75 = df_sept['TTM'].quantile(0.75)
    ttm_delta = oct_ttm_p75 - sept_ttm_p75
    ttm_pct = (ttm_delta / sept_ttm_p75 * 100) if sept_ttm_p75 > 0 else 0
    
    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df_oct.columns else 'Severity'
    
    output = f"""# October 2025 vs September 2025 - TTM Comparison

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Incident Volume

- **October:** {oct_count} incidents
- **September:** {sept_count} incidents
- **Change:** {count_delta:+d} incidents ({count_pct:+.1f}%)

## TTM Performance (P75)

- **October:** {oct_ttm_p75:.0f} minutes
- **September:** {sept_ttm_p75:.0f} minutes
- **Change:** {ttm_delta:+.0f} minutes ({ttm_pct:+.1f}%)

## Severity Distribution Comparison

| Severity | October | September | Change |
|----------|---------|-----------|--------|
"""
    
    for sev in sorted(df_oct[severity_col].unique()):
        oct_sev = len(df_oct[df_oct[severity_col] == sev])
        sept_sev = len(df_sept[df_sept[severity_col] == sev]) if sev in df_sept[severity_col].values else 0
        delta = oct_sev - sept_sev
        output += f"| Severity {sev} | {oct_sev} | {sept_sev} | {delta:+d} |\n"
    
    with open("October_vs_September_Comparison.md", "w", encoding="utf-8") as f:
        f.write(output)
    
    print("Created October_vs_September_Comparison.md")
else:
    print("September data not found")
