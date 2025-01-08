import sqlite3

def recreate_table_with_new_schema():
    """
    Recreates the journal_entries table with new fields: summary, keywords, and topics.
    Copies existing data to the new table.
    """
    conn = sqlite3.connect("journal_entries.db")
    cursor = conn.cursor()

    # Step 1: Rename the old table
    cursor.execute("ALTER TABLE journal_entries RENAME TO journal_entries_old")

    # Step 2: Create a new table with the updated schema
    cursor.execute("""
        CREATE TABLE journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            tag TEXT,
            additional_info TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            summary TEXT,
            keywords TEXT,
            topics TEXT
        )
    """)

    # Step 3: Copy data from the old table to the new table
    cursor.execute("""
        INSERT INTO journal_entries (id, title, content, tag, additional_info, created_at, updated_at)
        SELECT id, title, content, tag, additional_info, created_at, updated_at
        FROM journal_entries_old
    """)

    # Step 4: Drop the old table
    cursor.execute("DROP TABLE journal_entries_old")

    conn.commit()
    conn.close()
    print("Table recreated with new schema successfully!")

if __name__ == "__main__":
    try:
        recreate_table_with_new_schema()
    except Exception as e:
        print(f"Error recreating table: {e}")
