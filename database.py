import os
import json
import datetime
import urllib.parse
from typing import List, Optional, Dict, Any

LATEST_REPORT_FILE = "competitor_analysis.json"
HISTORY_FILE = "competitor_analysis_db.reports.json"

def get_latest_report_data() -> List[Dict[str, Any]]:
    """
    Reads the latest report data from competitor_analysis.json
    """
    if os.path.exists(LATEST_REPORT_FILE):
        try:
            with open(LATEST_REPORT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {LATEST_REPORT_FILE}: {e}")
    return []

def get_paginated_products(page: int = 1, limit: int = 50, search: Optional[str] = None) -> Dict[str, Any]:
    """
    Handles pagination and filtering locally from the JSON file.
    """
    data = get_latest_report_data()
    
    if search:
        search_lower = search.lower()
        data = [
            item for item in data 
            if search_lower in str(item.get("name", "")).lower()
        ]
    
    total = len(data)
    start = (page - 1) * limit
    end = start + limit
    
    paginated_data = data[start:end]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": paginated_data
    }

def get_product_history(product_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves history for a specific product from competitor_analysis_db.reports.json
    """
    decoded_id = urllib.parse.unquote(product_id)
    history = []
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                all_reports = json.load(f)
            
            for report in all_reports:
                timestamp = report.get("timestamp")
                # Handle both ISO strings and potential MongoDB-style $date dicts
                if isinstance(timestamp, dict) and "$date" in timestamp:
                    timestamp = timestamp["$date"]
                
                # Find product in this report
                products = report.get("data", [])
                for prod in products:
                    if prod.get("id") == decoded_id:
                        history.append({
                            "timestamp": timestamp,
                            "br_price": prod.get("br", {}).get("price"),
                            "lowest_competitor": prod.get("Lowest_Competitor_GBP"),
                            "competitor_name": prod.get("Competitor_Name"),
                            "rd": prod.get("rd"),
                            "deb": prod.get("deb"),
                            "lr": prod.get("lr"),
                            "inc": prod.get("inc"),
                            "margin_percent": prod.get("margin_percent")
                        })
                        break # Found it for this timestamp
        except Exception as e:
            print(f"Error reading {HISTORY_FILE}: {e}")
    
    # Sort by timestamp
    history.sort(key=lambda x: x["timestamp"])
    return history

# Compatibility placeholders or stubs if needed for main.py imports
def get_db():
    return None

COLLECTION_NAME = "reports"
