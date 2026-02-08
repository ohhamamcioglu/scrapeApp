import time
import pandas as pd
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BASE_URL = "https://www.therugshopuk.co.uk/rug-supplier/surya-rug.html"
OUTPUT_FILE = "rugshop_products.csv"

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    # Using version_main=144 as established previously
    driver = uc.Chrome(options=options, version_main=144)
    return driver

def scrape_rugshop():
    driver = get_driver()
    products = []
    page = 1
    
    try:
        url = BASE_URL
        while True:
            print(f"Scraping Page {page}: {url}")
            driver.get(url)
            
            if page == 1:
                print("Waiting for Cloudflare...")
                time.sleep(20)
                driver.save_screenshot("rugshop_attempt_1.png")
            else:
                time.sleep(random.uniform(5, 8))
            
            # Save debug info for the first page
            if page == 1:
                with open("rugshop_debug.html", "w") as f:
                    f.write(driver.page_source)

            # Try to detect products
            possible_selectors = [
                ".product-item", ".product-item-info", 
                "li.item.product", ".products-grid .item"
            ]
            
            product_cards = []
            found_selector = ""
            
            for selector in possible_selectors:
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(cards) > 1: 
                    product_cards = cards
                    found_selector = selector
                    break
            
            if not product_cards:
                print("No products found (or blocked). Ending scrape.")
                driver.save_screenshot(f"rugshop_fail_page_{page}.png")
                break
                
            print(f"Found {len(product_cards)} products on page {page} using '{found_selector}'")
            
            for card in product_cards:
                try:
                    title = ""
                    try:
                        title = card.find_element(By.CSS_SELECTOR, ".product-item-name a").text
                    except:
                        title = card.text.split("\n")[0]
                        
                    price = ""
                    try:
                        price = card.find_element(By.CSS_SELECTOR, ".price").text
                    except:
                        pass
                        
                    link = ""
                    try:
                        link = card.find_element(By.CSS_SELECTOR, ".product-item-name a").get_attribute("href")
                    except:
                        pass
                        
                    if title:
                        products.append({
                            'title': title,
                            'price': price,
                            'url': link,
                            'page': page
                        })
                except Exception as e:
                    continue
            
            # Pagination
            try:
                # Look for "Next" class or title
                next_btns = driver.find_elements(By.CSS_SELECTOR, "a.next")
                if next_btns:
                    url = next_btns[0].get_attribute("href")
                    page += 1
                else:
                    print("No Next button found. Finishing.")
                    break
            except:
                print("Pagination check failed. Finishing.")
                break
            
    except Exception as e:
        print(f"Global Error: {e}")
    finally:
        driver.quit()
        
    # Save Results
    df = pd.DataFrame(products)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Scraping Complete. Saved {len(df)} products to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_rugshop()
