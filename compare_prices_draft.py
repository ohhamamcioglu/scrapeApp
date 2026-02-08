import pandas as pd
from fuzzywuzzy import fuzz
import re

# --- Configuration ---
GBP_TO_USD = 1.25 # User specified/implied rate
OUTPUT_FILE = "final_comparison_report.csv"

# --- Load Data ---
print("Loading data...")
try:
    df_boutique = pd.read_csv("boutiquerugs_products.csv")
    df_rugsdirect = pd.read_csv("rugsdirect_products.csv")
    df_debenhams = pd.read_csv("debenhams_products.csv")
    df_incredible = pd.read_csv("incredible_products.csv")
    df_loverugs = pd.read_csv("loverugs_products.csv")
except Exception as e:
    print(f"Error loading CSVs: {e}")
    exit()

# --- Normalization Helpers ---

def normalize_price(price, currency='USD'):
    if pd.isna(price) or price == '':
        return 999999.0 # Sentinel for no price
    try:
        p = float(str(price).replace(',', '').replace('£', '').replace('$', ''))
        if currency == 'GBP':
            return round(p * GBP_TO_USD, 2)
        return p
    except:
        return 999999.0

def clean_sku(sku):
    # Remove common prefixes/suffixes to find core identifier if possible
    # Boutique: BOKM2305-31157 -> BOKM2305 (?)
    if pd.isna(sku): return ""
    return str(sku).strip().upper()

def normalize_size(size_str):
    # Convert various size formats to a standard key for matching
    # e.g., "120 x 170 cm" -> "120X170"
    # e.g., "5' x 8'" -> "5X8"
    if pd.isna(size_str): return ""
    s = str(size_str).lower().replace(' ', '')
    s = s.replace('cm', '').replace("'", '').replace('"', '').replace('feet', '')
    return s

# --- Pre-processing ---

# 1. Boutique Rugs (Base)
# Columns: product_id, title, variant_title, sku, price...
# Variant Title often: "Colour / Size" e.g., "Grey / 120 x 170 cm"
print("Processing Boutique Rugs...")
df_boutique['norm_price'] = df_boutique['price'].apply(lambda x: normalize_price(x, 'USD'))
df_boutique['norm_sku'] = df_boutique['sku'].apply(clean_sku)
# Extract size from variant_title
def extract_boutique_size(v_title):
    if pd.isna(v_title): return ""
    parts = v_title.split('/')
    if len(parts) > 1:
        return normalize_size(parts[-1])
    return normalize_size(v_title)
df_boutique['norm_size'] = df_boutique['variant_title'].apply(extract_boutique_size)


# 2. Rugs Direct (Target - GBP)
# Columns: id, title, handle... variant_sku, variant_price, variant_option1 (Size?)
print("Processing Rugs Direct...")
# Need to check actual headers from 'head' command output but making assumptions based on typical Shopify scrape
# Assuming: variant_price, variant_sku, variant_title (or option1/2)
if 'variant_price' in df_rugsdirect.columns:
    df_rugsdirect['norm_price'] = df_rugsdirect['variant_price'].apply(lambda x: normalize_price(x, 'USD')) # Already converted? No, usually native.
    # Wait, check if scrape_rugsdirect.py converted it? usually generic scraper dumps raw. Assuming GBP.
    # Actually wait, I need to be sure. I'll check the 'head' output in next turn if needed, but safe to assume it's GBP for .co.uk
    df_rugsdirect['norm_price'] = df_rugsdirect['variant_price'].apply(lambda x: normalize_price(x, 'GBP'))
else:
    # Fallback/Guess keys
    pass 
# ... (Will refine field names after seeing 'head' output)

# 3. Debenhams (Target - GBP)
# Columns: product_id, title, price, size, sku...
print("Processing Debenhams...")
df_debenhams['norm_price'] = df_debenhams['price'].apply(lambda x: normalize_price(x, 'GBP'))
df_debenhams['norm_size'] = df_debenhams['size'].apply(normalize_size)
df_debenhams['norm_sku'] = df_debenhams['sku'].apply(clean_sku)

# 4. Incredible Rugs (Target - USD)
print("Processing Incredible Rugs...")
# columns: ...
# Assumption: price is USD
pass

# 5. Love Rugs (Target - GBP)
print("Processing Love Rugs...")
pass

# --- Matching Logic ---
# Iterate over Boutique Rugs
results = []

print("Starting Matching...")
for index, row in df_boutique.iterrows():
    b_title = row['title']
    b_sku = row['norm_sku']
    b_size = row['norm_size']
    b_price = row['norm_price']
    
    match_data = {
        'Boutique_Title': b_title,
        'Boutique_Variant': row['variant_title'],
        'Boutique_SKU': row['sku'],
        'Boutique_Price_USD': b_price,
        'RugsDirect_Price_USD': 'N/A',
        'Debenhams_Price_USD': 'N/A',
        'Incredible_Price_USD': 'N/A',
        'LoveRugs_Price_USD': 'N/A',
        'Best_Competitor_Price_USD': 999999.0,
        'Best_Competitor': 'N/A'
    }
    
    # -- Match Debenhams --
    # Strategy: Fuzzy match Title OR Exact Match SKU (unlikely if internal SKUs differ)
    # AND Match Size
    
    # Subset Debenhams by Size first to reduce search space? Or Title?
    # Fuzzy match title first
    
    # (Simple logic for now - optimization later)
    # Filter Debenhams by Size
    deb_candidates = df_debenhams[df_debenhams['norm_size'] == b_size]
    
    best_deb_score = 0
    best_deb_price = None
    
    for _, d_row in deb_candidates.iterrows():
        # Compare Titles
        # Debenhams Title: "Lilian Collection ... - Camel - 66x120"
        # Boutique Title: "Tansy Machine Washable..."
        score = fuzz.token_sort_ratio(b_title, d_row['base_title'])
        if score > 85: # Threshold
            if score > best_deb_score:
                best_deb_score = score
                best_deb_price = d_row['norm_price']
    
    if best_deb_price:
        match_data['Debenhams_Price_USD'] = best_deb_price
        if best_deb_price < match_data['Best_Competitor_Price_USD']:
            match_data['Best_Competitor_Price_USD'] = best_deb_price
            match_data['Best_Competitor'] = 'Debenhams'

    # -- Match Rugs Direct --
    # ... (Similar logic)
    
    # -- Match Incredible --
    # ...
    
    # -- Match Love Rugs --
    # ...
    
    if match_data['Best_Competitor_Price_USD'] == 999999.0:
        match_data['Best_Competitor_Price_USD'] = 'N/A'
    
    results.append(match_data)

# --- Save ---
final_df = pd.DataFrame(results)
final_df.to_csv(OUTPUT_FILE, index=False)
print("Done.")
