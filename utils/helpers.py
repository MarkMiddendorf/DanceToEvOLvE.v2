import pandas as pd
import streamlit as st
from datetime import datetime

def compute_school_year(df):
    df = df.copy()
    school_year_order = [
        ('Fall', 1), ('Fall', 2), ('Winter', 1), ('Winter', 2),
        ('Spring', 1), ('Spring', 2), ('Summer', 1), ('Summer', 2), ('Camp', 3)
    ]
    school_year_mapping = {}
    school_year_string_mapping = {}

    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    years = sorted(df['Year'].dropna().astype(int).unique())

    for year_start in years:
        start_periods = [
            (year_start, 'Fall', 1), (year_start, 'Fall', 2),
            (year_start + 1, 'Winter', 1), (year_start + 1, 'Winter', 2),
            (year_start + 1, 'Spring', 1), (year_start + 1, 'Spring', 2),
            (year_start + 1, 'Summer', 1), (year_start + 1, 'Summer', 2),
            (year_start + 1, 'Camp', 3),
        ]
        school_year_str = f"{year_start}-{year_start - 1999}"
        for period in start_periods:
            school_year_mapping[period] = year_start
            school_year_string_mapping[period] = school_year_str

        # Override for Summer 2022 → School Year 2021
        override_periods = [
            ('Summer', 1), ('Summer', 2)
        ]
        for season, session in override_periods:
            school_year_mapping[(2022, season, session)] = 2021
            school_year_string_mapping[(2022, season, session)] = f"2021-{2021 - 1999}"

    df['School Year'] = df.apply(lambda row: school_year_mapping.get((row['Year'], row['Season'], row['Session'])), axis=1)
    df['School Year String'] = df.apply(lambda row: school_year_string_mapping.get((row['Year'], row['Season'], row['Session'])), axis=1)
    return df

# Cached school year logic
@st.cache_data
def school_year(df):
    return compute_school_year(df)

@st.cache_data
def calculate_age(df):
    # Define season/session start dates
    season_session_starts = {
        ('Fall', 1): (9, 1),    # September 1
        ('Fall', 2): (11, 1),   # November 1
        ('Winter', 1): (1, 1),  # January 1
        ('Winter', 2): (2, 1),  # February 1
        ('Spring', 1): (4, 1),  # April 1
        ('Spring', 2): (5, 1),  # May 1
        ('Summer', 1): (6, 1),  # June 1
        ('Summer', 2): (7, 1)   # July 1
    }

    def compute_age(row):
        try:
            # Parse BirthDate (e.g., "Jan 01, 2000")
            birth_date = datetime.strptime(row['BirthDate'], '%m/%d/%Y')
            year = row['Year']
            season = row['Season']
            session = row['Session']
            
            # Get month and day for the season/session
            if pd.isna(year) or pd.isna(season) or pd.isna(session):
                return None
            month, day = season_session_starts.get((season, int(session)), (1, 1))  # Default to Jan 1 if invalid
            
            # Create event date (start of season/session in Year)
            event_date = datetime(int(year), month, day)
            
            # Calculate age in years as a float
            age = (event_date - birth_date).days / 365.25  # Approximate years, accounting for leap years

            # Round to nearest 0.5
            age_rounded = round(age * 2) / 2
            
            return age_rounded if age_rounded >= 0 else None
        except (ValueError, TypeError, KeyError):
            return None

    # Create or overwrite Age column
    df['Age'] = df.apply(compute_age, axis=1)
    return df

