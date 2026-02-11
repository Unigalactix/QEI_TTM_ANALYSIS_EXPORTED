import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

df = pd.read_csv("october_2025_ttm_full_month.csv")
df['OutageCreateDate'] = pd.to_datetime(df['OutageCreateDate'], format='mixed', errors='coerce')
df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]
severity_col = 'OutageIncidentSeverity'

sns.set_style("whitegrid")

# 1. TTM Distribution
plt.figure(figsize=(12, 6))
plt.hist(df_ttm['TTM'], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
plt.axvline(df_ttm['TTM'].median(), color='red', linestyle='--', linewidth=2, label=f'Median: {df_ttm["TTM"].median():.0f} min')
plt.axvline(df_ttm['TTM'].quantile(0.75), color='orange', linestyle='--', linewidth=2, label=f'P75: {df_ttm["TTM"].quantile(0.75):.0f} min')
plt.xlabel('Time to Mitigate (minutes)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('October 2025 - TTM Distribution', fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig("October_TTM_Distribution.png", dpi=300, bbox_inches='tight')
plt.close()
print("Created October_TTM_Distribution.png")

# 2. Top Services
plt.figure(figsize=(12, 8))
top_services = df['ServiceName'].value_counts().head(15)
plt.barh(range(len(top_services)), top_services.values, color='steelblue')
plt.yticks(range(len(top_services)), top_services.index, fontsize=10)
plt.xlabel('Number of Incidents', fontsize=12)
plt.ylabel('Service Name', fontsize=12)
plt.title('October 2025 - Top 15 Affected Services', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("October_Top_Services.png", dpi=300, bbox_inches='tight')
plt.close()
print("Created October_Top_Services.png")

# 3. Daily Timeline
plt.figure(figsize=(14, 6))
df_timeline = df[df['OutageCreateDate'].notna()].copy()
df_timeline['Date'] = df_timeline['OutageCreateDate'].dt.date
daily_counts = df_timeline.groupby('Date').size()
plt.plot(daily_counts.index, daily_counts.values, marker='o', color='darkblue', linewidth=2, markersize=6)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Number of Incidents', fontsize=12)
plt.title('October 2025 - Daily Incident Timeline', fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("October_Daily_Timeline.png", dpi=300, bbox_inches='tight')
plt.close()
print("Created October_Daily_Timeline.png")

# 4. Severity Distribution
plt.figure(figsize=(8, 8))
severity_dist = df[severity_col].value_counts().sort_index()
colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(severity_dist)))
plt.pie(severity_dist, labels=[f'Sev {s}' for s in severity_dist.index], 
        autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 11})
plt.title('October 2025 - Severity Distribution', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("October_Severity_Distribution.png", dpi=300, bbox_inches='tight')
plt.close()
print("Created October_Severity_Distribution.png")

print("\nAll visualizations created successfully!")
