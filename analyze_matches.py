import json
from collections import Counter

def analyze_matches():
    with open('competitor_analysis.json', 'r') as f:
        data = json.load(f)

    stats = Counter()
    total_products = len(data)
    
    # Competitor keys to check
    uk_competitors = ['rd', 'deb', 'lr']
    
    for item in data:
        # Count non-null matches among UK competitors
        match_count = sum(1 for key in uk_competitors if item.get(key) is not None)
        stats[match_count] += 1

    print(f"Total Products Processed: {total_products}")
    print("-" * 30)
    print("Match Distribution (UK Competitors: RD, DEB, LR):")
    for i in range(3, -1, -1):
        count = stats[i]
        percentage = (count / total_products) * 100 if total_products > 0 else 0
        print(f"{i} Matches: {count} products ({percentage:.1f}%)")
        
    # Overlap Details
    print("-" * 30)
    print("Specific Overlaps:")
    
    # All 3
    all_3 = sum(1 for item in data if all(item.get(k) for k in uk_competitors))
    print(f"RD + DEB + LR: {all_3}")
    
    # RD + DEB
    rd_deb = sum(1 for item in data if item.get('rd') and item.get('deb') and not item.get('lr'))
    print(f"RD + DEB (only): {rd_deb}")
    
    # RD + LR
    rd_lr = sum(1 for item in data if item.get('rd') and item.get('lr') and not item.get('deb'))
    print(f"RD + LR (only): {rd_lr}")
    
    # DEB + LR
    deb_lr = sum(1 for item in data if item.get('deb') and item.get('lr') and not item.get('rd'))
    print(f"DEB + LR (only): {deb_lr}")

if __name__ == "__main__":
    analyze_matches()
