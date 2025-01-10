import sqlite3
import json

# Load data from actionable_steps.json
with open("actionable_steps.json", "r") as file:
    data = json.load(file)["steps"]

# Connect to the SQLite database
conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

# Insert entries into the jobs table
for job in data:
    cursor.execute('''
        INSERT INTO jobs (category, description, relation_to_user, actionable_details, expected_outcome, timeline)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (job["category"], job["description"], job["relation_to_user"], job["actionable_details"], job["expected_outcome"], job["timeline"]))

conn.commit()
conn.close()

print("Jobs migrated to jobs.db successfully!")
