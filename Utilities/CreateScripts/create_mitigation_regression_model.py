"""
Mitigation Time Regression Model

Predict: Mitigation Time (TTM - TTO)
Features: 
  - OutageIncidentSeverity
  - RootCause (classified from set_Whys and RootCauses columns)

This model allows prediction of total TTM given TTO and incident characteristics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import re

# Load data
df = pd.read_csv('data/october_2025_ttm_filtered.csv')

print("=" * 80)
print("MITIGATION TIME REGRESSION MODEL")
print("=" * 80)
print()

# Calculate mitigation time
df['MitigationTime'] = df['TTM'] - df['TTO']

print(f"Total Incidents: {len(df)}")
print(f"Mitigation Time Stats:")
print(f"  Mean: {df['MitigationTime'].mean():.1f} minutes")
print(f"  Median: {df['MitigationTime'].median():.1f} minutes")
print(f"  Std: {df['MitigationTime'].std():.1f} minutes")
print(f"  Min: {df['MitigationTime'].min():.1f} minutes")
print(f"  Max: {df['MitigationTime'].max():.1f} minutes")
print()

# === ROOT CAUSE CLASSIFICATION ===
print("=" * 80)
print("STEP 1: ROOT CAUSE CLASSIFICATION")
print("=" * 80)
print()

def classify_root_cause(row):
    """
    Classify root cause from set_Whys and RootCauses columns
    
    Categories:
    - Hardware Failure
    - Software Bug
    - Configuration Issue
    - Capacity/Resource Exhaustion
    - Network Issue
    - Deployment/Change
    - External Dependency
    - Transient/Unknown
    """
    
    # Combine text sources
    text = ""
    if pd.notna(row.get('set_Whys')):
        text += str(row['set_Whys']).lower() + " "
    if pd.notna(row.get('RootCauses')):
        text += str(row['RootCauses']).lower() + " "
    
    if not text.strip():
        return "Unknown"
    
    # Classification rules (order matters - most specific first)
    
    # Hardware Failure
    if any(kw in text for kw in ['hardware failure', 'hardware error', 'psu', 'power loss', 
                                   'fuse', 'ssd failure', 'disk failure', 'memory failure',
                                   'nic failure', 'tor switch', 'power breaker', 'parity error']):
        return "Hardware Failure"
    
    # Software Bug
    if any(kw in text for kw in ['software bug', 'code bug', 'null reference', 'exception',
                                   'assertion failure', 'crash', 'memory leak', 'deadlock',
                                   'race condition', 'known bug', 'csc', 'process crash']):
        return "Software Bug"
    
    # Configuration Issue
    if any(kw in text for kw in ['configuration', 'misconfiguration', 'config error', 
                                   'wrong setting', 'incorrect parameter', 'config change',
                                   'settings', 'firewall rule', 'acl', 'policy']):
        return "Configuration Issue"
    
    # Capacity/Resource Exhaustion
    if any(kw in text for kw in ['capacity', 'exhaustion', 'out of memory', 'oom', 
                                   'disk full', 'cpu high', 'throttling', 'quota',
                                   'resource limit', 'scaling', 'overload']):
        return "Capacity/Resource"
    
    # Network Issue
    if any(kw in text for kw in ['network', 'connectivity', 'packet loss', 'latency',
                                   'bgp', 'routing', 'dns', 'timeout', 'connection reset']):
        return "Network Issue"
    
    # Deployment/Change
    if any(kw in text for kw in ['deployment', 'rollout', 'release', 'code push',
                                   'change', 'update', 'upgrade', 'migration', 'rollback']):
        return "Deployment/Change"
    
    # External Dependency
    if any(kw in text for kw in ['external', 'dependency', 'downstream', 'upstream',
                                   'third party', 'vendor', 'azure ad', 'cosmos']):
        return "External Dependency"
    
    # Transient
    if any(kw in text for kw in ['transient', 'intermittent', 'temporary', 'flaky',
                                   'self-healing', 'self-resolved', 'recovered']):
        return "Transient"
    
    return "Unknown"

# Apply classification
df['RootCause_Classified'] = df.apply(classify_root_cause, axis=1)

print("Root Cause Classification Results:")
root_cause_counts = df['RootCause_Classified'].value_counts()
for rc, count in root_cause_counts.items():
    avg_mit = df[df['RootCause_Classified'] == rc]['MitigationTime'].mean()
    print(f"  {rc}: {count} incidents ({count/len(df)*100:.1f}%), avg mitigation = {avg_mit:.1f} min")
print()

# === FEATURE ENGINEERING ===
print("=" * 80)
print("STEP 2: FEATURE ENGINEERING")
print("=" * 80)
print()

# Encode severity
severity_map = {
    'Sev0': 0,
    'Sev1': 1,
    'Sev2': 2,
    'Sev3': 3,
    'Sev4': 4
}
df['Severity_Numeric'] = df['OutageIncidentSeverity'].map(severity_map)

# Fill missing severity with median (Sev2)
df['Severity_Numeric'].fillna(2, inplace=True)

# One-hot encode root cause
root_cause_dummies = pd.get_dummies(df['RootCause_Classified'], prefix='RC')

# Combine features
feature_columns = ['Severity_Numeric', 'TTO'] + list(root_cause_dummies.columns)
X = pd.concat([df[['Severity_Numeric', 'TTO']], root_cause_dummies], axis=1)
y = df['MitigationTime']

print(f"Features ({len(feature_columns)}):")
for col in feature_columns:
    print(f"  - {col}")
print()
print(f"Target: MitigationTime (TTM - TTO)")
print()

# Remove rows with missing values
mask = X.notna().all(axis=1) & y.notna()
X_clean = X[mask]
y_clean = y[mask]
df_clean = df[mask].copy()

print(f"Clean dataset: {len(X_clean)} incidents (removed {len(X) - len(X_clean)} with missing values)")
print()

# === MODEL TRAINING ===
print("=" * 80)
print("STEP 3: MODEL TRAINING")
print("=" * 80)
print()

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)
df_train, df_test = train_test_split(df_clean, test_size=0.2, random_state=42)

print(f"Training set: {len(X_train)} incidents")
print(f"Test set: {len(X_test)} incidents")
print()

# Train multiple models
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
}

results = {}

for name, model in models.items():
    print(f"Training {name}...")
    
    # Train
    model.fit(X_train, y_train)
    
    # Predict
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Evaluate
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    
    results[name] = {
        'model': model,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_rmse': train_rmse,
        'test_rmse': test_rmse,
        'cv_r2_mean': cv_scores.mean(),
        'cv_r2_std': cv_scores.std(),
        'y_test_pred': y_test_pred
    }
    
    print(f"  Train R²: {train_r2:.3f}, Test R²: {test_r2:.3f}")
    print(f"  Train MAE: {train_mae:.1f} min, Test MAE: {test_mae:.1f} min")
    print(f"  Train RMSE: {train_rmse:.1f} min, Test RMSE: {test_rmse:.1f} min")
    print(f"  CV R² (5-fold): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print()

# Select best model (highest test R²)
best_model_name = max(results, key=lambda k: results[k]['test_r2'])
best_model = results[best_model_name]['model']

print(f"✅ Best Model: {best_model_name} (Test R² = {results[best_model_name]['test_r2']:.3f})")
print()

# === FEATURE IMPORTANCE ===
print("=" * 80)
print("STEP 4: FEATURE IMPORTANCE")
print("=" * 80)
print()

if best_model_name == 'Random Forest':
    importances = best_model.feature_importances_
    feature_importance = pd.DataFrame({
        'Feature': feature_columns,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    print("Top 10 Most Important Features:")
    for i, row in feature_importance.head(10).iterrows():
        print(f"  {row['Feature']}: {row['Importance']:.4f}")
    print()
else:
    coefficients = best_model.coef_
    feature_importance = pd.DataFrame({
        'Feature': feature_columns,
        'Coefficient': coefficients
    }).sort_values('Coefficient', key=abs, ascending=False)
    
    print("Top 10 Features by Coefficient Magnitude:")
    for i, row in feature_importance.head(10).iterrows():
        print(f"  {row['Feature']}: {row['Coefficient']:.2f}")
    print()

# === VISUALIZATION ===
print("=" * 80)
print("STEP 5: VISUALIZATION")
print("=" * 80)
print()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Actual vs Predicted (Test Set)
ax1 = axes[0, 0]
y_test_pred = results[best_model_name]['y_test_pred']
ax1.scatter(y_test, y_test_pred, alpha=0.6, s=100)
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect Prediction')
ax1.set_xlabel('Actual Mitigation Time (minutes)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Predicted Mitigation Time (minutes)', fontsize=12, fontweight='bold')
ax1.set_title(f'Actual vs Predicted - {best_model_name}\n(Test Set, R² = {results[best_model_name]["test_r2"]:.3f})', 
              fontsize=13, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

# 2. Residuals
ax2 = axes[0, 1]
residuals = y_test - y_test_pred
ax2.scatter(y_test_pred, residuals, alpha=0.6, s=100)
ax2.axhline(0, color='r', linestyle='--', lw=2)
ax2.set_xlabel('Predicted Mitigation Time (minutes)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Residuals (Actual - Predicted)', fontsize=12, fontweight='bold')
ax2.set_title('Residual Plot', fontsize=13, fontweight='bold')
ax2.grid(alpha=0.3)

# 3. Model Comparison
ax3 = axes[1, 0]
model_names = list(results.keys())
test_r2_scores = [results[name]['test_r2'] for name in model_names]
test_mae_scores = [results[name]['test_mae'] for name in model_names]

x_pos = np.arange(len(model_names))
bars = ax3.bar(x_pos, test_r2_scores, alpha=0.7, color=['red' if name == best_model_name else 'steelblue' for name in model_names])
ax3.set_xticks(x_pos)
ax3.set_xticklabels(model_names, rotation=45, ha='right')
ax3.set_ylabel('R² Score (Test Set)', fontsize=12, fontweight='bold')
ax3.set_title('Model Performance Comparison', fontsize=13, fontweight='bold')
ax3.set_ylim([0, 1])
ax3.grid(axis='y', alpha=0.3)

# Add value labels
for bar, score in zip(bars, test_r2_scores):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'{score:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 4. Feature Importance (Top 10)
ax4 = axes[1, 1]
top_features = feature_importance.head(10)
if best_model_name == 'Random Forest':
    y_pos = np.arange(len(top_features))
    ax4.barh(y_pos, top_features['Importance'], alpha=0.7, color='steelblue')
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(top_features['Feature'])
    ax4.set_xlabel('Importance', fontsize=12, fontweight='bold')
else:
    y_pos = np.arange(len(top_features))
    colors = ['red' if x < 0 else 'steelblue' for x in top_features['Coefficient']]
    ax4.barh(y_pos, top_features['Coefficient'], alpha=0.7, color=colors)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(top_features['Feature'])
    ax4.set_xlabel('Coefficient', fontsize=12, fontweight='bold')
ax4.set_title('Top 10 Most Important Features', fontsize=13, fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('mitigation_time_regression_model.png', dpi=300, bbox_inches='tight')
print("✅ Saved: mitigation_time_regression_model.png")
plt.close()

# === PREDICTION EXAMPLES ===
print()
print("=" * 80)
print("STEP 6: PREDICTION EXAMPLES")
print("=" * 80)
print()

print("Example Predictions (using test set samples):")
print()

# Show 5 example predictions
for i in range(min(5, len(df_test))):
    row = df_test.iloc[i]
    incident_id = row['OutageIncidentId']
    severity = row['OutageIncidentSeverity']
    root_cause = row['RootCause_Classified']
    tto = row['TTO']
    actual_mit = row['MitigationTime']
    actual_ttm = row['TTM']
    
    # Predict
    X_example = X_test.iloc[i:i+1]
    predicted_mit = best_model.predict(X_example)[0]
    predicted_ttm = tto + predicted_mit
    
    print(f"Incident {incident_id}:")
    print(f"  Severity: {severity}")
    print(f"  Root Cause: {root_cause}")
    print(f"  TTO (Detection): {tto:.1f} min")
    print(f"  Actual Mitigation: {actual_mit:.1f} min → Actual TTM: {actual_ttm:.1f} min")
    print(f"  Predicted Mitigation: {predicted_mit:.1f} min → Predicted TTM: {predicted_ttm:.1f} min")
    print(f"  Error: {abs(actual_mit - predicted_mit):.1f} min ({abs(actual_mit - predicted_mit)/actual_mit*100:.1f}%)")
    print()

# === HYPOTHETICAL SCENARIOS ===
print("=" * 80)
print("STEP 7: HYPOTHETICAL PREDICTIONS")
print("=" * 80)
print()

print("Given TTO and incident characteristics, predict TTM:")
print()

# Create hypothetical scenarios
scenarios = [
    {'Severity': 'Sev0', 'RootCause': 'Hardware Failure', 'TTO': 10},
    {'Severity': 'Sev0', 'RootCause': 'Software Bug', 'TTO': 10},
    {'Severity': 'Sev0', 'RootCause': 'Configuration Issue', 'TTO': 10},
    {'Severity': 'Sev1', 'RootCause': 'Hardware Failure', 'TTO': 15},
    {'Severity': 'Sev1', 'RootCause': 'Capacity/Resource', 'TTO': 15},
    {'Severity': 'Sev2', 'RootCause': 'Network Issue', 'TTO': 20},
]

for scenario in scenarios:
    # Build feature vector
    severity_num = severity_map[scenario['Severity']]
    tto = scenario['TTO']
    
    # Create dummy vector
    X_hypo = pd.DataFrame(0, index=[0], columns=feature_columns)
    X_hypo['Severity_Numeric'] = severity_num
    X_hypo['TTO'] = tto
    
    # Set root cause dummy
    rc_col = f"RC_{scenario['RootCause']}"
    if rc_col in X_hypo.columns:
        X_hypo[rc_col] = 1
    
    # Predict
    predicted_mit = best_model.predict(X_hypo)[0]
    predicted_ttm = tto + predicted_mit
    
    print(f"Scenario: {scenario['Severity']} + {scenario['RootCause']} + TTO={tto}min")
    print(f"  → Predicted Mitigation: {predicted_mit:.1f} min")
    print(f"  → Predicted TTM: {predicted_ttm:.1f} min")
    print()

# === MODEL SUMMARY ===
print("=" * 80)
print("MODEL SUMMARY")
print("=" * 80)
print()

print(f"Best Model: {best_model_name}")
print(f"  R² Score: {results[best_model_name]['test_r2']:.3f}")
print(f"  MAE: {results[best_model_name]['test_mae']:.1f} minutes")
print(f"  RMSE: {results[best_model_name]['test_rmse']:.1f} minutes")
print()
print("Interpretation:")
if results[best_model_name]['test_r2'] > 0.5:
    print("  ✅ Model explains >50% of variance in mitigation time")
elif results[best_model_name]['test_r2'] > 0.3:
    print("  ⚠️  Model explains 30-50% of variance (moderate predictive power)")
else:
    print("  ❌ Model explains <30% of variance (low predictive power)")
print()
print(f"Average prediction error: ±{results[best_model_name]['test_mae']:.1f} minutes")
print()

# Save model
import pickle
with open('mitigation_time_model.pkl', 'wb') as f:
    pickle.dump({
        'model': best_model,
        'feature_columns': feature_columns,
        'severity_map': severity_map,
        'results': results[best_model_name]
    }, f)

print("✅ Model saved to: mitigation_time_model.pkl")
print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
