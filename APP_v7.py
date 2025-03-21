import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Load existing food data or use default
def load_food_data():
    if os.path.exists("food_database.csv"):
        return pd.read_csv("food_database.csv", index_col=0).to_dict(orient="index")
    return {}

food_data = load_food_data()

# Save function to update CSV
def save_food_data():
    df = pd.DataFrame.from_dict(food_data, orient="index")
    df.to_csv("food_database.csv")

st.title("Macro Tracker")
st.subheader("Log Your Food")

# Step 1: Create list of existing foods + "Add New Food..."
food_options = ["Add New Food..."] + list(food_data.keys())

# Step 2: Select box with existing foods
selection = st.selectbox("Select Food or Add New", options=food_options)

# Step 3: If "Add New Food..." is chosen, show text input for new entry
if selection == "Add New Food...":
    new_food = st.text_input("Enter new food name:")
    food = new_food if new_food else None  # Ensure user actually types something
else:
    food = selection  # Selected from existing foods

# Step 4: Show confirmation of selection
if food:
    st.info(f":white_check_mark: Selected Food: {food}")


quantity = st.number_input("Quantity", min_value=0.1, step=0.1)

# Step 4: Handle food selection or new entry
if food in food_data:
    # Existing food - Compute macros
    factor = quantity if food_data[food]["Unit"] == "piece" else quantity / 100
    protein = food_data[food]["Protein"] * factor
    carbs = food_data[food]["Carbs"] * factor
    fats = food_data[food]["Fats"] * factor
else:
    # New food - Ask for macros
    st.warning("Food not found. Enter macros below to save it.")
    unit = st.text_input("Unit (e.g., grams, piece, cup)")
    protein = st.number_input("Protein (g)", min_value=0.0, format="%.1f")
    carbs = st.number_input("Carbs (g)", min_value=0.0, format="%.1f")
    fats = st.number_input("Fats (g)", min_value=0.0, format="%.1f")

    # Step 5: Save new food
    if st.button("Save New Food"):
        food_data[food] = {"Unit": unit, "Protein": protein, "Carbs": carbs, "Fats": fats}
        save_food_data()
        st.success(f"{food} has been added to the database!")


#quantity = st.number_input("Quantity", min_value=0.1, step=0.1)

# Compute macros if food exists
if food in food_data:
    factor = quantity if food_data[food]["Unit"] == "piece" else quantity / 100
    protein = food_data[food]["Protein"] * factor
    carbs = food_data[food]["Carbs"] * factor
    fats = food_data[food]["Fats"] * factor

    if st.button("Add to Log"):
        new_entry = {
            "Date": pd.Timestamp.today().strftime('%Y-%m-%d'),
            "Food": food,
            "Quantity": quantity,
            "Unit": food_data[food]["Unit"],
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats
        }

        if os.path.exists("food_log.csv"):
            log_data = pd.read_csv("food_log.csv")
            log_data = pd.concat([log_data, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            log_data = pd.DataFrame([new_entry])

        log_data.to_csv("food_log.csv", index=False)
        st.success("Entry Added!")

# Show log
st.subheader("Food Log")
if os.path.exists("food_log.csv"):
    log_data = pd.read_csv("food_log.csv")
    st.dataframe(log_data.tail(10))


# Macro breakdown over time
st.subheader("Macro Breakdown")
time_filter = st.radio("View by:", ("Daily", "Weekly", "Monthly"))

def plot_macros(filtered_data):
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
        