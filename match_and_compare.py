import pandas as pd
from fuzzywuzzy import fuzz
import re

# --- Configuration ---
OUTPUT_FILE = "UK_Competitor_Analysis_Report.csv"

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

def clean_price(price):
    if pd.isna(price) or price == '':
        return None
    try:
        # Remove currency symbols and commas
        p_str = str(price).replace(',', '').replace('£', '').replace('$', '').strip()
        return float(p_str)
    except:
        return None

def normalize_size(size_str):
    if pd.isna(size_str): return ""
    # Standardize to roughly "120x170" format
    # Lowercase, remove spaces
    s = str(size_str).lower().replace(' ', '')
    # Remove units for cleaner comparison if needed, or keep 'cm'
    # "120x170cm" -> "120x170"
    s = s.replace('cm', '').replace('feet', '').replace("'", '').replace('"', '')
    # "rectangle", "runner" removal
    s = s.replace('rectangle', '').replace('runner', '').replace('round', '')
    return s.strip()

def clean_sku(sku):
    if pd.isna(sku): return ""
    # Remove common vendor prefixes if known, otherwise just strip
    # Boutique SKUs seem to be clean "BOKM2305-31157"
    return str(sku).strip().upper()

# --- Pre-processing DataFrames ---

print("Processing Boutique Rugs...")
df_boutique['clean_price'] = df_boutique['price'].apply(clean_price)
df_boutique['clean_sku'] = df_boutique['sku'].apply(clean_sku)
# Boutique variant title: "Colour / Size" usually
def extract_boutique_size(v_title):
    if pd.isna(v_title): return ""
    parts = str(v_title).split('/')
    if len(parts) > 1:
        return normalize_size(parts[-1])
    return normalize_size(v_title)
df_boutique['clean_size'] = df_boutique['variant_title'].apply(extract_boutique_size)

print("Processing Rugs Direct...")
# Rugs Direct usually has Size in 'variant_title' -> "66cm x 115cm Rectangle"
df_rugsdirect['clean_price'] = df_rugsdirect['price'].apply(clean_price)
df_rugsdirect['clean_sku'] = df_rugsdirect['sku'].apply(clean_sku)
df_rugsdirect['clean_size'] = df_rugsdirect['variant_title'].apply(normalize_size)

print("Processing Debenhams...")
df_debenhams['clean_price'] = df_debenhams['price'].apply(clean_price)
# Debenhams size is in 'size' column
df_debenhams['clean_size'] = df_debenhams['size'].apply(normalize_size)
df_debenhams['clean_sku'] = df_debenhams['sku'].apply(clean_sku)
df_debenhams['base_title'] = df_debenhams['base_title'].fillna('')

print("Processing Love Rugs...")
df_loverugs['clean_price'] = df_loverugs['price'].apply(clean_price)
df_loverugs['clean_sku'] = df_loverugs['sku'].apply(clean_sku)
# Love Rugs variant_public_title -> "170 x 120cm"
df_loverugs['clean_size'] = df_loverugs['variant_public_title'].apply(normalize_size)

print("Processing Incredible Rugs (USD Ref)...")
df_incredible['clean_price'] = df_incredible['price'].apply(clean_price)
df_incredible['clean_sku'] = df_incredible['sku'].apply(clean_sku)
# Incredible variant_title -> "20'' L X 20'' W Accent Pillow Square"
df_incredible['clean_size'] = df_incredible['variant_title'].apply(normalize_size)


# --- Matching Engine Optimized ---

results = []
print("Starting Matching Algorithm (Optimized)...")

# Indexing for Speed
# Create a dictionary mapping "First Word of Title" -> List of Rows (as dicts)
# This avoids scanning the entire dataframe for every query

def build_index(df, title_col):
    index = {}
    for _, row in df.iterrows():
        title = str(row[title_col])
        if not title: continue
        key = title.split(' ')[0].lower() # Normalize key
        if len(key) < 3: continue # Skip very short common words? No, keep them but be aware of collisions
        if key not in index:
            index[key] = []
        index[key].append(row)
    return index

print("Building indices...")
idx_rugsdirect = build_index(df_rugsdirect, 'title')
idx_debenhams = build_index(df_debenhams, 'base_title')
idx_loverugs = build_index(df_loverugs, 'title')
idx_incredible = build_index(df_incredible, 'title') # Critical optimization for 115k rows

competitor_indices = [
    {'name': 'RugsDirect', 'index': idx_rugsdirect, 'curr': 'GBP'},
    {'name': 'Debenhams', 'index': idx_debenhams, 'curr': 'GBP'},
    {'name': 'LoveRugs', 'index': idx_loverugs, 'curr': 'GBP'},
]

