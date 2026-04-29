import pyodbc

# Look up server, db and password from the Georelicate SQL Doc

server = "****.database.windows.net"
database = "****"
username = "***"
password = "*************" 

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    row = cursor.fetchone()
    print("Connection successful! Query result:", row[0])
except Exception as e:
    print("Connection failed:", e)
