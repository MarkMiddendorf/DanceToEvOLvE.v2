import streamlit as st
from utils.styling import apply_global_styles
from utils.state import init_session_state

def main():
    apply_global_styles() 
    init_session_state()
    #st.write("Session State Snapshot:", st.session_state)
    st.title("🧺 Group By")
    st.write("Group by logic here")
    # Display view
    display_toggle = st.session_state["display_toggle"]
    st.header(display_toggle)
    st.session_state['display_toggle'] = display_toggle

main()

