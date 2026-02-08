import time
import pandas as pd
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BASE_URL = "https://www.diy.com/search?term=livabliss"
OUTPUT_FILE = "diy_products_livabliss.csv"

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = uc.Chrome(options=options, version_main=144)
    return driver

def scrape_diy():
    driver = get_driver()
    products = []
    page = 1
    
    try:
        while True:
            # Construct URL with pagination
            url = f"{BASE_URL}&page={page}"
            print(f"Scraping Page {page}: {url}")
            driver.get(url)
            
            # Random sleep to look human
            time.sleep(random.uniform(3, 6))
            
            # Check for cookie banner and accept if found (only on first page usually)
            if page == 1:
                try:
                    # Generic selector for cookie buttons, adjust if needed
                    accept_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All Cookies')]"))
                    )
                    accept_btn.click()
                except:
                    pass

            # Detect products
            # Selector guesses based on common patterns, may need adjustment after first run
            # Looking for product cards. On diy.com they usually have data-test-id="product-card" or similar
            try:
                # Wait for at least one product to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-test-id='product-card']"))
                )
            except:
                print("No products found or timeout. Ending scrape.")
                # Save screenshot and HTML for debug
                driver.save_screenshot(f"debug_page_{page}.png")
                with open(f"debug_page_{page}.html", "w") as f:
                    f.write(driver.page_source)
                break
            
            product_cards = driver.find_elements(By.CSS_SELECTOR, "li[data-test-id='product-card']")
            
            if not product_cards:
                print("No product cards found on this page.")
                break
                
            print(f"Found {len(product_cards)} products on page {page}")
            
            for card in product_cards:
                try:
                    # Extract Data
                    title_el = card.find_element(By.CSS_SELECTOR, "p[data-test-id='product-title']")
                    title = title_el.text
                    
                    link_el = card.find_element(By.CSS_SELECTOR, "a[data-test-id='product-card-link']")
                    link = link_el.get_attribute("href")
                    
                    try:
                        price_el = card.find_element(By.CSS_SELECTOR, "div[data-test-id='product-primary-price']")
                        price = price_el.text.replace("\n", "").replace("£", "")
                    except:
                        price = "N/A"
                        
                    products.append({
                        'title': title,
                        'price': price,
                        'url': link,
                        'page': page
                    })
                except Exception as e:
                    # print(f"Error parsing card: {e}")
                    continue
            
            # Pagination Check
            # Check if "Next" button exists or if we've reached a limit
            # For B&Q, often the 'Next' button becomes disabled or disappears
            try:
                next_button = driver.find_elements(By.CSS_SELECTOR, "a[data-test-id='pagination-next']")
                if not next_button:
                    print("No 'Next' button found. Finished.")
                    break
                if "disabled" in next_button[0].get_attribute("class"):
                     print("'Next' button disabled. Finished.")
                     break
            except:
                print("Pagination check failed. Finished.")
                break
                
            page += 1
            
    except Exception as e:
        print(f"Global Error: {e}")
    finally:
        driver.quit()
        
    # Save Results
    df = pd.DataFrame(products)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Scraping Complete. Saved {len(df)} products to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_diy()
