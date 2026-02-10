import pandas as pd
from fuzzywuzzy import fuzz
import json
import re

# --- Configuration ---
OUTPUT_FILE = "competitor_analysis.json"

# --- Load Data ---
print("Loading data...")
try:
    df_boutique = pd.read_csv("boutiquerugs_products.csv")
    df_rugsdirect = pd.read_csv("rugsdirect_products.csv") # Has image_url
    df_debenhams = pd.read_csv("debenhams_products.csv") 
    df_loverugs = pd.read_csv("loverugs_products.csv") 
    df_incredible = pd.read_csv("incredible_products.csv")
    df_hilmi = pd.read_csv("hilmi_prices.csv")
except Exception as e:
    print(f"Error loading CSVs: {e}")
    exit()

# --- Pre-processing Hilmi Prices ---
print("Processing Hilmi Prices...")
hilmi_prices_map = {}
if 'SKU' in df_hilmi.columns and 'Supplier Price' in df_hilmi.columns:
    for _, row in df_hilmi.iterrows():
        sku = str(row['SKU']).strip().upper()
        try:
            price = float(str(row['Supplier Price']).replace(',', '').strip())
            hilmi_prices_map[sku] = price
        except:
            continue


# --- Normalization Helpers ---

def clean_price(price):
    if pd.isna(price) or price == '': return None
    try:
        p_str = str(price).replace(',', '').replace('£', '').replace('$', '').strip()
        return float(p_str)
    except: return None

def format_price(price, currency="£"):
    if price is None: return None
    return f"{currency}{price:.2f}"

def normalize_size(size_str):
    if pd.isna(size_str): return ""
    s = str(size_str).lower().replace(' ', '')
    s = s.replace('cm', '').replace('feet', '').replace("'", '').replace('"', '')
    s = s.replace('rectangle', '').replace('runner', '').replace('round', '')
    
    # Sort dimensions: 170x120 -> 120x170
    # Find numbers separated by x (allow extra chars like 'cm', spaces, 'L', 'W')
    match = re.search(r'(\d+).*?[xX].*?(\d+)', s)
    if match:
        d1, d2 = int(match.group(1)), int(match.group(2))
        return f"{min(d1, d2)}x{max(d1, d2)}"
    
    return s.strip()

def clean_sku(sku):
    if pd.isna(sku): return ""
    return str(sku).strip().upper()

def get_image(row, col_name='image_url'):
    # Helper to safely get image
    if col_name in row and pd.notna(row[col_name]):
        return row[col_name]
    # For Debenhams, checking 'image_url' column existence
    # We will check columns dynamically
    return None

# --- Pre-processing DataFrames ---

print("Processing Boutique Rugs...")
df_boutique['clean_price'] = df_boutique['price'].apply(clean_price)
# Use the updated normalize_size function
df_boutique['clean_size'] = df_boutique['variant_title'].apply(lambda x: normalize_size(str(x).split('/')[-1]) if '/' in str(x) else normalize_size(x))

print("Processing Rugs Direct...")
df_rugsdirect['clean_price'] = df_rugsdirect['price'].apply(clean_price)
df_rugsdirect['clean_size'] = df_rugsdirect['variant_title'].apply(normalize_size)

print("Processing Debenhams...")
df_debenhams['clean_price'] = df_debenhams['price'].apply(clean_price)
df_debenhams['clean_size'] = df_debenhams['size'].apply(normalize_size)
df_debenhams['base_title'] = df_debenhams['base_title'].fillna('')

print("Processing Love Rugs...")
df_loverugs['clean_price'] = df_loverugs['price'].apply(clean_price)
df_loverugs['clean_size'] = df_loverugs['variant_public_title'].apply(normalize_size)

print("Processing Incredible Rugs...")
df_incredible['clean_price'] = df_incredible['price'].apply(clean_price)
df_incredible['clean_size'] = df_incredible['variant_title'].apply(normalize_size)

# --- Indexing (Size Based) ---

