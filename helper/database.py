import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect("journal_entries.db")
    try:
        yield conn
    finally:
        conn.close()

def init_tags():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT tag FROM journal_entries")
        return [tag[0] for tag in cursor.fetchall() if tag[0] is not None]