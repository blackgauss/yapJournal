import sqlite3

def export_journal_entries_to_txt(db_path, output_file):
    """
    Exports all content from the journal_entries.db database, concatenates it, 
    and saves it to a .txt file.

    :param db_path: Path to the journal_entries.db file.
    :param output_file: Path to the output .txt file.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query to fetch all content
        cursor.execute("SELECT content FROM journal_entries")
        rows = cursor.fetchall()

        # Concatenate all content
        all_content = "\n\n".join(row[0] for row in rows if row[0])

        # Save to the .txt file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(all_content)

        print(f"Exported all journal entries to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# Usage
if __name__ == "__main__":
    db_path = "journal_entries.db"  # Path to your database
    output_file = "journal_entries_export.txt"  # Desired output file
    export_journal_entries_to_txt(db_path, output_file)
