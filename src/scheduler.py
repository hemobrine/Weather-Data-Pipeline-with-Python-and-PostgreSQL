"""
Scheduler — runs the ETL pipeline on a daily cron schedule.
"""

import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import settings
from src.etl import run_pipeline
from src.logger import logger


def start_scheduler():
    """
    Start a blocking scheduler that runs ``run_pipeline`` daily
    at the hour configured in ``SCHEDULE_HOUR``.
    """
    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_pipeline,
        trigger=CronTrigger(hour=settings.SCHEDULE_HOUR, minute=0),
        id="daily_weather_pipeline",
        name="Daily Weather Pipeline",
        replace_existing=True,
    )

    # Graceful shutdown on SIGTERM / SIGINT
    def _shutdown(signum, frame):
        logger.info("Received signal %s — shutting down scheduler", signum)
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    logger.info(
        "Scheduler started — pipeline will run daily at %02d:00",
        settings.SCHEDULE_HOUR,
    )
    scheduler.start()
