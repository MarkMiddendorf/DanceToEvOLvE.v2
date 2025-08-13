import streamlit as st

def init_session_state():
    #if "display_toggle" not in st.session_state:
        #st.session_state["display_toggle"] = "All Time"
    
    default_keys = {
        "reset_filters": False,
        "select_all_filters": False,
        "df": None,
        "filtered_df": None
    }

    for key, val in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ✅ Only initialize selected_filters if not already present
    if "selected_filters" not in st.session_state:
        st.session_state["selected_filters"] = {}

