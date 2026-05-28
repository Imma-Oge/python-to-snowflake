import os
import sys
import pandas as pd
from typing import Dict
from snowflake.connector.pandas_tools import write_pandas

# Path configuration to resolve module imports from parent folders safely
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.logging_config import logger
from src.connections import get_snowflake_connection


TABLE_MAPPINGS = {
    'residents_2026_01.csv': 'STG_RESIDENTS_RAW',
    'outreach_calls_phase1.csv': 'STG_OUTREACH_CALLS_RAW',
    'support_requests_january.json': 'STG_SUPPORT_REQUESTS_RAW'
}

def load_data_to_snowflake(transformed_datasets: Dict[str, pd.DataFrame]):
    """Loads all dataframes in the dataset payload straight into Snowflake staging tables."""
    conn = None
    try:
        # Fetch the secure connection session from src/connections.py
        conn = get_snowflake_connection()
        
        for file_name, df in transformed_datasets.items():
            if file_name in TABLE_MAPPINGS:
                target_table = TABLE_MAPPINGS[file_name]
                logger.info(f"Initiating bulk upload for {file_name} into Snowflake table {target_table} ({len(df)} rows)...")
                
                # Snowflake table column names set to uppercase to avoid querying issues
                df_upper = df.copy()
                df_upper.columns = [col.upper() for col in df_upper.columns]
                
                # High-performance write tool: Generates table structures and appends rows efficiently
                success, nchunks, nrows, _ = write_pandas(
                    conn=conn,
                    df=df_upper,
                    table_name=target_table,
                    auto_create_table=True, # Automatically creates the table DDL if it does not exist
                    overwrite=True          # Overwrites existing target data for clean, idempotent loads
                )
                
                if success:
                    logger.info(f"Successfully staged {nrows} rows into {target_table} across {nchunks} chunks.")
                else:
                    logger.error(f"Snowflake report indicated a structural issue loading dataset {file_name}.")
            else:
                logger.warning(f"No table mapping found for {file_name}. Skipping database stage load.")

    except Exception as load_error:
        logger.critical(f"Fatal load pipeline failure encountered: {load_error}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Snowflake database connection closed cleanly.")

# =====================================================================
# FULL END-TO-END WORKFLOW PIPELINE HARNESS
# =====================================================================
if __name__ == "__main__":
    print("--- Running Full End-to-End E-T-L Pipeline Test ---")
    try:
        # Import your previous clean modules
        from src.extract import extraction
        from src.transformed import transform_all_data
        
        # Step 1: Run Extraction
        raw_payload = extraction()
        
        # Step 2: Run Typing Transformations
        clean_payload = transform_all_data(raw_payload)
        
        # Step 3: Run Snowflake Database Load
        load_data_to_snowflake(clean_payload)
        
        print("\n--- Full ETL Pipeline Executed Successfully! ---")
        
    except Exception as pipeline_err:
        print(f"\nETL Execution halted with a fatal error: {pipeline_err}")