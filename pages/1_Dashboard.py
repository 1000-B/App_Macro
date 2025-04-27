import streamlit as st
import pandas as pd
import numpy as np
import calendar
from datetime import datetime
import plotly.graph_objects as go

# --- Load Food Log ---
if 'log_data_full' not in st.session_state:
    st.error("No Food Log data found. Please log some food first.")
    st.stop()

food_log = st.session_state.log_data_full.copy()

# --- Preprocess ---
# Ensure Date column is datetime
food_log['Date'] = pd.to_datetime(food_log['Date'], dayfirst=True)

# Aggregate daily totals
daily_macros = food_log.groupby('Date').agg({
    'Protein': 'sum',
    'Carbs': 'sum',
    'Fats': 'sum'
}).reset_index()

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Dashboard Settings")

# Macro selection
macro = st.sidebar.selectbox(
    "Select Macro to Visualize:",
    ['Protein', 'Carbs', 'Fats'],
    index=0
)

# Macro goal thresholds (editable)
st.sidebar.subheader("Threshold Settings (adjust if needed)")
if macro == "Protein":
    low_threshold = st.sidebar.number_input("Low (g)", value=50)
    medium_threshold = st.sidebar.number_input("Medium (g)", value=100)
    high_threshold = st.sidebar.number_input("High (g)", value=150)
elif macro == "Carbs":
    low_threshold = st.sidebar.number_input("Low (g)", value=150)
    medium_threshold = st.sidebar.number_input("Medium (g)", value=200)
    high_threshold = st.sidebar.number_input("High (g)", value=250)
else:  # Fat
    low_threshold = st.sidebar.number_input("Low (g)", value=30)
    medium_threshold = st.sidebar.number_input("Medium (g)", value=60)
    high_threshold = st.sidebar.number_input("High (g)", value=90)

# Date Range Selection
st.sidebar.subheader("Select Date Range")
min_date = daily_macros['Date'].min()
max_date = daily_macros['Date'].max()

start_date = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date!")
    st.stop()

# Filter for selected date range
mask = (daily_macros['Date'] >= pd.to_datetime(start_date)) & (daily_macros['Date'] <= pd.to_datetime(end_date))
filtered_macros = daily_macros.loc[mask]

# --- Main Page ---
st.title("📅 Macro Intake Calendar Overview")

st.markdown(f"### Macro: **{macro}** from {start_date} to {end_date}")

# --- Create Calendar Heatmap ---
# Create pivot table: rows = weeks, columns = weekdays
def create_calendar_data(df, macro_col):
    df['Day'] = df['Date'].dt.day
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Weekday'] = df['Date'].dt.weekday  # Monday=0

    pivot = pd.pivot_table(df, index='Week', columns='Weekday', values=macro_col, aggfunc='sum')
    pivot = pivot.fillna(0)
    return pivot

calendar_data = create_calendar_data(filtered_macros, macro)

# --- Color Mapping Function ---
def get_color(val):
    if val == 0:
        return "lightgrey"  # No entry
    elif val < low_threshold:
        return "#FF4B4B"  # Red
    elif val < medium_threshold:
        return "#FFA500"  # Orange
    elif val < high_threshold:
        return "#FFFF00"  # Yellow
    else:
        return "#4CAF50"  # Green

# --- Plot Heatmap ---
fig = go.Figure()

for week_idx, week in enumerate(calendar_data.index):
    for day_idx in range(7):
        value = calendar_data.loc[week, day_idx] if day_idx in calendar_data.columns else 0
        color = get_color(value)
        day_label = "" if value == 0 else str(int(value))

        fig.add_trace(go.Scatter(
            x=[day_idx],
            y=[-week_idx],
            text=[day_label],
            mode='markers+text',
            marker=dict(size=60, color=color, line=dict(width=1, color="black")),
            textfont=dict(color="black", size=14),
            hoverinfo="skip",
        ))

fig.update_layout(
    width=700,
    height=400,
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(7)),
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        side='top'
    ),
    yaxis=dict(showticklabels=False),
    margin=dict(l=20, r=20, t=50, b=20),
    plot_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)

# --- Some Stats ---
st.markdown("### 📊 Summary Stats")

total_macro = filtered_macros[macro].sum()
avg_macro = filtered_macros[macro].mean()

col1, col2 = st.columns(2)
col1.metric("Total Intake", f"{total_macro:.1f} g")
col2.metric("Average Daily Intake", f"{avg_macro:.1f} g")

# Optional: Show raw data
with st.expander("See Raw Macro Data for Selected Range"):
    st.dataframe(filtered_macros[['Date', 'Protein', 'Carbs', 'Fats']])
