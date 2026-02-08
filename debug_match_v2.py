import pandas as pd
from fuzzywuzzy import fuzz

def normalize_size(size_str):
    if pd.isna(size_str): return ""
    s = str(size_str).lower().replace(' ', '')
    s = s.replace('cm', '').replace('feet', '').replace("'", '').replace('"', '')
    s = s.replace('rectangle', '').replace('runner', '').replace('round', '')
    return s.strip()

print("--- DEBUG V2 ---")

# Load small subset
df_boutique = pd.read_csv("boutiquerugs_products.csv")
df_loverugs = pd.read_csv("loverugs_products.csv")

# Pick a Boutique Item that SHOULD match Love Rugs
# Love Rugs has "Lila Becki Owens x Livabliss... 170 x 120cm"
# Find equivalent in Boutique
# Search for "Lila" or "Becki"
candidates = df_boutique[df_boutique['title'].str.contains("Becki", case=False)]
print(f"Boutique 'Becki' items: {len(candidates)}")

if len(candidates) > 0:
    b_item = candidates.iloc[0]
    print(f"Boutique Item: {b_item['title']}")
    print(f"Boutique Variant: {b_item['variant_title']}")
    b_size_norm = normalize_size("120 x 170") # Manual override for test if needed, or extract
    # Extract from variant
    if '/' in str(b_item['variant_title']):
        b_size_norm = normalize_size(str(b_item['variant_title']).split('/')[-1])
    else:
        b_size_norm = normalize_size(b_item['variant_title'])
    
    print(f"Boutique Norm Size: '{b_size_norm}'")

    # Love Rugs Item
    lr_item = df_loverugs.iloc[0]
    print(f"Love Rugs Item: {lr_item['title']}")
    print(f"Love Rugs Variant: {lr_item['variant_public_title']}")
    lr_size_norm = normalize_size(lr_item['variant_public_title'])
    print(f"Love Rugs Norm Size: '{lr_size_norm}'")
    
    # Comparison
    print(f"Size Match? '{b_size_norm}' == '{lr_size_norm}'")
    
    score_sort = fuzz.token_sort_ratio(b_item['title'], lr_item['title'])
    score_set = fuzz.token_set_ratio(b_item['title'], lr_item['title'])
    print(f"Scores - Sort: {score_sort}, Set: {score_set}")
