import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Food Data
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

# Load existing data or create a new file
def load_data():
    if os.path.exists("food_log.csv"):
        return pd.read_csv("food_log.csv")
    else:
        return pd.DataFrame(columns=["Date", "Food", "Quantity", "Unit", "Protein", "Carbs", "Fats"])

# Load CSV data
data = load_data()

st.title("Macro Tracker")
st.subheader("Log Your Food")

food = st.selectbox("Select Food Item", list(food_data.keys()))
quantity = st.number_input("Quantity", min_value=0.1, step=0.1)
unit = food_data[food]["unit"]

# Function to calculate macros
def get_macros(food, quantity):
    if food in food_data:
        unit = food_data[food]["unit"]
        protein_per_unit = food_data[food]["Protein"]
        carbs_per_unit = food_data[food]["Carbs"]
        fats_per_unit = food_data[food]["Fats"]
        
        if unit == "grams":
            factor = quantity / 100  # Convert to per 100g
        elif unit == "ml":
            factor = quantity / 100  # Convert to per 100ml
        else:
            factor = quantity  # Per piece, no conversion needed

        return protein_per_unit * factor, carbs_per_unit * factor, fats_per_unit * factor
    return 0, 0, 0

# Get macros
protein, carbs, fats = get_macros(food, quantity)

if st.button("Add to Log"):
    new_entry = {"Date": pd.Timestamp.today().strftime('%Y-%m-%d'), "Food": food, "Quantity": quantity, "Unit": unit, "Protein": protein, "Carbs": carbs, "Fats": fats}
    data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
    data.to_csv("food_log.csv", index=False)
    st.success("Entry Added!")

# Display the logged data
st.subheader("Food Log")
st.dataframe(data.tail(10))

# Macro breakdown over time
st.subheader("Macro Breakdown")
time_filter = st.radio("View by:", ("Daily", "Weekly", "Monthly"))

def plot_macros(filtered_data):
    fig, ax = plt.subplots()
    filtered_data.set_index("Date")[['Protein', 'Carbs', 'Fats']].plot(kind='bar', ax=ax)
    st.pyplot(fig)

if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"])
    if time_filter == "Daily":
        plot_macros(data.groupby("Date").sum())
    elif time_filter == "Weekly":
        data["Week"] = data["Date"].dt.to_period("W")
        plot_macros(data.groupby("Week").sum())
    elif time_filter == "Monthly":
        data["Month"] = data["Date"].dt.to_period("M")
        plot_macros(data.groupby("Month").sum())
