import os
import pyodbc

def setup_dbs():
    try:
        global conns 
        global conns_cursor
        
        print("Initializing Epic Warehouse DB")
        server = os.getenv('DB_HOSTNAME')
        database = os.getenv('DB_NAME')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')

        if not all([server, database, username, password]):
            raise ValueError("One or more required environment variables are missing!")

        # Create connection and cursor
        conns = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        conns_cursor = conns.cursor()

        print("Connection to Epic Warehouse DB successful!")
        return conns, conns_cursor

    except Exception as e:
        print(f"Error encountered during DB setup: {e}")
        return None, None

def close_db_connections():
    print("Closing DB connections")
    try:
        if conns:
            conns.close()
            print("Connection closed successfully.")
        else:
            print("No connection to close.")
    except Exception as e:
        print(f"Error occurred while closing DB connection: {e}")

if __name__ == "__main__":
    setup_dbs()
    close_db_connections()