def build_index(df, size_col):
    index = {}
    for _, row in df.iterrows():
        # Key by Normalized Size
        key = str(row[size_col])
        if not key: continue
        if key not in index: index[key] = []
        index[key].append(row)
    return index

print("Building indices (Size-Based)...")
idx_rugsdirect = build_index(df_rugsdirect, 'clean_size')
idx_debenhams = build_index(df_debenhams, 'clean_size')
idx_loverugs = build_index(df_loverugs, 'clean_size')
idx_incredible = build_index(df_incredible, 'clean_size')

# --- Matching & JSON Construction ---

json_output = []
print("Generating JSON Report...")

for idx, b_row in df_boutique.iterrows():
    b_title = str(b_row['title'])
    b_size_clean = b_row['clean_size']
    b_size_orig = b_row['variant_title']
    b_price = b_row['clean_price']
    b_url = b_row['product_url']
    
    # Boutique Image: 'image_urls' (pipe separated?)
    b_image = ""
    if 'image_urls' in b_row and pd.notna(b_row['image_urls']):
        b_image = str(b_row['image_urls']).split(' | ')[0]
    
    if pd.isna(b_price): continue
    
    # Unique ID
    # Sluggify title + size
    safe_title = re.sub(r'[^a-zA-Z0-9]', '-', b_title.lower())
    safe_size = re.sub(r'[^a-zA-Z0-9]', '-', b_size_orig.lower())
    item_id = f"{safe_title}-{safe_size}"
    
    item_data = {
        "id": item_id,
        "name": b_title,
        "dimension": b_size_orig,
        "br": {
            "price": b_price,
            "formattedPrice": format_price(b_price),
            "url": b_url,
            "image": b_image,
            "size": b_size_orig
        },
        "rd": None,
        "deb": None,
        "lr": None
    }
    
    # --- Rugs Direct Match ---
    rd_candidates = idx_rugsdirect.get(b_size_clean, [])
    best_rd_score = 0
    best_rd_match = None
    
    # Keyword/Collection check (First word must match)
    b_first_word = b_title.split(' ')[0].lower()
    
    for row in rd_candidates:
        r_title_words = str(row['title']).lower().split(' ')
        # Enforce that the first word of Boutique title exists in target title (or vice versa is close)
        # Exception: 'The' or generic words. Assuming simplified first words like 'Kimi', 'Lilian'.
        if b_first_word not in str(row['title']).lower():
             # Strict check: Kimi != Rivi.
             continue
             
        score = fuzz.token_set_ratio(b_title, row['title'])
        if score > 65 and score > best_rd_score: # Raised threshold + word check
             best_rd_score = score
             best_rd_match = row
             
    if best_rd_match is not None:
        item_data["rd"] = {
            "price": best_rd_match['clean_price'],
            "formattedPrice": format_price(best_rd_match['clean_price']),
            "url": best_rd_match['product_url'],
            "image": get_image(best_rd_match, 'image_url'),
            "size": best_rd_match['variant_title']
        }

    # --- Debenhams Match ---
    deb_candidates = idx_debenhams.get(b_size_clean, [])
    best_deb_score = 0
    best_deb_match = None
    for row in deb_candidates:
        # Debenhams Base Title check
        if b_first_word not in str(row['base_title']).lower():
            continue

        score = fuzz.token_set_ratio(b_title, row['base_title'])
        if score > 60 and score > best_deb_score:
             best_deb_score = score
             best_deb_match = row

    if best_deb_match is not None:
        item_data["deb"] = {
            "price": best_deb_match['clean_price'],
            "formattedPrice": format_price(best_deb_match['clean_price']),
            "url": best_deb_match['url'],
            "image": get_image(best_deb_match, 'image_url'), 
            "size": best_deb_match['size']
        }

    # --- Love Rugs Match ---
    lr_candidates = idx_loverugs.get(b_size_clean, [])
    best_lr_score = 0
    best_lr_match = None
    for row in lr_candidates:
        if b_first_word not in str(row['title']).lower():
            continue

        score = fuzz.token_set_ratio(b_title, row['title'])
        if score > 60 and score > best_lr_score:
             best_lr_score = score
             best_lr_match = row

    if best_lr_match is not None:
        item_data["lr"] = {
            "price": best_lr_match['clean_price'],
            "formattedPrice": format_price(best_lr_match['clean_price']),
            "url": best_lr_match['product_url'],
            "image": get_image(best_lr_match, 'image_url'),
            "size": best_lr_match['variant_public_title']
        }

    # --- Incredible Match (Reference) ---
    inc_candidates = idx_incredible.get(b_size_clean, [])
    best_inc_score = 0
    best_inc_match = None
    for row in inc_candidates:
        score = fuzz.token_set_ratio(b_title, row['title'])
        if score > 45 and score > best_inc_score:
             best_inc_score = score
             best_inc_match = row
             
    if best_inc_match is not None:
        item_data["inc"] = {
            "price": best_inc_match['clean_price'], # USD
            "formattedPrice": format_price(best_inc_match['clean_price'], "$"),
            "url": best_inc_match['product_url'],
            "image": get_image(best_inc_match, 'image_urls'),
            "size": best_inc_match['variant_title']
        }
        item_data["Incredible_Price_USD"] = best_inc_match['clean_price']
    else:
        item_data["inc"] = None
        item_data["Incredible_Price_USD"] = None

    # --- Hilmi (Supplier) Price Match ---
    b_sku = str(b_row.get('sku', '')).strip().upper()
    hilmi_price = None
    if b_sku in hilmi_prices_map:
        hilmi_price = hilmi_prices_map[b_sku]
        item_data["hilmi"] = {
            "price": hilmi_price,
            "formattedPrice": format_price(hilmi_price),
            "url": None, # No URL for supplier
            "image": None,
            "size": None
        }
        
        # Calculate Margin
        if b_price and hilmi_price and b_price > 0:
            margin = b_price - hilmi_price
            margin_percent = (margin / b_price) * 100
            item_data["margin_gbp"] = round(margin, 2)
            item_data["margin_percent"] = round(margin_percent, 2)
        else:
            item_data["margin_gbp"] = None
            item_data["margin_percent"] = None
    else:
        item_data["hilmi"] = None
        item_data["margin_gbp"] = None
        item_data["margin_percent"] = None

    # --- Analysis & Summary ---
    competitors = []
    if item_data["rd"]: competitors.append( (item_data["rd"]["price"], "RugsDirect") )
    if item_data["deb"]: competitors.append( (item_data["deb"]["price"], "Debenhams") )
    if item_data["lr"]: competitors.append( (item_data["lr"]["price"], "LoveRugs") )
    
    if competitors:
        min_price, min_comp_name = min(competitors, key=lambda x: x[0])
        item_data["Lowest_Competitor_GBP"] = min_price
        item_data["Competitor_Name"] = min_comp_name
        item_data["Price_Difference_GBP"] = round(min_price - b_price, 2)
        if b_price > 0:
            item_data["Price_Difference_Percent"] = round(((min_price - b_price) / b_price) * 100, 2)
        else:
            item_data["Price_Difference_Percent"] = 0.0
    else:
        item_data["Lowest_Competitor_GBP"] = None
        item_data["Competitor_Name"] = None
        item_data["Price_Difference_GBP"] = None
        item_data["Price_Difference_Percent"] = None

    json_output.append(item_data)

# --- Save ---
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, indent=2)

print(f"JSON Report Generated: {OUTPUT_FILE}")
print(f"Total Items: {len(json_output)}")

# --- Save to MongoDB ---
try:
    from database import save_report_to_db
    report_id = save_report_to_db(json_output)
    print(f"Report saved to MongoDB with ID: {report_id}")
except Exception as e:
    print(f"Error saving to MongoDB: {e}")
    # Don't fail the script if DB save fails, just log it

