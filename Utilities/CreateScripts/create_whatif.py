import pandas as pd
import numpy as np
from datetime import datetime

# Load data
df = pd.read_csv("october_2025_ttm_full_month.csv")
df['TTM'] = pd.to_numeric(df['TTM'], errors='coerce')
df_clean = df[df['TTM'].notna() & (df['TTM'] >= 0)].copy()

# Calculate baseline
baseline_p75 = df_clean['TTM'].quantile(0.75)
baseline_mean = df_clean['TTM'].mean()
baseline_median = df_clean['TTM'].median()
baseline_count = len(df_clean)

# Get severity column
severity_col = 'OutageIncidentSeverity' if 'OutageIncidentSeverity' in df_clean.columns else 'Severity'

print(f"Total incidents: {len(df_clean)}")
print(f"Checking for RootResponsibleIncidentId column...")

# Check if RootResponsibleIncidentId exists
if 'RootResponsibleIncidentId' in df_clean.columns:
    print(f"✓ RootResponsibleIncidentId column found")
    
    # Events are incidents where RootResponsibleIncidentId == OutageIncidentId (or is NaN/same as self)
    # Outages are incidents where RootResponsibleIncidentId points to a different incident
    df_clean['RootId'] = df_clean['RootResponsibleIncidentId'].fillna(df_clean['OutageIncidentId'])
    df_clean['IsRootEvent'] = df_clean['RootId'] == df_clean['OutageIncidentId']
    
    root_events = df_clean['IsRootEvent'].sum()
    cascading_outages = (~df_clean['IsRootEvent']).sum()
    
    print(f"  - Root Events: {root_events}")
    print(f"  - Cascading Outages: {cascading_outages}")
    
    # Get unique root events
    unique_roots = df_clean['RootId'].unique()
    print(f"  - Unique Event Systems: {len(unique_roots)}")
    
else:
    print(f"✗ RootResponsibleIncidentId column NOT found")
    print(f"  Available columns with 'Root' or 'Event': {', '.join([c for c in df_clean.columns if 'Root' in c or 'Event' in c or 'Responsible' in c][:10])}")
    # Fallback to EventId
    df_clean['RootId'] = df_clean['EventId'].fillna(df_clean['OutageIncidentId'])
    df_clean['IsRootEvent'] = df_clean['RootId'] == df_clean['OutageIncidentId']
    root_events = df_clean['IsRootEvent'].sum()
    cascading_outages = (~df_clean['IsRootEvent']).sum()

# Function to get all incidents in an event system (root + all cascades)
def get_event_system_incidents(root_id):
    """Get root event and all cascading outages with same RootResponsibleIncidentId"""
    return df_clean[df_clean['RootId'] == root_id]['OutageIncidentId'].tolist()

# Function to calculate metrics without specific incidents
def calculate_without(exclude_ids):
    remaining = df_clean[~df_clean['OutageIncidentId'].isin(exclude_ids)]
    if len(remaining) == 0:
        return None, None, None, 0
    return (
        remaining['TTM'].quantile(0.75),
        remaining['TTM'].mean(),
        remaining['TTM'].median(),
        len(remaining)
    )

# Calculate impact for each event system
event_impacts = []

for root_id in df_clean['RootId'].unique():
    # Get all incidents in this event system
    system_incidents = get_event_system_incidents(root_id)
    system_df = df_clean[df_clean['RootId'] == root_id]
    
    # Get the root event details
    root_event = system_df[system_df['OutageIncidentId'] == root_id]
    if root_event.empty:
        # If no exact match, take the first incident in the system as representative
        root_event = system_df.iloc[[0]]
    
    root_event = root_event.iloc[0]
    
    # Calculate impact of removing this entire event system
    p75_without, mean_without, median_without, count_without = calculate_without(system_incidents)
    
    if p75_without is not None:
        p75_delta = baseline_p75 - p75_without
        p75_pct = (p75_delta / baseline_p75 * 100)
        mean_delta = baseline_mean - mean_without
        
        cascade_count = len(system_incidents) - 1  # -1 for the root itself
        total_system_ttm = system_df['TTM'].sum()
        max_ttm = system_df['TTM'].max()
        
        event_impacts.append({
            'root_id': root_id,
            'service': root_event['ServiceName'] if 'ServiceName' in root_event else 'Unknown',
            'severity': root_event[severity_col] if severity_col in root_event else 'N/A',
            'root_ttm': root_event['TTM'],
            'max_ttm': max_ttm,
            'cascade_count': cascade_count,
            'total_incidents': len(system_incidents),
            'total_ttm': total_system_ttm,
            'p75_without': p75_without,
            'p75_delta': p75_delta,
            'p75_pct': p75_pct,
            'mean_without': mean_without,
            'mean_delta': mean_delta,
            'median_without': median_without,
            'count_without': count_without,
            'create_date': root_event.get('OutageCreateDate', 'N/A'),
            'root_cause': root_event.get('RootCauseCategory', 'N/A'),
            'system_df': system_df
        })

