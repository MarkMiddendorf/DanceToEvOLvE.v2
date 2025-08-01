import streamlit as st
import plotly.express as px
import pandas as pd
from utils.styling import apply_global_styles
from PIL import Image
from utils.display import metric_card
from utils.display import plot_individual_metric
from utils.state import init_session_state
from utils.display import apply_display_toggle


logo = Image.open("assets/danceLogo.png")

col1, col2 = st.columns([1, 11])
with col1:
    st.image(logo, width=80)
with col2:
    st.markdown("## Dance To EvOLvE Dashboard")

def main():
    apply_global_styles() 
    init_session_state()
    #st.write("Session State Snapshot:", st.session_state)
    
    # Display view
    df = st.session_state['df']
    #df, display_toggle = apply_display_toggle(df) 
    #display_toggle = st.session_state.get("display_toggle")
    #st.session_state['display_toggle'] = display_toggle
    #st.header(display_toggle)


    if 'filtered_df' in st.session_state:
        filtered_df = st.session_state['filtered_df']
        filtered_df, display_toggle = apply_display_toggle(filtered_df) 
        #display_toggle = st.session_state.get("display_toggle")
        #st.session_state['display_toggl`e'] = display_toggle
        st.header(display_toggle)

        #st.write(filtered_df)  # or use it in charts, logic, etc.

        # Total Enrollment (head count) -> filtered dataframe count
        grouped_df = filtered_df.groupby('x_axisLabel').agg({'DancerID': 'count'}).reset_index()
        grouped_df.rename(columns={'DancerID': 'Number of Dancers'}, inplace=True)
        grouped_df = grouped_df.merge(filtered_df[['x_axisLabel', 'Sort_Key']].drop_duplicates(), on='x_axisLabel')
        grouped_df = grouped_df.sort_values('Sort_Key')
        total_dancers = grouped_df['Number of Dancers'].sum()

        #st.write("Total Dancers: ", total_dancers)

        # Unique Students (unique head count) -> filtered dataframe unique count
        unique_dancers_df = filtered_df.groupby(['School Year String', 'x_axisLabel', 'Sort_Key', 'Session_Index']).agg({'DancerID': 'nunique'}).reset_index()
        #st.write(unique_dancers_df)
        unique_dancers_df.rename(columns={'DancerID': 'Number of Unique Dancers'}, inplace=True)
        #st.write(unique_dancers_df)
        total_unique_dancers = unique_dancers_df['Number of Unique Dancers'].sum()


        #st.write("Total Unique Dancers: ", total_unique_dancers)

    # Brand New Students (never taken a class) -> filtered dataframe...Are all students brand new period 0?
        # 1. Sort filtered data
        filtered_pool = df.sort_values('Sort_Key')
        #st.write(filtered_pool)

        # 2. Track last seen by Sort_Key (session-based)
        last_seen = {}
        newly_acquired = []

        for _, row in filtered_pool.iterrows():
            dancer_id = row['DancerID']
            sort_key = row['Sort_Key']
            xaxislabel = row['x_axisLabel']
            session_index = row['Session_Index']
            school_year = row['School Year']  # assuming this is an int

            is_new = False
            if dancer_id not in last_seen:
                is_new = True
            else:
                last = last_seen[dancer_id]

                if display_toggle == "All Time":
                    # If they were never seen before = new
                    if last is None:
                        is_new = True
                    else:
                        is_new = False

                elif display_toggle == "Intra Year":
                    # Only count the first time in current year
                    if last['school_year'] != school_year:
                        is_new = True
                    else:
                        is_new = False  # already seen in current year

                elif display_toggle == "Session (Consecutive)":
                    # New if they missed at least 1 session
                    if session_index - last['session_index'] > 1:
                        is_new = True
                    else:
                        is_new = False

            if is_new:
                newly_acquired.append({
                    'Year_Season_Session': row['Year_Season_Session'],
                    'School Year String': row['School Year String'],
                    'DancerID': dancer_id,
                    'Class': row['Class'],
                    'Location': row['Location'],
                    'Teacher': row['Teacher'],
                    'Age': row['Age'],
                    'Reg/NonReg': row['Reg/NonReg'],
                    'x_axisLabel': xaxislabel,
                    'Sort_Key': sort_key,
                    'Session_Index': session_index,
                    'School Year': school_year
                })

            # Always update last seen info
            last_seen[dancer_id] = {
                'session_index': session_index,
                'school_year': school_year
            }

        # 3. After loop: create DataFrame
        acquired_df = pd.DataFrame(newly_acquired)
        #st.write("AquiredDF: ", acquired_df)

        # 4. Count new students
        if display_toggle == "Session (Consecutive)":
            new_students_df = acquired_df.groupby(['School Year String', 'Session_Index','Sort_Key']).agg({'DancerID': 'nunique','x_axisLabel':'first'}).reset_index()
            new_students_df.rename(columns={'DancerID': 'Number of New Students'}, inplace=True)
            new_students_df = new_students_df.merge(unique_dancers_df,on=['x_axisLabel','School Year String','Sort_Key'], how='left')
            new_students_df['New Student %'] = (new_students_df['Number of New Students'] / new_students_df['Number of Unique Dancers'])*100
            num_new_students = new_students_df['Number of New Students'].sum()
        else:
            new_students_df = acquired_df.groupby(['School Year String', 'x_axisLabel','Sort_Key']).agg({'DancerID': 'nunique'}).reset_index()
            new_students_df.rename(columns={'DancerID': 'Number of New Students'}, inplace=True)
            new_students_df = new_students_df.merge(unique_dancers_df,on=['x_axisLabel','School Year String','Sort_Key'], how='left')
            new_students_df['New Student %'] = (new_students_df['Number of New Students'] / new_students_df['Number of Unique Dancers'])*100
            num_new_students = new_students_df['Number of New Students'].sum()

        st.write(new_students_df)

        #st.write("Number of New Students: ", num_new_students)

    # Retained Students (Unique students - brand new) -> filtered dataframe.... only in p1 forward
        # Merge the unique enrollment and acquisition DataFrames on 'x_axisLabel'
        retention_df = new_students_df
        
        # Calculate Retained Dancers as the difference between Total Unique Dancers and Newly Acquired Students
        retention_df['Retained Students'] = retention_df['Number of Unique Dancers'] - retention_df['Number of New Students'].fillna(0)
        num_retained_students = retention_df['Retained Students'].sum()
        
        # Calculate retention as a percentage
        retention_df['Retention %'] = (retention_df['Retained Students'] / retention_df['Number of Unique Dancers']) * 100
        
        # Sort the DataFrame based on Sort_Key for proper session ordering
        #retention_df = retention_df.merge(df[['x_axisLabel', 'Sort_Key']].drop_duplicates(), on='x_axisLabel')
        retention_df = retention_df.sort_values('Sort_Key')
        #st.write(retention_df)

        # ---- Metric Cards ----
        # 1. Number of classes by source
        num_classes = filtered_df['Source'].nunique()
        #st.write("Number of Classes:", num_classes)

        # 2. Enrollment Ratio (Total dancers / Total classes) as a percentage
        enrollment_ratio = (total_dancers / num_classes) if num_classes > 0 else 0

        enrollment_df = filtered_df.groupby('x_axisLabel').agg({'Source': 'nunique'}).reset_index()
        enrollment_df.rename(columns={'Source': 'Number of Classes'}, inplace=True)
        enrollment_df = enrollment_df.merge(filtered_df[['x_axisLabel', 'Sort_Key']].drop_duplicates(), on='x_axisLabel')
        enrollment_df = enrollment_df.sort_values('Sort_Key')
        # Assuming enrollment_df and grouped_df are defined
        enrollment_df = enrollment_df.merge(
             grouped_df[['x_axisLabel', 'Number of Dancers']],  # Select only necessary columns
            on='x_axisLabel',
            how='left'
        )
        enrollment_df['Enrollment %'] = enrollment_df['Number of Dancers'] / enrollment_df['Number of Classes'].astype(int)

        #st.write(enrollment_df)


        # 3. Average Slots Attended (Total dancer slots / Total unique dancers)
        average_slots_attended = (total_dancers / total_unique_dancers) if total_unique_dancers > 0 else 0

        # 4. Display as metric cards using Markdown
        col1, col2 = st.columns(2)
        with col1:
            metric_card("Enrollment Ratio (Total Dancers / Total Classes)", f"{enrollment_ratio:.0f}")
        with col2:
            metric_card("Slots Attended (Total Dancers / Total Unique Dancers)", f"{average_slots_attended:.0f}")
        metric_card("Total Number of Classes", f"{num_classes}")

        # Plot Enrollment Ratio
        fig = plot_individual_metric(
            df=enrollment_df,
            x_axis_label='x_axisLabel',
            metric='Number of Classes',
            base_metric_df = None,
            base_metric = None,
            title='Number of Classes',
            as_percentage= False,
            trace_color='aqua'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Plot Enrollment Ratio
        fig = plot_individual_metric(
            df=enrollment_df,
            x_axis_label='x_axisLabel',
            metric='Enrollment %',
            base_metric_df = None,
            base_metric = None,
            title='Enrollment Ratio',
            as_percentage=False,
            trace_color='lightgreen'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Plot Dancer Enrollment
        fig = plot_individual_metric(
            df=grouped_df,
            x_axis_label='x_axisLabel',
            metric='Number of Dancers',
            base_metric_df = None,
            base_metric = None,
            title='Dancer Enrollment',
            as_percentage=False,
            trace_color='pink'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write("Total Dancers: ", total_dancers)

        # Plot Unique Dancers
        fig = plot_individual_metric(
            df=unique_dancers_df,
            x_axis_label='x_axisLabel',
            metric='Number of Unique Dancers',
            base_metric_df = None,
            base_metric = None,
            title='Unique Dancers',
            as_percentage=False,
            trace_color='purple'
        )
        #st.plotly_chart(fig, use_container_width=True)

        # Plot New Students
        fig = plot_individual_metric(
            df=new_students_df,
            x_axis_label='x_axisLabel',
            metric='New Student %',
            base_metric_df = None,
            base_metric = None,
            title='New Dancers',
            as_percentage=True,
            trace_color='orange'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write("Number of New Students: ", num_new_students)

        # Plot Retained Students
        fig = plot_individual_metric(
            df=retention_df,
            x_axis_label='x_axisLabel',
            metric='Retention %',
            base_metric_df = None,
            base_metric = None,
            title='Retention',
            as_percentage=True,
            trace_color='lightblue'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.write("Number of Retained Students: ", num_retained_students)


    else:
        st.warning("Please select filters on the main page first.")

main()
