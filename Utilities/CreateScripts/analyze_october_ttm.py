#!/usr/bin/env python3""""""

# October 2025 TTM Analysis - Steps 2-4 and 6

# Generates statistics, metrics, comparisons, and visualizationsOctober 2025 TTM Analysis ScriptComplete October 2025 TTM Analysis



import pandas as pdGenerates: Summary Statistics, Key Metrics, Month-over-Month Comparison, VisualizationsGenerates statistics, metrics, comparisons, and visualizations

import numpy as np

import matplotlib.pyplot as pltSteps 2-4 and 6 of PROMPT_1.md workflow"""

import seaborn as sns

from datetime import datetime"""

import json

import osimport pandas as pd



# Configurationimport pandas as pdimport matplotlib.pyplot as plt

CURRENT_MONTH_CSV = "october_2025_ttm_full_month.csv"

PREVIOUS_MONTH_CSV = "../SeptTTM/september_ttm_analysis.csv"import numpy as npimport seaborn as sns

OUTPUT_FOLDER = "."

import matplotlib.pyplot as pltfrom pathlib import Path

def load_data():

    """Load current and previous month data"""import seaborn as snsfrom datetime import datetime

    print("=" * 80)

    print("LOADING DATA")from datetime import datetimeimport json

    print("=" * 80)

    import json

    df_current = pd.read_csv(CURRENT_MONTH_CSV)

    print(f"Loaded October data: {len(df_current)} incidents, {len(df_current.columns)} columns")import os# Configuration

    

    df_previous = NoneOUTPUT_FOLDER = Path(r"C:\Users\nigopal\OneDrive - Microsoft\Documents\QEI_TTM_Analysis\OctTTM")

    if os.path.exists(PREVIOUS_MONTH_CSV):

        df_previous = pd.read_csv(PREVIOUS_MONTH_CSV)# ConfigurationOCTOBER_CSV = OUTPUT_FOLDER / "october_2025_ttm_full_month.csv"

        print(f"Loaded September data: {len(df_previous)} incidents")

    else:CURRENT_MONTH_CSV = "october_2025_ttm_full_month.csv"SEPTEMBER_CSV = Path(r"C:\Users\nigopal\OneDrive - Microsoft\Documents\QEI_TTM_Analysis\SeptTTM\september_ttm_analysis.csv")

        print(f"Warning: Previous month data not found")

    PREVIOUS_MONTH_CSV = "../SeptTTM/september_ttm_analysis.csv"

    if 'OutageCreateDate' in df_current.columns:

        df_current['OutageCreateDate'] = pd.to_datetime(df_current['OutageCreateDate'], format='mixed', errors='coerce')OUTPUT_FOLDER = "."# Set style for visualizations

    

    return df_current, df_previoussns.set_style("whitegrid")



def generate_summary_statistics(df):def load_data():plt.rcParams['figure.dpi'] = 300

    """Generate Step 2: Summary Statistics"""

    print("\n" + "=" * 80)    """Load current and previous month data"""

    print("STEP 2: GENERATING SUMMARY STATISTICS")

    print("=" * 80)    print("=" * 80)def load_data():

    

    total_incidents = len(df)    print("LOADING DATA")    """Load October and September data"""

    

    # TTM statistics    print("=" * 80)    print("="*80)

    df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]

            print("LOADING DATA")

    ttm_stats = {

        'mean': df_ttm['TTM'].mean(),    # Load October data    print("="*80)

        'median': df_ttm['TTM'].median(),

        'p75': df_ttm['TTM'].quantile(0.75),    df_current = pd.read_csv(CURRENT_MONTH_CSV)    

        'p90': df_ttm['TTM'].quantile(0.90),

        'min': df_ttm['TTM'].min(),    print(f"✅ Loaded October data: {len(df_current)} incidents, {len(df_current.columns)} columns")    print(f"📂 Loading October data from: {OCTOBER_CSV}")

        'max': df_ttm['TTM'].max()

    }        df_oct = pd.read_csv(OCTOBER_CSV)

    

    # Severity distribution    # Load September data for comparison    print(f"✅ Loaded {len(df_oct)} incidents with {len(df_oct.columns)} columns")

    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df.columns else 'Severity'

    severity_dist = df[severity_col].value_counts().sort_index() if severity_col in df.columns else {}    df_previous = None    

    

    # Auto-detection rate    if os.path.exists(PREVIOUS_MONTH_CSV):    df_sep = None

    auto_detected = len(df[df['OutageDetectedBy'] == 'AUTOMATED']) if 'OutageDetectedBy' in df.columns else 0

    auto_rate = (auto_detected / total_incidents * 100) if total_incidents > 0 else 0        df_previous = pd.read_csv(PREVIOUS_MONTH_CSV)    if SEPTEMBER_CSV.exists():

    

    # Multi-region incidents        print(f"✅ Loaded September data: {len(df_previous)} incidents")        print(f"📂 Loading September data from: {SEPTEMBER_CSV}")

    multi_region = len(df[df['IsMultiRegion'] == True]) if 'IsMultiRegion' in df.columns else 0

        else:        df_sep = pd.read_csv(SEPTEMBER_CSV)

    # Change-related

    change_related = len(df[df['IsCausedBy'] == True]) if 'IsCausedBy' in df.columns else 0        print(f"⚠️ Previous month data not found at {PREVIOUS_MONTH_CSV}")        print(f"✅ Loaded {len(df_sep)} incidents")

    

    # Write to markdown        else:

    output_file = os.path.join(OUTPUT_FOLDER, "October_Summary_Statistics.md")

    with open(output_file, 'w', encoding='utf-8') as f:    # Convert date columns        print(f"⚠️  September CSV not found at: {SEPTEMBER_CSV}")

        f.write("# October 2025 TTM Analysis - Summary Statistics\n\n")

        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")    if 'OutageCreateDate' in df_current.columns:    

        

        f.write("## Overview\n\n")        df_current['OutageCreateDate'] = pd.to_datetime(df_current['OutageCreateDate'], format='mixed', errors='coerce')    return df_oct, df_sep

        f.write(f"- **Total Incidents:** {total_incidents}\n")

        f.write(f"- **Auto-Detection Rate:** {auto_rate:.1f}%\n")    

        f.write(f"- **Multi-Region Incidents:** {multi_region} ({multi_region/total_incidents*100:.1f}%)\n")

        f.write(f"- **Change-Related Incidents:** {change_related} ({change_related/total_incidents*100:.1f}%)\n\n")    return df_current, df_previousdef generate_summary_statistics(df):

        

        f.write("## TTM Metrics\n\n")    """Generate summary statistics"""

        f.write(f"- **Mean TTM:** {ttm_stats['mean']:.0f} minutes\n")

        f.write(f"- **Median (P50):** {ttm_stats['median']:.0f} minutes\n")def generate_summary_statistics(df):    print(f"\n{'='*80}")

        f.write(f"- **P75:** {ttm_stats['p75']:.0f} minutes\n")

        f.write(f"- **P90:** {ttm_stats['p90']:.0f} minutes\n")    """Generate Step 2: Summary Statistics"""    print("GENERATING SUMMARY STATISTICS")

        f.write(f"- **Range:** {ttm_stats['min']:.0f} - {ttm_stats['max']:.0f} minutes\n\n")

            print("\n" + "=" * 80)    print("="*80)

        f.write("## Severity Distribution\n\n")

        for sev, count in severity_dist.items():    print("STEP 2: GENERATING SUMMARY STATISTICS")    

            f.write(f"- **Severity {sev}:** {count} incidents ({count/total_incidents*100:.1f}%)\n")

        f.write("\n")    print("=" * 80)    stats = {}

        

        # Top 10 services        

        if 'ServiceName' in df.columns:

            f.write("## Top 10 Affected Services\n\n")    # Basic counts    # Total incidents

            top_services = df['ServiceName'].value_counts().head(10)

            for service, count in top_services.items():    total_incidents = len(df)    stats['total_incidents'] = len(df)

                avg_ttm = df[df['ServiceName'] == service]['TTM'].mean()

                f.write(f"- **{service}:** {count} incidents (Avg TTM: {avg_ttm:.0f} min)\n")        print(f"📊 Total Incidents: {stats['total_incidents']}")

    

    print(f"Saved: {output_file}")    # TTM statistics    

    return ttm_stats, severity_dist

    ttm_col = 'TTM'    # TTM Statistics

