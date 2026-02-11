import json
from datetime import datetime

log_data = {
    "timestamp": datetime.now().isoformat(),
    "month": "October 2025",
    "workflow": "PROMPT_1.md Complete TTM Analysis",
    "status": "completed",
    "steps_completed": [
        {
            "step": 1,
            "description": "Query and CSV Generation",
            "script": "execute_kusto_query_to_csv.py",
            "output": "october_2025_ttm_full_month.csv",
            "incident_count": 117,
            "column_count": 487
        },
        {
            "step": 2,
            "description": "Summary Statistics",
            "output": "October_Summary_Statistics.md"
        },
        {
            "step": 3,
            "description": "Key Metrics",
            "output": "October_Key_Metrics.md"
        },
        {
            "step": 4,
            "description": "Month-over-Month Comparison",
            "output": "October_vs_September_Comparison.md"
        },
        {
            "step": 5,
            "description": "Comprehensive Narrative",
            "output": "October_Narrative.md",
            "line_count": 309
        },
        {
            "step": 6,
            "description": "Visualizations",
            "outputs": [
                "October_TTM_Distribution.png",
                "October_Top_Services.png",
                "October_Daily_Timeline.png",
                "October_Severity_Distribution.png"
            ]
        }
    ],
    "key_metrics": {
        "total_incidents": 117,
        "mean_ttm_minutes": 293,
        "median_ttm_minutes": 71,
        "p75_ttm_minutes": 190,
        "severity_2_count": 107
    }
}

with open("workflow_execution_log.json", "w") as f:
    json.dump(log_data, f, indent=2)

print("Created workflow_execution_log.json")
