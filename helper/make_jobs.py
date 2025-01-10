import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

# Create the jobs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    description TEXT,
    relation_to_user TEXT,
    actionable_details TEXT,
    expected_outcome TEXT,
    timeline TEXT,
    liked BOOLEAN DEFAULT NULL, -- Stores user feedback: NULL = no feedback, 1 = like, 0 = dislike
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("jobs.db and jobs table created successfully!")