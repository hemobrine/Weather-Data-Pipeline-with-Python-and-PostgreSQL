"""
Weather Data Pipeline — Entry Point

1.  Initializes the logger
2.  Creates database tables (if they don't exist)
3.  Runs the ETL pipeline once immediately
4.  Starts the daily scheduler
"""

from src.logger import logger
from src.db import init_schema
from src.etl import run_pipeline
from src.scheduler import start_scheduler


def main():
    logger.info("=" * 60)
    logger.info("Weather Data Pipeline — starting up")
    logger.info("=" * 60)

    # 1. Ensure DB schema exists
    init_schema()

    # 2. Run pipeline once on startup
    logger.info("Running initial pipeline execution …")
    try:
        run_pipeline()
    except Exception as exc:
        logger.error("Initial pipeline run failed: %s", exc)
        # Don't exit — let the scheduler retry later

    # 3. Start daily scheduler (blocks forever)
    logger.info("Handing off to the scheduler …")
    start_scheduler()


if __name__ == "__main__":
    main()
