import pandas as pd

def match_products():
    # Load data
    try:
        boutique_df = pd.read_csv("boutiquerugs_products.csv")
        incredible_df = pd.read_csv("incredible_products.csv")
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    print(f"Boutique Rows: {len(boutique_df)}")
    print(f"Incredible Rows: {len(incredible_df)}")

    # Ensure SKUs are strings for matching
    boutique_df['sku'] = boutique_df['sku'].astype(str).str.strip()
    incredible_df['sku'] = incredible_df['sku'].astype(str).str.strip()

    # Merge on Title Similarity
    import difflib
    
    matches = []
    
    # Optimize: Create a dictionary or list for faster lookups if possible, but for 2000x100000 it might be slow.
    # Strategy: Filter Incredible list by " Rug" if Boutique item is a Rug?
    # Simple nested loop is O(N*M) -> 2300 * 115000 = 264 million ops. Too slow.
    
    # Optimization: 
    # 1. Block match: First word of title (often collection name) must match?
    # Boutique: "Kimi ...", "Tansy ..."
    # Incredible: "Livabliss Trenza ..." -> "Trenza" might be the key.
    
    # Let's try to normalize titles
    def normalize(text):
        if not isinstance(text, str): return ""
        text = text.lower().replace("livabliss", "").replace("rug", "").strip()
        return " ".join(text.split())

    boutique_df['norm_title'] = boutique_df['title'].apply(normalize)
    incredible_df['norm_title'] = incredible_df['title'].apply(normalize)
    
    # Create lookup map by first word of normalized title
    incredible_map = {}
    for idx, row in incredible_df.iterrows():
        nt = row['norm_title']
        if not nt: continue
        first_word = nt.split()[0]
        if first_word not in incredible_map:
            incredible_map[first_word] = []
        incredible_map[first_word].append(row)
        
    print("Starting fuzzy match...")
    
    count = 0
    for idx, row in boutique_df.iterrows():
        b_title = row['norm_title']
        if not b_title: continue
        
        first_word = b_title.split()[0]
        
        # Check in map
        candidates = incredible_map.get(first_word, [])
        
        best_score = 0
        best_match = None
        
        for cand in candidates:
            score = difflib.SequenceMatcher(None, b_title, cand['norm_title']).ratio()
            if score > 0.85: # Threshold
                if score > best_score:
                    best_score = score
                    best_match = cand
        
        if best_match is not None:
            matches.append({
                'Boutique Title': row['title'],
                'Boutique SKU': row['sku'],
                'Boutique Price': row['price'],
                'Boutique URL': row['product_url'],
                'Incredible Title': best_match['title'],
                'Incredible SKU': best_match['sku'],
                'Incredible Price': best_match['price'],
                'Incredible URL': best_match['product_url'],
                'Match Score': best_score
            })
            count += 1
            if count % 100 == 0:
                print(f"Matched {count} products...")

    merged_df = pd.DataFrame(matches)
    
    if not merged_df.empty:
        merged_df['Boutique Price'] = pd.to_numeric(merged_df['Boutique Price'], errors='coerce')
        merged_df['Incredible Price'] = pd.to_numeric(merged_df['Incredible Price'], errors='coerce')
        merged_df['Price Difference'] = merged_df['Boutique Price'] - merged_df['Incredible Price']
    
    # Save
    output_file = "price_comparison_fuzzy.csv"
    merged_df.to_csv(output_file, index=False)
    
    print(f"Matching complete.")
    print(f"Found {len(merged_df)} matching products.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    match_products()
