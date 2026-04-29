import streamlit as st
import pyodbc

st.set_page_config(page_title="hospsys-bdo-sql", layout="wide")
st.title("SQL Server Connection Test")

server = st.secrets['azsqldb']['server']
database = st.secrets['azsqldb']['database']
username = st.secrets['azsqldb']['username']
password = st.secrets['azsqldb']['password']

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

if st.button("Test Connection"):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        st.success("Connected successfully!")
    except Exception as e:
        st.error(f"Connection failed: {e}")
