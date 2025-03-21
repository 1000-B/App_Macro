import csv

food_data = {
    "Apple Cider Vinegar": {"unit": "caps", "Protein": 0.0, "Carbs": 0.0, "Fats": 0.0},
    "Turmeric Latte": {"unit": "tbsp", "Protein": 0.0, "Carbs": 1.0, "Fats": 0.5},
    "Coffee": {"unit": "cup", "Protein": 0.3, "Carbs": 0.0, "Fats": 0.0},
    "Protein Bread": {"unit": "piece", "Protein": 10.0, "Carbs": 15.0, "Fats": 3.0},
    "Weetabix": {"unit": "piece", "Protein": 2.0, "Carbs": 12.0, "Fats": 0.8},
    "Provita": {"unit": "piece", "Protein": 1.0, "Carbs": 4.0, "Fats": 0.5},
    "Greek Yogurt": {"unit": "grams", "Protein": 7.0, "Carbs": 4.0, "Fats": 3.0},
    "Cashews": {"unit": "grams", "Protein": 5.0, "Carbs": 9.0, "Fats": 12.0},
    "Almonds": {"unit": "grams", "Protein": 6.0, "Carbs": 6.0, "Fats": 14.0},
    "Banana": {"unit": "piece", "Protein": 1.3, "Carbs": 27.0, "Fats": 0.3},
    "Guava": {"unit": "piece", "Protein": 2.6, "Carbs": 14.0, "Fats": 1.0},
    "Avocado": {"unit": "grams", "Protein": 2.0, "Carbs": 9.0, "Fats": 15.0},
    "White Quinoa+Brown Rice+Mixed Veggies": {"unit": "grams", "Protein": 2.8, "Carbs": 22.0, "Fats": 1.5},
    "Firm Tofu": {"unit": "grams", "Protein": 8.0, "Carbs": 2.0, "Fats": 4.5},
    "Okra": {"unit": "piece", "Protein": 0.2, "Carbs": 1.0, "Fats": 0.1},
    "Red Beans & Chickpeas": {"unit": "grams", "Protein": 7.0, "Carbs": 20.0, "Fats": 1.0},
    "Soybeans": {"unit": "grams", "Protein": 12.0, "Carbs": 9.0, "Fats": 6.0},
    "High Protein Milk": {"unit": "ml", "Protein": 5.0, "Carbs": 4.0, "Fats": 1.5},
    "Flaxseed": {"unit": "tbsp", "Protein": 1.3, "Carbs": 3.0, "Fats": 4.0},
    "Chia Seeds": {"unit": "tbsp", "Protein": 2.0, "Carbs": 5.0, "Fats": 4.5},
    "Passion Fruit": {"unit": "piece", "Protein": 0.5, "Carbs": 10.0, "Fats": 0.4},
    "Soy Milk": {"unit": "ml", "Protein": 7.7, "Carbs": 6.0, "Fats": 4.0},
    "Brown Rice with Mixed Veggies": {"unit": "grams", "Protein": 2.5, "Carbs": 23.0, "Fats": 1.0},
    "Chilli Red Bean Soup with Maize": {"unit": "grams", "Protein": 4.0, "Carbs": 12.0, "Fats": 1.0},
    "Lima Beans with Potatoes": {"unit": "grams", "Protein": 6.0, "Carbs": 21.0, "Fats": 0.8},
    "Farata": {"unit": "grams", "Protein": 3.0, "Carbs": 18.0, "Fats": 2.0},
    "Oatibix": {"unit": "piece", "Protein": 3.0, "Carbs": 16.0, "Fats": 1.0},
    "Lentil Soup": {"unit": "grams", "Protein": 4.0, "Carbs": 10.0, "Fats": 0.5},
    "Bounty Chocolate": {"unit": "piece", "Protein": 1.5, "Carbs": 18.0, "Fats": 9.0},
    "Mars Bar": {"unit": "piece", "Protein": 2.0, "Carbs": 35.0, "Fats": 8.0},
    "Coke Zero": {"unit": "ml", "Protein": 0.0, "Carbs": 0.0, "Fats": 0.0}
}

# Define CSV file name
csv_filename = "food_database.csv"

# Write data to CSV
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow(["Food Item", "Unit", "Protein", "Carbs", "Fats"])
    
    # Write data rows
    for food, values in food_data.items():
        writer.writerow([food, values["unit"], values["Protein"], values["Carbs"], values["Fats"]])

print(f"CSV file '{csv_filename}' created successfully.")
