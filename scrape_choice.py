import time
import pandas as pd
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BASE_URL = "https://www.choicefurnituresuperstore.co.uk/Livabliss-Rugs-Rugs-361-797-cb.html"
OUTPUT_FILE = "choice_products.csv"

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

def scrape_choice():
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
                driver.save_screenshot("choice_attempt_2.png")
            else:
                time.sleep(random.uniform(5, 8))

            
            # Save debug info for the first page to analyze structure if needed
            if page == 1:
                with open("choice_debug.html", "w") as f:
                    f.write(driver.page_source)
                driver.save_screenshot("choice_debug.png")

            # Try to detect products
            # Common selectors for ecommerce; verified against HTML dump if this fails
            # Most sites use a container for products
            possible_selectors = [
                ".product-item", ".product-box", ".item", 
                ".product-layout", ".product-thumb",
                "div[class*='product']" 
            ]
            
            product_cards = []
            found_selector = ""
            
            for selector in possible_selectors:
                cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(cards) > 5: # Threshold to ensure we found the main grid
                    product_cards = cards
                    found_selector = selector
                    break
            
            if not product_cards:
                print("No products found (or blocked). Ending scrape.")
                driver.save_screenshot(f"choice_fail_page_{page}.png")
                break
                
            print(f"Found {len(product_cards)} products on page {page} using '{found_selector}'")
            
            for card in product_cards:
                try:
                    # Generic extraction attempts
                    title = ""
                    try:
                        title = card.find_element(By.TAG_NAME, "h4").text # Common for titles
                    except:
                        try:
                            title = card.find_element(By.CSS_SELECTOR, "a[title]").get_attribute("title")
                        except:
                            pass
                    
                    if not title:
                        title = card.text.split("\n")[0] # Fallback
                        
                    price = ""
                    try:
                        price = card.find_element(By.CSS_SELECTOR, ".price, .price-new, .special-price").text
                    except:
                        pass
                        
                    link = ""
                    try:
                        link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
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
            # Look for "Next" or "gt" (greater than) sign in pagination
            try:
                next_btns = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next') or contains(text(), '>')]")
                # Filter for actual next button
                found_next = False
                for btn in next_btns:
                    if "pagination" in btn.find_element(By.XPATH, "./..").get_attribute("class") or \
                       "links" in btn.find_element(By.XPATH, "./..").get_attribute("class"):
                        url = btn.get_attribute("href")
                        found_next = True
                        page += 1
                        break
                
                if not found_next:
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
    scrape_choice()
