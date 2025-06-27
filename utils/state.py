import streamlit as st

def init_session_state():
    defaults = {
        if "display_toggle" not in st.session_state:
        st.session_state["display_toggle"] = "School Year / School Year"
        # other shared keys...
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
