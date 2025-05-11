import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime




# Load existing food data or use default
# def load_food_data():
#     if os.path.exists("food_database.csv"):
#         return pd.read_csv("food_database.csv", index_col=0).to_dict(orient="index")
#     return {}

# food_data = load_food_data()

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mVbGbsThxK9L1mC2-2n_qlC2S0IoPM7zxQYT8DVBiAA/edit?gid=1560030794#gid=1560030794"
spreadsheet = client.open_by_url(SHEET_URL)
food_sheet = spreadsheet.worksheet("FoodDatabase")
log_sheet = spreadsheet.worksheet("FoodLog")

# Load existing food data from Google Sheets
def load_food_data():
    data = food_sheet.get_all_records()
    return {row["Food"]: row for row in data} if data else {}


food_data = load_food_data()

# # Save function to update CSV
# def save_food_data():
#     df = pd.DataFrame.from_dict(food_data, orient="index")
#     df.to_csv("food_database.csv")

st.markdown("<h1 style='text-align: center;'>You Are What You Eat</h1>", unsafe_allow_html=True)
st.subheader("Log Your Food Man")

from datetime import datetime

# Default: today's date
selected_date = datetime.today().date()

def is_weight_based(unit):
    return unit.lower() in ["gram", "grams", "g", "ml"]

# Advanced options toggle
with st.expander("🔧 Advanced Options"):
    selected_date = st.date_input("Select Date to Log", value=datetime.today().date())

    log_date_str = selected_date.strftime('%d/%m/%Y')
    st.markdown("---")
    st.markdown("### 🔁 Delete Latest Log Entry")
    if st.button("Delete Latest Log Entry from Food Log"):
        log_records = log_sheet.get_all_records()
        if log_records:
            log_sheet.delete_rows(len(log_records)+1)  # Add 2: 1 for headers, 1 for 1-based index
            st.success("Deleted the latest entry from the Food Log.")
        else:
            st.warning("Food Log is empty.")

    st.markdown("---")
    # --- Frequently Used Food Buttons ---
    st.markdown("### ⚡ Quick Add")

    # Define your frequent food list
    frequent_food_names = ["Apple Cider Vinegar", "Turmeric Latte", "Lemon Juice", "Green Tea"]  # You define this list

    # Set how many buttons per row
    buttons_per_row = 4

    # Create buttons in rows using st.columns
    for i in range(0, len(frequent_food_names), buttons_per_row):
        cols = st.columns(buttons_per_row)
        for j, food_name in enumerate(frequent_food_names[i:i+buttons_per_row]):
            with cols[j]:
                if st.button(food_name):
                    if food_name in food_data:
                        unit = food_data[food_name]["Unit"]
                        default_qty = 100 if is_weight_based(unit) else 1
                        factor = default_qty / 100 if is_weight_based(unit) else default_qty

                        new_entry = {
                            "Date": log_date_str,
                            "Food": food_name,
                            "Quantity": default_qty,
                            "Unit": unit,
                            "Protein": food_data[food_name]["Protein"] * factor,
                            "Carbs": food_data[food_name]["Carbs"] * factor,
                            "Fats": food_data[food_name]["Fats"] * factor,
                            "Calories": food_data[food_name]["Calories"] * factor,
                        }

                        log_sheet.append_rows([list(new_entry.values())])
                        st.success(f"{food_name} ({default_qty} {unit}) added to log!")
                    else:
                        st.warning(f"{food_name} not found in Food Database.")


        # ✅ NEW: Refresh button and session cache
    st.markdown("---")
    st.markdown("### 📋 Latest 10 Entries View (with Refresh)")
    if st.button("🔄 Refresh Tables"):
        st.session_state.log_data_full = pd.DataFrame(log_sheet.get_all_records())
        st.session_state.food_data_full = pd.DataFrame(food_sheet.get_all_records())
        st.success("Tables refreshed!")

    if 'log_data_full' not in st.session_state:
        st.session_state.log_data_full = pd.DataFrame(log_sheet.get_all_records())
    if 'food_data_full' not in st.session_state:
        st.session_state.food_data_full = pd.DataFrame(food_sheet.get_all_records())

            
    st.markdown("---")
    st.markdown("### 🗑️ Delete Entries by Row Number")
    delete_target = st.radio("Choose what to delete", ["Food Log Entry", "Food Database Entry"])

    if delete_target == "Food Log Entry":
        df = st.session_state.log_data_full
        st.dataframe(df.tail(10))  # ✅ Display last 10 entries with index
        row_index_to_delete = st.number_input(
            "Enter the DataFrame index to delete from Food Log", 
            min_value=int(df.index.min()), 
            max_value=int(df.index.max()), 
            step=1
        )
        if st.button("Delete Row from Food Log"):
            sheet_row_to_delete = row_index_to_delete + 2  # +1 for header, +1 for 1-based indexing
            log_sheet.delete_rows(sheet_row_to_delete)
            st.success(f"Deleted DataFrame index {row_index_to_delete} (Sheet row {sheet_row_to_delete}) from Food Log")

    elif delete_target == "Food Database Entry":
        df = st.session_state.food_data_full
        st.dataframe(df)
        row_index_to_delete = st.number_input(
            "Enter the DataFrame index to delete from Food Database", 
            min_value=int(df.index.min()), 
            max_value=int(df.index.max()), 
            step=1
        )
        if st.button("Delete Row from Food Database"):
            sheet_row_to_delete = row_index_to_delete + 2
            food_sheet.delete_rows(sheet_row_to_delete)
            st.success(f"Deleted DataFrame index {row_index_to_delete} (Sheet row {sheet_row_to_delete}) from Food Database")



