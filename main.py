

import os
import sys
import time

# Resolve internal imports cleanly from the root workspace
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.logging_config import logger
from src.extract import extraction
from src.transformed import transform_all_data
from src.load import load_data_to_snowflake

def run_pipeline():
    """Orchestrates the full data pipeline workflow end-to-end."""
    start_time = time.time()
    logger.info("=========================================")
    logger.info("         STARTING PIPELINE RUN           ")
    logger.info("=========================================")

    try:
        # Phase 1: Extraction
        logger.info("[ORCHESTRATOR] Initializing E-T-L Phase 1: Extraction")
        raw_payload = extraction()
        logger.info(f"[ORCHESTRATOR] Phase 1 Complete. Extracted {len(raw_payload)} payloads.")

        # Phase 2: Transformation
        logger.info("[ORCHESTRATOR] Initializing E-T-L Phase 2: Transformation")
        clean_payload = transform_all_data(raw_payload)
        logger.info("[ORCHESTRATOR] Phase 2 Complete. Structural schemas applied cleanly.")

        # Phase 3: Loading
        logger.info("[ORCHESTRATOR] Initializing E-T-L Phase 3: Snowflake Database Load")
        load_data_to_snowflake(clean_payload)
        logger.info("[ORCHESTRATOR] Phase 3 Complete. Data pushed to warehouse.")

        # Success metrics logging
        execution_time = round(time.time() - start_time, 2)
        logger.info("=========================================")
        logger.info(f" PIPELINE RUN SUCCESSFUL | Duration: {execution_time}s")

        logger.info("=========================================")
        print(f"\n Pipeline finished successfully in {execution_time} seconds!")

    except Exception as pipeline_error:
        # Catch any failure anywhere in the chain and log the execution crash status
        execution_time = round(time.time() - start_time, 2)
        logger.critical("=========================================")
        logger.critical(f" PIPELINE RUN FAILED | Interrupted after {execution_time}s")
        logger.critical(f" Error Details: {pipeline_error}")
        logger.critical("=========================================")
        print(f"\n Pipeline aborted with critical error: {pipeline_error}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
