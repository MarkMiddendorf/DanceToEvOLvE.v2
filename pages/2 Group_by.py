import streamlit as st
import pandas as pd
import plotly.express as px
from utils.styling import apply_global_styles
from utils.state import init_session_state
from utils.display import metric_card
from utils.display import plot_individual_metric

def calculate_grouped_metrics(filtered_df, acquired_df, group_col):
    grouped_df = filtered_df.groupby([group_col, 'x_axisLabel', 'Sort_Key']).agg({
        'DancerID': 'count',
        'Source': 'nunique'
    }).reset_index().rename(columns={
        'DancerID': 'Number of Dancers',
        'Source': 'Number of Classes'
    })

    unique_dancers_df = filtered_df.groupby([group_col, 'x_axisLabel']).agg({'DancerID': 'nunique'}).reset_index()
    unique_dancers_df.rename(columns={'DancerID': 'Number of Unique Dancers'}, inplace=True)

    grouped_df = grouped_df.merge(unique_dancers_df, on=[group_col, 'x_axisLabel'], how='left')

    new_students_df = acquired_df.groupby([group_col, 'x_axisLabel']).agg({'DancerID': 'nunique'}).reset_index()
    new_students_df.rename(columns={'DancerID': 'Number of New Students'}, inplace=True)

    grouped_df = grouped_df.merge(new_students_df, on=[group_col, 'x_axisLabel'], how='left')
    grouped_df['Number of New Students'] = grouped_df['Number of New Students'].fillna(0)

    grouped_df['Enrollment %'] = grouped_df['Number of Dancers'] / grouped_df['Number of Classes']
    grouped_df['New Student %'] = grouped_df['Number of New Students'] / grouped_df['Number of Unique Dancers']
    grouped_df['Retained Students'] = grouped_df['Number of Unique Dancers'] - grouped_df['Number of New Students']
    grouped_df['Retention %'] = grouped_df['Retained Students'] / grouped_df['Number of Unique Dancers']

    return grouped_df

def plot_grouped_metric(df, group_col, x_axis_label, metric, title, as_percentage=False):
    df = df.sort_values("Sort_Key")
    fig = px.line(
        df,
        x=x_axis_label,
        y=metric,
        color=group_col,
        markers=True,
        title=title,
        labels={metric: title, x_axis_label: "Session"},
        category_orders={x_axis_label: sorted(df[x_axis_label].unique(), key=lambda x: df[df[x_axis_label] == x]["Sort_Key"].iloc[0])}
    )
    if as_percentage:
        fig.update_layout(yaxis_tickformat=".1%")
    fig.update_layout(legend_title_text=group_col)
        # Add rounded percentage labels to each point
    for group in df[group_col].unique():
        group_df = df[df[group_col] == group]
        for _, row in group_df.iterrows():
            fig.add_annotation(
                x=row[x_axis_label],
                y=row[metric],
                text=f"{int(round(row[metric]*100))}%" if as_percentage else str(int(round(row[metric]))),
                showarrow=False,
                font=dict(color='black'),
                xanchor='center',
                yanchor='bottom'
            )
    return fig


def main():
    apply_global_styles()
    init_session_state()
    st.write("Session State Snapshot:", st.session_state)

    display_toggle = st.session_state["display_toggle"]
    st.session_state['display_toggle'] = display_toggle

    st.title("🧺 Group By")
    display_toggleVar = st.radio("Display", options=["City", "Teacher", "Location", "Class", "Day","Time"], index=0)
    group_col = display_toggleVar

    if 'filtered_df' in st.session_state:
        filtered_df = st.session_state['filtered_df']
        filtered_pool = filtered_df.sort_values('Sort_Key')
        last_seen = {}
        newly_acquired = []

        for _, row in filtered_pool.iterrows():
            dancer_id = row['DancerID']
            session_index = row['Session_Index']
            school_year = row['School Year']

            if dancer_id not in last_seen or last_seen[dancer_id]['school_year'] != school_year:
                newly_acquired.append({
                    group_col: row[group_col],
                    'x_axisLabel': row['x_axisLabel'],
                    'Sort_Key': row['Sort_Key'],
                    'DancerID': dancer_id,
                    'School Year String': row['School Year String']
                })

            last_seen[dancer_id] = {
                'session_index': session_index,
                'school_year': school_year
            }

        acquired_df = pd.DataFrame(newly_acquired)
        grouped_df = calculate_grouped_metrics(filtered_df, acquired_df, group_col)

        total_dancers = grouped_df['Number of Dancers'].sum()
        total_unique_dancers = grouped_df['Number of Unique Dancers'].sum()

        #col1, col2 = st.columns(2)
        #with col1:
            #metric_card("Enrollment Ratio", f"{total_dancers / max(filtered_df['Source'].nunique(), 1):.2f}")
        #with col2:
            #metric_card("Slots Attended", f"{total_dancers / max(total_unique_dancers, 1):.2f}")
        #metric_card("Total Number of Classes", f"{filtered_df['Source'].nunique()}")

        for metric, title, as_percentage in [
            ("Number of Classes", 'Number of Classes', False),
            ("Enrollment %", 'Enrollment Ratio', False),
            ("Number of Dancers", 'Dancer Enrollment', False),
            ("Number of Unique Dancers", 'Unique Dancers', False),
            ("New Student %", 'New Dancers', True),
            ("Retention %", 'Retention', True)
        ]:
            fig = plot_grouped_metric(
                df=grouped_df,
                group_col=group_col,
                x_axis_label='x_axisLabel',
                metric=metric,
                title=title,
                as_percentage=as_percentage
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select filters on the main page first.")

main()