def calculate_key_metrics(df):

    """Generate Step 3: Key Metrics"""    df_ttm = df[df[ttm_col].notna() & (df[ttm_col] >= 0)]    if 'TTM' in df.columns:

    print("\n" + "=" * 80)

    print("STEP 3: CALCULATING KEY METRICS")            ttm_data = df['TTM'].dropna()

    print("=" * 80)

        ttm_stats = {        stats['ttm_mean'] = ttm_data.mean()

    # High-impact incidents

    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df.columns else 'Severity'        'mean': df_ttm[ttm_col].mean(),        stats['ttm_median'] = ttm_data.median()

    high_impact = df[(df[severity_col] == 2) | (df['IsMultiRegion'] == True)] if severity_col in df.columns else df[df['IsMultiRegion'] == True]

            'median': df_ttm[ttm_col].median(),        stats['ttm_p50'] = ttm_data.quantile(0.50)

    # Customer impact

    total_customers = 0        'p75': df_ttm[ttm_col].quantile(0.75),        stats['ttm_p75'] = ttm_data.quantile(0.75)

    if 'CustomerImpactedCount' in df.columns:

        total_customers = df['CustomerImpactedCount'].sum()        'p90': df_ttm[ttm_col].quantile(0.90),        stats['ttm_p90'] = ttm_data.quantile(0.90)

    elif 'SubscriptionsImpacted' in df.columns:

        total_customers = df['SubscriptionsImpacted'].sum()        'min': df_ttm[ttm_col].min(),        stats['ttm_p95'] = ttm_data.quantile(0.95)

    

    # PIR completion        'max': df_ttm[ttm_col].max()        

    pir_complete = 0

    pir_rate = 0    }        print(f"⏱️  TTM Statistics (minutes):")

    if 'PIRRequired' in df.columns and 'PIRStatus' in df.columns:

        pir_required = df[df['PIRRequired'] == True]            print(f"   - Mean: {stats['ttm_mean']:.2f}")

        pir_complete = len(pir_required[pir_required['PIRStatus'].str.contains('Complete', case=False, na=False)])

        pir_rate = (pir_complete / len(pir_required) * 100) if len(pir_required) > 0 else 0    # Severity distribution        print(f"   - Median (P50): {stats['ttm_p50']:.2f}")

    

    # TTM by quintile    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df.columns else 'Severity'        print(f"   - P75: {stats['ttm_p75']:.2f}")

    df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]

    quintiles = pd.qcut(df_ttm['TTM'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], duplicates='drop')    severity_dist = df[severity_col].value_counts().sort_index() if severity_col in df.columns else {}        print(f"   - P90: {stats['ttm_p90']:.2f}")

    quintile_stats = {}

    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:            print(f"   - P95: {stats['ttm_p95']:.2f}")

        if q in quintiles.values:

            q_data = df_ttm[quintiles == q]    # Auto-detection rate    

            quintile_stats[q] = {

                'count': len(q_data),    auto_detected = len(df[df['OutageDetectedBy'] == 'AUTOMATED']) if 'OutageDetectedBy' in df.columns else 0    # Severity Distribution

                'min': q_data['TTM'].min(),

                'max': q_data['TTM'].max(),    auto_rate = (auto_detected / total_incidents * 100) if total_incidents > 0 else 0    if 'Severity' in df.columns:

                'mean': q_data['TTM'].mean()

            }            severity_dist = df['Severity'].value_counts().sort_index()

    

    # Write to markdown    # Multi-region incidents        stats['severity_distribution'] = severity_dist.to_dict()

    output_file = os.path.join(OUTPUT_FOLDER, "October_Key_Metrics.md")

    with open(output_file, 'w', encoding='utf-8') as f:    multi_region = len(df[df['IsMultiRegion'] == True]) if 'IsMultiRegion' in df.columns else 0        print(f"\n🚨 Severity Distribution:")

        f.write("# October 2025 TTM Analysis - Key Metrics\n\n")

        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")            for sev, count in severity_dist.items():

        

        f.write("## High-Impact Incidents\n\n")    # Change-related            pct = (count / len(df)) * 100

        f.write(f"- **Count:** {len(high_impact)}\n")

        f.write(f"- **Average TTM:** {high_impact['TTM'].mean():.0f} minutes\n")    change_related = len(df[df['IsCausedBy'] == True]) if 'IsCausedBy' in df.columns else 0            print(f"   - Sev {sev}: {count} incidents ({pct:.1f}%)")

        f.write(f"- **Median TTM:** {high_impact['TTM'].median():.0f} minutes\n\n")

                

        f.write("## Customer Impact\n\n")

        f.write(f"- **Total Customers/Subscriptions Affected:** {int(total_customers):,}\n")    # Write to markdown    # Top Services

        f.write(f"- **Average per Incident:** {total_customers/len(df):.0f}\n\n")

            output_file = os.path.join(OUTPUT_FOLDER, "October_Summary_Statistics.md")    if 'ServiceName' in df.columns:

        f.write("## PIR Completion\n\n")

        f.write(f"- **Completion Rate:** {pir_rate:.1f}%\n")    with open(output_file, 'w', encoding='utf-8') as f:        top_services = df['ServiceName'].value_counts().head(10)

        f.write(f"- **Completed PIRs:** {pir_complete}\n\n")

                f.write("# October 2025 TTM Analysis - Summary Statistics\n\n")        stats['top_services'] = top_services.to_dict()

        f.write("## TTM by Quintile\n\n")

        for q, stats in quintile_stats.items():        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")        print(f"\n🔧 Top 10 Services:")

            f.write(f"### {q}\n")

            f.write(f"- Incidents: {stats['count']}\n")                for service, count in top_services.items():

            f.write(f"- TTM Range: {stats['min']:.0f} - {stats['max']:.0f} minutes\n")

            f.write(f"- Average TTM: {stats['mean']:.0f} minutes\n\n")        f.write("## Overview\n\n")            print(f"   - {service}: {count} incidents")

    

    print(f"Saved: {output_file}")        f.write(f"- **Total Incidents:** {total_incidents}\n")    

    return quintile_stats

        f.write(f"- **Auto-Detection Rate:** {auto_rate:.1f}%\n")    # Detection Method