def save_food_data():
    df = pd.DataFrame.from_dict(food_data, orient="index").reset_index()
    df.rename(columns={"index": "Food"}, inplace=True)  

    # Ensure no duplicate "Food" entries in df
    if df["Food"].duplicated().any():
        st.error("Duplicate food entries found in the database. Please resolve duplicates before saving.")
        return  # Stop execution if duplicates are found

    existing_foods = {row["Food"] for row in food_sheet.get_all_records()}

    new_rows = df[~df["Food"].isin(existing_foods)].values.tolist()
    
    if new_rows:
        food_sheet.append_rows(new_rows)  # Append only new foods

existing_foods = [row["Food"] for row in food_sheet.get_all_records()]
duplicates = set([food for food in existing_foods if existing_foods.count(food) > 1])

if duplicates:
    st.error(f"Duplicate foods in Google Sheets: {duplicates}. Please remove them.")



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

# Get the unit of the selected food (if it exists)
unit_display = food_data[food]["Unit"] if food in food_data else ""

# Display quantity input along with the unit
quantity = st.number_input(f"Quantity ({unit_display})", min_value=1, step=1)

def is_weight_based(unit):
    return unit.lower() in ["gram", "grams", "g", "ml"]

# Step 4: Handle food selection or new entry
if food in food_data:
    unit = food_data[food]["Unit"]  # Get the unit for this food item
    # Existing food - Compute macros
    factor = quantity / 100 if is_weight_based(unit) else quantity
    protein = food_data[food]["Protein"] * factor
    carbs = food_data[food]["Carbs"] * factor
    fats = food_data[food]["Fats"] * factor
    calories = food_data[food]["Calories"]*factor
else:
    # New food - Ask for macros
    st.warning("Food not found. Enter macros below to save it.")
    
    # Predefined unit options
    unit_options = sorted({row["Unit"] for row in food_data.values() if row.get("Unit")})
    
    # Dropdown for unit selection
    unit = st.selectbox("Select Unit", options=unit_options)
    
    # Allow manual entry if needed
    custom_unit = st.text_input("Or enter a custom unit")
    
    # If the user enters a custom unit, override the selection
    if custom_unit:
        unit = custom_unit
    
    # Macro inputs
    protein = st.number_input("Protein (g)", min_value=0.0, format="%.1f")
    carbs = st.number_input("Carbs (g)", min_value=0.0, format="%.1f")
    fats = st.number_input("Fats (g)", min_value=0.0, format="%.1f")
    calories = st.number_input("Calories", min_value=0.0, format="%.1f")

    

    # Step 5: Save new food
    if st.button("Save New Food"):
        # Ensure the food name is not empty
        if not food:
            st.error("Food name cannot be empty!")
        elif food in food_data:
            st.warning(f"{food} already exists in the database.")
        else:
            # Append new food entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {
                "Food": food,
                "Unit": unit,
                "Protein": protein,
                "Carbs": carbs,
                "Fats": fats,
                "Calories": calories,
                "Timestamp": timestamp  # Add timestamp
            }
            
            # Convert food_data to DataFrame before saving
            df_new_food = pd.DataFrame([new_entry])  # Convert single entry to DataFrame
            
            # Save new food to Google Sheets
            food_sheet.append_rows(df_new_food.values.tolist())
            
            # Update local food_data dictionary
            food_data[food] = {"Unit": unit, "Protein": protein, "Carbs": carbs, "Fats": fats, "Calories": calories}
            
            st.success(f"{food} has been added to the database!")

