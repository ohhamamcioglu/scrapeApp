import requests
import json
import re

def debug_loverugs():
    base_url = "https://www.love-rugs.com/search"
    params = {'q': 'livabliss', 'options[prefix]': 'last', 'page': 1}
    
    response = requests.get(base_url, params=params)
    html = response.text
    match = re.search(r'var meta = ({.*?});', html, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        products = data.get('products', [])
        if products:
            print(json.dumps(products[0], indent=2))
        else:
            print("No products in meta.")
    else:
        print("No meta block found.")

if __name__ == "__main__":
    debug_loverugs()
