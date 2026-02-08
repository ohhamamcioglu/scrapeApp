import time
import pandas as pd
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Configuration
BASE_URL = "https://www.debenhams.com/categories/brands-livabliss"
OUTPUT_FILE = "debenhams_products.csv"

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

def scrape_debenhams():
    driver = get_driver()
    products_list = []
    
    try:
        print(f"Opening {BASE_URL}...")
        driver.get(BASE_URL)
        
        # Wait for potential Cloudflare/WAF challenge
        time.sleep(10)
        
        # Check if we are blocked
        title = driver.title
        print(f"Page Title: {title}")
        
        if "Access Denied" in title or "Challenge" in title:
            print("Blocked by WAF.")
            # Take screenshot
            driver.save_screenshot("debenhams_blocked.png")
            return

        # Attempt to find product cards
        # Debenhams likely uses specific data-test-ids or classes
        # We'll dump the source to check if needed, but let's try generic selectors first
        
        # Scroll down to trigger lazy load
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
        # Try to find JSON in script tag if DOM scraping is hard
        # Look for window.__PRELOADED_STATE__ or similar
        try:
             # This is a React app, often has a hydration state in a script tag
            scripts = driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                content = script.get_attribute("innerHTML")
                if "listingContent" in content and "products" in content:
                    print("Found hydration script!")
                    # Just saving the raw content to debug file for now
                    with open("debenhams_hydration.js", "w") as f:
                        f.write(content)
                    break
        except Exception as e:
            print(f"Error checking scripts: {e}")

        # Fallback: DOM Scraping
        # Looking for generic product card elements
        # Based on previous HTML dump: <div data-test-id="product-card"> or similar?
        # Actually checking 'debenhams_debug.html' again...
        # It was mostly empty/initial shell.
        
        # Let's save the rendered HTML to inspect
        with open("debenhams_rendered.html", "w") as f:
            f.write(driver.page_source)
            
        print("Saved rendered HTML to debenhams_rendered.html")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_debenhams()