def compare_to_previous_month(df_current, df_previous):

    """Generate Step 4: Month-over-Month Comparison"""        f.write(f"- **Multi-Region Incidents:** {multi_region} ({multi_region/total_incidents*100:.1f}%)\n")    if 'IsManualDetection' in df.columns:

    print("\n" + "=" * 80)

    print("STEP 4: MONTH-OVER-MONTH COMPARISON")        f.write(f"- **Change-Related Incidents:** {change_related} ({change_related/total_incidents*100:.1f}%)\n\n")        manual_count = df['IsManualDetection'].sum()

    print("=" * 80)

                    auto_count = len(df) - manual_count

    if df_previous is None:

        print("Warning: No previous month data for comparison")        f.write("## TTM Metrics\n\n")        auto_rate = (auto_count / len(df)) * 100

        return

            f.write(f"- **Mean TTM:** {ttm_stats['mean']:.0f} minutes\n")        stats['auto_detection_rate'] = auto_rate

    # Calculate deltas

    current_count = len(df_current)        f.write(f"- **Median (P50):** {ttm_stats['median']:.0f} minutes\n")        print(f"\n🔍 Detection Method:")

    previous_count = len(df_previous)

    count_delta = current_count - previous_count        f.write(f"- **P75:** {ttm_stats['p75']:.0f} minutes\n")        print(f"   - Auto-detected: {auto_count} ({auto_rate:.1f}%)")

    count_pct = (count_delta / previous_count * 100) if previous_count > 0 else 0

            f.write(f"- **P90:** {ttm_stats['p90']:.0f} minutes\n")        print(f"   - Manual: {manual_count} ({100-auto_rate:.1f}%)")

    current_ttm_p75 = df_current['TTM'].quantile(0.75)

    previous_ttm_p75 = df_previous['TTM'].quantile(0.75)        f.write(f"- **Range:** {ttm_stats['min']:.0f} - {ttm_stats['max']:.0f} minutes\n\n")    

    ttm_delta = current_ttm_p75 - previous_ttm_p75

    ttm_pct = (ttm_delta / previous_ttm_p75 * 100) if previous_ttm_p75 > 0 else 0            # Save to markdown

    

    # Write to markdown        f.write("## Severity Distribution\n\n")    output_file = OUTPUT_FOLDER / "October_Summary_Statistics.md"

    output_file = os.path.join(OUTPUT_FOLDER, "October_vs_September_Comparison.md")

    with open(output_file, 'w', encoding='utf-8') as f:        for sev, count in severity_dist.items():    with open(output_file, 'w', encoding='utf-8') as f:

        f.write("# October 2025 vs September 2025 - TTM Comparison\n\n")

        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")            f.write(f"- **Severity {sev}:** {count} incidents ({count/total_incidents*100:.1f}%)\n")        f.write("# October 2025 TTM Summary Statistics\n\n")

        

        f.write("## Incident Volume\n\n")        f.write("\n")        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write(f"- **October:** {current_count} incidents\n")

        f.write(f"- **September:** {previous_count} incidents\n")                f.write(f"## Overview\n\n")

        f.write(f"- **Change:** {count_delta:+d} incidents ({count_pct:+.1f}%)\n\n")

                # Top 10 services        f.write(f"- **Total Incidents:** {stats['total_incidents']}\n")

        f.write("## TTM Performance (P75)\n\n")

        f.write(f"- **October:** {current_ttm_p75:.0f} minutes\n")        if 'ServiceName' in df.columns:        f.write(f"- **Data Columns:** {len(df.columns)}\n\n")

        f.write(f"- **September:** {previous_ttm_p75:.0f} minutes\n")

        f.write(f"- **Change:** {ttm_delta:+.0f} minutes ({ttm_pct:+.1f}%)\n\n")            f.write("## Top 10 Affected Services\n\n")        

        

        # Severity comparison            top_services = df['ServiceName'].value_counts().head(10)        if 'ttm_mean' in stats:

        severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df_current.columns else 'Severity'

        if severity_col in df_current.columns and severity_col in df_previous.columns:            for service, count in top_services.items():            f.write(f"## TTM Statistics\n\n")

            f.write("## Severity Distribution Comparison\n\n")

            f.write("| Severity | October | September | Change |\n")                avg_ttm = df[df['ServiceName'] == service][ttm_col].mean()            f.write(f"| Metric | Value (minutes) |\n")

            f.write("|----------|---------|-----------|--------|\n")

            for sev in sorted(df_current[severity_col].unique()):                f.write(f"- **{service}:** {count} incidents (Avg TTM: {avg_ttm:.0f} min)\n")            f.write(f"|--------|----------------|\n")

                oct_count = len(df_current[df_current[severity_col] == sev])

                sept_count = len(df_previous[df_previous[severity_col] == sev])                f.write(f"| Mean | {stats['ttm_mean']:.2f} |\n")

                delta = oct_count - sept_count

                f.write(f"| Severity {sev} | {oct_count} | {sept_count} | {delta:+d} |\n")    print(f"✅ Saved: {output_file}")            f.write(f"| Median (P50) | {stats['ttm_p50']:.2f} |\n")

    

    print(f"Saved: {output_file}")    return ttm_stats, severity_dist            f.write(f"| P75 | {stats['ttm_p75']:.2f} |\n")



