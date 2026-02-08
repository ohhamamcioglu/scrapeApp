import pandas as pd
import time
import random
import os
from duckduckgo_search import DDGS
from urllib.parse import urlparse

# --- Configuration ---
INPUT_FILE = "boutiquerugs_products.csv"
OUTPUT_FILE = "competitor_prices_all.csv"
MAX_RETRIES = 3
DELAY_MIN = 2
DELAY_MAX = 5  # Seconds between requests to be polite

def get_competitor_prices():
    # Load input data
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Check for existing progress
    if os.path.exists(OUTPUT_FILE):
        existing_df = pd.read_csv(OUTPUT_FILE)
        processed_ids = set(existing_df['variant_id'].astype(str))
        print(f"Resuming... {len(processed_ids)} variants already processed.")
    else:
        existing_df = pd.DataFrame(columns=[
            'variant_id', 'sku', 'title', 'variant_title', 
            'search_query', 'competitor_1_url', 'competitor_1_title', 'competitor_1_snippet',
            'competitor_2_url', 'competitor_2_title', 'competitor_2_snippet',
            'competitor_3_url', 'competitor_3_title', 'competitor_3_snippet'
        ])
        existing_df.to_csv(OUTPUT_FILE, index=False)
        processed_ids = set()

    # Iterate through variants
    total_variants = len(df)
    
    with DDGS() as ddgs:
        for index, row in df.iterrows():
            variant_id = str(row['variant_id'])
            
            if variant_id in processed_ids:
                continue
            
            sku = row['sku']
            title = row['title']
            variant_title = row['variant_title']
            
            # Strategy: Try SKU first, then Title, then broader title
            queries_to_try = [
                f'"{sku}" -site:boutiquerugs.co.uk', # Just SKU, no 'price' or 'uk' strictness
                f'Livabliss {title} -site:boutiquerugs.co.uk', # Brand + Title
                f'{title.split(" x ")[0]}' # Just product name
            ]
            
            results = []
            final_query = ""
            
            for q in queries_to_try:
                try:
                    # DuckDuckGo Search
                    print(f"[{index+1}/{total_variants}] Searching: {q}")
                    search_results = list(ddgs.text(q, region='uk-en', max_results=3))
                    
                    if search_results:
                        for res in search_results:
                            results.append({
                                'url': res.get('href'),
                                'title': res.get('title'),
                                'snippet': res.get('body')
                            })
                        final_query = q
                        break # Found results, stop trying other queries
                    
                    time.sleep(1) # Small pause between retries
                    
                except Exception as e:
                    print(f"  Error searching for {sku}: {e}")
                    time.sleep(5)
            
            # If still nothing, leave empty
            if not results:
                print(f"  No results found for {sku}")
                final_query = "ALL QUERIES FAILED"

            # Prepare row data
            row_data = {
                'variant_id': variant_id,
                'sku': sku,
                'title': title,
                'variant_title': variant_title,
                'search_query': final_query,
            }
            
            # Fill competitor columns (up to 3)
            for i in range(3):
                key_prefix = f'competitor_{i+1}'
                if i < len(results):
                    row_data[f'{key_prefix}_url'] = results[i]['url']
                    row_data[f'{key_prefix}_title'] = results[i]['title']
                    row_data[f'{key_prefix}_snippet'] = results[i]['snippet']
                else:
                    row_data[f'{key_prefix}_url'] = ""
                    row_data[f'{key_prefix}_title'] = ""
                    row_data[f'{key_prefix}_snippet'] = ""

            # Append to CSV immediately
            pd.DataFrame([row_data]).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
            
            # Sleep to report progress and avoid blocks
            sleep_time = random.uniform(DELAY_MIN, DELAY_MAX)
            time.sleep(sleep_time)

if __name__ == "__main__":
    get_competitor_prices()
