import streamlit as st

def apply_global_styles():

    st.markdown(
        f"""
        <style>
            [data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"] {{
                font-family: 'Georgia', serif;
                font-size: 16px;
            }}

            section[data-testid="stSidebar"] ul li:first-child span {{
                text-transform: uppercase;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
