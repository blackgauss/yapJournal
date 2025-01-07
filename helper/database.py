import sqlite3

# Database file path
DB_FILE = "journal_entries.db"

# Connect to SQLite database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create the table with FTS5 for full-text search
cursor.execute('''
CREATE VIRTUAL TABLE IF NOT EXISTS journal_entries
USING fts5(
    id UNINDEXED,
    title,
    content,
    tag,
    additional_info,
    created_at UNINDEXED,
    updated_at UNINDEXED
)
''')

conn.commit()
conn.close()

print("Database and table created successfully!")
