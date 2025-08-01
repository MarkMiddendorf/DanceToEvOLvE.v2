import streamlit as st
import os
import re
from datetime import datetime
import pandas as pd
from utils.styling import apply_global_styles
from utils.state import init_session_state
import openpyxl

def main():
    apply_global_styles()
    init_session_state()
    #st.write("Session State Snapshot:", st.session_state)
    display_toggle = st.session_state["display_toggle"]
    st.session_state['display_toggle'] = display_toggle

    st.title("🧹 Format Data")
    def extract_info_from_filename(filename):
        file_name = os.path.basename(filename)
        parts = os.path.splitext(file_name)[0].split('_')
        
        # Ensure the parts list has at least 7 elements, filling missing values with "N/A"
        while len(parts) < 9:
            parts.append("N/A")
        
        return {
            "Location": parts[0],
            "Reg/NonReg": parts[1],
            "Season": parts[2],
            "Session": parts[3],
            "Year": parts[4],
            "Class": parts[5],
            "Teacher": parts[6],
            "Day": parts[7],  # This will be "N/A" if missing
            "Time": parts[8], # This will be "N/A" if missing
            "Source": file_name
        }

    def clean_last_name(last_name):
        return re.sub(r"\s?\(.*\)", "", last_name)

    def process_files(file_buffers):
        consolidated_data = []
        for file_buffer in file_buffers:
            try:
                info = extract_info_from_filename(file_buffer.name)

                session = int(info["Session"]) if info["Session"].isdigit() else None
                year = int(info["Year"]) if info["Year"].isdigit() else None

                df = pd.read_excel(file_buffer)
                
                for index, row in df.iterrows():
                    cleaned_last_name = clean_last_name(row['Last Name'])
                    
                    # Attempt to convert birth_date, with error handling
                    try:
                        birth_date = datetime.strptime(row['Birth Date'], '%b %d, %Y')
                    except (ValueError, TypeError) as e:
                        # If the date is invalid or None, set to default value (Jan 1, 2000)
                        birth_date = datetime(2000, 1, 1)
                        print(f"Error parsing date for {row['Last Name']} at index {index}: {e}")
                    
                    formatted_birth_date = birth_date.strftime('%b %d, %Y')
                    
                    consolidated_data.append({
                        "DancerID": f"{row['First Name']}_{cleaned_last_name}_{formatted_birth_date}",
                        "FirstName": row['First Name'],
                        "LastName": cleaned_last_name,
                        "Phone": row['Phone'],
                        "Email": row['Email'],
                        "Address": row['Address'],
                        "BirthDate": formatted_birth_date,
                        "Age": None,  # Set to "leave blank" (None in pandas)
                        "City": None,
                        "Location": info["Location"],
                        "Reg/NonReg": info["Reg/NonReg"],
                        "Season": info["Season"],
                        "Session": session,
                        "Year": year,
                        "Class": info["Class"],
                        "Teacher": info["Teacher"],
                        "Day": info["Day"],
                        "Time": info["Time"],
                        "Source": info["Source"]
                    })
            except Exception as e:
                st.error(f"Error processing file {file_buffer.name}: {e}")

        return pd.DataFrame(consolidated_data)

    def save_to_excel(dataframe):
        output_path = f"Consolidated_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        dataframe.to_excel(output_path, index=False)
        return output_path

    def format_data_tab():
        st.title("Data Format Application")
        st.write("Upload your Excel files to process and format the data.")

        uploaded_files = st.file_uploader("Upload Excel Files", type=['xls', 'xlsx', 'xlsm'], accept_multiple_files=True)

        if st.button("Process Files"):
            if uploaded_files:
                consolidated_df = process_files(uploaded_files)
                if not consolidated_df.empty:
                    st.success("Files processed successfully!")
                    st.write(consolidated_df)

                    output_file = save_to_excel(consolidated_df)
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="Download Consolidated Data",
                            data=file,
                            file_name=output_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No data was consolidated. Please check your files.")
            else:
                st.warning("Please upload at least one file.")

    # Main entry point
    if __name__ == "__main__":
        format_data_tab()
main()