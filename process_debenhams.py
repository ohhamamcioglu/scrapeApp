import pandas as pd
import json
import re

data = [
  {
    "title": "Becki Owens x Livabliss Vintage Oriental Boho Davine Area Rug",
    "price": "From £63.99 / £83.99",
    "url": "https://www.debenhams.com/product/livabliss-becki-owens-x-livabliss-vintage-oriental-boho-davine-area-rug_p-62610263-3222-4761-860e-863ed2ccdd9d?colour=Camel"
  },
  {
    "title": "Lilian Collection – Washable Vintage Traditional Boho Rug",
    "price": "From £40.99 / £49.99",
    "url": "https://www.debenhams.com/product/livabliss-lilian-collection-washable-vintage-traditional-boho-rug_p-90b0e930-9fc2-47f3-ae4b-99ec857e2232?colour=Camel"
  },
  {
    "title": "Becki Owens x Livabliss Vintage Oriental Boho Margot Area Rug",
    "price": "From £68.99 / £91.99",
    "url": "https://www.debenhams.com/product/livabliss-becki-owens-x-livabliss-vintage-oriental-boho-margot-area-rug_p-8bb97a0a-c5f9-4e7c-9c8d-cba6a2651ba6?colour=Green"
  },
  {
    "title": "Scandi Modern High Pile Amandine Area Rug",
    "price": "From £57.99 / £74.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-modern-high-pile-amandine-area-rug_p-8ff20a9b-19ab-460d-8104-a02e7abadea1?colour=Brown"
  },
  {
    "title": "Vintage Oriental Boho Ines Area Rug",
    "price": "From £39.99 / £48.99",
    "url": "https://www.debenhams.com/product/livabliss-vintage-oriental-boho-ines-area-rug_p-679353ba-898e-44ea-a2c3-c2ab3a844888?colour=Burnt%20Orange"
  },
  {
    "title": "Abstract Modern Marble Giulia Area Rug",
    "price": "From £48.99 / £62.99",
    "url": "https://www.debenhams.com/product/livabliss-abstract-modern-marble-giulia-area-rug_p-555ed053-86fc-4c79-93e8-b6889e8eb39d?colour=Navy"
  },
  {
    "title": "Shaggy Modern Plush Pile Checkered Kittu Area Rug",
    "price": "£115.99 / £179.99",
    "url": "https://www.debenhams.com/product/livabliss-shaggy-modern-plush-pile-checkered-kittu-area-rug_p-3718db0c-7968-4d37-a377-04bcfb2852e3?colour=Yellow"
  },
  {
    "title": "Scandi Modern High Pile Lisa Area Rug",
    "price": "From £80.99 / £121.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-modern-high-pile-lisa-area-rug_p-7ca2c688-f3d7-4085-8965-324ac2063cd2?colour=Ivory"
  },
  {
    "title": "In- & Outdoor Cottage Jute-Look Mindy Area Rug",
    "price": "From £61.99 / £81.99",
    "url": "https://www.debenhams.com/product/livabliss-in--outdoor-cottage-jute-look-mindy-area-rug_p-99da67e8-c3b9-4ba4-9bb2-8479e0b18c68?colour=Beige"
  },
  {
    "title": "Ankara Collection – Vintage Traditional Boho Area Rug",
    "price": "From £53.99 / £68.99",
    "url": "https://www.debenhams.com/product/livabliss-ankara-collection-vintage-traditional-boho-area-rug_p-881a4485-4ed0-4bdd-ae8f-01d46a921c00?colour=Red"
  },
  {
    "title": "Vintage Oriental Boho Sage Area Rug",
    "price": "From £54.99 / £71.99",
    "url": "https://www.debenhams.com/product/livabliss-vintage-oriental-boho-sage-area-rug_p-f84e0672-5de6-4e06-93e0-40210f3afd83?colour=Mid%20Grey"
  },
  {
    "title": "Nora Collection – Gloabl High Pile Area Rug",
    "price": "From £62.99 / £83.99",
    "url": "https://www.debenhams.com/product/livabliss-nora-collection-gloabl-high-pile-area-rug_p-104cf424-0a0e-44ae-b76f-836ca94dd545?colour=Ivory"
  },
  {
    "title": "City Collection - Multicoloured Living, Dining, Bedroom Rug",
    "price": "From £40.99 / £49.99",
    "url": "https://www.debenhams.com/product/livabliss-city-collection---multicoloured-living-dining-bedroom-rug_p-5db66b3c-1059-425f-b077-522e14baaee9?colour=Coral"
  },
  {
    "title": "Vintage Oriental Boho Ileana Area Rug",
    "price": "£140.99 / £221.99",
    "url": "https://www.debenhams.com/product/livabliss-vintage-oriental-boho-ileana-area-rug_p-afbf72ba-6e82-4585-9b59-0d4ade3c75b9?colour=Light%20Sand"
  },
  {
    "title": "Shaggy Modern Plush Pile Checkered Willa Area Rug",
    "price": "From £61.99 / £81.99",
    "url": "https://www.debenhams.com/product/livabliss-shaggy-modern-plush-pile-checkered-willa-area-rug_p-ad329998-dc55-4b7e-979f-5fb6572218fe?colour=Light%20Grey"
  },
  {
    "title": "Shaggy Solid Color Plush Pile Soso Area Rug",
    "price": "From £48.99 / £63.99",
    "url": "https://www.debenhams.com/product/livabliss-shaggy-solid-color-plush-pile-soso-area-rug_p-a2fa15f6-59a6-4c09-bb10-9bc90e45180c?colour=Light%20Grey"
  },
  {
    "title": "Fossay Shag Collection - Machine Washable Modern High Pile Area Rug",
    "price": "From £60.99 / £78.99",
    "url": "https://www.debenhams.com/product/livabliss-fossay-shag-collection---machine-washable-modern-high-pile-area-rug_p-98762ee1-3189-4490-89f5-71a9f0f8f0cb?colour=Charcoal"
  },
  {
    "title": "Scandi Boho Zebra Cybele Area Rug",
    "price": "From £49.99 / £63.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-boho-zebra-cybele-area-rug_p-6a5c3110-c0dd-4883-a2c2-f8b8301ec9b1?colour=Grey"
  },
  {
    "title": "Ankara Collection – Abstract Modern Marble Area Rug",
    "price": "From £37.99 / £46.99",
    "url": "https://www.debenhams.com/product/livabliss-ankara-collection-abstract-modern-marble-area-rug_p-638f51c3-d30a-4401-8dec-a381f3242997?colour=Blue"
  },
  {
    "title": "Berber Modern High Pile Induja Area Rug",
    "price": "From £54.99 / £71.99",
    "url": "https://www.debenhams.com/product/livabliss-berber-modern-high-pile-induja-area-rug_p-d46208e7-cbab-4e63-b666-ef4c4d08b8ec?colour=Cream"
  },
  {
    "title": "Abstract Modern Marble Victoire Area Rug",
    "price": "From £39.99 / £48.99",
    "url": "https://www.debenhams.com/product/livabliss-abstract-modern-marble-victoire-area-rug_p-d29d7ce8-a35a-4e20-9d0d-7b8856220b13?colour=Grey"
  },
  {
    "title": "Galey Alix x Livabliss Vintage Oriental Boho Brown/Olive Myrtle Avenue II Area Rug",
    "price": "From £62.99 / £82.99",
    "url": "https://www.debenhams.com/product/livabliss-galey-alix-x-livabliss-vintage-oriental-boho-brown-olive-myrtle-avenue-ii-area-rug_p-4eeffb30-3a86-457a-8868-edc5ba8617c8?colour=Green"
  },
  {
    "title": "Ankara Collection – Vintage Traditional Boho Area Rug",
    "price": "From £37.99 / £46.99",
    "url": "https://www.debenhams.com/product/livabliss-ankara-collection-vintage-traditional-boho-area-rug_p-f99e3156-96dc-443b-a4d5-b41e0e849c13?colour=Grey"
  },
  {
    "title": "Lilian Collection – Washable Vintage Traditional Boho Rug",
    "price": "From £50.99 / £64.99",
    "url": "https://www.debenhams.com/product/livabliss-lilian-collection-washable-vintage-traditional-boho-rug_p-dfb0a5ab-f33f-4024-a56a-0162580cd206?colour=Brown"
  },
  {
    "title": "Shaggy Modern Plush Pile Polka Dot Hekuba Area Rug",
    "price": "£80.99 / £122.99",
    "url": "https://www.debenhams.com/product/livabliss-shaggy-modern-plush-pile-polka-dot-hekuba-area-rug_p-acfd548f-7ab5-4c3e-89bd-c6c043e21e63?colour=Black"
  },
  {
    "title": "Abstract Modern Marble Nalany Area Rug",
    "price": "£116.99 / £181.99",
    "url": "https://www.debenhams.com/product/livabliss-abstract-modern-marble-nalany-area-rug_p-394cdef0-9d49-4165-a0fe-d70e052f7dea?colour=Charcoal"
  },
  {
    "title": "Scandi Modern High Pile Alma Area Rug",
    "price": "£72.99 / £96.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-modern-high-pile-alma-area-rug_p-d2a019d4-5056-40a8-9940-2f3a2cf53851?colour=Brown"
  },
  {
    "title": "In- & Outdoor Global Diksha Area Rug",
    "price": "£60.99 / £77.99",
    "url": "https://www.debenhams.com/product/livabliss-in--outdoor-global-diksha-area-rug_p-22f99ab1-9ba9-4c11-9795-3d8d7dfa79f1?colour=Yellow"
  },
  {
    "title": "In- & Outdoor Modern Rubal Area Rug",
    "price": "£72.99 / £109.99",
    "url": "https://www.debenhams.com/product/livabliss-in--outdoor-modern-rubal-area-rug_p-f30d0b1c-69ee-4d68-a0eb-f59f8b2f6b62?colour=Pink"
  },
  {
    "title": "Abstract Modern Marble Alix Area Rug",
    "price": "£89.99 / £135.99",
    "url": "https://www.debenhams.com/product/livabliss-abstract-modern-marble-alix-area-rug_p-e25c585a-5e88-4b36-8e03-6419646ba5ec?colour=Charcoal"
  },
  {
    "title": "Scandi Modern Aqua Bea Area Rug",
    "price": "£87.99 / £135.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-modern-aqua-bea-area-rug_p-0d82589b-021a-4531-a32e-e3b6adc023d6?colour=Blue"
  },
  {
    "title": "Vintage Oriental Boho Wren Area Rug",
    "price": "From £50.99 / £63.99",
    "url": "https://www.debenhams.com/product/livabliss-vintage-oriental-boho-wren-area-rug_p-fb3265b1-42eb-4c58-bd64-5aee382e320c?colour=Orange"
  },
  {
    "title": "Scandi Coastal Alaya Area Rug",
    "price": "£76.99 / £115.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-coastal-alaya-area-rug_p-c81e72f2-ffbb-4443-b139-0f97a0eb1cb5?colour=Green"
  },
  {
    "title": "Lilian Collection – Washable Modern Rug",
    "price": "From £53.99 / £69.99",
    "url": "https://www.debenhams.com/product/livabliss-lilian-collection-washable-modern-rug_p-ea82c535-c691-4ed0-afca-b90d3429b015?colour=Beige"
  },
  {
    "title": "Lilian Collection – Washable Vintage Traditional Boho Rug",
    "price": "From £53.99 / £69.99",
    "url": "https://www.debenhams.com/product/livabliss-lilian-collection-washable-vintage-traditional-boho-rug_p-6615422c-eb50-4b37-981a-d6f8fce7faf0?colour=Burnt%20Orange"
  },
  {
    "title": "In- & Outdoor 3D High & Low Pile Textured Ayumi Area Rug",
    "price": "From £48.99 / £63.99",
    "url": "https://www.debenhams.com/product/livabliss-in--outdoor-3d-high-low-pile-textured-ayumi-area-rug_p-ec754a5b-89ea-49c7-8e6b-ebb46782c0d5?colour=White"
  },
  {
    "title": "Abstract Modern Marble Bellatrix Area Rug",
    "price": "From £57.99 / £74.99",
    "url": "https://www.debenhams.com/product/livabliss-abstract-modern-marble-bellatrix-area-rug_p-7f879723-bb2d-4727-8537-9887412e9340?colour=Mustard"
  },
  {
    "title": "Ankara Collection – Washable Modern Rug for Kids' Rooms",
    "price": "From £44.99 / £56.99",
    "url": "https://www.debenhams.com/product/livabliss-ankara-collection-washable-modern-rug-for-kids-rooms_p-840853da-1932-414f-bb36-da0de0fcb053?colour=Grey"
  },
  {
    "title": "Scandi Geometric Bianca Area Rug",
    "price": "From £69.99 / £98.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-geometric-bianca-area-rug_p-5ced9de8-169a-4fe4-8aa8-8e5ac6e74edc?colour=Light%20Grey"
  },
  {
    "title": "Scandi Modern Perla Area Rug",
    "price": "£59.99 / £77.99",
    "url": "https://www.debenhams.com/product/livabliss-scandi-modern-perla-area-rug_p-31212119-1329-48af-a80a-9c931af2f949?colour=Coral"
  }
]

def clean_price(price_str):
    # Example: "From £63.99 / £83.99" -> 63.99
    # Example: "£115.99 / £179.99" -> 115.99
    # Example: "N/A" -> None
    if not price_str or "N/A" in price_str:
        return None
        
    # Extract all numbers like 63.99
    matches = re.findall(r"\d+\.\d+", price_str)
    if not matches:
        return None
    
    # Return the lowest price found (usually the first one, or the Sale price)
    return float(matches[0])

cleaned_data = []
for item in data:
    item['cleaned_price'] = clean_price(item['price'])
    item['vendor'] = 'Livabliss'
    cleaned_data.append(item)

df = pd.DataFrame(cleaned_data)
df.to_csv("debenhams_products.csv", index=False)
print(f"Saved {len(df)} products to debenhams_products.csv")
