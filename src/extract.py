import os
import sys
import pandas as pd


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
                             
from config.logging_config import logger

def extraction():
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    files = [ 
        os.path.join(data_dir, 'outreach_calls_phase1.csv'),
        os.path.join(data_dir, 'residents_2026_01.csv'),
        os.path.join(data_dir, 'support_requests_january.json')
    ]
    
    dataset = {}
    logger.info("Extraction pipeline started.")

    try:
        for file in files:
            file_name = os.path.basename(file)

            if not os.path.exists(file):
                logger.error(f"Target file not found at path location: {file}")
                continue

            if file.endswith('csv'):
                df = pd.read_csv(file)
            elif file.endswith('json'):
                df = pd.read_json(file)
            else:
                logger.warning(f"Unsupported file format skipped: {file_name}")
                continue

            
            dataset[file_name] = df  
            logger.info(f"Successfully extracted {file_name} with {len(df)} rows.")

        return dataset

    except Exception as e:
        logger.critical(f"Extraction execution failed due to a structural error: {e}")
        raise

if __name__ == "__main__":
    extraction()