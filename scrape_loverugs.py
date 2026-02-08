import requests
import pandas as pd
import json
import re
import time

def scrape_loverugs():
    # Parsing the 'var meta = ...' JSON block from the HTML search results
    base_url = "https://www.love-rugs.com/search"
    products_list = []
    seen_product_ids = set()
    page = 1
    query = "livabliss"
    
    while True:
        params = {
            'q': query,
            'options[prefix]': 'last',
            'page': page
        }
        
        print(f"Fetching page {page}...")
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            html = response.text
            
            # Extract the 'var meta = {...};' block
            # Regex to find the variable assignment until the terminating semicolon
            match = re.search(r'var meta = ({.*?});', html, re.DOTALL)
            
            if not match:
                print("Could not find 'var meta' block. Ending scrape.")
                # This might happen if there are no results or structure changes
                break
                
            json_str = match.group(1)
            data = json.loads(json_str)
            
            products = data.get('products', [])
            
            if not products:
                print("No products in meta block. Ending scrape.")
                break

            new_products_count = 0
            for product in products:
                product_id = product.get('id')
                if product_id in seen_product_ids:
                    continue
                seen_product_ids.add(product_id)
                new_products_count += 1
                
                # ... (rest of processing) ...
                
                base_title = product.get('handle').replace('-', ' ').title()
                handle = product.get('handle')
                product_url = f"https://www.love-rugs.com/products/{handle}"
                
                # Fetch detailed JSON for image
                json_url = f"{product_url}.json"
                image_url = None
                try:
                    # polite delay
                    time.sleep(0.2) 
                    p_resp = requests.get(json_url)
                    if p_resp.status_code == 200:
                        p_data = p_resp.json()
                        # Shopify JSON structure: {'product': {'image': {'src': '...'}, 'images': [...]}}
                        img_obj = p_data.get('product', {}).get('image')
                        if img_obj:
                            image_url = img_obj.get('src')
                except Exception as e:
                    print(f"Error fetching detail {handle}: {e}")
                
                vendor = product.get('vendor')
                
                variants = product.get('variants', [])
                
                for variant in variants:
                    variant_data = {
                        'product_id': product_id,
                        'title': variant.get('name'), 
                        'handle': handle,
                        'product_url': product_url,
                        'vendor': vendor,
                        'variant_id': variant.get('id'),
                        'sku': variant.get('sku'),
                        'price': (variant.get('price', 0) / 100.0) / 1.2, # User sees Ex-VAT prices (~16.6% lower)
                        'variant_public_title': variant.get('public_title'),
                        'image_url': image_url
                    }
                    products_list.append(variant_data)
            
            if new_products_count == 0:
                print("No new products found on this page (Duplicate Page). Ending scrape.")
                break
                
            page += 1
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

            
    # Create DataFrame and Save
    df = pd.DataFrame(products_list)
    output_file = "loverugs_products.csv"
    df.to_csv(output_file, index=False)
    print(f"Scraping complete. Saved {len(df)} variants to {output_file}")

if __name__ == "__main__":
    scrape_loverugs()
