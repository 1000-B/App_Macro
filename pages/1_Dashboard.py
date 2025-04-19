


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.title("📊 Dashboard")

# Get the full food log
log_data = pd.DataFrame(st.session_state['full_log_data'])

# Convert date column
log_data['Date'] = pd.to_datetime(log_data['Date'], format='%d/%m/%Y')

# Sidebar controls
st.sidebar.header("📅 Time Range & Metrics")

# Time range selection
range_option = st.sidebar.selectbox("Select Time Range", ["Week", "Month", "Quarter", "Semester", "Year", "All"])

# Metric selection
metric_options = ["Protein", "Carbs", "Fats", "Calories"]
selected_metrics = st.sidebar.multiselect("Select Metrics", metric_options, default=metric_options)

# Determine date cutoff and resample frequency
today = datetime.today()

if range_option == "Week":
    cutoff = today - timedelta(days=7)
    resample_rule = 'D'
    label_format = '%a'
elif range_option == "Month":
    cutoff = today - timedelta(days=30)
    resample_rule = 'D'
    label_format = '%d-%b'
elif range_option == "Quarter":
    cutoff = today - timedelta(weeks=13)
    resample_rule = 'W'
    label_format = '%d-%b'
elif range_option == "Semester":
    cutoff = today - timedelta(weeks=26)
    resample_rule = 'M'
    label_format = '%b'
elif range_option == "Year":
    cutoff = today - timedelta(weeks=52)
    resample_rule = 'M'
    label_format = '%b'
else:
    cutoff = None
    resample_rule = 'M'
    label_format = '%b %Y'

# Filter data
if cutoff:
    filtered_data = log_data[log_data['Date'] >= cutoff]
else:
    filtered_data = log_data.copy()

# Set index to Date and group
filtered_data.set_index('Date', inplace=True)

# Resample for aggregation (average)
resampled_avg = filtered_data[selected_metrics].resample(resample_rule).mean()
resampled_sum = filtered_data[selected_metrics].resample('D').sum()

# Plotting
st.subheader("📊 Macro Trends Over Time")
fig, ax = plt.subplots(figsize=(10, 5))

# Actual values (grey lines)
if range_option in ["Week", "Month"]:
    for metric in selected_metrics:
        ax.plot(resampled_sum.index, resampled_sum[metric], label=f"{metric} (actual)", linestyle='--', alpha=0.4)

# Smoothed/averaged values
for metric in selected_metrics:
    ax.plot(resampled_avg.index, resampled_avg[metric], label=f"{metric} (avg)")

ax.set_xlabel("Date")
ax.set_ylabel("Grams / Calories")
ax.set_title(f"{', '.join(selected_metrics)} over {range_option.lower()} timeframe")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

