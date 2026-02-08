import requests

url = "https://www.love-rugs.com/products/lila-becki-owens-x-livabliss-oriental-vintage-bolc2301-rug"
resp = requests.get(url)
html = resp.text

print("Searching for £257.50...")
if "257.50" in html:
    print("Found 257.50!")
    # Print context
    idx = html.find("257.50")
    print(html[idx-100:idx+100])
else:
    print("257.50 NOT found.")

print("Searching for £309...")
if "309" in html:
    print("Found 309!")
    idx = html.find("309")
    print(html[idx-100:idx+100])
else:
    print("309 NOT found.")

print("Searching for VAT or Tax...")
if "VAT" in html:
    print("Found VAT mention.")
