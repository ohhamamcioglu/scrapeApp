import requests
import pandas as pd
import time
import json

def scrape_debenhams_algolia():
    # Algolia credentials found via browser agent
    APP_ID = "HNC30IYYNP"
    API_KEY = "6e5de83d201b6bdaac45d449a9466a42"
    INDEX_NAME = "debenhams-dbz-prod"
    
    url = f"https://{APP_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/query"
    
    headers = {
        "X-Algolia-API-Key": API_KEY,
        "X-Algolia-Application-Id": APP_ID,
        "Content-Type": "application/json"
    }
    
    products_list = []
    page = 0
    hits_per_page = 100 # Algolia usually allows up to 1000, keep it safe
    
    while True:
        payload = {
            "query": "",
            "filters": "brand:Livabliss",
            "page": page,
            "hitsPerPage": hits_per_page
        }
        
        print(f"Fetching page {page}...")
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            hits = data.get('hits', [])
            nb_pages = data.get('nbPages', 0)
            nb_hits = data.get('nbHits', 0)
            
            print(f"Found {len(hits)} hits (Total expected: {nb_hits})")
            
            if not hits:
                break
                
            for hit in hits:
                product_id = hit.get('productKey') or hit.get('objectID')
                base_title = hit.get('name')
                url_slug = hit.get('slug')
                product_url = f"https://www.debenhams.com/product/{url_slug}" if url_slug else "N/A"
                brand = hit.get('brand')
                
                # Variants parsing
                # Debenhams stores variant pricing in 'pricesBySize' usually
                pricing_variants = hit.get('pricesBySize', [])
                
                # If no specific variant pricing, fallback to base info
                if not pricing_variants:
                    item_data = {
                        'product_id': product_id,
                        'title': base_title, # No specific size
                        'url': product_url,
                        'sku': hit.get('sku') or product_id,
                        'price': hit.get('price', 0), # Base price
                        'size': 'N/A',
                        'brand': brand,
                        'image_url': hit.get('media', {}).get('images', [{}])[0].get('url') # speculative
                    }
                    products_list.append(item_data)
                    continue

                for variant_group in pricing_variants:
                    # variant_group usually contains 'colour' and 'sizePrices' or just direct list
                    # Structure seen in debug: [{'colour': 'Camel', 'sizePrices': [...]}]
                    
                    colour_name = variant_group.get('colour', 'Default')
                    size_prices = variant_group.get('sizePrices', [])
                    
                    for sp in size_prices:
                        # sp structure: {'price': {'centamount': 40.99, ...}, 'size': '66cm x 120cm'}
                        price_info = sp.get('price', {})
                        # 'centamount' appears to be the actual price.
                        # Observed behavior: Some items are 40.99 (float £), some are 6699 (int pennies).
                        # Heuristic: If price > 2000, assumes pennies.
                        raw_price = price_info.get('centamount', 0)
                        if raw_price > 2000:
                            price = raw_price / 100.0
                        else:
                            price = raw_price
                        
                        size = sp.get('size')
                        
                        # Variant Title = Base Title + Size + Colour
                        variant_title = f"{base_title} - {colour_name} - {size}"
                        
                        # Extract Image
                        # Debug structure shows 'images': ['url1', 'url2'] at root level
                        image_list = hit.get('images', [])
                        image_url = image_list[0] if image_list else None
                        
                        item_data = {
                            'product_id': product_id,
                            'title': variant_title,
                            'base_title': base_title,
                            'url': product_url,
                            'sku': product_id, 
                            'price': price,
                            'size': size,
                            'colour': colour_name,
                            'brand': brand,
                            'status': 'Available', 
                            'image_url': image_url
                        }
                        products_list.append(item_data)
            
            if page >= nb_pages - 1:
                print("Reached last page.")
                break
                
            page += 1
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    # Create DataFrame and Save
    df = pd.DataFrame(products_list)
    output_file = "debenhams_products.csv"
    df.to_csv(output_file, index=False)
    print(f"Scraping complete. Saved {len(df)} products to {output_file}")

if __name__ == "__main__":
    scrape_debenhams_algolia()
