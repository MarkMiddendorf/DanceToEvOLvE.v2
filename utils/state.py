import streamlit as st

def init_session_state():
    if "display_toggle" not in st.session_state:
        st.session_state["display_toggle"] = "School Year / School Year"
    
    # Add other keys as needed
    default_keys = {
        "reset_filters": False,
        "select_all_filters": False,
        # Add more shared state keys if needed
    }

    for key, val in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = val
