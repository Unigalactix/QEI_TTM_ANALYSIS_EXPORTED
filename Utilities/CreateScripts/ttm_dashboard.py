"""
TTM Analysis Interactive Dashboard - Simplified & Robust Version
================================================================
Run: python ttm_dashboard.py
Then open: http://127.0.0.1:8050
"""

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

print("Loading data...")
df = pd.read_csv('october_2025_ttm_full_month.csv', encoding='utf-8-sig')
print(f"Loaded {len(df)} incidents with {len(df.columns)} columns")

# Map column names to standard names
column_mapping = {
    'OutageCreateDate': 'CreateDate',
    'OutageIncidentId': 'IncidentId',
    'ServiceName': 'Service',
    'Severity': 'Severity',
    'TTM': 'TTM',
    'IsCritSit': 'CritSit',
    'OwningTeamName': 'Team',
    'ImpactedRegion': 'Region',
    'RootCauses': 'RootCause'
}

# Rename columns that exist
for old_col, new_col in column_mapping.items():
    if old_col in df.columns:
        df[new_col] = df[old_col]

# Handle date parsing
if 'CreateDate' in df.columns:
    df['CreateDate'] = pd.to_datetime(df['CreateDate'], errors='coerce')
    df['Date'] = df['CreateDate'].dt.date
    df['Hour'] = df['CreateDate'].dt.hour
    df['DayOfWeek'] = df['CreateDate'].dt.day_name()

