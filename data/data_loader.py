import os
import streamlit as st
import toml
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


def load_credentials():
    """
    Load credentials from Streamlit secrets or local TOML file.
    Streamlit's secrets file and local file must match in structure.
    """
    if hasattr(st, "secrets") and "google_credentials" in st.secrets:
        google = st.secrets["google_credentials"]
        return {
            "type": google["type"],
            "project_id": google["project_id"],
            "private_key_id": google["private_key_id"],
            "private_key": google["private_key"].replace("\\n", "\n"),
            "client_email": google["client_email"],
            "client_id": google["client_id"],
            "auth_uri": google["auth_uri"],
            "token_uri": google["token_uri"],
            "auth_provider_x509_cert_url": google["auth_provider_x509_cert_url"],
            "client_x509_cert_url": google["client_x509_cert_url"]
        }
    else:
        # Local development: load from secrets.toml
        toml_path = os.getenv("LOCAL_TOML_PATH", "secrets.toml")
        with open(toml_path, "r") as f:
            toml_data = toml.load(f)
            gcreds = toml_data.get("google_credentials", {})

        return {
            "type": gcreds["type"],
            "project_id": gcreds["project_id"],
            "private_key_id": gcreds["private_key_id"],
            "private_key": gcreds["private_key"].replace("\\n", "\n"),
            "client_email": gcreds["client_email"],
            "client_id": gcreds["client_id"],
            "auth_uri": gcreds["auth_uri"],
            "token_uri": gcreds["token_uri"],
            "auth_provider_x509_cert_url": gcreds["auth_provider_x509_cert_url"],
            "client_x509_cert_url": gcreds["client_x509_cert_url"]
        }


def load_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = load_credentials()
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    # Load worksheet
    sheet = client.open("DanceToEvolve_Data").worksheet("Data")
    records = sheet.get_all_records()
    return pd.DataFrame(records)


