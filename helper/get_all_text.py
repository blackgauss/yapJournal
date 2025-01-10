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

def export_recent_journal_entries_to_txt(db_path, output_file, percentage=20):
    """
    Exports the most recent entries from the journal_entries.db database,
    concatenates them, and saves to a .txt file.

    :param db_path: Path to the journal_entries.db file.
    :param output_file: Path to the output .txt file.
    :param percentage: Percentage of most recent entries to export (default 20%)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get total count of entries
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total_entries = cursor.fetchone()[0]
        
        # Calculate number of entries to fetch
        entries_to_fetch = int(total_entries * (percentage / 100))
        
        # Query to fetch most recent entries
        cursor.execute("SELECT content FROM journal_entries ORDER BY id DESC LIMIT ?", 
                        (entries_to_fetch,))
        rows = cursor.fetchall()

        # Concatenate content in chronological order
        all_content = "\n\n".join(row[0] for row in reversed(rows) if row[0])

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(all_content)

        print(f"Exported last {percentage}% of journal entries to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
# Usage
if __name__ == "__main__":
    db_path = "journal_entries.db"  # Path to your database
    output_file = "journal_entries_recent.txt"  # Desired output file
    # export_journal_entries_to_txt(db_path, output_file)
    export_recent_journal_entries_to_txt(db_path, output_file, percentage=100)
