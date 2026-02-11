"""
Execute Kusto Query and Save to CSV
This script executes the ttm_query.csl against the Kusto cluster and saves results to CSV.
"""

import pandas as pd
from pathlib import Path
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from datetime import datetime

# Configuration
CLUSTER_URI = "https://icmdataro.centralus.kusto.windows.net"
DATABASE = "IcmDataCommon"
QUERY_FILE = Path(r"C:\Users\nigopal\OneDrive - Microsoft\Documents\QEI_TTM_Analysis\Utilities\ttm_query.csl")
OUTPUT_FOLDER = Path(r"C:\Users\nigopal\OneDrive - Microsoft\Documents\QEI_TTM_Analysis\OctTTM")
OUTPUT_CSV = OUTPUT_FOLDER / "october_2025_ttm_full_month.csv"

# October 2025 date range for the query
START_DATE = "2025-10-01"
END_DATE = "2025-10-31"

def read_query_file(query_file_path):
    """Read the KQL query from file"""
    print(f"📖 Reading query from: {query_file_path}")
    with open(query_file_path, 'r', encoding='utf-8') as f:
        query = f.read()
    return query

def update_query_dates(query, start_date, end_date):
    """Update the query with October 2025 dates"""
    print(f"📅 Updating query dates to: {start_date} - {end_date}")
    
    # Replace the date range in the query
    # The template has: let startDate = startofday(todatetime('01/01/2025'));
    query = query.replace(
        "let startDate = startofday(todatetime('01/01/2025'));",
        f"let startDate = startofday(todatetime('{start_date}'));"
    )
    query = query.replace(
        "let endDate = endofday(todatetime('09/30/2025'));",
        f"let endDate = endofday(todatetime('{end_date}'));"
    )
    
    return query

def execute_kusto_query(cluster_uri, database, query):
    """Execute the Kusto query and return results as DataFrame"""
    print(f"\n{'='*80}")
    print("CONNECTING TO KUSTO CLUSTER")
    print("="*80)
    print(f"Cluster: {cluster_uri}")
    print(f"Database: {database}")
    
    print("\n🔐 Using Interactive Browser Authentication...")
    print("A browser window will open for you to sign in.")
    
    try:
        # Use interactive browser authentication directly
        credential = InteractiveBrowserCredential()
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(cluster_uri, credential)
        client = KustoClient(kcsb)
        print("✅ Authentication successful!")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nAlternative: You can also authenticate using Azure CLI:")
        print("  1. Run: az login")
        print("  2. Then run this script again")
        raise
    
    # Execute query
    print(f"\n{'='*80}")
    print("EXECUTING KUSTO QUERY")
    print("="*80)
    print(f"Timestamp: {datetime.now()}")
    print("Please wait, this may take a few minutes for large result sets...")
    
    try:
        response = client.execute(database, query)
        print("✅ Query executed successfully!")
        
        # Convert to DataFrame with proper column names
        print("\n🔄 Converting results to DataFrame...")
        primary_result = response.primary_results[0]
        
        # Extract column names from the Kusto response
        column_names = [col.column_name for col in primary_result.columns]
        
        # Convert rows to DataFrame with column names
        rows = [row for row in primary_result]
        df = pd.DataFrame(rows, columns=column_names)
        
        print(f"✅ Loaded {len(df)} incidents")
        print(f"✅ Columns: {len(df.columns)}")
        print(f"✅ Column names preserved: {', '.join(column_names[:5])}...")
        
        return df
        
    except KustoServiceError as e:
        print(f"❌ Kusto query error: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

def save_to_csv(df, output_path):
    """Save DataFrame to CSV"""
    print(f"\n{'='*80}")
    print("SAVING TO CSV")
    print("="*80)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Saved to: {output_path}")
    print(f"   - Rows: {len(df)}")
    print(f"   - Columns: {len(df.columns)}")
    print(f"   - File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Display sample data
    print(f"\n📊 Sample Data (first 5 rows):")
    display_cols = [col for col in ['OutageIncidentId', 'ServiceName', 'Severity', 'TTM', 'TTD', 'TTO', 'OutageCreateDate'] 
                    if col in df.columns]
    if display_cols:
        print(df[display_cols].head().to_string(index=False))
    
    # Display summary statistics
    if 'TTM' in df.columns:
        print(f"\n📈 TTM Statistics:")
        print(f"   - Mean: {df['TTM'].mean():.2f} minutes")
        print(f"   - Median (P50): {df['TTM'].median():.2f} minutes")
        print(f"   - P75: {df['TTM'].quantile(0.75):.2f} minutes")
        print(f"   - P90: {df['TTM'].quantile(0.90):.2f} minutes")
    
    return output_path

def main():
    """Main execution function"""
    print("="*80)
    print("OCTOBER 2025 TTM ANALYSIS - KUSTO QUERY TO CSV")
    print("="*80)
    print(f"Execution Time: {datetime.now()}")
    
    try:
        # Step 1: Read query file
        query = read_query_file(QUERY_FILE)
        
        # Step 2: Update query with October 2025 dates
        query = update_query_dates(query, START_DATE, END_DATE)
        
        # Step 3: Execute query
        df = execute_kusto_query(CLUSTER_URI, DATABASE, query)
        
        # Step 4: Save to CSV
        csv_path = save_to_csv(df, OUTPUT_CSV)
        
        # Step 5: Success message
        print(f"\n{'='*80}")
        print("✅ SUCCESS - CSV FILE CREATED")
        print("="*80)
        print(f"\nNext steps:")
        print(f"1. Verify the CSV file: {csv_path}")
        print(f"2. Run the full analysis: python run_full_analysis.py")
        print(f"3. Generate the narrative following: Narrative_Generation_Instructions.md")
        
        return 0
        
    except Exception as e:
        print(f"\n{'='*80}")
        print("❌ ERROR OCCURRED")
        print("="*80)
        print(f"Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Ensure you're authenticated to Azure (run 'az login')")
        print(f"2. Check you have access to the Kusto cluster")
        print(f"3. Verify the query file exists at: {QUERY_FILE}")
        return 1

if __name__ == "__main__":
    exit(main())