def create_visualizations(df):            f.write(f"| P90 | {stats['ttm_p90']:.2f} |\n")

    """Generate Step 6: Visualizations"""

    print("\n" + "=" * 80)def calculate_key_metrics(df):            f.write(f"| P95 | {stats['ttm_p95']:.2f} |\n\n")

    print("STEP 6: CREATING VISUALIZATIONS")

    print("=" * 80)    """Generate Step 3: Key Metrics"""        

    

    sns.set_style("whitegrid")    print("\n" + "=" * 80)        if 'severity_distribution' in stats:

    plt.rcParams['figure.figsize'] = (12, 6)

        print("STEP 3: CALCULATING KEY METRICS")            f.write(f"## Severity Distribution\n\n")

    df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]

        print("=" * 80)            f.write(f"| Severity | Count | Percentage |\n")

    # 1. TTM Distribution

    plt.figure(figsize=(12, 6))                f.write(f"|----------|-------|------------|\n")

    plt.hist(df_ttm['TTM'], bins=50, edgecolor='black', alpha=0.7)

    plt.axvline(df_ttm['TTM'].median(), color='red', linestyle='--', label=f'Median: {df_ttm["TTM"].median():.0f} min')    # High-impact incidents (Severity 2 or multi-region)            for sev in sorted(stats['severity_distribution'].keys()):

    plt.axvline(df_ttm['TTM'].quantile(0.75), color='orange', linestyle='--', label=f'P75: {df_ttm["TTM"].quantile(0.75):.0f} min')

    plt.xlabel('Time to Mitigate (minutes)')    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df.columns else 'Severity'                count = stats['severity_distribution'][sev]

    plt.ylabel('Frequency')

    plt.title('October 2025 - TTM Distribution')    high_impact = df[(df[severity_col] == 2) | (df['IsMultiRegion'] == True)] if severity_col in df.columns else df[df['IsMultiRegion'] == True]                pct = (count / stats['total_incidents']) * 100

    plt.legend()

    plt.tight_layout()                    f.write(f"| Sev {sev} | {count} | {pct:.1f}% |\n")

    output_file = os.path.join(OUTPUT_FOLDER, "October_TTM_Distribution.png")

    plt.savefig(output_file, dpi=300, bbox_inches='tight')    # Customer impact            f.write("\n")

    plt.close()

    print(f"Saved: {output_file}")    customer_cols = [col for col in df.columns if 'customer' in col.lower() or 'subscription' in col.lower()]        

    

    # 2. Top Services    total_customers = 0        if 'top_services' in stats:

    if 'ServiceName' in df.columns:

        plt.figure(figsize=(12, 8))    if 'CustomerImpactedCount' in df.columns:            f.write(f"## Top 10 Services\n\n")

        top_services = df['ServiceName'].value_counts().head(15)

        top_services.plot(kind='barh', color='steelblue')        total_customers = df['CustomerImpactedCount'].sum()            f.write(f"| Rank | Service | Incidents |\n")

        plt.xlabel('Number of Incidents')

        plt.ylabel('Service Name')    elif 'SubscriptionsImpacted' in df.columns:            f.write(f"|------|---------|----------|\n")

        plt.title('October 2025 - Top 15 Affected Services')

        plt.gca().invert_yaxis()        total_customers = df['SubscriptionsImpacted'].sum()            for i, (service, count) in enumerate(list(stats['top_services'].items())[:10], 1):

        plt.tight_layout()

        output_file = os.path.join(OUTPUT_FOLDER, "October_Top_Services.png")                    f.write(f"| {i} | {service} | {count} |\n")

        plt.savefig(output_file, dpi=300, bbox_inches='tight')

        plt.close()    # PIR completion            f.write("\n")

        print(f"Saved: {output_file}")

        pir_complete = 0        

    # 3. Daily Timeline

    if 'OutageCreateDate' in df.columns:    pir_rate = 0        if 'auto_detection_rate' in stats:

        plt.figure(figsize=(14, 6))

        df_timeline = df[df['OutageCreateDate'].notna()].copy()    if 'PIRRequired' in df.columns and 'PIRStatus' in df.columns:            f.write(f"## Detection Method\n\n")

        df_timeline['Date'] = df_timeline['OutageCreateDate'].dt.date

        daily_counts = df_timeline.groupby('Date').size()        pir_required = df[df['PIRRequired'] == True]            f.write(f"- **Auto-Detection Rate:** {stats['auto_detection_rate']:.1f}%\n")

        daily_counts.plot(kind='line', marker='o', color='darkblue', linewidth=2)

        plt.xlabel('Date')        pir_complete = len(pir_required[pir_required['PIRStatus'].str.contains('Complete', case=False, na=False)])    

        plt.ylabel('Number of Incidents')

        plt.title('October 2025 - Daily Incident Timeline')        pir_rate = (pir_complete / len(pir_required) * 100) if len(pir_required) > 0 else 0    print(f"\n✅ Saved to: {output_file}")

        plt.xticks(rotation=45)

        plt.grid(True, alpha=0.3)        return stats

        plt.tight_layout()

        output_file = os.path.join(OUTPUT_FOLDER, "October_Daily_Timeline.png")    # TTM by quintile

        plt.savefig(output_file, dpi=300, bbox_inches='tight')

        plt.close()    df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]def calculate_key_metrics(df):

        print(f"Saved: {output_file}")

        quintiles = pd.qcut(df_ttm['TTM'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'], duplicates='drop')    """Calculate key metrics"""

    # 4. Severity Distribution

    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df.columns else 'Severity'    quintile_stats = {}    print(f"\n{'='*80}")

    if severity_col in df.columns:

        plt.figure(figsize=(8, 8))    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:    print("CALCULATING KEY METRICS")

        severity_dist = df[severity_col].value_counts().sort_index()

        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(severity_dist)))        if q in quintiles.values:    print("="*80)

        plt.pie(severity_dist, labels=[f'Sev {s}' for s in severity_dist.index], 

                autopct='%1.1f%%', colors=colors, startangle=90)            q_data = df_ttm[quintiles == q]    

        plt.title('October 2025 - Severity Distribution')

        plt.tight_layout()            quintile_stats[q] = {    metrics = {}

        output_file = os.path.join(OUTPUT_FOLDER, "October_Severity_Distribution.png")

        plt.savefig(output_file, dpi=300, bbox_inches='tight')                'count': len(q_data),    

        plt.close()

        print(f"Saved: {output_file}")                'min': q_data['TTM'].min(),    # P75 for timing metrics



def create_execution_log():                'max': q_data['TTM'].max(),    timing_cols = ['TTM', 'TTD', 'TTO', 'TTN', 'TTEng', 'TTFix']

    """Create execution log"""

    log_data = {                'mean': q_data['TTM'].mean()    for col in timing_cols:

        'timestamp': datetime.now().isoformat(),

        'script': 'analyze_october_ttm.py',            }        if col in df.columns:

        'status': 'completed',

        'outputs': [                p75 = df[col].quantile(0.75)

            'October_Summary_Statistics.md',

            'October_Key_Metrics.md',    # Write to markdown            metrics[f'{col}_P75'] = p75

            'October_vs_September_Comparison.md',

            'October_TTM_Distribution.png',    output_file = os.path.join(OUTPUT_FOLDER, "October_Key_Metrics.md")            print(f"📊 {col} P75: {p75:.2f} minutes")

            'October_Top_Services.png',

            'October_Daily_Timeline.png',    with open(output_file, 'w', encoding='utf-8') as f:    

            'October_Severity_Distribution.png'

        ]        f.write("# October 2025 TTM Analysis - Key Metrics\n\n")    # High Impact Incidents

    }

            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")    if 'IsHighImpactOutage' in df.columns:

    output_file = os.path.join(OUTPUT_FOLDER, "analysis_execution_log.json")

    with open(output_file, 'w') as f:                high_impact = df['IsHighImpactOutage'].sum()

        json.dump(log_data, f, indent=2)

            f.write("## High-Impact Incidents\n\n")        high_impact_pct = (high_impact / len(df)) * 100

    print(f"\nExecution log saved: {output_file}")

        f.write(f"- **Count:** {len(high_impact)}\n")        metrics['high_impact_count'] = high_impact

