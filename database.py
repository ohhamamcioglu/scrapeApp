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
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    # Aggregation to unwind data and filter by product_id
    pipeline = [
        {"$unwind": "$data"},
        {"$match": {"data.id": product_id}},
        {"$project": {
            "_id": 0,
            "timestamp": 1,
            "br_price": "$data.br.price",
            "lowest_competitor": "$data.Lowest_Competitor_GBP",
            "competitor_name": "$data.Competitor_Name",
            # We can include specific competitors if needed
            "rd_price": "$data.rd.price",
            "deb_price": "$data.deb.price",
            "lr_price": "$data.lr.price"
        }},
        {"$sort": {"timestamp": 1}}
    ]
    
    history = list(collection.aggregate(pipeline))
    return history
