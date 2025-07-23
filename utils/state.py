import streamlit as st

def init_session_state():
    if "display_toggle" not in st.session_state:
        st.session_state["display_toggle"] = "All Time"
    
    # Add other keys as needed
    default_keys = {
        "reset_filters": False,
        "select_all_filters": False,
        "df": None,  # main dataset
        "filtered_df": None,  # post-filtered version
        "selected_filters": {}  # dict of filters by field
    }

    for key, val in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = val
