import pandas as pd
import db

def load_from_csv(file_path):
    return pd.read_csv(file_path)

def load_from_excel(file_path):
    return pd.read_excel(file_path)

def load_from_sql(query="SELECT * FROM [bcra].[dbo].exampledata;"):
    db.setup_dbs()
    df = pd.read_sql(query, db.conns)
    db.close_db_connections()
    return df

