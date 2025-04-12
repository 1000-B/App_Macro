import streamlit as st

st.title("📊 Dashboard")

if 'total_macros' in st.session_state:
    macros = st.session_state['total_macros']
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Protein (g)", f"{macros['protein']:.1f}")
    col2.metric("Carbs (g)", f"{macros['carbs']:.1f}")
    col3.metric("Fats (g)", f"{macros['fats']:.1f}")
    col4.metric("Calories", f"{macros['calories']:.1f}")

    # 🎯 Protein Tracker
    st.markdown("### 🎯 Protein Goal Tracker")
    target_protein = st.number_input("Your Protein Target (g)", min_value=0.0, value=110.0, format="%.1f", key="dashboard_protein_target")

    if target_protein > 0:
        percent = min((macros['protein'] / target_protein) * 100, 100)
        st.progress(percent / 100, text=f"{percent:.1f}% of your goal")

        diff = macros['protein'] - target_protein
        if diff < 0:
            st.info(f"You need {abs(diff):.1f}g more protein to reach your goal.")
        else:
            st.success(f"🎉 You've exceeded your protein goal by {diff:.1f}g!")
else:
    st.warning("No data available yet. Please log some food on the Home page.")
