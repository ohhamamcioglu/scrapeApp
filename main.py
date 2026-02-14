from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import subprocess
import os
import logging
from database import get_db, COLLECTION_NAME
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from typing import List, Optional

# New Modules
from models import ProductItem, PaginatedResponse, ScrapeResponse, PriceHistoryItem
from auth import get_api_key

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler Setup
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    trigger = CronTrigger(hour=3, minute=0)
    scheduler.add_job(run_scrapers_task, trigger=trigger, id="daily_scrape")
    scheduler.start()
    logger.info("Scheduler started.")
    yield
    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped.")

app = FastAPI(title="Competitor Price Scraper API", version="2.0", lifespan=lifespan)

SCRIPTS = [
    "scrape.py",
    "scrape_rugsdirect.py",
    "scrape_debenhams_algolia.py",
    "scrape_loverugs.py"
]
REPORT_SCRIPT = "generate_json_report.py"

def run_scrapers_task():
    logger.info("Starting scrape job...")
    import sys
    python_exec = sys.executable 

    for script in SCRIPTS:
        try:
            logger.info(f"Running {script} with {python_exec}...")
            # Use sys.executable to ensure we use the same python running the app
            result = subprocess.run([python_exec, script], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error running {script}: {result.stderr}")
            else:
                logger.info(f"Finished {script}: {result.stdout[:100]}...") # Log first 100 chars
        except Exception as e:
            logger.error(f"Exception running {script}: {e}")

    try:
        logger.info(f"Generating report with {python_exec}...")
        result = subprocess.run([python_exec, REPORT_SCRIPT], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Error generating report: {result.stderr}")
        else:
            logger.info(f"Report generated: {result.stdout[:100]}...")
    except Exception as e:
        logger.error(f"Error generating report: {e}")
    logger.info("Scrape job finished.")

@app.post("/api/scrape", response_model=ScrapeResponse, dependencies=[Depends(get_api_key)])
async def trigger_scrape(background_tasks: BackgroundTasks):
    """
    Triggers a full scrape. Protected by API Key.
    """
    background_tasks.add_task(run_scrapers_task)
    return {"message": "Scraping started in background."}

@app.get("/api/products", response_model=PaginatedResponse, dependencies=[Depends(get_api_key)])
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = None
):
    """
    Retrieves paginated product data from the latest report.
    Supports search by product name.
    """
    from database import get_paginated_products
    return get_paginated_products(page=page, limit=limit, search=search)

@app.get("/api/history/{product_id}", response_model=List[PriceHistoryItem], dependencies=[Depends(get_api_key)])
async def get_history(product_id: str):
    from database import get_product_history
    history = get_product_history(product_id)
    return history or []

@app.get("/health")
async def health_check():
    return {"status": "ok"}
