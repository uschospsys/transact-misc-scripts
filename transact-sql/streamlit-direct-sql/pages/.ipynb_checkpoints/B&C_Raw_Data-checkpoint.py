import streamlit as st
import pyodbc
import pandas as pd
import datetime

# sql-db Connection Parameters
SERVER = st.secrets['azsqldb']['server']
DATABASE = st.secrets['azsqldb']['database']
USERNAME = st.secrets['azsqldb']['username']
PASSWORD = st.secrets['azsqldb']['password']

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

# Helper to load sql queries from .sql files
def load_sql_file(path):
    with open(path, "r") as file:
        return file.read()


st.title("USC Banquets and Catering - Raw Data")

# Query Choices
query_options = {
    "B&C Raw Data - Date Range": "queries/banquets_and_catering_raw_data.sql",
    "B&C Raw Data - Yesterday": "queries/banquets_and_catering_yesterday.sql"
}

selection = st.selectbox("Choose query type:", list(query_options.keys()))

# Dynamically show parameters based on selection
params = {}

# Parameter Selection
if selection == "B&C Raw Data - Date Range":
    st.subheader("Parameters")
    params["start_date"] = st.date_input("Start Date", datetime.date.today())
    params["end_date"] = st.date_input("End Date", datetime.date.today())


# Run Query with parameters
if st.button("Run Query"):
    try:
        sql_template = load_sql_file(query_options[selection])
        sql = sql_template.format(**params)

        conn = pyodbc.connect(CONN_STR)
        df = pd.read_sql(sql, conn)

        st.success("Query executed successfully!")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Error running query: {e}")
        st.code(sql)


# --- ADVANCED OPTIONS ---
with st.expander("Advanced Options: Run Custom SQL"):
    custom_sql = st.text_area("Enter your SQL query here:", height=250)

    if st.button("Execute Custom SQL"):
        try:
            conn = pyodbc.connect(CONN_STR)
            df = pd.read_sql(custom_sql, conn)
            st.success("Custom SQL executed successfully!")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Query failed: {e}")
