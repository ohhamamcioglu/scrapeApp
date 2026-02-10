import os
from pymongo import MongoClient
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Connection
# Get URI from env, simplified default removed for security/clarity in this context
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("Warning: MONGO_URI not found in environment variables.")

DB_NAME = "competitor_analysis_db"
COLLECTION_NAME = "reports"

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def save_report_to_db(report_data):
    """
    Saves the generated report to MongoDB with a timestamp.
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    document = {
        "timestamp": datetime.datetime.utcnow(),
        "data": report_data,
        "summary": {
            "total_items": len(report_data),
            # Add more summary stats if needed
        }
    }
    
    result = collection.insert_one(document)
    return str(result.inserted_id)

def get_latest_report():
    """
    Retrieves the most recent report from MongoDB.
    """
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    # Sort by timestamp descending and get the first one
    latest_report = collection.find_one({}, sort=[("timestamp", -1)])
    
    if latest_report:
        # Convert ObjectId to string for JSON serialization if needed
        latest_report['_id'] = str(latest_report['_id'])
        return latest_report
    return None

def get_product_history(product_id):
    """
    Retrieves the price history for a specific product ID.
    Returns a list of snapshots: [{timestamp, br_price, lowest_competitor_price, competitors: []}]
    """
    import urllib.parse
    # Ensure ID is decoded
    decoded_id = urllib.parse.unquote(product_id)
    
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    # Aggregation to find, unwind and filter by product_id
    # Optimization: Match documents containing the ID *before* unwinding
    # Use exact match first for speed, if empty, maybe try regex? 
    # For now, stick to exact match but ensure decoding is correct.
    pipeline = [
        {"$match": {"data.id": decoded_id}},
        {"$unwind": "$data"},
        {"$match": {"data.id": decoded_id}},
        {"$project": {
            "_id": 0,
            "timestamp": 1,
            "br_price": "$data.br.price",
            "lowest_competitor": "$data.Lowest_Competitor_GBP",
            "competitor_name": "$data.Competitor_Name",
            "rd": "$data.rd",
            "deb": "$data.deb",
            "lr": "$data.lr",
            "inc": "$data.inc",
            "hilmi": "$data.hilmi",
            "hilmi_price": "$data.hilmi.price", # Accessing nested price for history
            "margin_percent": "$data.margin_percent"
        }},
        {"$sort": {"timestamp": 1}}
    ]
    
    try:
        history = list(collection.aggregate(pipeline))
        return history
    except Exception as e:
        print(f"Error fetching history for {decoded_id}: {e}")
        return []
