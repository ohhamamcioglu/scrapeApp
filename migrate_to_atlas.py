import json
from database import save_report_to_db

def migrate():
    input_file = 'competitor_analysis.json'
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        print(f"Read {len(data)} items from {input_file}. Uploading to MongoDB Atlas...")
        
        report_id = save_report_to_db(data)
        
        print(f"Successfully migrated data! Report ID: {report_id}")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
