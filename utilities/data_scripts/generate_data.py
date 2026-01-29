import pandas as pd
import os

# Data Definitions
products = [
    {
        "category": "Home Care",
        "sub_category": "Pest Control",
        "product_name": "Power Fly Killer Spray",
        "variant": "500ml",
        "price_lkr": 1590,
        "available": "Yes",
        "description": "100% natural, eco-friendly fly repellent made with turmeric, cinnamon, kasthuri, and kohoba. Safe for children and pets. Kills flies by damaging their nervous system upon consumption. Also effective against ants and cockroaches.",
        "tags": "fly killer, repellent, natural, safe, pest control, 500ml"
    },
    {
        "category": "Home Care",
        "sub_category": "Pest Control",
        "product_name": "Power Fly Killer Spray",
        "variant": "4L",
        "price_lkr": 9900,
        "available": "Yes",
        "description": "Bulk 4L pack. 100% natural, eco-friendly fly repellent made with turmeric, cinnamon, kasthuri, and kohoba. Safe for children and pets. Kills flies by damaging their nervous system upon consumption.",
        "tags": "fly killer, repellent, natural, safe, pest control, 4L, bulk"
    },
    {
        "category": "Home Care",
        "sub_category": "Cleaning",
        "product_name": "Power Odour Neutralizer Spray",
        "variant": "500ml",
        "price_lkr": 1290,
        "available": "Yes",
        "description": "Advanced air freshener that neutralizes odors at the molecular level. Eliminates smells from smoke, food, pets, garbage, and dampness. Non-toxic and biodegradable.",
        "tags": "odour neutralizer, air freshener, smell remover, pet friendly"
    },
    {
        "category": "Home Care",
        "sub_category": "Cleaning",
        "product_name": "Power DeepCleaner",
        "variant": "500ml",
        "price_lkr": 1290,
        "available": "Yes",
        "description": "Ultimate multi-surface deep cleaner. Removes rust rings, hard water spots, baked-on grease, and tarnished metal. Safe for tile, glass, plastic, ceramic, and stainless steel. Fast-acting formula.",
        "tags": "deep cleaner, rust remover, stain remover, heavy duty, multi surface"
    }
]

# Create DataFrame
df = pd.DataFrame(products)

# Ensure output directory exists
output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend/data")
os.makedirs(output_dir, exist_ok=True)

# Save to Excel
output_path = os.path.join(output_dir, "power_products.xlsx")
df.to_excel(output_path, index=False)

print(f"File created successfully at: {output_path}")
print(df)
