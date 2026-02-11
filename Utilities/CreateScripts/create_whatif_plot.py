import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Data from the cumulative removal table
data = {
    'Events_Removed': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    'P75_TTM': [190.0, 180.0, 139.2, 133.0, 121.8, 121.0, 120.2, 116.0, 111.5, 110.0, 102.5, 95.5, 90.0, 87.0, 87.0, 84.5],
    'Incidents_Removed': [0, 1, 4, 7, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    'Pct_Removed': [0, 0.9, 3.4, 6.0, 10.3, 11.1, 12.0, 12.8, 13.7, 14.5, 15.4, 16.2, 17.1, 17.9, 18.8, 19.7]
}

df = pd.DataFrame(data)

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: P75 TTM vs Events Removed
ax1.plot(df['Events_Removed'], df['P75_TTM'], marker='o', linewidth=2.5, 
         markersize=8, color='#1f77b4', label='P75 TTM')
ax1.fill_between(df['Events_Removed'], df['P75_TTM'], alpha=0.3, color='#1f77b4')

# Add baseline line
ax1.axhline(y=190, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Baseline (190 min)')

# Highlight key milestones
milestone_indices = [1, 5, 10, 15]
milestone_colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
for idx, color in zip(milestone_indices, milestone_colors):
    ax1.plot(df.loc[idx, 'Events_Removed'], df.loc[idx, 'P75_TTM'], 
             marker='*', markersize=20, color=color, zorder=5)
    ax1.annotate(f"{df.loc[idx, 'P75_TTM']:.1f} min\n({df.loc[idx, 'Events_Removed']} events)", 
                xy=(df.loc[idx, 'Events_Removed'], df.loc[idx, 'P75_TTM']),
                xytext=(10, -15), textcoords='offset points',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

ax1.set_xlabel('Number of Top Event Systems Removed', fontsize=12, fontweight='bold')
ax1.set_ylabel('P75 TTM (minutes)', fontsize=12, fontweight='bold')
ax1.set_title('Cumulative Impact of Event Prevention on P75 TTM\nOctober 2025', 
              fontsize=14, fontweight='bold', pad=20)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', fontsize=10)
ax1.set_xlim(-0.5, 15.5)
ax1.set_ylim(75, 195)

# Add text box with insights
textstr = 'Key Insights:\n'
textstr += f'• Top 1 event: {190-180:.0f} min reduction (5.3%)\n'
textstr += f'• Top 5 events: {190-121:.0f} min reduction (36.3%)\n'
textstr += f'• Top 10 events: {190-102.5:.1f} min reduction (46.1%)\n'
textstr += f'• Top 15 events: {190-84.5:.1f} min reduction (55.5%)'
ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Plot 2: Percentage Reduction vs Events Removed
df['Pct_Reduction'] = ((190 - df['P75_TTM']) / 190 * 100)

ax2.bar(df['Events_Removed'], df['Pct_Reduction'], color='#2ca02c', alpha=0.7, 
        edgecolor='black', linewidth=1.5)

# Add value labels on bars
for idx, row in df.iterrows():
    if idx in [1, 5, 10, 15]:
        ax2.text(row['Events_Removed'], row['Pct_Reduction'] + 1, 
                f"{row['Pct_Reduction']:.1f}%\n({row['Incidents_Removed']} incidents)",
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

ax2.set_xlabel('Number of Top Event Systems Removed', fontsize=12, fontweight='bold')
ax2.set_ylabel('P75 TTM Reduction (%)', fontsize=12, fontweight='bold')
ax2.set_title('Percentage Reduction in P75 TTM\nby Event Prevention', 
              fontsize=14, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xlim(-0.5, 15.5)

# Add efficiency line annotation
ax2.axhline(y=36.3, color='red', linestyle='--', linewidth=2, alpha=0.5)
ax2.text(12, 38, 'Top 5 events = 36.3% reduction', fontsize=10, 
         color='red', fontweight='bold', ha='center')

plt.tight_layout()
plt.savefig('WhatIf_Cumulative_Impact.png', dpi=300, bbox_inches='tight')
print(f"✅ Created WhatIf_Cumulative_Impact.png")
print(f"   - Shows P75 TTM reduction as top events are removed")
print(f"   - Baseline: 190.0 minutes")
print(f"   - After removing top 15 events: 84.5 minutes (55.5% reduction)")
plt.close()

# Create a second detailed plot showing the rate of change
fig, ax = plt.subplots(figsize=(14, 8))

# Calculate marginal impact (how much each additional event reduces P75)
df['Marginal_Impact'] = df['P75_TTM'].diff() * -1  # Make positive for reduction
df.loc[0, 'Marginal_Impact'] = 0

# Create dual-axis plot
color1 = '#1f77b4'
color2 = '#ff7f0e'

ax.plot(df['Events_Removed'], df['P75_TTM'], marker='o', linewidth=3, 
        markersize=10, color=color1, label='P75 TTM (Cumulative)')
ax.fill_between(df['Events_Removed'], df['P75_TTM'], alpha=0.2, color=color1)
ax.axhline(y=190, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Baseline (190 min)')

ax.set_xlabel('Number of Top Event Systems Removed', fontsize=13, fontweight='bold')
ax.set_ylabel('P75 TTM (minutes)', fontsize=13, fontweight='bold', color=color1)
ax.tick_params(axis='y', labelcolor=color1)
ax.set_xlim(-0.5, 15.5)
ax.set_ylim(75, 195)

# Create second y-axis for marginal impact
ax2 = ax.twinx()
bars = ax2.bar(df['Events_Removed'][1:], df['Marginal_Impact'][1:], 
               alpha=0.6, color=color2, edgecolor='black', linewidth=1.5, 
               label='Marginal Impact (per event)', width=0.6)
ax2.set_ylabel('Marginal P75 Reduction (minutes per event)', fontsize=13, 
               fontweight='bold', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_ylim(0, 45)

# Highlight the big drops
big_drops = df[df['Marginal_Impact'] > 5].iloc[1:]
for idx, row in big_drops.iterrows():
    ax2.text(row['Events_Removed'], row['Marginal_Impact'] + 2, 
            f"{row['Marginal_Impact']:.1f}", ha='center', va='bottom', 
            fontsize=9, fontweight='bold', color=color2)

ax.set_title('Cumulative & Marginal Impact of Event Prevention on P75 TTM\nOctober 2025', 
            fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Combine legends
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=11)

# Add annotation for diminishing returns
ax.annotate('Steep decline:\nTop 5 events have\nlargest impact', 
           xy=(2.5, 136), xytext=(5, 170),
           arrowprops=dict(arrowstyle='->', lw=2, color='black'),
           fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='yellow', alpha=0.7))

ax.annotate('Diminishing returns:\nIncremental benefit\ndecreases', 
           xy=(12, 88), xytext=(9, 110),
           arrowprops=dict(arrowstyle='->', lw=2, color='black'),
           fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='lightblue', alpha=0.7))

plt.tight_layout()
plt.savefig('WhatIf_Cumulative_Marginal.png', dpi=300, bbox_inches='tight')
print(f"\n✅ Created WhatIf_Cumulative_Marginal.png")
print(f"   - Shows both cumulative and marginal (per-event) impact")
print(f"   - Illustrates diminishing returns after top 5 events")

plt.close()

# Create summary statistics
print(f"\n📊 Summary Statistics:")
print(f"   - Events 1-5 average marginal impact: {df['Marginal_Impact'][1:6].mean():.1f} min/event")
print(f"   - Events 6-10 average marginal impact: {df['Marginal_Impact'][6:11].mean():.1f} min/event")
print(f"   - Events 11-15 average marginal impact: {df['Marginal_Impact'][11:16].mean():.1f} min/event")
print(f"   - Top event impact: {df.loc[1, 'Marginal_Impact']:.1f} minutes (5.3%)")
print(f"   - Preventing top 5 events reduces P75 by {190-121:.0f} minutes (36.3%)")
