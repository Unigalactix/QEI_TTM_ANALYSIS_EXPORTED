# QEI_TTM_ANALYSIS_EXPORTED

Automated Time-To-Mitigation (TTM) analysis and reporting workspace for QEI data. This repository contains scripts, prompts, and utilities for generating incident narratives, executive summaries, dashboards, and what-if analysis based on TTM data exports.

## Structure

- [DecTTM/](DecTTM) – December TTM analysis data, models, scripts, reports, and visualizations.
- [Utilities/](Utilities) – Shared utilities, prompts, and higher-level scripts for creating presentations, narratives, and metrics.
- [mcp.json](mcp.json) – Model Context Protocol configuration for automated workflows.
- [TTMAnalysis.prompt.md](TTMAnalysis.prompt.md) – Core prompt for TTM analysis workflows.

## Getting Started

1. Ensure Python 3.10+ is installed.
2. (Optional) Create and activate a virtual environment.
3. Install any dependencies required by the scripts you plan to run (for example, pandas, matplotlib, scikit-learn, etc.).
4. Use the scripts under [DecTTM/scripts/](DecTTM/scripts) or [Utilities/CreateScripts/](Utilities/CreateScripts) to generate reports and visualizations.

## High-Level Workflow (Mermaid)

```mermaid
flowchart LR
	A[Raw TTM export\nfrom incident system] --> B[Data preparation scripts\nDecTTM/scripts]
	B --> C[Filtered & enriched TTM data\nDecTTM/data]
	C --> D[Modeling & analysis\nDecTTM/models + Utilities/CreateScripts]
	D --> E[Reports & narratives\nDecTTM/reports]
	D --> F[Dashboards & visuals\nDecTTM/visualizations]
	E --> G[Executive & operational stakeholders]
	F --> G
```

## Execution Flow (Scripts)

```mermaid
flowchart TD
	subgraph Utilities Layer
		U1[execute_kusto_query_to_csv.py] --> U2[ttm_query.csl]
		U3[CreateScripts/analyze_october_ttm.py]
		U4[CreateScripts/create_metrics.py]
		U5[CreateScripts/create_visualizations.py]
	end

	subgraph DecTTM Layer
		D1[scripts/execute_kusto_query_to_csv.py]
		D2[scripts/ttm_dashboard.py]
		D3[scripts/create_regression_model.py]
		D4[scripts/create_narrative.py]
		D5[scripts/create_executive_summary.py]
		D6[scripts/create_whatif_analysis.py]
	end

	U1 -->|Export raw TTM data| D1
	D1 -->|Write CSVs| D2
	D1 --> D3
	D3 --> D6
	D2 -->|Generate visuals| DecReports[DecTTM/reports]
	D4 --> DecReports
	D5 --> DecReports
	D6 --> DecReports
```

## System Flow (Components)

```mermaid
flowchart LR
	ext[Incident & telemetry sources] --> K[Kusto / Log Analytics]
	K -->|KQL queries\nUtilities/ttm_query.csl| Q[CSV exports]

	Q --> P[Processing & analysis scripts\nDecTTM/scripts + Utilities/CreateScripts]
	P --> M[Models & metrics\nDecTTM/models]
	P --> V[Visualizations & dashboards\nDecTTM/visualizations]
	P --> R[Markdown reports & narratives\nDecTTM/reports]

	R --> Stake[Stakeholders\nEngineers, PMs, Leadership]
	V --> Stake
```

## Version Control Notes

- Large raw data exports and derived CSV files should generally not be committed.
- Local environment files, caches, and build artifacts are ignored via `.gitignore`.

## License

Specify the license for this repository (e.g., MIT, Apache-2.0) before public use.
