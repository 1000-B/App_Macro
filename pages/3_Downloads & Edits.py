import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Auth ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["service_account"], scopes=scope)
client = gspread.authorize(creds)

# --- Sheets ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mVbGbsThxK9L1mC2-2n_qlC2S0IoPM7zxQYT8DVBiAA/edit#gid=1560030794"
spreadsheet = client.open_by_url(SHEET_URL)
food_sheet = spreadsheet.worksheet("FoodDatabase")
log_sheet = spreadsheet.worksheet("FoodLog")

# --- Load Data ---
@st.cache_data(ttl=60, show_spinner=False)
def load_data():
    food = pd.DataFrame(food_sheet.get_all_records())
    log = pd.DataFrame(log_sheet.get_all_records())
    return food, log

food_data, log_data = load_data()

st.title("📥 Download, Edit & Manage Data")

# --- Download Buttons ---
st.subheader("⬇️ Download Sheets")
col1, col2 = st.columns(2)

with col1:
    if not food_data.empty:
        st.download_button(
            label="Download Food Database as CSV",
            data=food_data.to_csv(index=False).encode('utf-8'),
            file_name='food_database.csv',
            mime='text/csv'
        )

with col2:
    if not log_data.empty:
        st.download_button(
            label="Download Food Log as CSV",
            data=log_data.to_csv(index=False).encode('utf-8'),
            file_name='food_log.csv',
            mime='text/csv'
        )

# --- Function to push updates ---
def save_to_sheet(sheet, df, name="Sheet"):
    try:
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success(f"{name} updated successfully!")
    except Exception as e:
        st.error(f"Failed to update {name}: {e}")

# ============================
# 🔧 Food Database Editor
# ============================
st.subheader("🍽️ Edit Food Database")

food_data_editable = food_data.copy()

# Add new empty row
if st.button("➕ Add Row to Food Database"):
    new_row = pd.DataFrame([[""] * len(food_data.columns)], columns=food_data.columns)
    food_data_editable = pd.concat([food_data_editable, new_row], ignore_index=True)

# Delete rows checkbox
delete_food_rows = st.multiselect("🗑️ Select rows to delete (FoodDatabase):", options=food_data_editable.index.tolist())

if delete_food_rows:
    food_data_editable = food_data_editable.drop(index=delete_food_rows).reset_index(drop=True)

edited_food_data = st.data_editor(
    food_data_editable,
    num_rows="dynamic",
    use_container_width=True,
    key="edit_food"
)

col_save_food, col_revert_food = st.columns(2)
with col_save_food:
    if st.button("✅ Save Changes to Food Database"):
        save_to_sheet(food_sheet, edited_food_data, "Food Database")

with col_revert_food:
    if st.button("🔄 Revert Food Database"):
        st.cache_data.clear()
        st.experimental_rerun()

# ============================
# 📒 Food Log Editor
# ============================
st.subheader("🧾 Edit Food Log")

log_data_editable = log_data.copy()

# Add new empty row
if st.button("➕ Add Row to Food Log"):
    new_row = pd.DataFrame([[""] * len(log_data.columns)], columns=log_data.columns)
    log_data_editable = pd.concat([log_data_editable, new_row], ignore_index=True)

# Delete rows checkbox
delete_log_rows = st.multiselect("🗑️ Select rows to delete (FoodLog):", options=log_data_editable.index.tolist())

if delete_log_rows:
    log_data_editable = log_data_editable.drop(index=delete_log_rows).reset_index(drop=True)

edited_log_data = st.data_editor(
    log_data_editable,
    num_rows="dynamic",
    use_container_width=True,
    key="edit_log"
)

col_save_log, col_revert_log = st.columns(2)
with col_save_log:
    if st.button("✅ Save Changes to Food Log"):
        save_to_sheet(log_sheet, edited_log_data, "Food Log")

with col_revert_log:
    if st.button("🔄 Revert Food Log"):
        st.cache_data.clear()
        st.experimental_rerun()
