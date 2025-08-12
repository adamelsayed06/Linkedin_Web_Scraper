import psycopg2
import spacy
from dotenv import load_dotenv
import os

load_dotenv()

# Replace with host/db/user/password with postgres information
conn_string = "host='localhost' dbname='my_database' user='postgres' password='secret'"

nlp = spacy.load("en_core_web_sm")

def connect():
    try:
        conn = psycopg2.connect(conn_string)
        print("Connected to the database successfully")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_profiles(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, profile_text FROM profiles")
        profiles = cursor.fetchall()
        return profiles
    except Exception as e:
        print(f"Error fetching profiles: {e}")
        return []