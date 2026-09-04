import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Возвращает соединение с SQL Server (Windows Authentication + Encryption)."""
    server = os.getenv("DB_SERVER", r"CHARMANDER\SQLEXPRESS")
    database = os.getenv("DB_DATABASE", "ITIncidentAnalytics")

    # Trusted_Connection=yes соответствует "Проверка подлинности Windows"
    # Encrypt=yes и TrustServerCertificate=yes соответствуют галочкам безопасности из окна подключения
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )
    
    return pyodbc.connect(conn_str)