# Sort by P75 impact (descending - most impact first)
event_impacts.sort(key=lambda x: abs(x['p75_delta']), reverse=True)

print(f"\nCalculated impacts for {len(event_impacts)} event systems")
top3_pcts = [e['p75_pct'] for e in event_impacts[:3]]
print(f"Top 3 impacts: {top3_pcts}")

# Build markdown output
output = f"""# October 2025 TTM Analysis - What-If Scenario Analysis (Event Systems)

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This analysis uses **RootResponsibleIncidentId** to identify complete event systems, where a root event causes cascading downstream outages. When an event system is excluded in what-if scenarios, both the root event and ALL cascading outages (regardless of level) are removed together, providing the true total impact of preventing that event.

### Dataset Classification

- **Total Incidents:** {baseline_count}
- **Root Events:** {root_events}
- **Cascading Outages:** {cascading_outages}
- **Unique Event Systems:** {len(event_impacts)}
- **Average incidents per event system:** {baseline_count/len(event_impacts):.1f}

### Baseline Metrics (All Incidents)

- **P75 TTM:** {baseline_p75:.1f} minutes
- **Mean TTM:** {baseline_mean:.1f} minutes
- **Median TTM:** {baseline_median:.1f} minutes

---

## Part 1: Individual Event System Impacts (Ranked by P75 Impact)

This section ranks each event system by its impact on P75 TTM if that system (root + all cascades) were prevented.

**Interpretation:** The higher the P75 delta, the more that event system contributed to overall TTM.

"""

# Part 1: Individual event impacts ranked by P75 delta
for idx, event in enumerate(event_impacts, 1):
    root_id = int(event['root_id'])
    
    output += f"""### Rank #{idx}: Event System {root_id}

**Event System Details:**
- **Root Event ID:** {root_id}
- **Service:** {event['service']}
- **Severity:** {event['severity']}
- **Root Event TTM:** {event['root_ttm']:.0f} minutes
- **Cascading Outages:** {event['cascade_count']}
- **Total Incidents in System:** {event['total_incidents']}
- **System Total TTM:** {event['total_ttm']:.0f} minutes
- **Date:** {str(event['create_date'])[:10] if pd.notna(event['create_date']) else 'N/A'}

"""
    
    # List cascading outages if any
    if event['cascade_count'] > 0:
        output += "**Cascading Outages:**\n"
        cascades = event['system_df'][event['system_df']['OutageIncidentId'] != root_id]
        for _, outage in cascades.head(10).iterrows():
            output += f"  - Outage {int(outage['OutageIncidentId'])} ({outage['ServiceName']}, TTM: {outage['TTM']:.0f} min"
            if 'Level' in outage and pd.notna(outage['Level']):
                output += f", Level: {outage['Level']}"
            output += ")\n"
        if event['cascade_count'] > 10:
            output += f"  - ...and {event['cascade_count'] - 10} more cascading outages\n"
        output += "\n"
    
    output += f"""**Impact if This Event System Prevented:**
- **P75 TTM:** {event['p75_without']:.1f} minutes
- **P75 Delta:** {event['p75_delta']:+.1f} minutes ({event['p75_pct']:+.1f}%)
- **Mean TTM:** {event['mean_without']:.1f} minutes (Δ {event['mean_delta']:+.1f} min)
- **Median TTM:** {event['median_without']:.1f} minutes
- **Remaining Incidents:** {event['count_without']}

"""
    
    if pd.notna(event['root_cause']) and event['root_cause'] != 'N/A':
        output += f"**Root Cause:** {event['root_cause']}\n\n"
    
    # Flag high-impact events
    if abs(event['p75_pct']) >= 2.0:
        output += f"⚠️ **High Impact:** Preventing this event system would change P75 by {abs(event['p75_pct']):.1f}%\n\n"
    
    if event['cascade_count'] >= 3:
        output += f"🔗 **High Cascade:** This event triggered {event['cascade_count']} downstream outages\n\n"
    
    output += "---\n\n"

