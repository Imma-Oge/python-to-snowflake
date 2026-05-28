import os
import sys
import pandas as pd
from typing import Dict


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.logging_config import logger

# =====================================================================
# DATA TYPE SCHEMAS (Perfect match to clean filenames)
# =====================================================================
RESIDENT_SCHEMA = {
    'resident_id': 'str',
    'first_name': 'str',
    'last_name': 'str',
    'gender': 'str',
    'date_of_birth': 'datetime',
    'phone_number': 'str',
    'email': 'str',
    'state': 'str',
    'local_government': 'str',
    'registration_date': 'datetime',
    'employment_status': 'str',
    'monthly_income': 'float',
    'household_size': 'int'
}

OUTREACH_SCHEMA = {
    'call_id': 'str',
    'resident_id': 'str',
    'call_date': 'datetime',
    'connected': 'str',
    'call_duration_seconds': 'float',
    'outcome': 'str',
    'officer_name': 'str',
    'campaign_phase': 'str'
}

SUPPORT_REQUEST_SCHEMA = {
    'request_id': 'str',
    'resident_id': 'str',
    'request_type': 'str',
    'request_date': 'datetime',
    'urgency_level': 'str',
    'support_amount_requested': 'float', 
    'status': 'str',
    'assigned_officer': 'str'
}

FILE_SCHEMAS = {
    'residents_2026_01.csv': RESIDENT_SCHEMA,
    'outreach_calls_phase1.csv': OUTREACH_SCHEMA,
    'support_requests_january.json': SUPPORT_REQUEST_SCHEMA
}

# =====================================================================
# CORE TRANSFORMATION LOGIC
# =====================================================================
def profile_columns(df: pd.DataFrame, type_matching: dict, file_name: str) -> pd.DataFrame:
    """Profiles a single dataframe's structural types and cleans anomalies."""

    df = df.copy()
    logger.info(f"Starting column profiling schema checks for {file_name}")

    for col, match in type_matching.items():
        if col not in df.columns:
            logger.warning(f"[{file_name}] Expected structural column '{col}' missing from source data.")
            continue

        try:
            if match == 'datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif match == 'str':
                
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
                
                df[col] = df[col].replace(['nan', 'None', '<NA>'], None)
            else:
                df[col] = df[col].astype(match)

        except Exception as col_error:
            logger.error(f"[{file_name}] Failed to cast column '{col}' to type '{match}': {col_error}")

    return df

def transform_all_data(dataset_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Applies typing transformations globally over the dataset group."""

    if not dataset_dict:
        logger.error("Transformation layer received empty dictionary payload.")
        raise ValueError("No data provided for transformation.")

    cleaned_dataset = {}
    logger.info("Initializing data transformation pipeline.")

    for raw_key, df in dataset_dict.items():
        
        file_name = os.path.basename(raw_key) 
        
        if file_name in FILE_SCHEMAS:
            try:
                schema = FILE_SCHEMAS[file_name]
                cleaned_df = profile_columns(df, schema, file_name)
                cleaned_dataset[file_name] = cleaned_df
                logger.info(f"Successfully profiled and typed structural data for: {file_name}")
            except Exception as file_error:
                logger.critical(f"Fatal transformation processing error on file {file_name}: {file_error}")
                raise
        else:
            logger.warning(f"No explicit schema definition mapping matches file: '{file_name}'. Passing through raw.")
            cleaned_dataset[file_name] = df

    logger.info("Global data transformation pipeline completed successfully.")
    return cleaned_dataset

# =====================================================================
# PIPELINE EXECUTION HUB
# =====================================================================
if __name__ == "__main__":
    print("--- Executing Integrated E-T Pipeline Test ---")
    try:
        # Import extraction logic dynamically
        from src.extract import extraction
        
        
        raw_data = extraction()
        
        
        transformed_data = transform_all_data(raw_data)
        
        
        print("\n--- Pipeline Check Success ---")
        for name, df in transformed_data.items():
            print(f"Dataset Key: {name:<32} | Rows: {len(df):<5} | Status: Ready for Snowflake Loading")
            
    except Exception as pipeline_error:
        logger.critical(f"Pipeline flow stopped during test run execution: {pipeline_error}")
        print(f"\nExecution Failed. View application logs for details: {pipeline_error}")