def main():

    """Main execution"""        f.write(f"- **Average TTM:** {high_impact['TTM'].mean():.0f} minutes\n")        metrics['high_impact_pct'] = high_impact_pct

    print("=" * 80)

    print("OCTOBER 2025 TTM ANALYSIS")        f.write(f"- **Median TTM:** {high_impact['TTM'].median():.0f} minutes\n\n")        print(f"\n🎯 High Impact: {high_impact} incidents ({high_impact_pct:.1f}%)")

    print("Steps 2-4 and 6 of PROMPT_1.md")

    print("=" * 80)            

    

    df_current, df_previous = load_data()        f.write("## Customer Impact\n\n")    # Customer Impact

    generate_summary_statistics(df_current)

    calculate_key_metrics(df_current)        f.write(f"- **Total Customers/Subscriptions Affected:** {int(total_customers):,}\n")    if 'S400CustomerCount' in df.columns:

    compare_to_previous_month(df_current, df_previous)

    create_visualizations(df_current)        f.write(f"- **Average per Incident:** {total_customers/len(df):.0f}\n\n")        s400_total = df['S400CustomerCount'].sum()

    create_execution_log()

                    metrics['s400_total'] = s400_total

    print("\n" + "=" * 80)

    print("ANALYSIS COMPLETE")        f.write("## PIR Completion\n\n")        print(f"👥 S400 Customers: {int(s400_total)}")

    print("=" * 80)

    print("\nNext step: python generate_narrative.py")        f.write(f"- **Completion Rate:** {pir_rate:.1f}%\n")    



if __name__ == "__main__":        f.write(f"- **Completed PIRs:** {pir_complete}\n\n")    if 'F500CustomerCount' in df.columns:

    main()

                f500_total = df['F500CustomerCount'].sum()

        f.write("## TTM by Quintile\n\n")        metrics['f500_total'] = f500_total

        for q, stats in quintile_stats.items():        print(f"🏢 F500 Customers: {int(f500_total)}")

            f.write(f"### {q}\n")    

            f.write(f"- Incidents: {stats['count']}\n")    # CritSit Cases

            f.write(f"- TTM Range: {stats['min']:.0f} - {stats['max']:.0f} minutes\n")    if 'TotalCritsit' in df.columns:

            f.write(f"- Average TTM: {stats['mean']:.0f} minutes\n\n")        critsit_total = df['TotalCritsit'].sum()

            metrics['critsit_total'] = critsit_total

    print(f"✅ Saved: {output_file}")        print(f"🚨 CritSit Cases: {int(critsit_total)}")

    return quintile_stats    

    # PIR Completion