# Part 2: Cumulative removal impact
output += """## Part 2: Cumulative Removal Impact Analysis

This section shows the cumulative impact of removing event systems in order of their individual impact (from Part 1). This answers: "What if we prevented the top N most impactful events?"

**Methodology:** Events are removed in rank order (highest individual impact first), and metrics are recalculated after each removal to show cumulative effect.

"""

# Calculate cumulative impacts
cumulative_excluded = []
cumulative_results = []

for idx, event in enumerate(event_impacts, 1):
    # Add this event system's incidents to cumulative list
    system_incidents = get_event_system_incidents(event['root_id'])
    cumulative_excluded.extend(system_incidents)
    cumulative_excluded = list(set(cumulative_excluded))  # Remove duplicates
    
    # Calculate metrics with all excluded so far
    p75_cum, mean_cum, median_cum, count_cum = calculate_without(cumulative_excluded)
    
    if p75_cum is not None:
        p75_delta_cum = baseline_p75 - p75_cum
        p75_pct_cum = (p75_delta_cum / baseline_p75 * 100)
        mean_delta_cum = baseline_mean - mean_cum
        
        cumulative_results.append({
            'rank': idx,
            'events_removed': idx,
            'total_incidents_removed': len(cumulative_excluded),
            'pct_removed': (len(cumulative_excluded) / baseline_count * 100),
            'p75': p75_cum,
            'p75_delta': p75_delta_cum,
            'p75_pct': p75_pct_cum,
            'mean': mean_cum,
            'mean_delta': mean_delta_cum,
            'median': median_cum,
            'remaining': count_cum,
            'latest_event': event
        })

# Display cumulative results
for result in cumulative_results[:20]:  # Show top 20
    latest = result['latest_event']
    
    output += f"""### Cumulative Step {result['rank']}: Remove Top {result['events_removed']} Event System{"s" if result['events_removed'] > 1 else ""}

**Latest Event Added:** {int(latest['root_id'])} ({latest['service']}, {latest['total_incidents']} incidents)

**Cumulative Exclusions:**
- **Event Systems Removed:** {result['events_removed']}
- **Total Incidents Removed:** {result['total_incidents_removed']} ({result['pct_removed']:.1f}% of all incidents)
- **Remaining Incidents:** {result['remaining']}

**Cumulative Impact on Metrics:**
- **P75 TTM:** {result['p75']:.1f} minutes
- **P75 Delta from Baseline:** {result['p75_delta']:+.1f} minutes ({result['p75_pct']:+.1f}%)
- **Mean TTM:** {result['mean']:.1f} minutes (Δ {result['mean_delta']:+.1f} min)
- **Median TTM:** {result['median']:.1f} minutes

"""
    
    # Highlight milestones
    if result['events_removed'] in [1, 3, 5, 10]:
        if result['events_removed'] == 1:
            output += f"📊 **Insight:** Single most impactful event system accounts for {abs(result['p75_pct']):.1f}% of P75 TTM\n\n"
        else:
            output += f"📊 **Insight:** Top {result['events_removed']} event systems account for {abs(result['p75_pct']):.1f}% of P75 TTM\n\n"
    
    output += "---\n\n"

# Summary comparison table
output += """## Summary: Cumulative Removal Comparison Table

| Rank | Events Removed | Incidents Removed | % of Total | P75 TTM (min) | Δ P75 (min) | Δ P75 (%) | Remaining |
|------|----------------|-------------------|------------|---------------|-------------|-----------|-----------|
"""

for result in cumulative_results[:15]:
    output += f"| {result['rank']} | {result['events_removed']} | {result['total_incidents_removed']} | {result['pct_removed']:.1f}% | {result['p75']:.1f} | {result['p75_delta']:+.1f} | {result['p75_pct']:+.1f}% | {result['remaining']} |\n"

output += "\n---\n\n"

# Top event systems summary
output += """## Top Event Systems Summary (Top 10 by Impact)

| Rank | Event ID | Service | Cascades | Total TTM | P75 Impact | P75 Δ % |
|------|----------|---------|----------|-----------|------------|---------|
"""

