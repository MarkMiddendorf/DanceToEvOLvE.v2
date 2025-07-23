import streamlit as st
import pandas as pd
import numpy as np

def select_all_option_expander(label, options, sort_order=None, key=None):
    
    # Normalize key used inside selected_filters
    key = label.lower().replace(" ", "_")

    if sort_order == 'alphabetical':
        options = sorted(options)
    elif sort_order == 'numerical':
        options = sorted(
            options,
            key=lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else float('inf')
        )

    options = list(options)

    # Initialize selected_filters dict
    if "selected_filters" not in st.session_state:
        st.session_state["selected_filters"] = {}

    # Reset / Select All / Default logic
    if st.session_state.get("reset_filters"):
        st.session_state["selected_filters"][key] = []
    elif st.session_state.get("select_all_filters"):
        st.session_state["selected_filters"][key] = options
    elif key not in st.session_state["selected_filters"]:
        st.session_state["selected_filters"][key] = options
    else:
        st.session_state["selected_filters"][key] = [
            val for val in st.session_state["selected_filters"][key] if val in options
        ]

    # Render the widget
    user_selection =  st.multiselect(
        f"Select {label}:",
        options,
        default=st.session_state["selected_filters"][key],
    )

    st.session_state["selected_filters"][key] = user_selection

    return user_selection




def get_or_init_session_state(key, default_values):
    """Initialize or retrieve session state for a given key."""
    if key not in st.session_state:
        st.session_state[key] = default_values
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

    # Convert Age to numeric for sorting
    #df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(float)

    # Initialize selected_filters in session state if not present
    if 'selected_filters' not in st.session_state:
        st.session_state['selected_filters'] = {
            'classes': df['Class'].unique().tolist(),
            'locations': df['Location'].unique().tolist(),
            'teachers': df['Teacher'].unique().tolist(),
            'ages': df['Age'].unique().tolist(),
            'reg_nonreg': df['Reg/NonReg'].unique().tolist(),
            'school_years': df['School Year'].unique().tolist(),
            'seasons': df['Season'].unique().tolist(),
            'cities': df['City'].unique().tolist(),
            'days': df['Day'].unique().tolist(),
            'times': df['Time'].unique().tolist(),
            'sessions': df['Session'].unique().tolist()
        }

    selected_filters = st.session_state['selected_filters']

    # --- Top Filters ---
    col_school_year, col_season, col_session = st.columns(3)
    with col_school_year:
        selected_filters['school_years'] = select_all_option_expander(
            'School Year',
            df['School Year'].unique(),
            sort_order='Numerical',
            #default=selected_filters['school_years'],
            #key='School Year-multiselect'
        )

    with col_season:
        selected_filters['seasons'] = select_all_option_expander(
            'Season',
            df['Season'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['seasons'],
            #key='Season-multiselect'
        )

    with col_session:
        selected_filters['sessions'] = select_all_option_expander(
            'Session',
            df['Session'].unique(),
            sort_order='numerical',
            #default=selected_filters['sessions'],
            #key='Session-multiselect'
        )

    # --- Additional Filters ---
    st.markdown("<h5 style='text-align: left;'>Additional Filters</h5>", unsafe_allow_html=True)

    col_city, col_location, col_reg_nonreg = st.columns(3)
    with col_city:
        selected_filters['cities'] = select_all_option_expander(
            'City',
            df['City'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['cities'],
            #key='City-multiselect'
        )
    #st.session_state['City-multiselect'] = selected_filters['cities']

    with col_location:
        filtered_locations = df[df['City'].isin(selected_filters['cities'])]['Location'].unique()
        selected_filters['locations'] = select_all_option_expander(
            'Location',
            filtered_locations,
            sort_order='alphabetical',
            #default=selected_filters['locations'],
            #key='Location-multiselect'
        )

    with col_reg_nonreg:
        selected_filters['reg_nonreg'] = select_all_option_expander(
            'Reg/NonReg',
            df['Reg/NonReg'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['reg_nonreg'],
            #key='Reg/NonReg-multiselect'
        )

    col_class, = st.columns(1)
    with col_class:
        selected_filters['classes'] = select_all_option_expander(
            'Class',
            df['Class'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['classes'],
            #key='Class-multiselect'
        )

    col_age, col_teacher, col_day, col_time = st.columns(4)
    with col_age:
        selected_filters['ages'] = select_all_option_expander(
            'Age',
            df['Age'].unique(),
            sort_order='numerical',
            #default=selected_filters['ages'],
            #key='Age-multiselect'
        )

    with col_teacher:
        selected_filters['teachers'] = select_all_option_expander(
            'Teacher',
            df['Teacher'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['teachers'],
            #key='Teacher-multiselect'
        )

    with col_day:
        selected_filters['days'] = select_all_option_expander(
            'Day',
            df['Day'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['days'],
            #key='Day-multiselect'
        )

    with col_time:
        selected_filters['times'] = select_all_option_expander(
            'Time',
            df['Time'].unique(),
            sort_order='alphabetical',
            #default=selected_filters['times'],
            #key='Time-multiselect'
        )

    # Update session state with the latest filter selections
    st.session_state['selected_filters'] = selected_filters

    # Update filtered_df in session state
    #filtered_df = get_filtered_df(df, selected_filters)
    #st.session_state['filtered_df'] = filtered_df

    return selected_filters