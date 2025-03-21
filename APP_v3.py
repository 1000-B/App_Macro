import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Load existing food data or create a new file
def load_food_data():
    if os.path.exists("food_database.csv"):
        return pd.read_csv("food_database.csv", index_col=0).to_dict(orient="index")
    else:
        return {}

food_data = load_food_data()

def save_food_data():
    df = pd.DataFrame.from_dict(food_data, orient="index")
    df.to_csv("food_database.csv")

st.title("Macro Tracker")
st.subheader("Log Your Food")

food = st.text_input("Enter Food Item").strip()
quantity = st.number_input("Quantity", min_value=0.1, step=0.1)

# Function to get or input macros
def get_macros(food, quantity):
    if food in food_data:
        unit = food_data[food]["unit"]
        protein_per_unit = food_data[food]["Protein"]
        carbs_per_unit = food_data[food]["Carbs"]
        fats_per_unit = food_data[food]["Fats"]
    else:
        st.warning("New food detected! Please enter macros.")
        unit = st.selectbox("Unit", ["grams", "ml", "piece"])
        protein_per_unit = st.number_input("Protein (per unit)", min_value=0.0, step=0.1)
        carbs_per_unit = st.number_input("Carbs (per unit)", min_value=0.0, step=0.1)
        fats_per_unit = st.number_input("Fats (per unit)", min_value=0.0, step=0.1)
        
        if st.button("Save New Food"):
            food_data[food] = {"unit": unit, "Protein": protein_per_unit, "Carbs": carbs_per_unit, "Fats": fats_per_unit}
            save_food_data()
            st.success(f"{food} added to database!")

    factor = quantity if unit == "piece" else quantity / 100  # Normalize grams/ml
    return protein_per_unit * factor, carbs_per_unit * factor, fats_per_unit * factor, unit

if food:
    protein, carbs, fats, unit = get_macros(food, quantity)
    
    if st.button("Add to Log"):
        new_entry = {"Date": pd.Timestamp.today().strftime('%Y-%m-%d'), "Food": food, "Quantity": quantity, "Unit": unit, "Protein": protein, "Carbs": carbs, "Fats": fats}
        
        if os.path.exists("food_log.csv"):
            log_data = pd.read_csv("food_log.csv")
            log_data = pd.concat([log_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            log_data = pd.DataFrame([new_entry])
        
        log_data.to_csv("food_log.csv", index=False)
        st.success("Entry Added!")

# Display the logged data
st.subheader("Food Log")
if os.path.exists("food_log.csv"):
    log_data = pd.read_csv("food_log.csv")
    st.dataframe(log_data.tail(10))

# Macro breakdown over time
st.subheader("Macro Breakdown")
time_filter = st.radio("View by:", ("Daily", "Weekly", "Monthly"))

def plot_macros(filtered_data):
    if "Date" not in filtered_data.columns:
        filtered_data.reset_index(inplace=True)  # Ensure 'Date' is present
    fig, ax = plt.subplots()
    filtered_data.set_index("Date")[['Protein', 'Carbs', 'Fats']].plot(kind='bar', ax=ax)
    st.pyplot(fig)



if os.path.exists("food_log.csv"):
    log_data["Date"] = pd.to_datetime(log_data["Date"])
    
    if time_filter == "Daily":
        daily_data = log_data.groupby("Date", as_index=False).sum()  # Keep 'Date' as a column
        plot_macros(daily_data)

    elif time_filter == "Weekly":
        log_data["Week"] = log_data["Date"].dt.to_period("W")
        plot_macros(log_data.groupby("Week", as_index=False).sum())

    elif time_filter == "Monthly":
        log_data["Month"] = log_data["Date"].dt.to_period("M")
        plot_macros(log_data.groupby("Month", as_index=False).sum())

