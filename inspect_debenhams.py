import re
import json

def inspect_html():
    with open("debenhams_debug.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Look for algolia config
    algolia_pattern = r'algolia":(\{.*?\})'
    match = re.search(algolia_pattern, content)
    if match:
        print("\n--- Algolia Config Found ---")
        print(match.group(1))

    # Look for API Keys (generic)
    # Search for patterns like 'apiKey":"..."'
    api_k_pattern = r'"apiKey":"(.*?)"'
    keys = re.findall(api_k_pattern, content)
    if keys:
        print("\n--- Potential API Keys ---")
        for k in keys:
            print(k)

    # Look for App IDs
    app_id_pattern = r'"appId":"(.*?)"'
    app_ids = re.findall(app_id_pattern, content)
    if app_ids:
        print("\n--- Potential App IDs ---")
        for k in app_ids:
            print(k)

    # Look for product data
    # "products":[{...}]
    products_pattern = r'"products":\[(.*?)\]'
    prod_match = re.search(products_pattern, content)
    if prod_match:
        print("\n--- Products List Found (first 500 chars) ---")
        print(prod_match.group(1)[:500])
    
    # Check for specific 'Livabliss' string context
    print("\n--- 'Livabliss' Context ---")
    start = content.find("Livabliss")
    if start != -1:
        print(content[start-100:start+100])

if __name__ == "__main__":
    inspect_html()