def compare_to_previous_month(df_current, df_previous):    if 'IsPIRPresent' in df.columns:

    """Generate Step 4: Month-over-Month Comparison"""        pir_present = df['IsPIRPresent'].sum()

    print("\n" + "=" * 80)        pir_rate = (pir_present / len(df)) * 100

    print("STEP 4: MONTH-OVER-MONTH COMPARISON")        metrics['pir_completion_rate'] = pir_rate

    print("=" * 80)        print(f"📝 PIR Completion: {pir_rate:.1f}%")

        

    if df_previous is None:    # Save to markdown

        print("⚠️ No previous month data available for comparison")    output_file = OUTPUT_FOLDER / "October_Key_Metrics.md"

        return    with open(output_file, 'w', encoding='utf-8') as f:

            f.write("# October 2025 Key Metrics\n\n")

    # Calculate deltas        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    current_count = len(df_current)        

    previous_count = len(df_previous)        f.write(f"## Timing Metrics (P75)\n\n")

    count_delta = current_count - previous_count        f.write(f"| Metric | P75 (minutes) |\n")

    count_pct = (count_delta / previous_count * 100) if previous_count > 0 else 0        f.write(f"|--------|---------------|\n")

            for col in timing_cols:

    current_ttm_p75 = df_current['TTM'].quantile(0.75)            if f'{col}_P75' in metrics:

    previous_ttm_p75 = df_previous['TTM'].quantile(0.75)                f.write(f"| {col} | {metrics[f'{col}_P75']:.2f} |\n")

    ttm_delta = current_ttm_p75 - previous_ttm_p75        f.write("\n")

    ttm_pct = (ttm_delta / previous_ttm_p75 * 100) if previous_ttm_p75 > 0 else 0        

            f.write(f"## Impact Metrics\n\n")

    # Write to markdown        if 'high_impact_count' in metrics:

    output_file = os.path.join(OUTPUT_FOLDER, "October_vs_September_Comparison.md")            f.write(f"- **High Impact Incidents:** {metrics['high_impact_count']} ({metrics['high_impact_pct']:.1f}%)\n")

    with open(output_file, 'w', encoding='utf-8') as f:        if 's400_total' in metrics:

        f.write("# October 2025 vs September 2025 - TTM Comparison\n\n")            f.write(f"- **S400 Customers Impacted:** {int(metrics['s400_total'])}\n")

        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")        if 'f500_total' in metrics:

                    f.write(f"- **F500 Customers Impacted:** {int(metrics['f500_total'])}\n")

        f.write("## Incident Volume\n\n")        if 'critsit_total' in metrics:

        f.write(f"- **October:** {current_count} incidents\n")            f.write(f"- **CritSit Cases:** {int(metrics['critsit_total'])}\n")

        f.write(f"- **September:** {previous_count} incidents\n")        if 'pir_completion_rate' in metrics:

        f.write(f"- **Change:** {count_delta:+d} incidents ({count_pct:+.1f}%)\n\n")            f.write(f"- **PIR Completion Rate:** {metrics['pir_completion_rate']:.1f}%\n")

            

        f.write("## TTM Performance (P75)\n\n")    print(f"\n✅ Saved to: {output_file}")

        f.write(f"- **October:** {current_ttm_p75:.0f} minutes\n")    return metrics

        f.write(f"- **September:** {previous_ttm_p75:.0f} minutes\n")

        f.write(f"- **Change:** {ttm_delta:+.0f} minutes ({ttm_pct:+.1f}%)\n\n")def compare_to_previous_month(df_oct, df_sep):

            """Compare October to September"""

        # Severity comparison    if df_sep is None:

        severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df_current.columns else 'Severity'        print("\n⚠️  Skipping comparison - September data not available")

        if severity_col in df_current.columns and severity_col in df_previous.columns:        return None

            f.write("## Severity Distribution Comparison\n\n")    

            f.write("| Severity | October | September | Change |\n")    print(f"\n{'='*80}")

            f.write("|----------|---------|-----------|--------|\n")    print("COMPARING TO SEPTEMBER")

            for sev in sorted(df_current[severity_col].unique()):    print("="*80)

                oct_count = len(df_current[df_current[severity_col] == sev])    

                sept_count = len(df_previous[df_previous[severity_col] == sev])    comparison = {}

                delta = oct_count - sept_count    

                f.write(f"| Severity {sev} | {oct_count} | {sept_count} | {delta:+d} |\n")    # Incident Volume

        oct_count = len(df_oct)

    print(f"✅ Saved: {output_file}")    sep_count = len(df_sep)

    volume_delta = oct_count - sep_count

