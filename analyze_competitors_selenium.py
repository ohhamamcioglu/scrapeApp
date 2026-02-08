import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def test_single_scrape():
    # Setup Chrome Options (Headless for speed, or visible for debug)
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    print("Initializing Chrome Driver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Load one product to test
    df = pd.read_csv("boutiquerugs_products.csv")
    row = df.iloc[0] # First product
    sku = row['sku']
    title = row['title']
    
    # Try query
    query = f'Livabliss "{sku}" price uk -site:boutiquerugs.co.uk' 
    if " " not in sku: # Fallback query if SKU is simple/short
        query = f'Livabliss {title} price uk -site:boutiquerugs.co.uk'

    print(f"Searching Google for: {query}")
    driver.get("https://www.google.co.uk")
    
    # Accept cookies if button appears (simple attempt)
    try:
        button = driver.find_element(By.XPATH, "//button[div[contains(text(), 'Accept all')]]")
        button.click()
        time.sleep(1)
    except:
        pass

    # Search Box
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    
    time.sleep(3) # Wait for results
    driver.save_screenshot("google_result.png")

    # process results
    results = driver.find_elements(By.CSS_SELECTOR, "div.g")
    
    print(f"\nFound {len(results)} results:")
    for i, res in enumerate(results[:3]):
        try:
            link = res.find_element(By.TAG_NAME, "a").get_attribute("href")
            title_text = res.find_element(By.TAG_NAME, "h3").text
            print(f"{i+1}. {title_text}\n   {link}")
        except:
            continue

    driver.quit()

if __name__ == "__main__":
    test_single_scrape()
