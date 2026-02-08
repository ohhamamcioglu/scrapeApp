import pandas as pd
from fuzzywuzzy import fuzz

def normalize_size(size_str):
    if pd.isna(size_str): return ""
    s = str(size_str).lower().replace(' ', '')
    s = s.replace('cm', '').replace('feet', '').replace("'", '').replace('"', '')
    s = s.replace('rectangle', '').replace('runner', '').replace('round', '')
    return s.strip()

print("--- DEBUGGING MATCHING ---")

# Sample Data
boutique_title = "Kimi Becki Owens x Livabliss Solid And Border Charcoal Jute Rug"
boutique_size = "120x170" # normalized from "Grey / 120 x 170 cm"

# Real Debenhams Data
deb_title = "Lilian Collection – Washable Vintage Traditional Boho Rug" 
deb_size = "120x170" # normalized
deb_full_title = "Lilian Collection – Washable Vintage Traditional Boho Rug - Camel - 120cm x 170cm"

# Test 1: Title Match Score
score = fuzz.token_sort_ratio(boutique_title, deb_title)
print(f"Title Score (Boutique vs Deb): {score}")

# Test 2: Size Match
print(f"Size Match: {boutique_size == deb_size}")

# Test 3: Love Rugs
lr_title = "Lila Becki Owens x Livabliss Oriental Vintage BOLC2301 Rug - 170 x 120cm"
lr_norm_size = normalize_size("170 x 120cm") # -> 170x120
print(f"Love Rugs Norm Size: {lr_norm_size}")
# Boutique Size is 120x170.
# 170x120 != 120x170. Order matters!

# Test 4: Common Word Indexing
b_key = boutique_title.split(' ')[0].lower() # "kimi"
d_key = deb_title.split(' ')[0].lower() # "lilian"
print(f"Keys: B='{b_key}', D='{d_key}'") 
# They don't match! The indexing strategy is blocking valid matches if the first word differs.
