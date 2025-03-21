import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# File to store data
DATA_FILE = "food_log.csv"

# Predefined food database (example)
FOOD_DB = {
    "Oats": {"Protein": 2.4, "Carbs": 12, "Fats": 1.4},
    "Eggs": {"Protein": 6.3, "Carbs": 0.6, "Fats": 5.0},
    "Milk": {"Protein": 3.4, "Carbs": 5.0, "Fats": 1.0},
    "Almonds": {"Protein": 6.0, "Carbs": 6.0, "Fats": 14.0},
    "Cashews": {"Protein": 5.0, "Carbs": 9.0, "Fats": 12.0},
    "Tofu": {"Protein": 8.0, "Carbs": 2.0, "Fats": 4.0},
    "Greek Yogurt": {"Protein": 7.0, "Carbs": 4.0, "Fats": 3.0},
    "Banana": {"Protein": 1.3, "Carbs": 23.0, "Fats": 0.3},
    "Avocado": {"Protein": 2.0, "Carbs": 9.0, "Fats": 15.0},
    "Peanut Butter": {"Protein": 8.0, "Carbs": 6.0, "Fats": 16.0},
    "Soy Milk": {"Protein": 7.7, "Carbs": 4.0, "Fats": 4.0},
    "Chia Seeds": {"Protein": 4.7, "Carbs": 42.0, "Fats": 31.0},
    "Flax Seeds": {"Protein": 1.9, "Carbs": 8.0, "Fats": 9.0},
    "Provita": {"Protein": 2.0, "Carbs": 8.0, "Fats": 1.0},
    "Weetabix": {"Protein": 4.5, "Carbs": 26.0, "Fats": 1.0},
    "Quinoa": {"Protein": 4.1, "Carbs": 21.3, "Fats": 1.9},
    "Brown Rice": {"Protein": 2.5, "Carbs": 23.0, "Fats": 1.0},
    "Chickpeas": {"Protein": 8.9, "Carbs": 27.4, "Fats": 2.6},
    "Tomato": {"Protein": 1.0, "Carbs": 4.0, "Fats": 0.2},
    "Honey": {"Protein": 0.1, "Carbs": 17.3, "Fats": 0.0},
    "Red Beans": {"Protein": 8.7, "Carbs": 22.0, "Fats": 0.8},
    "Mixed Veggies": {"Protein": 2.0, "Carbs": 10.0, "Fats": 0.3},
    "Passion Fruit": {"Protein": 2.2, "Carbs": 23.0, "Fats": 0.4},
    "Lima Beans": {"Protein": 7.6, "Carbs": 20.0, "Fats": 0.8},
    "Soya": {"Protein": 36.0, "Carbs": 30.0, "Fats": 19.0},
    "Aloe Vera": {"Protein": 0.0, "Carbs": 0.0, "Fats": 0.0},
    "Taro Leaves": {"Protein": 2.1, "Carbs": 5.5, "Fats": 0.3},
    "Okra": {"Protein": 1.9, "Carbs": 7.5, "Fats": 0.2},
    "Cinnamon": {"Protein": 0.0, "Carbs": 0.7, "Fats": 0.0},
    "Cardamom": {"Protein": 0.0, "Carbs": 0.8, "Fats": 0.0},
    "Acerola Cherry": {"Protein": 1.0, "Carbs": 8.0, "Fats": 0.1},
    "Bounty Chocolate": {"Protein": 2.0, "Carbs": 33.0, "Fats": 11.0},
    "Milka Chocolate": {"Protein": 4.0, "Carbs": 23.0, "Fats": 11.0},
    "Kiri Cheese": {"Protein": 5.0, "Carbs": 1.0, "Fats": 9.0},
    "Pumpkin": {"Protein": 1.0, "Carbs": 7.0, "Fats": 0.1},
    "Mango": {"Protein": 0.8, "Carbs": 15.0, "Fats": 0.4},
    "Pawpaw": {"Protein": 1.0, "Carbs": 15.0, "Fats": 0.3},
    "Fruity Greek Yogurt": {"Protein": 6.0, "Carbs": 10.0, "Fats": 3.0},
    "Baked Beans": {"Protein": 5.0, "Carbs": 27.0, "Fats": 1.0},
    "Birthday Cake": {"Protein": 3.0, "Carbs": 45.0, "Fats": 10.0},
    "Teokon": {"Protein": 5.0, "Carbs": 15.0, "Fats": 3.0},
    "Farata": {"Protein": 3.0, "Carbs": 35.0, "Fats": 5.0},
    "Red Currant": {"Protein": 0.7, "Carbs": 8.0, "Fats": 0.1},
    "Raspberry": {"Protein": 1.5, "Carbs": 12.0, "Fats": 0.5},
    "Blackberry": {"Protein": 1.3, "Carbs": 10.0, "Fats": 0.5}
}

# Load existing data or create a new one
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Food", "Weight", "Protein", "Carbs", "Fats"])

data = load_data()

# Streamlit UI
st.title("Macro Tracker")

# Food Input Form
st.subheader("Log Your Meal")
date = st.date_input("Date")
food = st.selectbox("Food Item", list(FOOD_DB.keys()))
weight = st.number_input("Weight (grams)", min_value=0.0, step=1.0)

# Calculate macros automatically
if food in FOOD_DB:
    macros = FOOD_DB[food]
    protein = (macros["Protein"] * weight) / 100
    carbs = (macros["Carbs"] * weight) / 100
    fats = (macros["Fats"] * weight) / 100
else:
    protein, carbs, fats = 0, 0, 0

if st.button("Add Entry"):
    new_entry = pd.DataFrame({
        "Date": [date],
        "Food": [food],
        "Weight": [weight],
        "Protein": [protein],
        "Carbs": [carbs],
        "Fats": [fats]
    })
    data = pd.concat([data, new_entry], ignore_index=True)
    data.to_csv(DATA_FILE, index=False)
    st.success("Entry Added!")

# Display Logged Data
st.subheader("Logged Data")
st.dataframe(data.tail(10))

# Macro Graphs
st.subheader("Macro Breakdown")
time_filter = st.selectbox("View by", ["Daily", "Weekly", "Monthly"])

data["Date"] = pd.to_datetime(data["Date"])

def plot_macros(data):
    fig, ax = plt.subplots()
    data.groupby("Date")["Protein", "Carbs", "Fats"].sum().plot(kind="bar", ax=ax)
    st.pyplot(fig)

if time_filter == "Daily":
    plot_macros(data)
elif time_filter == "Weekly":
    data["Week"] = data["Date"].dt.to_period("W")
    plot_macros(data.groupby("Week").sum())
elif time_filter == "Monthly":
    data["Month"] = data["Date"].dt.to_period("M")
    plot_macros(data.groupby("Month").sum())