def create_visualizations(df):    volume_pct = ((oct_count - sep_count) / sep_count) * 100

    """Generate Step 6: Visualizations"""    

    print("\n" + "=" * 80)    comparison['october_count'] = oct_count

    print("STEP 6: CREATING VISUALIZATIONS")    comparison['september_count'] = sep_count

    print("=" * 80)    comparison['volume_delta'] = volume_delta

        comparison['volume_pct'] = volume_pct

    # Set style    

    sns.set_style("whitegrid")    print(f"📊 Incident Volume:")

    plt.rcParams['figure.figsize'] = (12, 6)    print(f"   - October: {oct_count}")

        print(f"   - September: {sep_count}")

    df_ttm = df[df['TTM'].notna() & (df['TTM'] >= 0)]    print(f"   - Change: {volume_delta:+d} ({volume_pct:+.1f}%)")

        

    # 1. TTM Distribution    # TTM P75 Comparison

    plt.figure(figsize=(12, 6))    if 'TTM' in df_oct.columns and 'TTM' in df_sep.columns:

    plt.hist(df_ttm['TTM'], bins=50, edgecolor='black', alpha=0.7)        oct_ttm_p75 = df_oct['TTM'].quantile(0.75)

    plt.axvline(df_ttm['TTM'].median(), color='red', linestyle='--', label=f'Median: {df_ttm["TTM"].median():.0f} min')        sep_ttm_p75 = df_sep['TTM'].quantile(0.75)

    plt.axvline(df_ttm['TTM'].quantile(0.75), color='orange', linestyle='--', label=f'P75: {df_ttm["TTM"].quantile(0.75):.0f} min')        ttm_delta = oct_ttm_p75 - sep_ttm_p75

    plt.xlabel('Time to Mitigate (minutes)')        ttm_pct = ((oct_ttm_p75 - sep_ttm_p75) / sep_ttm_p75) * 100

    plt.ylabel('Frequency')        

    plt.title('October 2025 - TTM Distribution')        comparison['oct_ttm_p75'] = oct_ttm_p75

    plt.legend()        comparison['sep_ttm_p75'] = sep_ttm_p75

    plt.tight_layout()        comparison['ttm_delta'] = ttm_delta

    output_file = os.path.join(OUTPUT_FOLDER, "October_TTM_Distribution.png")        comparison['ttm_pct'] = ttm_pct

    plt.savefig(output_file, dpi=300, bbox_inches='tight')        

    plt.close()        print(f"\n⏱️  TTM P75:")

    print(f"✅ Saved: {output_file}")        print(f"   - October: {oct_ttm_p75:.2f} minutes")

            print(f"   - September: {sep_ttm_p75:.2f} minutes")

    # 2. Top Services        print(f"   - Change: {ttm_delta:+.2f} minutes ({ttm_pct:+.1f}%)")

    if 'ServiceName' in df.columns:    

        plt.figure(figsize=(12, 8))    # Severity Mix Comparison

        top_services = df['ServiceName'].value_counts().head(15)    if 'Severity' in df_oct.columns and 'Severity' in df_sep.columns:

        top_services.plot(kind='barh', color='steelblue')        oct_sev1_pct = (df_oct['Severity'] == 1).sum() / len(df_oct) * 100

        plt.xlabel('Number of Incidents')        sep_sev1_pct = (df_sep['Severity'] == 1).sum() / len(df_sep) * 100

        plt.ylabel('Service Name')        sev1_delta = oct_sev1_pct - sep_sev1_pct

        plt.title('October 2025 - Top 15 Affected Services')        

        plt.gca().invert_yaxis()        comparison['oct_sev1_pct'] = oct_sev1_pct

        plt.tight_layout()        comparison['sep_sev1_pct'] = sep_sev1_pct

        output_file = os.path.join(OUTPUT_FOLDER, "October_Top_Services.png")        comparison['sev1_delta'] = sev1_delta

        plt.savefig(output_file, dpi=300, bbox_inches='tight')        

        plt.close()        print(f"\n🚨 Severity 1 %:")

        print(f"✅ Saved: {output_file}")        print(f"   - October: {oct_sev1_pct:.1f}%")

            print(f"   - September: {sep_sev1_pct:.1f}%")

    # 3. Daily Timeline        print(f"   - Change: {sev1_delta:+.1f} percentage points")

    if 'OutageCreateDate' in df.columns:    

        plt.figure(figsize=(14, 6))    # Top Services Shifts

        df_timeline = df[df['OutageCreateDate'].notna()].copy()    if 'ServiceName' in df_oct.columns and 'ServiceName' in df_sep.columns:

        df_timeline['Date'] = df_timeline['OutageCreateDate'].dt.date        oct_top = df_oct['ServiceName'].value_counts().head(5)

        daily_counts = df_timeline.groupby('Date').size()        sep_top = df_sep['ServiceName'].value_counts().head(5)

        daily_counts.plot(kind='line', marker='o', color='darkblue', linewidth=2)        

        plt.xlabel('Date')        print(f"\n🔧 Top Services Comparison:")

        plt.ylabel('Number of Incidents')        print(f"   October Top 5: {', '.join(oct_top.index.tolist())}")

        plt.title('October 2025 - Daily Incident Timeline')        print(f"   September Top 5: {', '.join(sep_top.index.tolist())}")

        plt.xticks(rotation=45)    

        plt.grid(True, alpha=0.3)    # Save to markdown

        plt.tight_layout()    output_file = OUTPUT_FOLDER / "October_vs_September_Comparison.md"

        output_file = os.path.join(OUTPUT_FOLDER, "October_Daily_Timeline.png")    with open(output_file, 'w', encoding='utf-8') as f:

        plt.savefig(output_file, dpi=300, bbox_inches='tight')        f.write("# October vs September 2025 Comparison\n\n")

        plt.close()        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        print(f"✅ Saved: {output_file}")        

            f.write(f"## Incident Volume\n\n")

    # 4. Severity Distribution        f.write(f"| Month | Count | Change |\n")

    severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df.columns else 'Severity'        f.write(f"|-------|-------|--------|\n")

    if severity_col in df.columns:        f.write(f"| October | {oct_count} | {volume_delta:+d} ({volume_pct:+.1f}%) |\n")

        plt.figure(figsize=(8, 8))        f.write(f"| September | {sep_count} | - |\n\n")

        severity_dist = df[severity_col].value_counts().sort_index()        

        colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(severity_dist)))        if 'oct_ttm_p75' in comparison:

        plt.pie(severity_dist, labels=[f'Sev {s}' for s in severity_dist.index],             f.write(f"## TTM P75 Comparison\n\n")

                autopct='%1.1f%%', colors=colors, startangle=90)            f.write(f"| Month | TTM P75 (min) | Change |\n")

        plt.title('October 2025 - Severity Distribution')            f.write(f"|-------|---------------|--------|\n")

        plt.tight_layout()            f.write(f"| October | {comparison['oct_ttm_p75']:.2f} | {comparison['ttm_delta']:+.2f} ({comparison['ttm_pct']:+.1f}%) |\n")

        output_file = os.path.join(OUTPUT_FOLDER, "October_Severity_Distribution.png")            f.write(f"| September | {comparison['sep_ttm_p75']:.2f} | - |\n\n")

        plt.savefig(output_file, dpi=300, bbox_inches='tight')        

        plt.close()        if 'oct_sev1_pct' in comparison:

        print(f"✅ Saved: {output_file}")            f.write(f"## Severity Mix\n\n")

            f.write(f"| Month | Sev 1 % | Change |\n")

def create_execution_log():            f.write(f"|-------|---------|--------|\n")

    """Create execution log (Step 6 completion)"""            f.write(f"| October | {comparison['oct_sev1_pct']:.1f}% | {comparison['sev1_delta']:+.1f} pp |\n")

    log_data = {            f.write(f"| September | {comparison['sep_sev1_pct']:.1f}% | - |\n\n")

        'timestamp': datetime.now().isoformat(),    

        'script': 'analyze_october_ttm.py',    print(f"\n✅ Saved to: {output_file}")

        'status': 'completed',    return comparison

        'outputs': [

            'October_Summary_Statistics.md',def create_visualizations(df):

            'October_Key_Metrics.md',    """Create visualization charts"""

            'October_vs_September_Comparison.md',    print(f"\n{'='*80}")

            'October_TTM_Distribution.png',    print("CREATING VISUALIZATIONS")

            'October_Top_Services.png',    print("="*80)

            'October_Daily_Timeline.png',    

            'October_Severity_Distribution.png'    # 1. TTM Distribution Histogram

        ]    if 'TTM' in df.columns:

    }        print("📊 Creating TTM distribution histogram...")

            fig, ax = plt.subplots(figsize=(12, 6))

    output_file = os.path.join(OUTPUT_FOLDER, "analysis_execution_log.json")        ttm_data = df['TTM'].dropna()

    with open(output_file, 'w') as f:        

        json.dump(log_data, f, indent=2)        ax.hist(ttm_data, bins=30, edgecolor='black', alpha=0.7)

            ax.axvline(ttm_data.median(), color='red', linestyle='--', label=f'Median: {ttm_data.median():.0f} min')

    print(f"\n✅ Execution log saved: {output_file}")        ax.axvline(ttm_data.quantile(0.75), color='orange', linestyle='--', label=f'P75: {ttm_data.quantile(0.75):.0f} min')

        

