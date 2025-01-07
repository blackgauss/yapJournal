import os
import json
import sqlite3
from datetime import datetime

# Folder containing JSON files
JSON_FOLDER = "./transcriptions"
DB_FILE = "journal_entries.db"

# Connect to the SQLite database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Function to migrate JSON files into the database
def migrate_json_to_db():
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(JSON_FOLDER, filename)
            with open(file_path, "r") as f:
                data = json.load(f)

                # Extract fields from JSON
                title = data.get("note_name", "Untitled")
                content = data.get("transcription", "")
                tag = data.get("tag", "miscellaneous")
                created_at = data.get("date_created", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                updated_at = created_at

                # Insert into the database
                cursor.execute('''
                INSERT INTO journal_entries (title, content, tag, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ''', (title, content, tag, created_at, updated_at))
    
    # Commit the changes
    conn.commit()
    print("Migration complete!")

# Run the migration
migrate_json_to_db()

# Close the connection
conn.close()
