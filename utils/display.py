import streamlit as st
import plotly.graph_objects as go

def apply_display_toggle(df):

    options = ["All Time", "Intra Year", "Session (Consecutive)"]

    # Use session state value if it exists, else default to first option
    default_option = st.session_state.get("display_toggle", options[0])
    default_index = options.index(default_option) if default_option in options else 0
    
    display_toggle = st.radio(
        "Display",
        options=options,
        index=default_index,
        key="display_toggle"
    )

    # Access the persisted selection
    toggle_value = st.session_state["display_toggle"]

    if toggle_value == "All Time":
        df["x_axisLabel"] = df["School Year String"]
        df["Sort_Key"] = df["School Year"]
    else:
        df["x_axisLabel"] = df["Year_Season_Session"]
        df["Sort_Key"] = df["School Year"] * 100 + df["Season_Order"] * 10 + df["Session"]

    df = df.sort_values("Sort_Key")

    # Normalize Camp 3 to Summer 2
    df["Normalized_Label"] = df["x_axisLabel"].str.replace("Camp 3", "Summer 2")
    session_order = {
        label: i for i, label in enumerate(
            sorted(df["Normalized_Label"].unique(), key=lambda x: df[df["Normalized_Label"] == x]["Sort_Key"].min())
        )
    }
    df["Session_Index"] = df["Normalized_Label"].map(session_order)

    return df, toggle_value


def metric_card(title, value, suffix="", title_color="#A8B2FF", value_color="#000000", background_color="#f5f5f5"):
    """Display a styled metric card without a progress bar and customizable font colors."""
    st.markdown(f"""
        <div style="
            background-color: {background_color};
            padding: 1.2rem;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 1.1rem; color: {title_color};">{title}</div>
            <div style="font-size: 2rem; font-weight: bold; color: {value_color};">{value}{suffix}</div>
        </div>
    """, unsafe_allow_html=True)

def plot_individual_metric(df, x_axis_label='x_axisLabel', metric='Number of Dancers', 
                         base_metric_df=None, base_metric=None, title=None, 
                         as_percentage=False, trace_color='pink'):
    """
    Generate a Plotly bar chart for a single metric, optionally as a percentage of a base metric.
    
    Parameters:
    - df: DataFrame containing the data (e.g., grouped_df, unique_dancers_df)
    - x_axis_label: Column name for x-axis (default: 'x_axisLabel')
    - metric: Column name for the metric to plot (default: 'Number of Dancers')
    - base_metric_df: DataFrame containing the base metric for percentage calculation (optional)
    - base_metric: Column name of the base metric (e.g., 'Number of Dancers' from grouped_df)
    - title: Custom title for the chart (optional)
    - as_percentage: If True, convert metric to percentage of base_metric (default: False)
    - trace_color: Color for the trace (default: 'pink')
    """
    # Sort DataFrame by Sort_Key if available
    if 'Sort_Key' in df.columns:
        df = df.sort_values('Sort_Key')
    
    # Initialize y-values
    y_values = df[metric]
    y_axis_title = metric
    
    # If percentage is requested, calculate percentage relative to base_metric
    if as_percentage and base_metric_df is not None and base_metric is not None:
        # Merge df with base_metric_df on x_axis_label
        merged_df = df[[x_axis_label, metric, 'Sort_Key']].merge(
            base_metric_df[[x_axis_label, base_metric]], 
            on=x_axis_label, 
            how='left'
        )
        # Calculate percentage (handle division by zero)
        merged_df['Percentage'] = (merged_df[metric] / merged_df[base_metric].replace(0, 1)) * 100
        y_values = merged_df['Percentage']
        y_axis_title = f"{metric} (% of {base_metric})"
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add bar trace with custom styling
    fig.add_trace(
        go.Scatter(
            x=df[x_axis_label],
            y=y_values,
            mode='lines+markers',
            name=metric,
            marker=dict(size=10, symbol="circle", line=dict(width=1, color='darkslategray')),
            line=dict(width=3, color=trace_color)
        )
    )
    
    # Add annotations to each point
    for _, row in df.iterrows():
        fig.add_annotation(
            x=row[x_axis_label],
            y=row[metric], #if not as_percentage else (row[metric] / base_metric_df[base_metric_df[x_axis_label] == row[x_axis_label]][base_metric].iloc[0] * 100) if as_percentage else 0,
            #text=str(round(row[metric], 1)) if not as_percentage else f"{round((row[metric] / base_metric_df[base_metric_df[x_axis_label] == row[x_axis_label]][base_metric].iloc[0] * 100), 1)}%",
            text = f"{int(round(row[metric]))}%" if as_percentage else str(round(row[metric])),
            showarrow=False,
            xanchor='left',
            yanchor='middle',
            xshift=10,
            font=dict(color='black', weight='bold')
        )
    
    # Set title if not provided
    if title is None:
        title = f"{metric} Over Time" if not as_percentage else f"{metric} as % of {base_metric} Over Time"
    
    # Update layout with specified formatting
    fig.update_layout(
        xaxis_title="School Year (Sept - Aug)",
        yaxis_title=y_axis_title,
        xaxis_tickangle=-45,
        template='plotly_white',
        font=dict(size=14, color='black'),
        title_font=dict(size=24, color='black'),
        title_x=0.44,
        xaxis=dict(showgrid=True, zeroline=False, showline=True, linewidth=2, linecolor='lightgrey'),
        yaxis=dict(showgrid=True, zeroline=False, showline=True, linewidth=2, linecolor='lightgrey'),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        title = title
    )
    
    return fig