for idx, event in enumerate(event_impacts[:10], 1):
    output += f"| {idx} | {int(event['root_id'])} | {event['service'][:30]} | {event['cascade_count']} | {event['total_ttm']:.0f} min | {event['p75_delta']:+.1f} min | {event['p75_pct']:+.1f}% |\n"

output += "\n---\n\n"

# Key insights
output += f"""## Key Insights & Recommendations

### Impact Concentration

"""

if len(cumulative_results) > 0:
    top1_impact = cumulative_results[0]['p75_pct']
    top5_impact = cumulative_results[4]['p75_pct'] if len(cumulative_results) > 4 else cumulative_results[-1]['p75_pct']
    top10_impact = cumulative_results[9]['p75_pct'] if len(cumulative_results) > 9 else cumulative_results[-1]['p75_pct']
    
    output += f"""- **Single Most Impactful Event:** {abs(top1_impact):.1f}% of P75 TTM
- **Top 5 Event Systems:** {abs(top5_impact):.1f}% of P75 TTM ({cumulative_results[4]['total_incidents_removed'] if len(cumulative_results) > 4 else cumulative_results[-1]['total_incidents_removed']} incidents)
- **Top 10 Event Systems:** {abs(top10_impact):.1f}% of P75 TTM ({cumulative_results[9]['total_incidents_removed'] if len(cumulative_results) > 9 else cumulative_results[-1]['total_incidents_removed']} incidents)

This demonstrates **extreme tail risk concentration** where a small number of event systems drive the majority of TTM impact.

### Cascading Analysis

"""

events_with_cascades = len([e for e in event_impacts if e['cascade_count'] > 0])
total_cascade_incidents = sum([e['cascade_count'] for e in event_impacts])
max_cascade = max([e['cascade_count'] for e in event_impacts])
avg_cascade = total_cascade_incidents / len(event_impacts)

output += f"""- **Event Systems with Cascades:** {events_with_cascades} ({events_with_cascades/len(event_impacts)*100:.1f}%)
- **Total Cascading Outages:** {cascading_outages}
- **Maximum Cascade Depth:** {max_cascade} outages from single event
- **Average Cascades per Event System:** {avg_cascade:.1f}

Preventing high-impact events eliminates not just the root incident but all downstream cascading failures.

### Prevention Priorities

1. **Focus on Top 10 Events:** These event systems account for {abs(top10_impact):.1f}% of P75 TTM
2. **Target Services:** {', '.join([e['service'] for e in event_impacts[:3]])} show highest individual event impacts
3. **Cascade Prevention:** Events with high cascade counts amplify their impact - faster root resolution reduces cascade duration
4. **Root Cause Focus:** Address root causes of top-ranked events: {', '.join(list(set([e['root_cause'] for e in event_impacts[:5] if pd.notna(e['root_cause']) and e['root_cause'] != 'N/A']))[:3])}

### Interpretation for Leadership

**What-If Question:** "If we prevented the top X events, what would P75 TTM be?"
- **Answer:** Use Part 2 (Cumulative table) to see exact impact
- **Example:** Preventing top 5 event systems would reduce P75 by {abs(top5_impact):.1f}% (from {baseline_p75:.0f} to {cumulative_results[4]['p75']:.1f} minutes)

**Key Takeaway:** P75 TTM is highly sensitive to a small number of high-impact event systems. Month-over-month metric changes can be significantly influenced by preventing (or experiencing) just a few major events.

---

**Analysis Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Methodology:** Event systems identified via RootResponsibleIncidentId (all levels)  
**Total Event Systems Analyzed:** {len(event_impacts)}  
**Baseline Dataset:** {baseline_count} incidents from October 2025  
"""

# Write output
with open("WhatIf.md", "w", encoding="utf-8") as f:
    f.write(output)

# Summary stats
line_count = len(output.split('\n'))

print(f"\n✅ Created WhatIf.md with event system analysis")
print(f"  - Total lines: {line_count}")
print(f"  - Event systems analyzed: {len(event_impacts)}")
print(f"  - Root events: {root_events}")
print(f"  - Cascading outages: {cascading_outages}")
top3_str = ', '.join([f"{e['p75_pct']:.1f}%" for e in event_impacts[:3]])
print(f"  - Top 3 event impacts: {top3_str}")
print(f"  - Top 10 cumulative impact: {abs(top10_impact):.1f}% of P75")