for idx, b_row in df_boutique.iterrows():
    b_title = str(b_row['title'])
    b_size = b_row['clean_size']
    b_price = b_row['clean_price']
    b_sku = b_row['clean_sku']
    
    if pd.isna(b_price): continue
    
    # Define Lookup Key
    search_key = b_title.split(' ')[0].lower()

    row_data = {
        'Product_Title': b_title,
        'SKU': b_sku,
        'Size': b_row['variant_title'], # Display original
        'Boutique_Price_GBP': b_price,
        'RugsDirect_Price_GBP': None,
        'Debenhams_Price_GBP': None,
        'LoveRugs_Price_GBP': None,
        'Incredible_Price_USD': None,
        'Lowest_Competitor_GBP': None,
        'Competitor_Name': None,
        'Price_Difference_GBP': None,
        'Price_Difference_Percent': None,
        'Match_Method': None
    }
    
    # 1. Match Incredible Rugs (USD Reference)
    candidates = idx_incredible.get(search_key, [])
    # Optimization: If too many candidates (common word like "The"), limit fuzzy match or skip?
    # For now, just proceed, it's much faster than 115k.
    
    best_inc_score = 0
    best_inc_price = None
    
    for inc_row in candidates:
        # Strict Size Filter first
        if inc_row['clean_size'] != b_size:
             # Fast substring check
             if b_size not in inc_row['clean_size']: continue
             
        score = fuzz.token_set_ratio(b_title, inc_row['title'])
        if score > 85:
            if score > best_inc_score:
                best_inc_score = score
                best_inc_price = inc_row['clean_price']
    
    row_data['Incredible_Price_USD'] = best_inc_price
    
    # 2. Match Main Competitors (GBP)
    competitor_prices = []
    
    for comp in competitor_indices:
        comp_name = comp['name']
        comp_idx = comp['index']
        
        candidates = comp_idx.get(search_key, [])
        if not candidates: continue
        
        best_match_score = 0
        best_match_price = None
        match_type = ""
        
        for comp_row in candidates:
            # Size Check (Crucial)
            c_size = comp_row['clean_size']
            
            # Fast size match
            size_match = (b_size == c_size) or (b_size and c_size and (b_size in c_size or c_size in b_size))
            if not size_match: continue
            
            # Title Fuzzy Match
            if comp_name == 'Debenhams':
                 comp_title = comp_row['base_title']
            else:
                 comp_title = comp_row['title']

            score = fuzz.token_sort_ratio(b_title, comp_title)
            
            if score > 85:
                if score > best_match_score:
                    best_match_score = score
                    best_match_price = comp_row['clean_price']
                    match_type = "Fuzzy Title + Size"
        
        # Save competitor result
        if best_match_price is not None:
            row_data[f'{comp_name}_Price_GBP'] = best_match_price
            competitor_prices.append((best_match_price, comp_name))
            if not row_data['Match_Method']: row_data['Match_Method'] = match_type
            
    # Calculate Lowest
    if competitor_prices:
        min_price, min_competitor = min(competitor_prices, key=lambda x: x[0])
        row_data['Lowest_Competitor_GBP'] = min_price
        row_data['Competitor_Name'] = min_competitor
        row_data['Price_Difference_GBP'] = min_price - b_price
        # handling division by zero just in case
        if b_price > 0:
            row_data['Price_Difference_Percent'] = round(((min_price - b_price) / b_price) * 100, 2)
        else:
            row_data['Price_Difference_Percent'] = 0.0

    results.append(row_data)

# --- Save Report ---
df_final = pd.DataFrame(results)

# Reorder columns
cols = [
    'Product_Title', 'SKU', 'Size', 
    'Boutique_Price_GBP', 
    'RugsDirect_Price_GBP', 'Debenhams_Price_GBP', 'LoveRugs_Price_GBP',
    'Lowest_Competitor_GBP', 'Competitor_Name', 'Price_Difference_GBP', 'Price_Difference_Percent',
    'Incredible_Price_USD', 'Match_Method'
]
# Ensure cols exist
for c in cols:
    if c not in df_final.columns:
        df_final[c] = None

df_final = df_final[cols]
df_final.sort_values(by='Price_Difference_Percent', ascending=True, inplace=True)

df_final.to_csv(OUTPUT_FILE, index=False)
print(f"Report Generated: {OUTPUT_FILE}")
print(f"Total Products compared: {len(df_final)}")
print(f"Matches found: {df_final['Lowest_Competitor_GBP'].notna().sum()}")
