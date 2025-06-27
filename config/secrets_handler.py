import streamlit as st
import os
import toml
import json


def get_google_credentials():
    """
    Return Google credentials from Streamlit secrets (TOML) or a local TOML fallback.
    """
    if hasattr(st, "secrets") and "type" in st.secrets:
        return {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
    else:
        # For local dev: load from a TOML file like secrets.toml
        toml_path = os.getenv("LOCAL_TOML_PATH", "secrets.toml")
        with open(toml_path, "r") as f:
            secrets = toml.load(f)
            google = secrets.get("google_credentials", {})

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
