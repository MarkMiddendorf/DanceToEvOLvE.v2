import streamlit as st
import pandas as pd
from utils.styling import apply_global_styles
from utils.state import init_session_state



def main():
    apply_global_styles() 
    init_session_state()
    st.write("Session State Snapshot:", st.session_state)
    st.title("🔢 Ages")
    display_toggle = st.session_state["display_toggle"]
    st.session_state['display_toggle'] = display_toggle

    if 'df' not in st.session_state:
        st.error("Master dataframe not loaded. Please return to Main page first.")
    else:
        df = st.session_state['df']
        invalid_ages_df = df[(df['Age'] < 1) | (df['Age'] > 16)]
        st.write("Rows with ages outside 1–16:")
        st.dataframe(invalid_ages_df)

main()

