from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import subprocess
import os
import logging
from database import get_latest_report, get_db, COLLECTION_NAME
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
    "scrape_rugsdirect.py",
    "scrape_debenhams_algolia.py",
    "scrape_loverugs.py"
]
REPORT_SCRIPT = "generate_json_report.py"

def run_scrapers_task():
    logger.info("Starting scrape job...")
    for script in SCRIPTS:
        try:
            logger.info(f"Running {script}...")
            python_exec = "venv/bin/python" if os.path.exists("venv/bin/python") else "python"
            subprocess.run([python_exec, script], check=True)
        except Exception as e:
            logger.error(f"Error running {script}: {e}")

    try:
        logger.info(f"Generating report...")
        python_exec = "venv/bin/python" if os.path.exists("venv/bin/python") else "python"
        subprocess.run([python_exec, REPORT_SCRIPT], check=True)
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
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    # Get latest report's timestamp first to filter by it
    latest = collection.find_one({}, sort=[("timestamp", -1)], projection={"_id": 1})
    if not latest:
        return {"total": 0, "page": page, "limit": limit, "data": []}
        
    latest_id = latest["_id"]
    
    # Aggregation Pipeline for Pagination & Search
    pipeline = [
        {"$match": {"_id": latest_id}},
        {"$unwind": "$data"},
    ]
    
    # Search Filter
    if search:
        pipeline.append({
            "$match": {
                "data.name": {"$regex": search, "$options": "i"} 
            }
        })
    
    # Pagination
    pipeline.append({"$skip": (page - 1) * limit})
    pipeline.append({"$limit": limit})
    
    # Project back to clean shape
    pipeline.append({"$replaceRoot": {"newRoot": "$data"}})
    
    data = list(collection.aggregate(pipeline))
    
    # Count Total (Separate query for efficiency or second facet)
    count_pipeline = [
        {"$match": {"_id": latest_id}},
        {"$unwind": "$data"}
    ]
    if search:
        count_pipeline.append({"$match": {"data.name": {"$regex": search, "$options": "i"}}})
    count_pipeline.append({"$count": "total"})
    
    count_res = list(collection.aggregate(count_pipeline))
    total = count_res[0]["total"] if count_res else 0
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }

@app.get("/api/history/{product_id}", response_model=List[PriceHistoryItem], dependencies=[Depends(get_api_key)])
async def get_history(product_id: str):
    from database import get_product_history
    history = get_product_history(product_id)
    return history or []

@app.get("/health")
async def health_check():
    return {"status": "ok"}
