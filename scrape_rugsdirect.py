import requests
import pandas as pd
import time

def scrape_rugsdirect():
    # Using the collection specific products.json endpoint
    base_url = "https://www.rugsdirect.co.uk/collections/livabliss/products.json"
    products_list = []
    page = 1
    limit = 250
    
    while True:
        params = {
            'limit': limit,
            'page': page
        }
        
        print(f"Fetching page {page}...")
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            products = data.get('products', [])
            
            if not products:
                print("No more products found.")
                break
                
            for product in products:
                product_id = product.get('id')
                title = product.get('title')
                handle = product.get('handle')
                product_url = f"https://www.rugsdirect.co.uk/products/{handle}"
                vendor = product.get('vendor')
                product_type = product.get('product_type')
                tags = ", ".join(product.get('tags', []))
                
                variants = product.get('variants', [])
                
                for variant in variants:
                    image_data = product.get('images')
                    image_url = image_data[0].get('src') if image_data else None

                    variant_data = {
                        'product_id': product_id,
                        'title': product.get('title'),
                        'handle': handle,
                        'product_url': product_url,
                        'vendor': vendor,
                        'product_type': product.get('product_type'),
                        'tags': tags,
                        'variant_id': variant.get('id'),
                        'variant_title': variant.get('title'),
                        'sku': variant.get('sku'),
                        'price': variant.get('price'),
                        'compare_at_price': variant.get('compare_at_price'),
                        'available': variant.get('available'),
                        'grams': variant.get('grams'),
                        'image_url': image_url
                    }
                    products_list.append(variant_data)
            
            page += 1
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    # Create DataFrame and Save
    df = pd.DataFrame(products_list)
    output_file = "rugsdirect_products.csv"
    df.to_csv(output_file, index=False)
    print(f"Scraping complete. Saved {len(df)} variants to {output_file}")

if __name__ == "__main__":
    scrape_rugsdirect()
