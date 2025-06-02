import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scope)
client = gspread.authorize(creds)

# Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mVbGbsThxK9L1mC2-2n_qlC2S0IoPM7zxQYT8DVBiAA/edit?gid=1560030794#gid=1560030794"
spreadsheet = client.open_by_url(SHEET_URL)
food_sheet = spreadsheet.worksheet("FoodDatabase")
log_sheet = spreadsheet.worksheet("FoodLog")

# Load data
food_data = pd.DataFrame(food_sheet.get_all_records())
log_data = pd.DataFrame(log_sheet.get_all_records())

st.title("📥 Download Data")

if not food_data.empty:
    st.download_button(
        label="Download Food Database as CSV",
        data=food_data.to_csv(index=False).encode('utf-8'),
        file_name='food_database.csv',
        mime='text/csv'
    )

if not log_data.empty:
    st.download_button(
        label="Download Food Log as CSV",
        data=log_data.to_csv(index=False).encode('utf-8'),
        file_name='food_log.csv',
        mime='text/csv'
    )

# --- Editable Tables ---
st.subheader("📝 Edit Food Database")
edited_food_data = st.data_editor(food_data, num_rows="dynamic", use_container_width=True, key="edit_food")

if st.button("✅ Save Changes to Food Database"):
    try:
        food_sheet.clear()
        food_sheet.update([edited_food_data.columns.values.tolist()] + edited_food_data.values.tolist())
        st.success("Food Database updated successfully!")
    except Exception as e:
        st.error(f"Failed to update Food Database: {e}")

st.subheader("📝 Edit Food Log")
edited_log_data = st.data_editor(log_data, num_rows="dynamic", use_container_width=True, key="edit_log")

if st.button("✅ Save Changes to Food Log"):
    try:
        log_sheet.clear()
        log_sheet.update([edited_log_data.columns.values.tolist()] + edited_log_data.values.tolist())
        st.success("Food Log updated successfully!")
    except Exception as e:
        st.error(f"Failed to update Food Log: {e}")