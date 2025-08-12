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
    
def process_profiles(profiles):
    processed_data = []
    for profile in profiles:
        profile_id, profile_text = profile
        doc = nlp(profile_text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        processed_data.append((profile_id, entities))
    return processed_data

def save_processed_data(conn, processed_data):
    try:
        cursor = conn.cursor()
        for profile_id, entities in processed_data:
            for entity_text, entity_label in entities:
                cursor.execute(
                    "INSERT INTO profile_entities (profile_id, entity_text, entity_label) VALUES (%s, %s, %s)",
                    (profile_id, entity_text, entity_label)
                )
        conn.commit()
        print("Processed data saved successfully")
    except Exception as e:
        print(f"Error saving processed data: {e}")
        conn.rollback()

def main():
    conn = connect()
    
    if not conn:
        return
    
    
    profiles = fetch_profiles(conn)
    if not profiles:
        print("No profiles found to process.")
        conn.close()
        return
    
    processed_data = process_profiles(profiles)
    
    save_processed_data(conn, processed_data)
    print("Done")
    conn.close()

