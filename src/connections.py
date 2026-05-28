import os
import sys
import snowflake.connector
from dotenv import load_dotenv


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.logging_config import logger

load_dotenv(os.path.join(parent_dir, '.env'))

def get_snowflake_connection():
    """Establishes and returns an active connection session to the Snowflake Data Warehouse."""
    try:
        logger.info("Initializing connection session with Snowflake Warehouse...")
        
        # This creates the active database connection session
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        
        logger.info("Successfully established connection session with Snowflake.")
        return conn
        
    except Exception as connection_error:
        logger.critical(f"Failed to establish Snowflake connection session: {connection_error}")
        raise