import streamlit as st
import pandas as pd
import numpy as np

def select_all_option_expander(label, options, sort_order=None):
    key = label.lower().replace(" ", "_")
    options_key = f"{key}_last_options"

    if sort_order == 'alphabetical':
        options = sorted(options)
    elif sort_order == 'numerical':
        options = sorted(
            options,
            key=lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else float('inf')
        )
    options = list(options)

    # Initialize selected_filters if needed
    if "selected_filters" not in st.session_state:
        st.session_state["selected_filters"] = {}

    # ----- Safe Initialization -----
    first_load = key not in st.session_state
    reset = st.session_state.get("reset_filters", False)
    select_all = st.session_state.get("select_all_filters", False)

    if first_load or select_all:
        st.session_state[key] = options
    elif reset:
        st.session_state[key] = []
    else:
        current = st.session_state.get(key, [])
        valid = [v for v in current if v in options]

        last_options = st.session_state.get(options_key, options)
        options_grew = len(options) > len(last_options)

        # Only auto-expand if user didn't deselect and options grew
        if current == valid and options_grew:
            st.session_state[key] = options
        else:
            st.session_state[key] = valid

    # Save latest options
    st.session_state[options_key] = options

    # Render multiselect
    st.multiselect(f"Select {label}:", options, key=key)

    # Update selected_filters
    st.session_state["selected_filters"][key] = st.session_state[key]

    return st.session_state[key]


@st.cache_data
def get_filtered_df(df, selected_filters: dict):
    """Filter DataFrame based on selected filters."""
    filtered = df[
        (df['Class'].isin(selected_filters['classes'])) &
        (df['Location'].isin(selected_filters['locations'])) &
        (df['Teacher'].isin(selected_filters['teachers'])) &
        (df['Age'].isin(selected_filters['ages'])) &
        (df['Reg/NonReg'].isin(selected_filters['reg_nonreg'])) &
        (df['School Year'].isin(selected_filters['school_years'])) &
        (df['Season'].isin(selected_filters['seasons'])) &
        (df['City'].isin(selected_filters['cities'])) &
        (df['Day'].isin(selected_filters['days'])) &
        (df['Time'].isin(selected_filters['times'])) &
        (df['Session'].isin(selected_filters['sessions']))
    ]
    return filtered

@st.cache_data
def get_camps_filtered_df(df):
    """Filter DataFrame for camps."""
    filtered = df[df['Season'] == 'Camp']
    return filtered

def render_persistent_filters(df):
    """Render filters with persistent session state across pages."""
    if "select_all_filters" not in st.session_state:
        st.session_state.select_all_filters = False
    sf = st.session_state["selected_filters"]

    # --- Top Filters (in order of dependency) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        sf["school_years"] = select_all_option_expander(
            'School Year',
            df["School Year"].unique(),
            sort_order='numerical'
        )

    # Filter df by School Year before next
    df = df[df["School Year"].isin(sf["school_years"])]

    with col2:
        sf["seasons"] = select_all_option_expander(
            'Season',
            df["Season"].unique(),
            sort_order='alphabetical'
        )

    df = df[df["Season"].isin(sf["seasons"])]

    with col3:
        sf["sessions"] = select_all_option_expander(
            'Session',
            df["Session"].unique(),
            sort_order='numerical'
        )

    df = df[df["Session"].isin(sf["sessions"])]

    # --- Additional Filters ---
    st.markdown("<h5 style='text-align: left;'>Additional Filters</h5>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        sf["cities"] = select_all_option_expander(
            'City',
            df["City"].unique(),
            sort_order='alphabetical'
        )

    df = df[df["City"].isin(sf["cities"])]

    with col2:
        sf["locations"] = select_all_option_expander(
            'Location',
            df["Location"].unique(),
            sort_order='alphabetical'
        )

    df = df[df["Location"].isin(sf["locations"])]

    with col3:
        sf["reg_nonreg"] = select_all_option_expander(
            'Reg/NonReg',
            df["Reg/NonReg"].unique(),
            sort_order='alphabetical'
        )

    df = df[df["Reg/NonReg"].isin(sf["reg_nonreg"])]

    col_class, = st.columns(1)
    with col_class:
        sf["classes"] = select_all_option_expander(
            'Class',
            df["Class"].unique(),
            sort_order='alphabetical'
        )

    df = df[df["Class"].isin(sf["classes"])]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sf["ages"] = select_all_option_expander(
            'Age',
            df["Age"].unique(),
            sort_order='numerical'
        )
    df = df[df["Age"].isin(sf["ages"])]

    with col2:
        sf["teachers"] = select_all_option_expander(
            'Teacher',
            df["Teacher"].unique(),
            sort_order='alphabetical'
        )
    df = df[df["Teacher"].isin(sf["teachers"])]

    with col3:
        sf["days"] = select_all_option_expander(
            'Day',
            df["Day"].unique(),
            sort_order='alphabetical'
        )
    df = df[df["Day"].isin(sf["days"])]

    with col4:
        sf["times"] = select_all_option_expander(
            'Time',
            df["Time"].unique(),
            sort_order='alphabetical'
        )
    df = df[df["Time"].isin(sf["times"])]

    return sf