# ---- Automatically log the newly added food ----
            unit = food_data[food]["Unit"]  # Get the unit for this food item
            factor = quantity / 100 if is_weight_based(unit) else quantity
            logged_entry = {
                "Date": log_date_str,
                "Food": food,
                "Quantity": quantity,
                "Unit": unit,
                "Protein": protein * factor,
                "Carbs": carbs * factor,
                "Fats": fats * factor,
                "Calories": calories * factor
            }
    
            # Append the logged entry to Google Sheets
            log_sheet.append_rows([list(logged_entry.values())])
            
            st.success(f"{food} has also been logged with {quantity} {unit}!")


#quantity = st.number_input("Quantity", min_value=0.1, step=0.1)

# Compute macros if food exists
if food in food_data:
    unit = food_data[food]["Unit"]  # Get the unit for this food item
    factor = quantity / 100 if is_weight_based(unit) else quantity
    protein = food_data[food]["Protein"] * factor
    carbs = food_data[food]["Carbs"] * factor
    fats = food_data[food]["Fats"] * factor
    calories = food_data[food]["Calories"] * factor

    if st.button("Add to Log"):
        new_entry = {
            "Date": log_date_str,
            "Food": food,
            "Quantity": quantity,
            "Unit": food_data[food]["Unit"],
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats,
            "Calories": calories
        }

        existing_log = log_sheet.get_all_records()
        log_data = pd.DataFrame(existing_log)
        log_data = pd.concat([log_data, pd.DataFrame([new_entry])], ignore_index=True)

        log_sheet.clear()
        log_sheet.update([log_data.columns.values.tolist()] + log_data.values.tolist())

        st.success("Entry Added!")


st.session_state.pop('log_data_today', None)
st.session_state.pop('total_macros', None)
st.session_state.pop('full_log_data', None)

# Show log
#log_data = pd.DataFrame(log_sheet.get_all_records())
#if not log_data.empty:
#    st.dataframe(log_data.tail(10))

# Filter today's data
log_data = pd.DataFrame(log_sheet.get_all_records())
log_data = log_data[log_data["Date"] == log_date_str]


if not log_data.empty:
    st.subheader(f"Today's Log ({log_date_str})")
    st.dataframe(log_data)

    # Show totals
    total_protein = log_data["Protein"].sum()
    total_carbs = log_data["Carbs"].sum()
    total_fats = log_data["Fats"].sum()
    total_calories = log_data["Calories"].sum()
    # Show totals in columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Protein (g)", f"{total_protein:.1f}")
    col2.metric("Carbs (g)", f"{total_carbs:.1f}")
    col3.metric("Fats (g)", f"{total_fats:.1f}")
    col4.metric("Calories", f"{total_calories:.1f}")

    # Protein target input and progress bar
    st.markdown("### 🎯 Protein Goal Tracker")
    target_protein = st.number_input("Your Protein Target (g)", min_value=0.0,value=110.0, format="%.1f", key="protein_target")
    if target_protein > 0:
        protein_percent = min((total_protein / target_protein) * 100, 100)
        st.progress(protein_percent / 100, text=f"{protein_percent:.1f}% of your goal")

        difference = total_protein - target_protein
        if difference < 0:
            st.info(f"You need {abs(difference):.1f}g more protein to reach your goal.")
        else:
            st.success(f"🎉 You've exceeded your protein goal by {difference:.1f}g!")


    if 'log_data_today' not in st.session_state:
        st.session_state['log_data_today'] = log_data

    if 'total_macros' not in st.session_state:
        st.session_state['total_macros'] = {
            'protein': total_protein,
            'carbs': total_carbs,
            'fats': total_fats,
            'calories': total_calories
        }

    st.markdown("### 🥇 Top Foods by Macro Contribution Today")

    def show_top_foods(nutrient, label, color):
        top = log_data.groupby("Food")[nutrient].sum().sort_values(ascending=False).head(3)
        if not top.empty:
            st.markdown(f"**Top 3 {label} Foods:**")
            for idx, (food, amount) in enumerate(top.items(), start=1):
                st.markdown(f"{idx}. {food} - **{amount:.1f}g**", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        show_top_foods("Protein", "Protein", "blue")
        show_top_foods("Fats", "Fats", "orange")

    with col2:
        show_top_foods("Carbs", "Carbs", "green")
        show_top_foods("Calories", "Calorie", "red")



if 'full_log_data' not in st.session_state:
    st.session_state['full_log_data'] = pd.DataFrame(log_sheet.get_all_records())


