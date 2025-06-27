import streamlit as st

def init_session_state():
    defaults = {
        #"display_toggle": "School Year / School Year"
        # other shared keys...
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
