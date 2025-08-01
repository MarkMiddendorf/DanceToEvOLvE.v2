import streamlit as st
import pandas as pd
from PIL import Image
from data.data_loader import load_data
from utils.styling import apply_global_styles
from utils.filters import get_filtered_df
from utils.filters import render_persistent_filters
from utils.display import apply_display_toggle
from utils.helpers import school_year
from utils.helpers import calculate_age
from utils.state import init_session_state
from streamlit import cache_data

st.set_page_config(page_title="Dance Filters", layout="wide")
apply_global_styles()
init_session_state()


logo = Image.open("assets/danceLogo.png")

col1, col2 = st.columns([1, 11])
with col1:
    st.image(logo, width=80)
with col2:
    st.markdown("## Dance To EvOLvE Filters")

# Cached data load
@st.cache_data
def get_data():
    return load_data()

# Load and process data
df = get_data()
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Session'] = pd.to_numeric(df['Session'], errors='coerce').fillna(0).astype(int)
df['Season'] = df['Season'].astype(str).str.title().str.strip()


df = school_year(df)

df = calculate_age(df)

#st.write(df)

# Format Data
df['School Year'] = df['School Year'].fillna(0).astype(int)
df['Session'] = pd.to_numeric(df['Session'], errors='coerce').fillna(0).astype(int)
df['Season'] = df['Season'].astype(str)
df['Phone'] = df['Phone'].astype(str).replace('nan', '')  # Convert to string, replace NaN with empty string
season_order = {'Fall': 1, 'Winter': 2, 'Spring': 3, 'Summer': 4, 'Camp': 5}
df['Season_Order'] = df['Season'].map(season_order)
df['Sort_Key'] = df['School Year'] * 100 + df['Season_Order'] * 10 + df['Session']
df['Year_Season_Session'] = df['School Year String'] + ' ' + df['Season'] + ' ' + df['Session'].astype(str)

st.session_state['df'] = df

# Initialize reset/select-all flags if not present
if "reset_filters" not in st.session_state:
    st.session_state.reset_filters = False
if "select_all_filters" not in st.session_state:
    st.session_state.select_all_filters = False

# Two-button layout
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Clear Filters"):
        st.session_state.reset_filters = True
with col2:
    if st.button("✅ Select All Filters"):
        st.session_state.select_all_filters = True

# Display toggle
df, display_toggle = apply_display_toggle(df)
st.session_state["display_toggle"] =  display_toggle

# Render persistent filters
selected_filters = render_persistent_filters(df)

# Clear flags after use
st.session_state["reset_filters"] = False
st.session_state["select_all_filters"] = False


# Apply filters to DataFrame
filtered_df = get_filtered_df(df, selected_filters)

st.session_state['filtered_df'] = filtered_df
#st.write("Session State Snapshot:", st.session_state)

