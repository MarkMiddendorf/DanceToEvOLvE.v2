import streamlit as st
import pandas as pd
from utils.styling import apply_global_styles
from utils.filters import get_camps_filtered_df
from utils.state import init_session_state

def main():
    apply_global_styles() 
    #init_session_state()
    # Display view
    display_toggle = st.session_state["display_toggle"]
    st.session_state['display_toggle'] = display_toggle

    #st.write("Session State Snapshot:", st.session_state)
        # Simulate loading the master df again here or store it globally
    if 'df' not in st.session_state:
        st.error("Master dataframe not loaded. Please return to Main page first.")
    else:
        df = st.session_state['df']  # Recommended to store full df once in session state

        # Process camps on this page
        camps_filtered_df = get_camps_filtered_df(df)

        st.title("🏕️ Camps")
        
        # Assume 'dancer_id' is the unique identifier for dancers and 'year' is the year column
        # Adjust these column names if they differ in your DataFrames
        dancer_col = 'DancerID'  # Replace with actual column name if different
        year_col = 'School Year'  # Replace with actual column name if different

        # Metric 1: Year-by-year count of dancers in camps who appeared earlier in the same year
        st.subheader("Dancers in Camps Appearing Earlier in the Same Year")
        years = sorted(camps_filtered_df[year_col].unique())
        metric1_results = []
        
        for year in years:
            # Filter camps for the current year
            year_camps = camps_filtered_df[camps_filtered_df[year_col] == year]
            # Get unique dancers in camps for the year
            camp_dancers = set(year_camps[dancer_col].unique())
            # Filter master df for the same year, excluding camps (if camps are a specific type)
            earlier_in_year = df[(df[year_col] == year) & (df['Season'] != 'Camp')]
            # Get unique dancers who appeared earlier
            earlier_dancers = set(earlier_in_year[dancer_col].unique())
            # Count dancers in camps who appeared earlier
            count = len(camp_dancers.intersection(earlier_dancers))
            metric1_results.append({'Year': year, 'Dancers Appearing Earlier': count})
        
        # Display Metric 1 results as a DataFrame
        metric1_df = pd.DataFrame(metric1_results)
        st.dataframe(metric1_df)

        # Metric 2: Year-by-year count of dancers in camps_filtered_df from Y-1 also in Y
        st.subheader("Dancers in Camps from Year Y-1 Also in Year Y")
        metric2_results = []
        
        for year in years[1:]:  # Start from second year to have Y-1
            # Get dancers in camps for year Y-1
            prev_year_camps = camps_filtered_df[camps_filtered_df[year_col] == year - 1]
            prev_year_dancers = set(prev_year_camps[dancer_col].unique())
            # Get dancers in camps for year Y
            current_year_camps = camps_filtered_df[camps_filtered_df[year_col] == year]
            current_year_dancers = set(current_year_camps[dancer_col].unique())
            # Count dancers present in both Y-1 and Y
            count = len(prev_year_dancers.intersection(current_year_dancers))
            metric2_results.append({'Year': year, 'Dancers from Y-1 in Y': count})
        
        # Display Metric 2 results as a DataFrame
        metric2_df = pd.DataFrame(metric2_results)
        st.dataframe(metric2_df)


main()
