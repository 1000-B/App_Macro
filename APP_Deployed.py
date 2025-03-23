##production app
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials




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

st.title("Macro Tracker")
st.subheader("Log Your Food")

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


quantity = st.number_input("Quantity", min_value=1, step=1)

# Step 4: Handle food selection or new entry
if food in food_data:
    # Existing food - Compute macros
    factor = quantity if food_data[food]["Unit"] == "piece" else quantity / 100
    protein = food_data[food]["Protein"] * factor
    carbs = food_data[food]["Carbs"] * factor
    fats = food_data[food]["Fats"] * factor
else:
    # New food - Ask for macros
    # New food - Ask for macros
    st.warning("Food not found. Enter macros below to save it.")
    
    # Predefined unit options
    unit_options = ["grams", "pieces", "cups", "tablespoons", "teaspoons", "ml"]
    
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

    

    # Step 5: Save new food
    if st.button("Save New Food"):
        # Ensure the food name is not empty
        if not food:
            st.error("Food name cannot be empty!")
        elif food in food_data:
            st.warning(f"{food} already exists in the database.")
        else:
            # Append new food entry
            new_entry = {
                "Food": food,
                "Unit": unit,
                "Protein": protein,
                "Carbs": carbs,
                "Fats": fats
            }
            
            # Convert food_data to DataFrame before saving
            df_new_food = pd.DataFrame([new_entry])  # Convert single entry to DataFrame
            
            # Save new food to Google Sheets
            food_sheet.append_rows(df_new_food.values.tolist())
            
            # Update local food_data dictionary
            food_data[food] = {"Unit": unit, "Protein": protein, "Carbs": carbs, "Fats": fats}
            
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
            "Date": pd.Timestamp.today().strftime('%d/%m/%Y'),
            "Food": food,
            "Quantity": quantity,
            "Unit": food_data[food]["Unit"],
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats
        }

        existing_log = log_sheet.get_all_records()
        log_data = pd.DataFrame(existing_log)
        log_data = pd.concat([log_data, pd.DataFrame([new_entry])], ignore_index=True)

        log_sheet.clear()
        log_sheet.update([log_data.columns.values.tolist()] + log_data.values.tolist())

        st.success("Entry Added!")

# Show log
log_data = pd.DataFrame(log_sheet.get_all_records())
if not log_data.empty:
    st.dataframe(log_data.tail(10))



# Macro breakdown over time
st.subheader("Macro Breakdown")
time_filter = st.radio("View by:", ("Daily", "Weekly", "Monthly"))

def plot_macros(filtered_data):
    fig, ax = plt.subplots()
    filtered_data.set_index("Date")[['Protein', 'Carbs', 'Fats']].plot(kind='bar', ax=ax)
    st.pyplot(fig)

log_data = pd.DataFrame(log_sheet.get_all_records())
if not log_data.empty:
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



        