def main():        ax.set_xlabel('Time to Mitigate (minutes)', fontsize=12)

    """Main execution function"""        ax.set_ylabel('Number of Incidents', fontsize=12)

    print("=" * 80)        ax.set_title('October 2025 TTM Distribution', fontsize=14, fontweight='bold')

    print("OCTOBER 2025 TTM ANALYSIS")        ax.legend()

    print("Steps 2-4 and 6 of PROMPT_1.md Workflow")        ax.grid(True, alpha=0.3)

    print("=" * 80)        

            output_file = OUTPUT_FOLDER / "October_TTM_Distribution.png"

    # Load data        plt.tight_layout()

    df_current, df_previous = load_data()        plt.savefig(output_file, dpi=300, bbox_inches='tight')

            plt.close()

    # Execute analysis steps        print(f"   ✅ Saved: {output_file.name}")

    generate_summary_statistics(df_current)    

    calculate_key_metrics(df_current)    # 2. Top Services Bar Chart

    compare_to_previous_month(df_current, df_previous)    if 'ServiceName' in df.columns:

    create_visualizations(df_current)        print("📊 Creating top services bar chart...")

    create_execution_log()        fig, ax = plt.subplots(figsize=(12, 8))

            top_services = df['ServiceName'].value_counts().head(10)

    print("\n" + "=" * 80)        

    print("✅ ANALYSIS COMPLETE")        top_services.plot(kind='barh', ax=ax, color='steelblue')

    print("=" * 80)        ax.set_xlabel('Number of Incidents', fontsize=12)

    print("\nGenerated files:")        ax.set_ylabel('Service', fontsize=12)

    print("  - October_Summary_Statistics.md")        ax.set_title('October 2025 Top 10 Services by Incident Count', fontsize=14, fontweight='bold')

    print("  - October_Key_Metrics.md")        ax.grid(True, axis='x', alpha=0.3)

    print("  - October_vs_September_Comparison.md")        

    print("  - October_TTM_Distribution.png")        output_file = OUTPUT_FOLDER / "October_Top_Services.png"

    print("  - October_Top_Services.png")        plt.tight_layout()

    print("  - October_Daily_Timeline.png")        plt.savefig(output_file, dpi=300, bbox_inches='tight')

    print("  - October_Severity_Distribution.png")        plt.close()

    print("  - analysis_execution_log.json")        print(f"   ✅ Saved: {output_file.name}")

    print("\nNext step: Run generate_narrative.py for Step 5")    

    # 3. Severity Pie Chart

if __name__ == "__main__":    if 'Severity' in df.columns:

    main()        print("📊 Creating severity distribution pie chart...")

        fig, ax = plt.subplots(figsize=(10, 8))
        severity_dist = df['Severity'].value_counts().sort_index()
        
        colors = ['#d32f2f', '#f57c00', '#fbc02d', '#689f38']
        labels = [f'Sev {sev}\n({count} incidents)' for sev, count in severity_dist.items()]
        
        ax.pie(severity_dist, labels=labels, autopct='%1.1f%%', colors=colors[:len(severity_dist)], 
               startangle=90, textprops={'fontsize': 11})
        ax.set_title('October 2025 Severity Distribution', fontsize=14, fontweight='bold')
        
        output_file = OUTPUT_FOLDER / "October_Severity_Distribution.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Saved: {output_file.name}")
    
    # 4. Daily Timeline
    if 'OutageCreateDate' in df.columns:
        print("📊 Creating daily incident timeline...")
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Parse dates and count by day (handle mixed date formats)
        df['CreateDate'] = pd.to_datetime(df['OutageCreateDate'], format='mixed', errors='coerce')
        daily_counts = df.groupby(df['CreateDate'].dt.date).size()
        
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=6)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Incidents', fontsize=12)
        ax.set_title('October 2025 Daily Incident Timeline', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        output_file = OUTPUT_FOLDER / "October_Daily_Timeline.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Saved: {output_file.name}")
    
    print("\n✅ All visualizations created!")

def create_execution_log():
    """Create execution log"""
    log = {
        'execution_time': datetime.now().isoformat(),
        'status': 'SUCCESS',
        'csv_file': str(OCTOBER_CSV),
        'steps_completed': [
            'Data loaded from CSV',
            'Summary statistics generated',
            'Key metrics calculated',
            'Month-over-month comparison completed',
            'Visualizations created'
        ],
        'next_steps': [
            'Generate October narrative following Narrative_Generation_Instructions.md',
            'Read through all 109 incidents in the CSV',
            'Create interconnected story with incident IDs as proof'
        ]
    }
    
    output_file = OUTPUT_FOLDER / "analysis_execution_log.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)
    
    print(f"\n📝 Execution log saved to: {output_file}")
    return log

def main():
    """Main execution"""
    print("="*80)
    print("OCTOBER 2025 TTM ANALYSIS - COMPLETE WORKFLOW")
    print("="*80)
    print(f"Execution Time: {datetime.now()}\n")
    
    try:
        # Load data
        df_oct, df_sep = load_data()
        
        # Generate summary statistics
        stats = generate_summary_statistics(df_oct)
        
        # Calculate key metrics
        metrics = calculate_key_metrics(df_oct)
        
        # Compare to previous month
        comparison = compare_to_previous_month(df_oct, df_sep)
        
        # Create visualizations
        create_visualizations(df_oct)
        
        # Create execution log
        log = create_execution_log()
        
        print(f"\n{'='*80}")
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\n📁 Generated Files:")
        print(f"   - October_Summary_Statistics.md")
        print(f"   - October_Key_Metrics.md")
        print(f"   - October_vs_September_Comparison.md")
        print(f"   - October_TTM_Distribution.png")
        print(f"   - October_Top_Services.png")
        print(f"   - October_Severity_Distribution.png")
        print(f"   - October_Daily_Timeline.png")
        print(f"   - analysis_execution_log.json")
        
        print(f"\n📝 Next Step: Generate Narrative")
        print(f"   Follow instructions in: Narrative_Generation_Instructions.md")
        print(f"   Read all 109 incidents in: {OCTOBER_CSV}")
        print(f"   Create: October_Narrative.md")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
