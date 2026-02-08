import requests
import pandas as pd
import time

def scrape_incredible_rugs():
    base_url = "https://incrediblerugsanddecor.com"
    products_list = []
    page = 1
    limit = 250
    vendor_filter = "Livabliss"
    
    while True:
        url = f"{base_url}/products.json?vendor={vendor_filter}&limit={limit}&page={page}"
        print(f"Fetching page {page}...")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            products = data.get('products', [])
            
            if not products:
                print("No more products found.")
                break
                
            for product in products:
                # Basic product info
                product_id = product.get('id')
                title = product.get('title')
                handle = product.get('handle')
                product_url = f"{base_url}/products/{handle}"
                # body_html = product.get('body_html', '')
                vendor = product.get('vendor')
                product_type = product.get('product_type')
                tags = ", ".join(product.get('tags', []))
                published_at = product.get('published_at')
                
                # Images (Scrape all, join with pipe)
                images = product.get('images', [])
                image_urls = [img.get('src') for img in images]
                image_urls_str = " | ".join(image_urls)
                
                # Variants
                variants = product.get('variants', [])
                for variant in variants:
                    variant_data = {
                        'product_id': product_id,
                        'title': title,
                        'handle': handle,
                        'product_url': product_url,
                        'vendor': vendor,
                        'product_type': product_type,
                        'tags': tags,
                        'published_at': published_at,
                        'variant_id': variant.get('id'),
                        'variant_title': variant.get('title'),
                        'sku': variant.get('sku'),
                        'price': variant.get('price'),
                        'compare_at_price': variant.get('compare_at_price'),
                        'available': variant.get('available'),
                        'grams': variant.get('grams'),
                        'image_urls': image_urls_str
                    }
                    products_list.append(variant_data)
                    
            page += 1
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    # Create DataFrame and Save
    df = pd.DataFrame(products_list)
    output_file = "incredible_products.csv"
    df.to_csv(output_file, index=False)
    print(f"Scraping complete. Saved {len(df)} variants to {output_file}")

if __name__ == "__main__":
    scrape_incredible_rugs()
