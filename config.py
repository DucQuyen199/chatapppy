import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    password = quote_plus(os.getenv('DB_PASSWORD', '@Ducquyenbg123'))
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://sa:{password}@localhost/chatapp?driver=ODBC+Driver+17+for+SQL+Server"
    SQLALCHEMY_TRACK_MODIFICATIONS = False 