import time
import pandas as pd
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BASE_URL = "https://www.ebay.co.uk/sch/i.html?_nkw=livabliss&_ipg=240"
OUTPUT_FILE = "ebay_products_livabliss.csv"

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Using version_main=144 as established in previous step
    driver = uc.Chrome(options=options, version_main=144)
    return driver

def scrape_ebay():
    driver = get_driver()
    products = []
    page = 1
    
    try:
        url = BASE_URL
        while True:
            print(f"Scraping Page {page}: {url}")
            driver.get(url)
            
            # Random sleep to look human
            time.sleep(random.uniform(3, 6))
            
            # Accept cookies if banner appears (generic attempt)
            if page == 1:
                try:
                    accept_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "gdpr-banner-accept"))
                    )
                    accept_btn.click()
                    print("Accepted cookies.")
                    time.sleep(2)
                except:
                    pass

            # Detect products
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "s-item"))
                )
            except:
                print("No products found or timeout. Ending scrape.")
                driver.save_screenshot(f"ebay_debug_page_{page}.png")
                with open(f"ebay_debug_page_{page}.html", "w") as f:
                    f.write(driver.page_source)
                break
            
            product_cards = driver.find_elements(By.CLASS_NAME, "s-item")
            
            # Filter out "Shop on eBay" pseudo-items if any (usually the first one is a header)
            valid_cards = [card for card in product_cards if "s-item__image" in card.get_attribute("innerHTML")]
            
            print(f"Found {len(valid_cards)} valid products on page {page}")
            
            if not valid_cards:
                print("No valid cards found.")
                break

            for card in valid_cards:
                try:
                    title_el = card.find_element(By.CLASS_NAME, "s-item__title")
                    title = title_el.text
                    
                    # Skip "Shop on eBay" or empty titles
                    if "Shop on eBay" in title or not title:
                        continue

                    link_el = card.find_element(By.CLASS_NAME, "s-item__link")
                    link = link_el.get_attribute("href")
                    
                    try:
                        price_el = card.find_element(By.CLASS_NAME, "s-item__price")
                        price = price_el.text
                    except:
                        price = "N/A"
                    
                    # Image src might be lazy loaded
                    try:
                        img_el = card.find_element(By.CLASS_NAME, "s-item__image-img")
                        image_url = img_el.get_attribute("src")
                    except:
                        image_url = ""

                    products.append({
                        'title': title,
                        'price': price,
                        'url': link,
                        'image_url': image_url,
                        'page': page
                    })
                except Exception as e:
                    continue
            
            # Pagination Logic
            # Look for the "Next" button aria-label="Next page" or class "pagination__next"
            try:
                next_btn = driver.find_elements(By.CSS_SELECTOR, "a[aria-label='Next page']")
                if next_btn:
                    url = next_btn[0].get_attribute("href")
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
    scrape_ebay()