# Calculate metrics
if 'TTM' in df.columns:
    df['TTM_Quintile'] = pd.qcut(df['TTM'].fillna(0), q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5 (High)'], duplicates='drop')
    
    # Calculate percentiles for P70-P80 filter
    p70 = df['TTM'].quantile(0.70)
    p80 = df['TTM'].quantile(0.80)
    df['IsP70P80'] = (df['TTM'] >= p70) & (df['TTM'] <= p80)
    print(f"P70-P80 Range: {p70:.0f} - {p80:.0f} minutes ({df['IsP70P80'].sum()} incidents)")

# Load exclusions
exclusions = [694602140, 694752515, 694624704]
if 'IncidentId' in df.columns:
    df['IsExcluded'] = df['IncidentId'].isin(exclusions)
    df['Dataset'] = df['IsExcluded'].map({True: 'Excluded (BCDR/EUAP)', False: 'Production'})
else:
    df['Dataset'] = 'Production'

# Identify events (groups of incidents with same OutageCorrelationId)
if 'OutageCorrelationId' in df.columns:
    event_counts = df.groupby('OutageCorrelationId').size()
    multi_incident_events = event_counts[event_counts > 1].index.tolist()
    df['IsPartOfEvent'] = df['OutageCorrelationId'].isin(multi_incident_events)
    df['EventSize'] = df['OutageCorrelationId'].map(event_counts)
    print(f"Events identified: {len(multi_incident_events)} events with {df['IsPartOfEvent'].sum()} total incidents")
else:
    df['IsPartOfEvent'] = False
    df['EventSize'] = 1

# Pre-compute keyword matches for performance optimization
# Root Cause themes
if 'RootCauses' in df.columns:
    df['has_connectivity'] = df['RootCauses'].str.lower().str.contains('connectivity|connection|network|endpoint|unreachable', na=False)
    df['has_configuration'] = df['RootCauses'].str.lower().str.contains('configuration|config|misconfigur|setting|drift', na=False)
    df['has_capacity'] = df['RootCauses'].str.lower().str.contains('capacity|resource|memory|cpu|throttl|scaling|exhaust', na=False)
    df['has_deployment'] = df['RootCauses'].str.lower().str.contains('deployment|deploy|rollout|release|code change', na=False)
    df['has_certificate'] = df['RootCauses'].str.lower().str.contains('certificate|cert|ssl|tls|authentication', na=False)
    df['has_timeout'] = df['RootCauses'].str.lower().str.contains('timeout|latency|slow|performance', na=False)
    df['has_dependency'] = df['RootCauses'].str.lower().str.contains('dependency|dependent|downstream|upstream|cascading', na=False)
else:
    for theme in ['connectivity', 'configuration', 'capacity', 'deployment', 'certificate', 'timeout', 'dependency']:
        df[f'has_{theme}'] = False

# Mitigation actions
if 'Mitigations' in df.columns:
    df['has_restart'] = df['Mitigations'].str.lower().str.contains('restart|reboot|recycle|bounce', na=False)
    df['has_rollback'] = df['Mitigations'].str.lower().str.contains('rollback|revert|roll back', na=False)
    df['has_scaling'] = df['Mitigations'].str.lower().str.contains('scal|add capacity|increase resource', na=False)
    df['has_failover'] = df['Mitigations'].str.lower().str.contains('failover|fail over|redirect|switch', na=False)
    df['has_config_change'] = df['Mitigations'].str.lower().str.contains('config|setting|parameter|adjust|modify', na=False)
    df['has_traffic_mgmt'] = df['Mitigations'].str.lower().str.contains('throttle|rate limit|block|traffic|load', na=False)
else:
    for action in ['restart', 'rollback', 'scaling', 'failover', 'config_change', 'traffic_mgmt']:
        df[f'has_{action}'] = False

# Impact types
if 'Impacts' in df.columns:
    df['has_availability'] = df['Impacts'].str.lower().str.contains('availability|unavailable|down|outage', na=False)
    df['has_performance'] = df['Impacts'].str.lower().str.contains('performance|slow|latency|delay', na=False)
    df['has_functionality'] = df['Impacts'].str.lower().str.contains('functionality|function|feature|capabilit', na=False)
    df['has_data_issue'] = df['Impacts'].str.lower().str.contains('data|corruption|loss|inconsisten', na=False)
    df['has_authentication'] = df['Impacts'].str.lower().str.contains('authentication|auth|login|access denied', na=False)
else:
    for impact in ['availability', 'performance', 'functionality', 'data_issue', 'authentication']:
        df[f'has_{impact}'] = False

print(f"Pre-computed {18} keyword matching columns for performance optimization")

# Define high-entropy columns for table display (based on entropy analysis)
TABLE_COLUMNS = [
    'OutageIncidentId', 'ServiceName', 'Severity', 'TTM', 'IsCritSit',
    'OwningTeamName', 'ImpactedRegion', 'OutageCreateDate', 
    'RootCauses', 'IncidentTitle', 'Mitigations', 'Impacts', 
    'OutageCorrelationId', 'EventSize'
]

# Get list of events for dropdown
if 'OutageCorrelationId' in df.columns:
    event_list = df[df['IsPartOfEvent'] == True].groupby('OutageCorrelationId').agg({
        'OutageIncidentId': 'count'
    }).sort_values('OutageIncidentId', ascending=False).reset_index()
    event_list.columns = ['EventName', 'IncidentCount']
    EVENT_OPTIONS = [{'label': f'{row["EventName"]} ({row["IncidentCount"]} incidents)', 
                     'value': row['EventName']} 
                    for _, row in event_list.iterrows()]
else:
    EVENT_OPTIONS = []

print(f"Date range: {df['CreateDate'].min()} to {df['CreateDate'].max()}" if 'CreateDate' in df.columns else "No date column found")
print(f"Ready to start dashboard!")

# ============================================================================
# APP SETUP
# ============================================================================

app = dash.Dash(__name__, title="TTM Dashboard")
BLUE = '#0078D4'
GRAY_BG = '#F3F2F1'
BORDER = '#EDEBE9'

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # Hidden stores for interactive chart clicks
    dcc.Store(id='chart-click-store', data={}),
    
    # Header
    html.Div([
        html.H1("TTM Analysis Dashboard", style={'color': 'white', 'margin': '0', 'padding': '20px'}),
        html.P("October 2025 - Quality Engineering Insights", 
               style={'color': 'white', 'margin': '0', 'padding': '0 20px 20px'})
    ], style={'backgroundColor': BLUE}),
    
    # Container with flexbox layout
    html.Div([
        # Left Sidebar - Filters
        html.Div([
            html.H3("Filters", style={'color': BLUE, 'borderBottom': f'2px solid {BLUE}', 'paddingBottom': '10px'}),
            
            html.Label("Date Range:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            html.Div([
                html.Label("Start:", style={'fontSize': '12px', 'marginRight': '5px'}),
                dcc.DatePickerSingle(
                    id='start-date-filter',
                    date=df['CreateDate'].min().date() if 'CreateDate' in df.columns and df['CreateDate'].notna().any() else None,
                    display_format='YYYY-MM-DD',
                    style={'marginBottom': '5px'}
                ),
            ]),
            html.Div([
                html.Label("End:", style={'fontSize': '12px', 'marginRight': '5px'}),
                dcc.DatePickerSingle(
                    id='end-date-filter',
                    date=df['CreateDate'].max().date() if 'CreateDate' in df.columns and df['CreateDate'].notna().any() else None,
                    display_format='YYYY-MM-DD'
                ),
            ]),
            
            html.Div([
                dcc.Checklist(
                    id='exclude-cascade-filter',
                    options=[{'label': ' Exclude Cascade (Events)', 'value': 'exclude'}],
                    value=[],
                    style={'marginTop': '15px'}
                ),
            ]),
            
            html.Div([
                dcc.Checklist(
                    id='exclude-bcdr-filter',
                    options=[{'label': ' Exclude BCDR/EUAP', 'value': 'exclude'}],
                    value=['exclude'],
                    style={'marginTop': '5px'}
                ),
            ]),
            
            html.Label("Severity:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.Dropdown(id='severity-filter',
                options=[{'label': str(s), 'value': s} for s in sorted(df['Severity'].dropna().unique())],
                multi=True, placeholder='All Severities'),
            
            html.Label("Service:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.Dropdown(id='service-filter',
                options=[{'label': s, 'value': s} for s in sorted(df['Service'].dropna().unique()[:50])],
                multi=True, placeholder='All Services'),
            
            html.Label("TTM Range (minutes):", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.RangeSlider(id='ttm-filter',
                min=0, max=int(df['TTM'].max()) if 'TTM' in df.columns else 1000,
                value=[0, int(df['TTM'].max()) if 'TTM' in df.columns else 1000],
                marks={0: '0', 180: '3h', 720: '12h', 1440: '24h'},
                tooltip={'placement': 'bottom', 'always_visible': False}),
            
            html.Label("Quintile:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.Dropdown(id='quintile-filter',
                options=[{'label': q, 'value': q} for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5 (High)']],
                multi=True, placeholder='All Quintiles'),
            
            html.Label("CritSit:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.Dropdown(id='critsit-filter',
                options=[{'label': 'Yes', 'value': True}, {'label': 'No', 'value': False}, {'label': 'All', 'value': 'All'}],
                value='All', clearable=False),
            
            html.Label("P70-P80 Only:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.Dropdown(id='p70p80-filter',
                options=[{'label': 'Yes (70th-80th percentile)', 'value': True}, 
                        {'label': 'No (All)', 'value': False}],
                value=False, clearable=False),
            
            html.Label("Event (Cascading):", style={'fontWeight': 'bold', 'marginTop': '15px'}),
            dcc.Dropdown(id='event-filter',
                options=[{'label': 'All Events', 'value': 'All'}] + EVENT_OPTIONS,
                value='All', clearable=False,
                placeholder='Select specific event'),
            
            html.Div([
                html.Button('Reset Filters', id='reset-btn', n_clicks=0,
                    style={'marginTop': '20px', 'width': '100%', 'padding': '10px',
                          'backgroundColor': BLUE, 'color': 'white', 'border': 'none',
                          'borderRadius': '4px', 'cursor': 'pointer'}),
                html.Button('Clear Chart Filters', id='clear-chart-btn', n_clicks=0,
                    style={'marginTop': '10px', 'width': '100%', 'padding': '10px',
                          'backgroundColor': '#666', 'color': 'white', 'border': 'none',
                          'borderRadius': '4px', 'cursor': 'pointer'})
            ])
        ], style={'width': '280px', 'padding': '20px',
                 'backgroundColor': 'white', 'minHeight': '100vh', 'overflowY': 'auto',
                 'borderRight': f'1px solid {BORDER}', 'flexShrink': '0'}),
        
        # Main Content
        html.Div([
            # Active Chart Filters Banner
            html.Div(id='chart-filter-banner', style={'marginBottom': '15px'}),
            
            # Summary Cards
            html.Div([
                html.Div([
                    html.H4("Total", style={'margin': '0', 'fontSize': '14px'}),
                    html.H2(id='card-total', style={'color': BLUE, 'margin': '5px 0'})
                ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '18%',
                         'display': 'inline-block', 'marginRight': '2%'}),
                
                html.Div([
                    html.H4("P75 TTM", style={'margin': '0', 'fontSize': '14px'}),
                    html.H2(id='card-p75', style={'color': BLUE, 'margin': '5px 0'})
                ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '18%',
                         'display': 'inline-block', 'marginRight': '2%'}),
                
                html.Div([
                    html.H4("Mean TTM", style={'margin': '0', 'fontSize': '14px'}),
                    html.H2(id='card-mean', style={'color': BLUE, 'margin': '5px 0'})
                ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '18%',
                         'display': 'inline-block', 'marginRight': '2%'}),
                
                html.Div([
                    html.H4("P90 TTM", style={'margin': '0', 'fontSize': '14px'}),
                    html.H2(id='card-p90', style={'color': BLUE, 'margin': '5px 0'})
                ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '18%',
                         'display': 'inline-block', 'marginRight': '2%'}),
                
                html.Div([
                    html.H4("CritSits", style={'margin': '0', 'fontSize': '14px'}),
                    html.H2(id='card-critsit', style={'color': '#D13438', 'margin': '5px 0'})
                ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px',
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '18%',
                         'display': 'inline-block'})
            ], style={'marginBottom': '20px'}),
            
            # Charts Row 1
            html.Div([
                html.Div([dcc.Graph(id='chart-dist')], 
                        style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
                html.Div([dcc.Graph(id='chart-services')], 
                        style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'marginBottom': '20px', 'width': '100%'}),
            
            # Charts Row 2
            html.Div([
                html.Div([dcc.Graph(id='chart-timeline')], 
                        style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
                html.Div([dcc.Graph(id='chart-severity')], 
                        style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'marginBottom': '20px', 'width': '100%'}),
            
            # Charts Row 3
            html.Div([
                html.Div([dcc.Graph(id='chart-quintile')], 
                        style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'}),
                html.Div([dcc.Graph(id='chart-region')], 
                        style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
            ], style={'marginBottom': '20px', 'width': '100%'}),
            
            # Data Table
            html.Div([
                html.Div([
                    html.H3("Incident Details", style={'color': BLUE, 'display': 'inline-block', 'marginRight': '20px'}),
                    html.Span(id='table-count', style={'color': '#666', 'fontSize': '16px'})
                ]),
                html.Div(id='table-incidents', style={'overflowX': 'auto', 'maxHeight': '600px', 'overflowY': 'auto'})
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
            
            # Service Analysis Table (Hierarchical)
            html.Div([
                html.H3("Service Analysis: Root Causes, Mitigations & Impacts by Team", style={'color': BLUE}),
                dcc.Loading(
                    id="loading-service",
                    type="circle",
                    children=html.Div(id='table-service-analysis', style={'overflowX': 'auto', 'maxHeight': '600px', 'overflowY': 'auto'})
                )
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
            
            # Pattern Analysis Section (New)
            html.Div([
                html.H3("Pattern & Correlation Analysis", style={'color': BLUE, 'marginBottom': '20px'}),
                dcc.Loading(
                    id="loading-pattern",
                    type="circle",
                    children=html.Div(id='pattern-analysis', style={'overflowX': 'auto'})
                )
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
            
            # Data Dictionary Section
            html.Div([
                html.H3("📖 Data Dictionary", style={'color': BLUE, 'marginBottom': '20px'}),
                
                # Root Cause Themes
                html.Div([
                    html.H4("Root Cause Themes", style={'color': BLUE, 'fontSize': '16px', 'marginBottom': '10px', 'marginTop': '0'}),
                    html.Table([
                        html.Tbody([
                            html.Tr([
                                html.Td("Connectivity", style={'padding': '8px', 'fontWeight': 'bold', 'width': '180px', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Issues related to network connections, endpoints becoming unreachable, connection timeouts, or network infrastructure failures", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Configuration", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Problems caused by incorrect settings, misconfigurations, configuration drift, or missing configuration parameters", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Capacity", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Resource exhaustion including memory limits, CPU constraints, throttling, or insufficient scaling to handle load", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Deployment", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Issues introduced during software deployments, rollouts, releases, or code changes that caused service degradation", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Certificate", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Certificate expiration, invalid certificates, SSL/TLS handshake failures, or authentication certificate issues", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Timeout", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Request timeouts, operation timeouts, slow performance leading to timeout errors, or latency-related failures", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Dependency", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top'}),
                                html.Td("Failures in dependent services, downstream/upstream service issues, or cascading failures from external dependencies", 
                                       style={'padding': '8px'})
                            ])
                        ])
                    ], style={'width': '100%', 'marginBottom': '25px', 'backgroundColor': 'white', 'border': '1px solid #eee'})
                ]),
                
                # Mitigation Actions
                html.Div([
                    html.H4("Mitigation Actions", style={'color': BLUE, 'fontSize': '16px', 'marginBottom': '10px'}),
                    html.Table([
                        html.Tbody([
                            html.Tr([
                                html.Td("Restart/Reboot", style={'padding': '8px', 'fontWeight': 'bold', 'width': '180px', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Restarting services, rebooting servers, recycling application pools, or bouncing processes to clear state and recover", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Rollback", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Reverting to a previous known-good version of code, configuration, or deployment to undo problematic changes", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Scaling", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Adding more resources by scaling up (vertical) or scaling out (horizontal) to handle increased load or resource demands", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Failover", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Switching to backup systems, redirecting traffic to healthy instances, or failing over to secondary regions/datacenters", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Config Change", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top', 'borderBottom': '1px solid #eee'}),
                                html.Td("Modifying configuration settings, updating parameters, adjusting thresholds, or reconfiguring services to resolve issues", 
                                       style={'padding': '8px', 'borderBottom': '1px solid #eee'})
                            ]),
                            html.Tr([
                                html.Td("Traffic Mgmt", style={'padding': '8px', 'fontWeight': 'bold', 'verticalAlign': 'top'}),
                                html.Td("Throttling requests, implementing rate limits, blocking problematic traffic, or managing load distribution to protect services", 
                                       style={'padding': '8px'})
                            ])
                        ])
                    ], style={'width': '100%', 'backgroundColor': 'white', 'border': '1px solid #eee'})
                ])
            ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                     'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'})
            
        ], style={'flex': '1', 'padding': '20px', 'minWidth': '0',
                 'backgroundColor': GRAY_BG, 'minHeight': '100vh', 'overflowX': 'hidden'})
    ], style={'display': 'flex'})
], style={'fontFamily': 'Segoe UI, sans-serif'})

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('card-total', 'children'), Output('card-p75', 'children'),
     Output('card-mean', 'children'), Output('card-p90', 'children'),
     Output('card-critsit', 'children'),
     Output('chart-dist', 'figure'), Output('chart-services', 'figure'),
     Output('chart-timeline', 'figure'), Output('chart-severity', 'figure'),
     Output('chart-quintile', 'figure'), Output('chart-region', 'figure'),
     Output('table-incidents', 'children'), Output('table-count', 'children'),
     Output('table-service-analysis', 'children'), Output('pattern-analysis', 'children'),
     Output('chart-filter-banner', 'children'), Output('chart-click-store', 'data')],
    [Input('start-date-filter', 'date'), Input('end-date-filter', 'date'),
     Input('exclude-cascade-filter', 'value'), Input('exclude-bcdr-filter', 'value'),
     Input('severity-filter', 'value'), Input('service-filter', 'value'), 
     Input('ttm-filter', 'value'), Input('quintile-filter', 'value'), 
     Input('critsit-filter', 'value'), Input('p70p80-filter', 'value'), 
     Input('event-filter', 'value'), Input('reset-btn', 'n_clicks'),
     Input('clear-chart-btn', 'n_clicks'),
     Input('chart-severity', 'clickData'), Input('chart-services', 'clickData'),
     Input('chart-quintile', 'clickData'), Input('chart-region', 'clickData'),
     Input('chart-timeline', 'clickData')],
    prevent_initial_call=False
)
def update_all(start_date, end_date, exclude_cascade, exclude_bcdr, severities, services, 
               ttm_range, quintiles, critsit, p70p80, event, reset, clear_chart,
               severity_click, services_click, quintile_click, region_click, timeline_click):
    
    # Determine which input triggered the callback
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Initialize chart filter storage
    chart_filters = {}
    chart_filter_labels = []
    
    # Handle "Clear Chart Filters" button
    if triggered_id == 'clear-chart-btn':
        severity_click = None
        services_click = None
        quintile_click = None
        region_click = None
        timeline_click = None
    
    # Process chart clicks to extract filter values
    if severity_click and triggered_id == 'chart-severity':
        clicked_severity = severity_click['points'][0]['label']
        chart_filters['severity'] = clicked_severity
        chart_filter_labels.append(f"📊 Severity: {clicked_severity}")
    
    if services_click and triggered_id == 'chart-services':
        clicked_service = services_click['points'][0]['label']
        chart_filters['service'] = clicked_service
        chart_filter_labels.append(f"📊 Service: {clicked_service}")
    
    if quintile_click and triggered_id == 'chart-quintile':
        clicked_quintile = quintile_click['points'][0]['label']
        chart_filters['quintile'] = clicked_quintile
        chart_filter_labels.append(f"📊 Quintile: {clicked_quintile}")
    
    if region_click and triggered_id == 'chart-region':
        clicked_region = region_click['points'][0]['label']
        chart_filters['region'] = clicked_region
        chart_filter_labels.append(f"📊 Region: {clicked_region}")
    
    if timeline_click and triggered_id == 'chart-timeline':
        clicked_date = timeline_click['points'][0]['x']
        chart_filters['date'] = clicked_date
        chart_filter_labels.append(f"📊 Date: {clicked_date}")
    
    # Create banner for active chart filters
    if chart_filter_labels:
        banner = html.Div([
            html.Span("🎯 Active Chart Filters: ", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            html.Span(' | '.join(chart_filter_labels), style={'color': BLUE}),
            html.Span(" (Click 'Clear Chart Filters' to remove)", 
                     style={'marginLeft': '10px', 'fontSize': '12px', 'fontStyle': 'italic', 'color': '#666'})
        ], style={'backgroundColor': '#FFF4CE', 'padding': '12px', 'borderRadius': '6px',
                 'border': '2px solid #FFD700', 'marginBottom': '10px'})
    else:
        banner = html.Div()
    
    # Filter
    fdf = df.copy()
    
    # Apply chart filters FIRST (before other filters)
    if 'severity' in chart_filters and 'Severity' in fdf.columns:
        fdf = fdf[fdf['Severity'] == chart_filters['severity']]
    
    if 'service' in chart_filters and 'ServiceName' in fdf.columns:
        fdf = fdf[fdf['ServiceName'] == chart_filters['service']]
    
    if 'quintile' in chart_filters and 'TTM_Quintile' in fdf.columns:
        fdf = fdf[fdf['TTM_Quintile'] == chart_filters['quintile']]
    
    if 'region' in chart_filters and 'Region' in fdf.columns:
        fdf = fdf[fdf['Region'] == chart_filters['region']]
    
    if 'date' in chart_filters and 'Date' in fdf.columns:
        clicked_date_obj = pd.to_datetime(chart_filters['date']).date()
        fdf = fdf[fdf['Date'] == clicked_date_obj]
    
    # Date range filter with timezone handling
    try:
        if start_date and 'CreateDate' in fdf.columns:
            start_dt = pd.to_datetime(start_date)
            # Make timezone aware if the column is timezone aware
            if fdf['CreateDate'].dt.tz is not None:
                start_dt = start_dt.tz_localize('UTC')
            fdf = fdf[fdf['CreateDate'] >= start_dt]
        
        if end_date and 'CreateDate' in fdf.columns:
            end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            # Make timezone aware if the column is timezone aware
            if fdf['CreateDate'].dt.tz is not None:
                end_dt = end_dt.tz_localize('UTC')
            fdf = fdf[fdf['CreateDate'] <= end_dt]
    except Exception as e:
        print(f"Date filter error: {e}")
    
    # Exclude cascade (events with multiple incidents)
    if exclude_cascade and 'exclude' in exclude_cascade and 'IsPartOfEvent' in fdf.columns:
        fdf = fdf[fdf['IsPartOfEvent'] == False]
    
    # Exclude BCDR/EUAP
    if exclude_bcdr and 'exclude' in exclude_bcdr and 'IsExcluded' in fdf.columns:
        fdf = fdf[fdf['IsExcluded'] == False]
    
    if severities:
        fdf = fdf[fdf['Severity'].isin(severities)]
    if services:
        fdf = fdf[fdf['Service'].isin(services)]
    if ttm_range and 'TTM' in fdf.columns:
        fdf = fdf[(fdf['TTM'] >= ttm_range[0]) & (fdf['TTM'] <= ttm_range[1])]
    if quintiles and 'TTM_Quintile' in fdf.columns:
        fdf = fdf[fdf['TTM_Quintile'].isin(quintiles)]
    if critsit != 'All' and 'CritSit' in fdf.columns:
        fdf = fdf[fdf['CritSit'] == critsit]
    if p70p80 and 'IsP70P80' in fdf.columns:
        fdf = fdf[fdf['IsP70P80'] == True]
    if event != 'All' and 'OutageCorrelationId' in fdf.columns:
        fdf = fdf[fdf['OutageCorrelationId'] == event]
    
    # Metrics
    total = len(fdf)
    p75 = f"{int(fdf['TTM'].quantile(0.75))} min" if total > 0 and 'TTM' in fdf.columns else "N/A"
    mean = f"{int(fdf['TTM'].mean())} min" if total > 0 and 'TTM' in fdf.columns else "N/A"
    p90 = f"{int(fdf['TTM'].quantile(0.90))} min" if total > 0 and 'TTM' in fdf.columns else "N/A"
    critsits = int(fdf['CritSit'].sum()) if 'CritSit' in fdf.columns and total > 0 else 0
    
    # Charts with error handling
    try:
        if total > 0 and 'TTM' in fdf.columns:
            fig_dist = px.histogram(fdf, x='TTM', nbins=50, title='TTM Distribution')
            fig_dist.update_layout(
                showlegend=False, 
                plot_bgcolor='white',
                margin=dict(l=40, r=20, t=40, b=40),
                height=300
            )
        else:
            fig_dist = go.Figure().update_layout(title='TTM Distribution (No Data)', height=300)
    except Exception as e:
        fig_dist = go.Figure().update_layout(title=f'TTM Distribution (Error: {str(e)[:30]})')
    
    try:
        if total > 0 and 'Service' in fdf.columns and 'TTM' in fdf.columns:
            top_svc = fdf.groupby('Service')['TTM'].sum().nlargest(10).reset_index()
            if len(top_svc) > 0:
                fig_services = px.bar(top_svc, x='TTM', y='Service', orientation='h',
                                     title='Top 10 Services by Total TTM')
                fig_services.update_layout(yaxis={'categoryorder': 'total ascending'})
            else:
                fig_services = go.Figure().update_layout(title='Top Services (No Data)')
        else:
            fig_services = go.Figure().update_layout(title='Top Services (No Data)')
    except Exception as e:
        fig_services = go.Figure().update_layout(title=f'Top Services (Error: {str(e)[:30]})')
    
    try:
        if total > 0 and 'Date' in fdf.columns:
            daily = fdf.groupby('Date').size().reset_index(name='Count')
            fig_timeline = px.bar(daily, x='Date', y='Count', title='Daily Timeline')
        else:
            fig_timeline = go.Figure().update_layout(title='Timeline (No Data)')
    except Exception as e:
        fig_timeline = go.Figure().update_layout(title=f'Timeline (Error: {str(e)[:30]})')
    
    try:
        if total > 0 and 'Severity' in fdf.columns:
            sev_counts = fdf['Severity'].value_counts().reset_index()
            sev_counts.columns = ['Severity', 'Count']
            fig_severity = px.pie(sev_counts, values='Count', names='Severity', title='By Severity')
        else:
            fig_severity = go.Figure().update_layout(title='Severity (No Data)')
    except Exception as e:
        fig_severity = go.Figure().update_layout(title=f'Severity (Error: {str(e)[:30]})')
    
    try:
        if total > 0 and 'TTM_Quintile' in fdf.columns:
            quint = fdf.groupby('TTM_Quintile').size().reset_index(name='Count')
            fig_quintile = px.bar(quint, x='TTM_Quintile', y='Count', title='By Quintile')
        else:
            fig_quintile = go.Figure().update_layout(title='Quintile (No Data)')
    except Exception as e:
        fig_quintile = go.Figure().update_layout(title=f'Quintile (Error: {str(e)[:30]})')
    
    try:
        if total > 0 and 'Region' in fdf.columns:
            reg_top = fdf['Region'].value_counts().nlargest(10).reset_index()
            reg_top.columns = ['Region', 'Count']
            if len(reg_top) > 0:
                fig_region = px.bar(reg_top, x='Count', y='Region', orientation='h', title='Top 10 Regions')
                fig_region.update_layout(yaxis={'categoryorder': 'total ascending'})
            else:
                fig_region = go.Figure().update_layout(title='Regions (No Data)')
        else:
            fig_region = go.Figure().update_layout(title='Regions (No Data)')
    except Exception as e:
        fig_region = go.Figure().update_layout(title=f'Regions (Error: {str(e)[:30]})')
    
    # Table with all incidents and high-entropy columns
    table_count_text = f"Showing all {total} incidents" if total > 0 else "No incidents"
    
    try:
        if total > 0:
            # Use high-entropy columns that exist in the dataframe
            display_cols = [c for c in TABLE_COLUMNS if c in fdf.columns]
            tdf = fdf[display_cols].copy()
            
            # Round TTM to 1 decimal place for readability
            if 'TTM' in tdf.columns:
                tdf['TTM'] = tdf['TTM'].round(1)
            
            # Truncate long text fields
            for col in ['IncidentTitle', 'RootCauses', 'Mitigations', 'Impacts']:
                if col in tdf.columns:
                    tdf[col] = tdf[col].apply(lambda x: str(x)[:100] + '...' if pd.notna(x) and len(str(x)) > 100 else str(x) if pd.notna(x) else '')
            
            # Sort by TTM descending
            if 'TTM' in tdf.columns:
                tdf = tdf.sort_values('TTM', ascending=False)
            
            table = html.Table([
                html.Thead(html.Tr([html.Th(c, style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}',
                                                      'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                                      'fontSize': '12px', 'whiteSpace': 'nowrap'}) 
                                   for c in tdf.columns])),
                html.Tbody([html.Tr([html.Td(str(row[c]) if pd.notna(row[c]) else '', 
                                             style={'padding': '6px', 'borderBottom': f'1px solid {BORDER}',
                                                   'fontSize': '11px', 'maxWidth': '300px', 'overflow': 'hidden',
                                                   'textOverflow': 'ellipsis'}) 
                                    for c in tdf.columns]) 
                           for _, row in tdf.iterrows()])
            ], style={'width': '100%', 'borderCollapse': 'collapse'})
        else:
            table = html.Div("No incidents match the current filters", 
                           style={'padding': '20px', 'textAlign': 'center', 'color': '#666'})
    except Exception as e:
        table = html.Div(f"Error loading table: {str(e)}", 
                        style={'padding': '20px', 'textAlign': 'center', 'color': 'red'})
        table_count_text = "Error"
    
    # Service Analysis Table (Hierarchical: Service > Team > Root Causes/Mitigations/Impacts)
    try:
        if total > 0 and 'ServiceName' in fdf.columns:
            # Create all-up summary across all services
            summary_sections = []
            
            # Root Causes All-Up Summary
            if 'RootCauses' in fdf.columns and 'OutageIncidentId' in fdf.columns:
                rc_all_data = fdf[['OutageIncidentId', 'RootCauses']].dropna(subset=['RootCauses'])
                if len(rc_all_data) > 0:
                    unique_rcs_all = rc_all_data['RootCauses'].unique()
                    all_text = ' '.join([str(rc).lower() for rc in unique_rcs_all])
                    
                    # Calculate additional statistics
                    event_count = fdf[fdf['IsPartOfEvent'] == True]['OutageIncidentId'].nunique() if 'IsPartOfEvent' in fdf.columns else 0
                    change_count = fdf[fdf['IsCausedByChange'] == 1]['OutageIncidentId'].nunique() if 'IsCausedByChange' in fdf.columns else 0
                    critsit_count = fdf[fdf['IsCritSit'] == 'Yes']['OutageIncidentId'].nunique() if 'IsCritSit' in fdf.columns else 0
                    
                    # Identify themes across all services
                    themes = []
                    theme_keywords = {
                        'connectivity': ['connectivity', 'connection', 'network', 'endpoint'],
                        'configuration': ['configuration', 'config', 'misconfiguration', 'setting'],
                        'capacity': ['capacity', 'resource exhaustion', 'memory', 'cpu', 'throttling'],
                        'deployment': ['deployment', 'rollout', 'release', 'code change'],
                        'certificate': ['certificate', 'cert', 'ssl', 'tls', 'authentication'],
                        'timeout': ['timeout', 'timed out', 'latency', 'slow'],
                        'failure': ['failure', 'failed', 'error', 'exception'],
                        'dependency': ['dependency', 'dependent', 'downstream', 'upstream']
                    }
                    
                    for theme, keywords in theme_keywords.items():
                        if any(kw in all_text for kw in keywords):
                            themes.append(theme)
                    
                    themes_str = ', '.join(themes) if themes else 'various issues'
                    rc_summary_text = f"📊 Across all services, {len(rc_all_data)} incidents occurred with {len(unique_rcs_all)} distinct root causes, primarily related to {themes_str}."
                    
                    # Add statistics breakdown
                    stats_text = f"• {event_count} incidents were part of cascading events | {change_count} were caused by changes | {critsit_count} were CritSit incidents"
                    
                    summary_sections.append(html.Div([
                        html.H4('Root Causes Overview', style={'color': BLUE, 'marginTop': '0', 'marginBottom': '8px', 'fontSize': '14px'}),
                        html.P(rc_summary_text, style={'fontSize': '12px', 'lineHeight': '1.6', 'margin': '0 0 8px 0'}),
                        html.P(stats_text, style={'fontSize': '11px', 'lineHeight': '1.6', 'margin': '0', 'color': '#666', 'fontStyle': 'italic'})
                    ], style={'marginBottom': '15px'}))
            
            # Mitigations All-Up Summary
            if 'Mitigations' in fdf.columns and 'OutageIncidentId' in fdf.columns:
                mit_all_data = fdf[['OutageIncidentId', 'Mitigations']].dropna(subset=['Mitigations'])
                if len(mit_all_data) > 0:
                    unique_mits_all = mit_all_data['Mitigations'].unique()
                    all_text = ' '.join([str(m).lower() for m in unique_mits_all])
                    
                    # Identify actions across all services
                    actions = []
                    action_keywords = {
                        'restart/reboot': ['restart', 'reboot', 'recycle', 'bounce'],
                        'rollback': ['rollback', 'rolled back', 'reverted', 'revert'],
                        'scaling': ['scale', 'scaled', 'scaling', 'capacity increase'],
                        'failover': ['failover', 'failed over', 'switched', 'redirected'],
                        'configuration change': ['config change', 'reconfigured', 'updated settings'],
                        'traffic management': ['traffic', 'throttle', 'rate limit', 'blocked'],
                        'repair': ['repair', 'fixed', 'patched', 'resolved'],
                        'isolation': ['isolated', 'quarantine', 'disabled', 'removed']
                    }
                    
                    for action, keywords in action_keywords.items():
                        if any(kw in all_text for kw in keywords):
                            actions.append(action)
                    
                    # Calculate TTM statistics
                    avg_ttm = fdf['TTM'].mean() if 'TTM' in fdf.columns else 0
                    median_ttm = fdf['TTM'].median() if 'TTM' in fdf.columns else 0
                    
                    actions_str = ', '.join(actions) if actions else 'various actions'
                    mit_summary_text = f"🔧 Teams applied {len(unique_mits_all)} distinct mitigations across {len(mit_all_data)} incidents, including {actions_str}."
                    
                    # Add TTM statistics
                    ttm_stats_text = f"• Average TTM: {avg_ttm:.0f} minutes | Median TTM: {median_ttm:.0f} minutes"
                    
                    summary_sections.append(html.Div([
                        html.H4('Mitigations Overview', style={'color': BLUE, 'marginTop': '0', 'marginBottom': '8px', 'fontSize': '14px'}),
                        html.P(mit_summary_text, style={'fontSize': '12px', 'lineHeight': '1.6', 'margin': '0 0 8px 0'}),
                        html.P(ttm_stats_text, style={'fontSize': '11px', 'lineHeight': '1.6', 'margin': '0', 'color': '#666', 'fontStyle': 'italic'})
                    ], style={'marginBottom': '15px'}))
            
            # Impacts All-Up Summary
            if 'Impacts' in fdf.columns and 'OutageIncidentId' in fdf.columns:
                imp_all_data = fdf[['OutageIncidentId', 'Impacts']].dropna(subset=['Impacts'])
                if len(imp_all_data) > 0:
                    unique_imps_all = imp_all_data['Impacts'].unique()
                    all_text = ' '.join([str(i).lower() for i in unique_imps_all])
                    
                    # Identify impact types across all services
                    impact_types = []
                    impact_keywords = {
                        'availability': ['availability', 'downtime', 'unavailable', 'outage'],
                        'performance degradation': ['degradation', 'slow', 'latency', 'delay'],
                        'customer impact': ['customer', 'user', 'client', 'tenant'],
                        'data issues': ['data', 'data loss', 'corruption', 'inconsistency'],
                        'API failures': ['api', 'endpoint', 'request', 'call'],
                        'authentication': ['authentication', 'login', 'access', 'authorization'],
                        'service errors': ['error', 'failure', 'failed', 'exception'],
                        'regional impact': ['region', 'regional', 'geography', 'geo']
                    }
                    
                    for impact_type, keywords in impact_keywords.items():
                        if any(kw in all_text for kw in keywords):
                            impact_types.append(impact_type)
                    
                    # Calculate severity breakdown
                    severity_counts = fdf['Severity'].value_counts().to_dict() if 'Severity' in fdf.columns else {}
                    severity_text = ' | '.join([f"{k}: {v}" for k, v in sorted(severity_counts.items())])
                    
                    impacts_str = ', '.join(impact_types) if impact_types else 'various areas'
                    imp_summary_text = f"⚠️ These incidents resulted in {len(unique_imps_all)} distinct impact types across {len(imp_all_data)} incidents, affecting {impacts_str}."
                    
                    # Add severity breakdown
                    severity_stats_text = f"• Severity breakdown: {severity_text}" if severity_text else "• Severity data not available"
                    
                    summary_sections.append(html.Div([
                        html.H4('Impacts Overview', style={'color': BLUE, 'marginTop': '0', 'marginBottom': '8px', 'fontSize': '14px'}),
                        html.P(imp_summary_text, style={'fontSize': '12px', 'lineHeight': '1.6', 'margin': '0 0 8px 0'}),
                        html.P(severity_stats_text, style={'fontSize': '11px', 'lineHeight': '1.6', 'margin': '0', 'color': '#666', 'fontStyle': 'italic'})
                    ], style={'marginBottom': '15px'}))
            
            # Add legend for symbols
            summary_sections.append(html.Div([
                html.Hr(style={'margin': '10px 0', 'border': 'none', 'borderTop': f'1px solid {BLUE}'}),
                html.P([
                    html.Strong('Legend: ', style={'fontSize': '11px'}),
                    html.Span('🔗 Part of cascading event  ', style={'fontSize': '11px', 'marginRight': '10px'}),
                    html.Span('🔄 Caused by change', style={'fontSize': '11px'})
                ], style={'margin': '5px 0 0 0', 'fontSize': '11px', 'color': '#666'})
            ]))
            
            # Create the all-up summary box
            all_up_summary = html.Div(
                summary_sections,
                style={
                    'backgroundColor': '#FFF9E6',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'border': f'2px solid {BLUE}',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }
            )
            
            service_rows = []
            
            # Group by Service
            for service in sorted(fdf['ServiceName'].dropna().unique()):
                svc_df = fdf[fdf['ServiceName'] == service]
                svc_incidents = len(svc_df)
                svc_ttm = svc_df['TTM'].mean() if 'TTM' in svc_df.columns else 0
                
                # Service header row (bold, larger)
                service_rows.append(html.Tr([
                    html.Td(service, colSpan=6, style={
                        'padding': '12px', 'backgroundColor': '#E1F5FE', 'fontWeight': 'bold',
                        'fontSize': '14px', 'borderBottom': f'2px solid {BLUE}'
                    })
                ]))
                
                # Group by Team within Service
                if 'OwningTeamName' in svc_df.columns:
                    for team in sorted(svc_df['OwningTeamName'].dropna().unique()):
                        team_df = svc_df[svc_df['OwningTeamName'] == team]
                        team_incidents = len(team_df)
                        team_ttm = team_df['TTM'].mean() if 'TTM' in team_df.columns else 0
                        
                        # Build detailed Root Causes breakdown
                        root_causes_content = []
                        if 'RootCauses' in team_df.columns and 'OutageIncidentId' in team_df.columns:
                            # Include additional columns for symbols
                            cols_to_select = ['OutageIncidentId', 'RootCauses']
                            if 'IsPartOfEvent' in team_df.columns:
                                cols_to_select.append('IsPartOfEvent')
                            if 'IsCausedByChange' in team_df.columns:
                                cols_to_select.append('IsCausedByChange')
                            
                            rc_data = team_df[cols_to_select].dropna(subset=['RootCauses'])
                            if len(rc_data) > 0:
                                # Extract key themes from root causes
                                unique_rcs = rc_data['RootCauses'].unique()
                                all_text = ' '.join([str(rc).lower() for rc in unique_rcs])
                                
                                # Identify common themes
                                themes = []
                                theme_keywords = {
                                    'connectivity': ['connectivity', 'connection', 'network', 'endpoint'],
                                    'configuration': ['configuration', 'config', 'misconfiguration', 'setting'],
                                    'capacity': ['capacity', 'resource exhaustion', 'memory', 'cpu', 'throttling'],
                                    'deployment': ['deployment', 'rollout', 'release', 'code change'],
                                    'certificate': ['certificate', 'cert', 'ssl', 'tls', 'authentication'],
                                    'timeout': ['timeout', 'timed out', 'latency', 'slow'],
                                    'failure': ['failure', 'failed', 'error', 'exception'],
                                    'dependency': ['dependency', 'dependent', 'downstream', 'upstream']
                                }
                                
                                for theme, keywords in theme_keywords.items():
                                    if any(kw in all_text for kw in keywords):
                                        themes.append(theme)
                                
                                # Create summary sentence with themes
                                rc_summary = f"This team experienced {len(rc_data)} incidents with {len(unique_rcs)} distinct root cause(s)"
                                if themes:
                                    themes_str = ', '.join(themes[:3])  # Limit to top 3 themes
                                    rc_summary += f", primarily related to {themes_str} issues."
                                else:
                                    rc_summary += "."
                                
                                root_causes_content.append(html.P(rc_summary, style={'margin': '0 0 8px 0', 'fontWeight': '500', 'fontSize': '11px'}))
                                
                                # List each root cause with incident IDs
                                for _, row in rc_data.iterrows():
                                    inc_id = row['OutageIncidentId']
                                    inc_url = f"https://portal.microsofticm.com/imp/v5/incidents/details/{inc_id}/summary"
                                    
                                    # Add symbols for Event and CausedByChange
                                    symbols = []
                                    if 'IsPartOfEvent' in row and row['IsPartOfEvent'] == True:
                                        symbols.append(html.Span('🔗', title='Part of cascading event', style={'marginLeft': '4px'}))
                                    if 'IsCausedByChange' in row and row['IsCausedByChange'] == 1:
                                        symbols.append(html.Span('🔄', title='Caused by change', style={'marginLeft': '4px'}))
                                    
                                    root_causes_content.append(html.Div([
                                        html.Span('• ', style={'color': BLUE, 'fontWeight': 'bold'}),
                                        html.A(f"[INC {inc_id}]", 
                                               href=inc_url, 
                                               target="_blank",
                                               style={'fontWeight': '600', 'color': BLUE, 'fontSize': '10px', 'textDecoration': 'none'}),
                                        *symbols,
                                        html.Span(": ", style={'fontWeight': '600', 'color': '#666', 'fontSize': '10px'}),
                                        html.Span(str(row['RootCauses']), style={'fontSize': '10px'})
                                    ], style={'marginLeft': '10px', 'marginBottom': '4px'}))
                        
                        if not root_causes_content:
                            root_causes_content = [html.P('N/A', style={'color': '#999', 'fontSize': '11px'})]
                        
                        # Build detailed Mitigations breakdown
                        mitigations_content = []
                        if 'Mitigations' in team_df.columns and 'OutageIncidentId' in team_df.columns:
                            # Include additional columns for symbols
                            cols_to_select = ['OutageIncidentId', 'Mitigations']
                            if 'IsPartOfEvent' in team_df.columns:
                                cols_to_select.append('IsPartOfEvent')
                            if 'IsCausedByChange' in team_df.columns:
                                cols_to_select.append('IsCausedByChange')
                            
                            mit_data = team_df[cols_to_select].dropna(subset=['Mitigations'])
                            if len(mit_data) > 0:
                                # Extract key themes from mitigations
                                unique_mits = mit_data['Mitigations'].unique()
                                all_text = ' '.join([str(m).lower() for m in unique_mits])
                                
                                # Identify common mitigation actions
                                actions = []
                                action_keywords = {
                                    'restart/reboot': ['restart', 'reboot', 'recycle', 'bounce'],
                                    'rollback': ['rollback', 'rolled back', 'reverted', 'revert'],
                                    'scaling': ['scale', 'scaled', 'scaling', 'capacity increase'],
                                    'failover': ['failover', 'failed over', 'switched', 'redirected'],
                                    'configuration change': ['config change', 'reconfigured', 'updated settings'],
                                    'traffic management': ['traffic', 'throttle', 'rate limit', 'blocked'],
                                    'repair': ['repair', 'fixed', 'patched', 'resolved'],
                                    'isolation': ['isolated', 'quarantine', 'disabled', 'removed']
                                }
                                
                                for action, keywords in action_keywords.items():
                                    if any(kw in all_text for kw in keywords):
                                        actions.append(action)
                                
                                # Create summary sentence with actions
                                mit_summary = f"This team applied {len(unique_mits)} distinct mitigation(s) across {len(mit_data)} incidents"
                                if actions:
                                    actions_str = ', '.join(actions[:3])  # Limit to top 3 actions
                                    mit_summary += f", including {actions_str}."
                                else:
                                    mit_summary += "."
                                
                                mitigations_content.append(html.P(mit_summary, style={'margin': '0 0 8px 0', 'fontWeight': '500', 'fontSize': '11px'}))
                                
                                # List each mitigation with incident IDs
                                for _, row in mit_data.iterrows():
                                    inc_id = row['OutageIncidentId']
                                    inc_url = f"https://portal.microsofticm.com/imp/v5/incidents/details/{inc_id}/summary"
                                    
                                    # Add symbols for Event and CausedByChange
                                    symbols = []
                                    if 'IsPartOfEvent' in row and row['IsPartOfEvent'] == True:
                                        symbols.append(html.Span('🔗', title='Part of cascading event', style={'marginLeft': '4px'}))
                                    if 'IsCausedByChange' in row and row['IsCausedByChange'] == 1:
                                        symbols.append(html.Span('🔄', title='Caused by change', style={'marginLeft': '4px'}))
                                    
                                    mitigations_content.append(html.Div([
                                        html.Span('• ', style={'color': BLUE, 'fontWeight': 'bold'}),
                                        html.A(f"[INC {inc_id}]", 
                                               href=inc_url, 
                                               target="_blank",
                                               style={'fontWeight': '600', 'color': BLUE, 'fontSize': '10px', 'textDecoration': 'none'}),
                                        *symbols,
                                        html.Span(": ", style={'fontWeight': '600', 'color': '#666', 'fontSize': '10px'}),
                                        html.Span(str(row['Mitigations']), style={'fontSize': '10px'})
                                    ], style={'marginLeft': '10px', 'marginBottom': '4px'}))
                        
                        if not mitigations_content:
                            mitigations_content = [html.P('N/A', style={'color': '#999', 'fontSize': '11px'})]
                        
                        # Build detailed Impacts breakdown
                        impacts_content = []
                        if 'Impacts' in team_df.columns and 'OutageIncidentId' in team_df.columns:
                            # Include additional columns for symbols
                            cols_to_select = ['OutageIncidentId', 'Impacts']
                            if 'IsPartOfEvent' in team_df.columns:
                                cols_to_select.append('IsPartOfEvent')
                            if 'IsCausedByChange' in team_df.columns:
                                cols_to_select.append('IsCausedByChange')
                            
                            imp_data = team_df[cols_to_select].dropna(subset=['Impacts'])
                            if len(imp_data) > 0:
                                # Extract key themes from impacts
                                unique_imps = imp_data['Impacts'].unique()
                                all_text = ' '.join([str(i).lower() for i in unique_imps])
                                
                                # Identify common impact types
                                impact_types = []
                                impact_keywords = {
                                    'availability': ['availability', 'downtime', 'unavailable', 'outage'],
                                    'performance degradation': ['degradation', 'slow', 'latency', 'delay'],
                                    'customer impact': ['customer', 'user', 'client', 'tenant'],
                                    'data issues': ['data', 'data loss', 'corruption', 'inconsistency'],
                                    'API failures': ['api', 'endpoint', 'request', 'call'],
                                    'authentication': ['authentication', 'login', 'access', 'authorization'],
                                    'service errors': ['error', 'failure', 'failed', 'exception'],
                                    'regional impact': ['region', 'regional', 'geography', 'geo']
                                }
                                
                                for impact_type, keywords in impact_keywords.items():
                                    if any(kw in all_text for kw in keywords):
                                        impact_types.append(impact_type)
                                
                                # Create summary sentence with impact types
                                imp_summary = f"This team's incidents resulted in {len(unique_imps)} distinct impact(s) across {len(imp_data)} incidents"
                                if impact_types:
                                    impacts_str = ', '.join(impact_types[:3])  # Limit to top 3 impact types
                                    imp_summary += f", affecting {impacts_str}."
                                else:
                                    imp_summary += "."
                                
                                impacts_content.append(html.P(imp_summary, style={'margin': '0 0 8px 0', 'fontWeight': '500', 'fontSize': '11px'}))
                                
                                # List each impact with incident IDs
                                for _, row in imp_data.iterrows():
                                    inc_id = row['OutageIncidentId']
                                    inc_url = f"https://portal.microsofticm.com/imp/v5/incidents/details/{inc_id}/summary"
                                    
                                    # Add symbols for Event and CausedByChange
                                    symbols = []
                                    if 'IsPartOfEvent' in row and row['IsPartOfEvent'] == True:
                                        symbols.append(html.Span('🔗', title='Part of cascading event', style={'marginLeft': '4px'}))
                                    if 'IsCausedByChange' in row and row['IsCausedByChange'] == 1:
                                        symbols.append(html.Span('🔄', title='Caused by change', style={'marginLeft': '4px'}))
                                    
                                    impacts_content.append(html.Div([
                                        html.Span('• ', style={'color': BLUE, 'fontWeight': 'bold'}),
                                        html.A(f"[INC {inc_id}]", 
                                               href=inc_url, 
                                               target="_blank",
                                               style={'fontWeight': '600', 'color': BLUE, 'fontSize': '10px', 'textDecoration': 'none'}),
                                        *symbols,
                                        html.Span(": ", style={'fontWeight': '600', 'color': '#666', 'fontSize': '10px'}),
                                        html.Span(str(row['Impacts']), style={'fontSize': '10px'})
                                    ], style={'marginLeft': '10px', 'marginBottom': '4px'}))
                        
                        if not impacts_content:
                            impacts_content = [html.P('N/A', style={'color': '#999', 'fontSize': '11px'})]
                                                
                        if not impacts_content:
                            impacts_content = [html.P('N/A', style={'color': '#999', 'fontSize': '11px'})]
                        
                        # Team row
                        service_rows.append(html.Tr([
                            html.Td(f'  └─ {team}', style={
                                'padding': '8px', 'fontWeight': '500', 'fontSize': '12px',
                                'borderBottom': f'1px solid {BORDER}', 'width': '15%',
                                'verticalAlign': 'top'
                            }),
                            html.Td(f'{team_incidents} incidents', style={
                                'padding': '8px', 'fontSize': '11px',
                                'borderBottom': f'1px solid {BORDER}', 'width': '10%',
                                'verticalAlign': 'top'
                            }),
                            html.Td(f'{team_ttm:.0f} min avg', style={
                                'padding': '8px', 'fontSize': '11px',
                                'borderBottom': f'1px solid {BORDER}', 'width': '10%',
                                'verticalAlign': 'top'
                            }),
                            html.Td(html.Div(root_causes_content), style={
                                'padding': '8px', 'fontSize': '11px',
                                'borderBottom': f'1px solid {BORDER}', 'width': '25%',
                                'verticalAlign': 'top'
                            }),
                            html.Td(html.Div(mitigations_content), style={
                                'padding': '8px', 'fontSize': '11px',
                                'borderBottom': f'1px solid {BORDER}', 'width': '20%',
                                'verticalAlign': 'top'
                            }),
                            html.Td(html.Div(impacts_content), style={
                                'padding': '8px', 'fontSize': '11px',
                                'borderBottom': f'1px solid {BORDER}', 'width': '20%',
                                'verticalAlign': 'top'
                            })
                        ]))
            
            # Build correlation analysis at the bottom
            correlation_sections = []
            
            # Analyze Root Cause patterns
            if 'RootCauses' in fdf.columns and len(fdf) > 0:
                # Extract common root cause themes
                rc_theme_mapping = {
                    'Connectivity': ['connectivity', 'connection', 'network', 'endpoint'],
                    'Configuration': ['configuration', 'config', 'misconfiguration'],
                    'Capacity': ['capacity', 'resource exhaustion', 'memory', 'throttling'],
                    'Deployment': ['deployment', 'rollout', 'release'],
                    'Certificate': ['certificate', 'cert', 'ssl', 'tls'],
                    'Timeout': ['timeout', 'timed out', 'latency'],
                    'Dependency': ['dependency', 'dependent', 'downstream']
                }
                
                rc_stats = []
                for theme, keywords in rc_theme_mapping.items():
                    # Find incidents matching this theme
                    mask = fdf['RootCauses'].fillna('').str.lower().apply(
                        lambda x: any(kw in x for kw in keywords)
                    )
                    theme_df = fdf[mask]
                    
                    if len(theme_df) > 0:
                        p75_ttm = theme_df['TTM'].quantile(0.75) if 'TTM' in theme_df.columns else 0
                        incident_count = len(theme_df)
                        service_count = theme_df['ServiceName'].nunique() if 'ServiceName' in theme_df.columns else 0
                        severity_counts = theme_df['Severity'].value_counts().to_dict() if 'Severity' in theme_df.columns else {}
                        
                        rc_stats.append({
                            'theme': theme,
                            'p75': p75_ttm,
                            'count': incident_count,
                            'services': service_count,
                            'severity': severity_counts
                        })
                
                if rc_stats:
                    # Sort by P75 TTM descending
                    rc_stats.sort(key=lambda x: x['p75'], reverse=True)
                    
                    rc_rows = []
                    for stat in rc_stats[:5]:  # Top 5
                        sev_text = ', '.join([f"{k}:{v}" for k, v in sorted(stat['severity'].items())])
                        rc_rows.append(html.Tr([
                            html.Td(stat['theme'], style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(f"{stat['p75']:.0f} min", style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold', 'color': BLUE}),
                            html.Td(str(stat['count']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(str(stat['services']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(sev_text, style={'padding': '8px', 'fontSize': '10px', 'borderBottom': '1px solid #eee'})
                        ]))
                    
                    correlation_sections.append(html.Div([
                        html.H4('Root Cause Pattern Analysis', style={'color': BLUE, 'marginTop': '20px', 'marginBottom': '10px', 'fontSize': '14px'}),
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th('Root Cause Theme', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold', 'textAlign': 'left'}),
                                html.Th('P75 TTM', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Incidents', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Services', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Severity Breakdown', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ])),
                            html.Tbody(rc_rows)
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
                    ]))
            
            # Analyze Mitigation effectiveness
            if 'Mitigations' in fdf.columns and len(fdf) > 0:
                mit_action_mapping = {
                    'Restart/Reboot': ['restart', 'reboot', 'recycle'],
                    'Rollback': ['rollback', 'rolled back', 'reverted'],
                    'Scaling': ['scale', 'scaled', 'scaling'],
                    'Failover': ['failover', 'failed over', 'switched'],
                    'Config Change': ['config change', 'reconfigured'],
                    'Traffic Mgmt': ['throttle', 'rate limit', 'blocked']
                }
                
                mit_stats = []
                for action, keywords in mit_action_mapping.items():
                    mask = fdf['Mitigations'].fillna('').str.lower().apply(
                        lambda x: any(kw in x for kw in keywords)
                    )
                    action_df = fdf[mask]
                    
                    if len(action_df) > 0:
                        p75_ttm = action_df['TTM'].quantile(0.75) if 'TTM' in action_df.columns else 0
                        incident_count = len(action_df)
                        service_count = action_df['ServiceName'].nunique() if 'ServiceName' in action_df.columns else 0
                        severity_counts = action_df['Severity'].value_counts().to_dict() if 'Severity' in action_df.columns else {}
                        
                        mit_stats.append({
                            'action': action,
                            'p75': p75_ttm,
                            'count': incident_count,
                            'services': service_count,
                            'severity': severity_counts
                        })
                
                if mit_stats:
                    # Sort by incident count descending
                    mit_stats.sort(key=lambda x: x['count'], reverse=True)
                    
                    mit_rows = []
                    for stat in mit_stats[:5]:  # Top 5
                        sev_text = ', '.join([f"{k}:{v}" for k, v in sorted(stat['severity'].items())])
                        mit_rows.append(html.Tr([
                            html.Td(stat['action'], style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(f"{stat['p75']:.0f} min", style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold', 'color': BLUE}),
                            html.Td(str(stat['count']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(str(stat['services']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(sev_text, style={'padding': '8px', 'fontSize': '10px', 'borderBottom': '1px solid #eee'})
                        ]))
                    
                    correlation_sections.append(html.Div([
                        html.H4('Mitigation Effectiveness Analysis', style={'color': BLUE, 'marginTop': '20px', 'marginBottom': '10px', 'fontSize': '14px'}),
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th('Mitigation Action', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold', 'textAlign': 'left'}),
                                html.Th('P75 TTM', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Incidents', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Services', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Severity Breakdown', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ])),
                            html.Tbody(mit_rows)
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
                    ]))
            
            # Analyze Impact patterns
            if 'Impacts' in fdf.columns and len(fdf) > 0:
                impact_type_mapping = {
                    'Availability': ['availability', 'downtime', 'unavailable'],
                    'Performance': ['degradation', 'slow', 'latency'],
                    'Customer': ['customer', 'user', 'tenant'],
                    'API Failures': ['api', 'endpoint', 'request'],
                    'Regional': ['region', 'regional', 'geography']
                }
                
                imp_stats = []
                for imp_type, keywords in impact_type_mapping.items():
                    mask = fdf['Impacts'].fillna('').str.lower().apply(
                        lambda x: any(kw in x for kw in keywords)
                    )
                    imp_df = fdf[mask]
                    
                    if len(imp_df) > 0:
                        p75_ttm = imp_df['TTM'].quantile(0.75) if 'TTM' in imp_df.columns else 0
                        incident_count = len(imp_df)
                        service_count = imp_df['ServiceName'].nunique() if 'ServiceName' in imp_df.columns else 0
                        severity_counts = imp_df['Severity'].value_counts().to_dict() if 'Severity' in imp_df.columns else {}
                        
                        imp_stats.append({
                            'type': imp_type,
                            'p75': p75_ttm,
                            'count': incident_count,
                            'services': service_count,
                            'severity': severity_counts
                        })
                
                if imp_stats:
                    # Sort by P75 TTM descending
                    imp_stats.sort(key=lambda x: x['p75'], reverse=True)
                    
                    imp_rows = []
                    for stat in imp_stats[:5]:  # Top 5
                        sev_text = ', '.join([f"{k}:{v}" for k, v in sorted(stat['severity'].items())])
                        imp_rows.append(html.Tr([
                            html.Td(stat['type'], style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(f"{stat['p75']:.0f} min", style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold', 'color': BLUE}),
                            html.Td(str(stat['count']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(str(stat['services']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(sev_text, style={'padding': '8px', 'fontSize': '10px', 'borderBottom': '1px solid #eee'})
                        ]))
                    
                    correlation_sections.append(html.Div([
                        html.H4('Impact Pattern Analysis', style={'color': BLUE, 'marginTop': '20px', 'marginBottom': '10px', 'fontSize': '14px'}),
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th('Impact Type', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold', 'textAlign': 'left'}),
                                html.Th('P75 TTM', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Incidents', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Services', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Severity Breakdown', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ])),
                            html.Tbody(imp_rows)
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
                    ]))
            
            # Create correlation analysis box
            if correlation_sections:
                correlation_analysis = html.Div(
                    correlation_sections,
                    style={
                        'backgroundColor': '#F8F9FA',
                        'padding': '20px',
                        'borderRadius': '8px',
                        'marginTop': '20px',
                        'border': '2px solid #e0e0e0',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                    }
                )
            else:
                correlation_analysis = html.Div()
            
            service_analysis_table = html.Div([
                all_up_summary,
                html.Table([
                    html.Thead(html.Tr([
                        html.Th('Team', style={'padding': '10px', 'borderBottom': f'2px solid {BLUE}',
                                              'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                              'fontSize': '12px', 'fontWeight': 'bold'}),
                        html.Th('Count', style={'padding': '10px', 'borderBottom': f'2px solid {BLUE}',
                                               'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                               'fontSize': '12px', 'fontWeight': 'bold'}),
                        html.Th('Avg TTM', style={'padding': '10px', 'borderBottom': f'2px solid {BLUE}',
                                                 'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                                 'fontSize': '12px', 'fontWeight': 'bold'}),
                        html.Th('Root Causes', style={'padding': '10px', 'borderBottom': f'2px solid {BLUE}',
                                                     'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                                     'fontSize': '12px', 'fontWeight': 'bold'}),
                        html.Th('Mitigations', style={'padding': '10px', 'borderBottom': f'2px solid {BLUE}',
                                                      'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                                      'fontSize': '12px', 'fontWeight': 'bold'}),
                        html.Th('Impacts', style={'padding': '10px', 'borderBottom': f'2px solid {BLUE}',
                                                 'position': 'sticky', 'top': '0', 'backgroundColor': 'white',
                                                 'fontSize': '12px', 'fontWeight': 'bold'})
                    ])),
                    html.Tbody(service_rows)
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ])
        else:
            service_analysis_table = html.Div("No data available for service analysis", 
                                             style={'padding': '20px', 'textAlign': 'center', 'color': '#666'})
    except Exception as e:
        service_analysis_table = html.Div(f"Error loading service analysis: {str(e)}", 
                                         style={'padding': '20px', 'textAlign': 'center', 'color': 'red'})
    
    # ========================================================================
    # PATTERN & CORRELATION ANALYSIS SECTION
    # ========================================================================
    try:
        if not fdf.empty:
            pattern_sections = []
            
            # Root cause theme mapping (same as used earlier)
            rc_theme_mapping = {
                'Connectivity': ['connectivity', 'connection', 'network', 'endpoint'],
                'Configuration': ['configuration', 'config', 'misconfiguration'],
                'Capacity': ['capacity', 'resource exhaustion', 'memory', 'throttling'],
                'Deployment': ['deployment', 'rollout', 'release'],
                'Certificate': ['certificate', 'cert', 'ssl', 'tls'],
                'Timeout': ['timeout', 'timed out', 'latency'],
                'Dependency': ['dependency', 'dependent', 'downstream']
            }
            
            # Mitigation action mapping (same as used earlier)
            mit_action_mapping = {
                'Restart/Reboot': ['restart', 'reboot', 'recycle'],
                'Rollback': ['rollback', 'rolled back', 'reverted'],
                'Scaling': ['scale', 'scaled', 'scaling'],
                'Failover': ['failover', 'failed over', 'switched'],
                'Config Change': ['config change', 'reconfigured'],
                'Traffic Mgmt': ['throttle', 'rate limit', 'blocked']
            }
            
            # Build Root Cause × Mitigation Combination Analysis (optimized with pre-computed columns)
            combination_stats = []
            rc_column_map = {
                'Connectivity': 'has_connectivity',
                'Configuration': 'has_configuration',
                'Capacity': 'has_capacity',
                'Deployment': 'has_deployment',
                'Certificate': 'has_certificate',
                'Timeout': 'has_timeout',
                'Dependency': 'has_dependency'
            }
            mit_column_map = {
                'Restart/Reboot': 'has_restart',
                'Rollback': 'has_rollback',
                'Scaling': 'has_scaling',
                'Failover': 'has_failover',
                'Config Change': 'has_config_change',
                'Traffic Mgmt': 'has_traffic_mgmt'
            }
            
            for rc_theme, rc_col in rc_column_map.items():
                for mit_action, mit_col in mit_column_map.items():
                    # Use pre-computed boolean columns (100x faster than keyword matching)
                    if rc_col in fdf.columns and mit_col in fdf.columns:
                        combo_df = fdf[fdf[rc_col] & fdf[mit_col]]
                    else:
                        combo_df = pd.DataFrame()
                    
                    if len(combo_df) >= 2:  # At least 2 incidents to avoid noise
                        p75_ttm = combo_df['TTM'].quantile(0.75)
                        incident_count = len(combo_df)
                        service_count = combo_df['ServiceName'].nunique() if 'ServiceName' in combo_df.columns else 0
                        severity_counts = combo_df['Severity'].value_counts().to_dict() if 'Severity' in combo_df.columns else {}
                        severity_str = ', '.join([f"{sev}: {cnt}" for sev, cnt in sorted(severity_counts.items())])
                        
                        combination_stats.append({
                            'root_cause': rc_theme,
                            'mitigation': mit_action,
                            'p75_ttm': p75_ttm,
                            'count': incident_count,
                            'services': service_count,
                            'severity': severity_str
                        })
            
            # Sort by P75 TTM descending (highest TTM first)
            combination_stats.sort(key=lambda x: x['p75_ttm'], reverse=True)
            
            # Create Combination Analysis Table (show top 15)
            combo_rows = []
            for stat in combination_stats[:15]:
                combo_rows.append(html.Tr([
                    html.Td(stat['root_cause'], style={'padding': '8px', 'borderBottom': '1px solid #ddd'}),
                    html.Td(stat['mitigation'], style={'padding': '8px', 'borderBottom': '1px solid #ddd'}),
                    html.Td(f"{stat['p75_ttm']:.1f} min", style={'padding': '8px', 'borderBottom': '1px solid #ddd',
                                                                   'color': BLUE, 'fontWeight': 'bold'}),
                    html.Td(str(stat['count']), style={'padding': '8px', 'borderBottom': '1px solid #ddd', 
                                                        'textAlign': 'center'}),
                    html.Td(str(stat['services']), style={'padding': '8px', 'borderBottom': '1px solid #ddd',
                                                           'textAlign': 'center'}),
                    html.Td(stat['severity'], style={'padding': '8px', 'borderBottom': '1px solid #ddd', 
                                                      'fontSize': '11px'})
                ]))
            
            combination_table = html.Div([
                html.H4("Root Cause × Mitigation Combination Analysis", 
                       style={'color': BLUE, 'marginBottom': '15px', 'marginTop': '0px'}),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th('Root Cause Theme', style={'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                           'borderBottom': '2px solid #dee2e6', 'textAlign': 'left'}),
                        html.Th('Mitigation Action', style={'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                            'borderBottom': '2px solid #dee2e6', 'textAlign': 'left'}),
                        html.Th('P75 TTM', style={'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                  'borderBottom': '2px solid #dee2e6', 'textAlign': 'left'}),
                        html.Th('Incidents', style={'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                    'borderBottom': '2px solid #dee2e6', 'textAlign': 'center'}),
                        html.Th('Services', style={'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                   'borderBottom': '2px solid #dee2e6', 'textAlign': 'center'}),
                        html.Th('Severity Breakdown', style={'padding': '10px', 'backgroundColor': '#f8f9fa',
                                                             'borderBottom': '2px solid #dee2e6', 'textAlign': 'left'})
                    ])),
                    html.Tbody(combo_rows)
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '10px'})
            ], style={'marginBottom': '30px'})
            
            pattern_sections.append(combination_table)
            
            # Build Root Cause Pattern Analysis (optimized with pre-computed columns)
            if 'RootCauses' in fdf.columns:
                rc_stats = []
                for theme, col_name in rc_column_map.items():
                    if col_name in fdf.columns:
                        theme_df = fdf[fdf[col_name]]
                        
                        if len(theme_df) > 0:
                            p75_ttm = theme_df['TTM'].quantile(0.75)
                            incident_count = len(theme_df)
                            service_count = theme_df['ServiceName'].nunique() if 'ServiceName' in theme_df.columns else 0
                            severity_counts = theme_df['Severity'].value_counts().to_dict() if 'Severity' in theme_df.columns else {}
                            
                            rc_stats.append({
                                'theme': theme,
                                'p75': p75_ttm,
                                'count': incident_count,
                                'services': service_count,
                                'severity': severity_counts
                            })
                
                if rc_stats:
                    rc_stats.sort(key=lambda x: x['p75'], reverse=True)
                    rc_rows = []
                    for stat in rc_stats[:5]:
                        sev_text = ', '.join([f"{k}:{v}" for k, v in sorted(stat['severity'].items())])
                        rc_rows.append(html.Tr([
                            html.Td(stat['theme'], style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(f"{stat['p75']:.0f} min", style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold', 'color': BLUE}),
                            html.Td(str(stat['count']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(str(stat['services']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(sev_text, style={'padding': '8px', 'fontSize': '10px', 'borderBottom': '1px solid #eee'})
                        ]))
                    
                    pattern_sections.append(html.Div([
                        html.H4('Root Cause Pattern Analysis', style={'color': BLUE, 'marginTop': '20px', 'marginBottom': '10px', 'fontSize': '14px'}),
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th('Root Cause Theme', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold', 'textAlign': 'left'}),
                                html.Th('P75 TTM', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Incidents', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Services', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Severity Breakdown', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ])),
                            html.Tbody(rc_rows)
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
                    ], style={'marginBottom': '20px'}))
            
            # Build Mitigation Effectiveness Analysis (optimized with pre-computed columns)
            if 'Mitigations' in fdf.columns:
                mit_stats = []
                for action, col_name in mit_column_map.items():
                    if col_name in fdf.columns:
                        action_df = fdf[fdf[col_name]]
                        
                        if len(action_df) > 0:
                            p75_ttm = action_df['TTM'].quantile(0.75)
                            incident_count = len(action_df)
                            service_count = action_df['ServiceName'].nunique() if 'ServiceName' in action_df.columns else 0
                            severity_counts = action_df['Severity'].value_counts().to_dict() if 'Severity' in action_df.columns else {}
                            
                            mit_stats.append({
                                'action': action,
                                'p75': p75_ttm,
                                'count': incident_count,
                                'services': service_count,
                                'severity': severity_counts
                            })
                
                if mit_stats:
                    mit_stats.sort(key=lambda x: x['count'], reverse=True)
                    mit_rows = []
                    for stat in mit_stats[:5]:
                        sev_text = ', '.join([f"{k}:{v}" for k, v in sorted(stat['severity'].items())])
                        mit_rows.append(html.Tr([
                            html.Td(stat['action'], style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(f"{stat['p75']:.0f} min", style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold', 'color': BLUE}),
                            html.Td(str(stat['count']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(str(stat['services']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(sev_text, style={'padding': '8px', 'fontSize': '10px', 'borderBottom': '1px solid #eee'})
                        ]))
                    
                    pattern_sections.append(html.Div([
                        html.H4('Mitigation Effectiveness Analysis', style={'color': BLUE, 'marginTop': '20px', 'marginBottom': '10px', 'fontSize': '14px'}),
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th('Mitigation Action', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold', 'textAlign': 'left'}),
                                html.Th('P75 TTM', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Incidents', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Services', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Severity Breakdown', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ])),
                            html.Tbody(mit_rows)
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
                    ], style={'marginBottom': '20px'}))
            
            # Build Impact Pattern Analysis (optimized with pre-computed columns)
            if 'Impacts' in fdf.columns:
                impact_column_map = {
                    'Availability': 'has_availability',
                    'Performance': 'has_performance',
                    'Functionality': 'has_functionality',
                    'Data Issue': 'has_data_issue',
                    'Authentication': 'has_authentication'
                }
                
                imp_stats = []
                for imp_type, col_name in impact_column_map.items():
                    if col_name in fdf.columns:
                        imp_df = fdf[fdf[col_name]]
                        
                        if len(imp_df) > 0:
                            p75_ttm = imp_df['TTM'].quantile(0.75)
                            incident_count = len(imp_df)
                            service_count = imp_df['ServiceName'].nunique() if 'ServiceName' in imp_df.columns else 0
                            severity_counts = imp_df['Severity'].value_counts().to_dict() if 'Severity' in imp_df.columns else {}
                            
                            imp_stats.append({
                                'type': imp_type,
                                'p75': p75_ttm,
                                'count': incident_count,
                                'services': service_count,
                                'severity': severity_counts
                            })
                
                if imp_stats:
                    imp_stats.sort(key=lambda x: x['p75'], reverse=True)
                    imp_rows = []
                    for stat in imp_stats[:5]:
                        sev_text = ', '.join([f"{k}:{v}" for k, v in sorted(stat['severity'].items())])
                        imp_rows.append(html.Tr([
                            html.Td(stat['type'], style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(f"{stat['p75']:.0f} min", style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee', 'fontWeight': 'bold', 'color': BLUE}),
                            html.Td(str(stat['count']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(str(stat['services']), style={'padding': '8px', 'fontSize': '11px', 'borderBottom': '1px solid #eee'}),
                            html.Td(sev_text, style={'padding': '8px', 'fontSize': '10px', 'borderBottom': '1px solid #eee'})
                        ]))
                    
                    pattern_sections.append(html.Div([
                        html.H4('Impact Pattern Analysis', style={'color': BLUE, 'marginTop': '20px', 'marginBottom': '10px', 'fontSize': '14px'}),
                        html.Table([
                            html.Thead(html.Tr([
                                html.Th('Impact Type', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold', 'textAlign': 'left'}),
                                html.Th('P75 TTM', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Incidents', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Services', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'}),
                                html.Th('Severity Breakdown', style={'padding': '8px', 'borderBottom': f'2px solid {BLUE}', 'fontSize': '11px', 'fontWeight': 'bold'})
                            ])),
                            html.Tbody(imp_rows)
                        ], style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
                    ]))
            
            pattern_analysis = html.Div(pattern_sections, style={
                'backgroundColor': '#F8F9FA',
                'padding': '20px',
                'borderRadius': '8px',
                'marginTop': '20px'
            })
        else:
            pattern_analysis = html.Div("No data available for pattern analysis", 
                                       style={'padding': '20px', 'textAlign': 'center', 'color': '#666'})
    except Exception as e:
        pattern_analysis = html.Div(f"Error loading pattern analysis: {str(e)}", 
                                    style={'padding': '20px', 'textAlign': 'center', 'color': 'red'})
    
    return total, p75, mean, p90, critsits, fig_dist, fig_services, fig_timeline, fig_severity, fig_quintile, fig_region, table, table_count_text, service_analysis_table, pattern_analysis, banner, chart_filters

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("TTM DASHBOARD - Starting server...")
    print("Open browser: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop")
    print("="*80 + "\n")
    app.run(debug=True, host='127.0.0.1', port=8050)
