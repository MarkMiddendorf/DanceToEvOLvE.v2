import streamlit as st
import pandas as pd
from utils.styling import apply_global_styles
from utils.filters import get_camps_filtered_df
from utils.state import init_session_state
from utils.display import plot_individual_metric

def main():
    apply_global_styles() 
    init_session_state()
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


        # 1. Sort by Sort_Key/session index so earliest records come first
        camps_filtered_sorted = camps_filtered_df.sort_values('Sort_Key')

        #st.write(camps_filtered_df)

        last_seen = {}
        new_campers_records = []

        for _, row in camps_filtered_sorted.iterrows():
            camper_id = row['DancerID']
            sort_key = row['Sort_Key']
            #session_index = row['Session_Index']
            school_year = row['School Year']

            is_new = camper_id not in last_seen

            if is_new:
                new_campers_records.append({
                    'Year_Season_Session': row['Year_Season_Session'],
                    'School Year String': row['School Year String'],
                    'DancerID': camper_id,
                    'Location': row['Location'],
                    'Teacher': row['Teacher'],
                    'Age': row['Age'],
                    'x_axisLabel': row['x_axisLabel'],
                    'Sort_Key': sort_key,
                    #'Session_Index': session_index,
                    'School Year': school_year
                })

            # Always update last seen info
            last_seen[camper_id] = {
                #'session_index': session_index,
                'school_year': school_year
            }

        # 2. Create DataFrame for new campers
        new_campers_df = pd.DataFrame(new_campers_records)

        # 3. Group and calculate counts
        new_campers_summary = new_campers_df.groupby(['School Year String', 'x_axisLabel']).agg({'DancerID': 'nunique'}).reset_index()
        new_campers_summary.rename(columns={'DancerID': 'Number of New Campers'}, inplace=True)

        # Optional: Merge with total unique campers for percentages
        total_campers_df = camps_filtered_df.groupby(['x_axisLabel']).agg({'DancerID': 'nunique'}).reset_index()
        total_campers_df.rename(columns={'DancerID': 'Total Unique Campers'}, inplace=True)

        new_campers_summary = new_campers_summary.merge(total_campers_df, on='x_axisLabel', how='left')
        new_campers_summary['New Camper %'] = (new_campers_summary['Number of New Campers'] / new_campers_summary['Total Unique Campers']) * 100

        # 4. Display
        #st.dataframe(new_campers_summary)

        # Camper Enrollment Ratio (Total dancers / Total classes) as a percentage
        camp_num_classes = camps_filtered_df['Source'].nunique()
        camp_total_dancers = len(camps_filtered_df)
        camp_enrollment_ratio = (camp_total_dancers / camp_num_classes) if camp_num_classes > 0 else 0

        camp_enrollment_df = camps_filtered_df.groupby('x_axisLabel').agg({'Source': 'nunique'}).reset_index()
        camp_enrollment_df.rename(columns={'Source': 'Number of Classes'}, inplace=True)

        camp_enrollment_df = camp_enrollment_df.merge(
            camps_filtered_df[['x_axisLabel', 'Sort_Key']].drop_duplicates(),
            on='x_axisLabel'
        )
        camp_enrollment_df = camp_enrollment_df.sort_values('Sort_Key')

        grouped_df = camps_filtered_df.groupby('x_axisLabel').agg({'DancerID': 'count'}).reset_index()
        grouped_df.rename(columns={'DancerID': 'Number of Dancers'}, inplace=True)

        camp_enrollment_df = camp_enrollment_df.merge(
            grouped_df[['x_axisLabel', 'Number of Dancers']],
            on='x_axisLabel',
            how='left'
        )

        camp_enrollment_df['Enrollment %'] = camp_enrollment_df['Number of Dancers'] / camp_enrollment_df['Number of Classes']
        camp_enrollment_df['Enrollment %'] = camp_enrollment_df['Enrollment %'].fillna(0)

        #st.write(camp_enrollment_df)
        #st.write(camp_enrollment_ratio)

        # Metric 2: Year-by-year count of dancers in camps who appeared earlier in the same year
        #st.subheader("Dancers in Camps Appearing Earlier in the Same Year")

        years = sorted(camps_filtered_df[year_col].unique())
        metric2_results = []

        for year in years:
            year_camps = camps_filtered_df[camps_filtered_df[year_col] == year]
            camp_dancers = set(year_camps[dancer_col].unique())

            earlier_in_year = df[(df[year_col] == year) & (df['Season'] != 'Camp')]
            earlier_dancers = set(earlier_in_year[dancer_col].unique())

            count = len(camp_dancers.intersection(earlier_dancers))
            total_unique_campers = year_camps[dancer_col].nunique()

            x_axisLabel = year_camps['x_axisLabel'].mode()[0] if not year_camps['x_axisLabel'].mode().empty else None
            Sort_Key = year_camps['Sort_Key'].mode()[0] if not year_camps['Sort_Key'].mode().empty else None

            metric2_results.append({
                'School Year': year,
                'x_axisLabel': x_axisLabel,
                'Sort_Key': Sort_Key,
                'Dancers Appearing Earlier': count,
                'Total Unique Campers': total_unique_campers,
                'Percentage Appearing Earlier': (count / total_unique_campers * 100) if total_unique_campers > 0 else 0
            })

        metric2_df = pd.DataFrame(metric2_results)
        #st.dataframe(metric2_df)


        #st.subheader("% Dancers in Camps Last Year and This Year by x_axisLabel")
        metric3_results = []

        for year in years[1:]:
            prev_year_camps = camps_filtered_df[camps_filtered_df[year_col] == year - 1]
            current_year_camps = camps_filtered_df[camps_filtered_df[year_col] == year]

            prev_year_dancers = set(prev_year_camps[dancer_col].unique())
            current_year_dancers = set(current_year_camps[dancer_col].unique())

            count = len(prev_year_dancers.intersection(current_year_dancers))
            total_unique_campers = current_year_camps[dancer_col].nunique()

            x_axisLabel = year_camps['x_axisLabel'].mode()[0] if not year_camps['x_axisLabel'].mode().empty else None
            Sort_Key = year_camps['Sort_Key'].mode()[0] if not year_camps['Sort_Key'].mode().empty else None

            metric3_results.append({
                'School Year': year,
                'x_axisLabel': x_axisLabel,
                'Sort_Key': Sort_Key,
                'Dancers from Y-1 in Y': count,
                'Total Unique Campers This Year': total_unique_campers,
                'Percentage Retained from Y-1': (count / total_unique_campers * 100) if total_unique_campers > 0 else 0
            })

        metric3_df = pd.DataFrame(metric3_results)
        #st.dataframe(metric3_df)

        # Plot Enrollment Ratio
        fig = plot_individual_metric(
            df=camp_enrollment_df,
            x_axis_label='x_axisLabel',
            metric='Enrollment %',
            base_metric_df = None,
            base_metric = None,
            title='Enrollment Ratio',
            as_percentage= False,
            trace_color='lightblue'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Plot New Campers
        fig = plot_individual_metric(
            df=new_campers_summary,
            x_axis_label='x_axisLabel',
            metric='New Camper %',
            base_metric_df = None,
            base_metric = None,
            title='Percentage of Brand New Campers',
            as_percentage= True,
            trace_color='orange'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Plot IntraYear Retention
        fig = plot_individual_metric(
            df=metric2_df,
            x_axis_label='x_axisLabel',
            metric='Percentage Appearing Earlier',
            base_metric_df = None,
            base_metric = None,
            title='Intra-Year Camper Retention',
            as_percentage= True,
            trace_color='pink'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Plot Year over Year Retention
        fig = plot_individual_metric(
            df=metric3_df,
            x_axis_label='x_axisLabel',
            metric='Percentage Retained from Y-1',
            base_metric_df = None,
            base_metric = None,
            title='Year over Year Camper Retention',
            as_percentage= True,
            trace_color='lightgreen'
        )
        st.plotly_chart(fig, use_container_width=True)


main()
