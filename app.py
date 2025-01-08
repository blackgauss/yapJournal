from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
import markdown
import sqlite3
from helper.transcribe import transcribe_audio
from helper.keywords import extract_keywords_and_summary


app = Flask(__name__)

# Ensure the /audio directory exists
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

TRANSCRIPTIONS_DIR = "transcriptions"
# Ensure the /transcriptions directory exists
if not os.path.exists(TRANSCRIPTIONS_DIR):
    os.makedirs(TRANSCRIPTIONS_DIR)

@app.route("/")
def home():
    # Read the Markdown file with UTF-8 encoding
    with open("description.md", "r", encoding="utf-8") as md_file:
        md_content = md_file.read()
    
    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content)

    # Pass the HTML content to the template
    return render_template("home.html", description=html_content)

@app.route("/record")
def record():
    return render_template("record.html")

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    audio_file = request.files.get("audio")
    note_name = request.form.get("note_name", "").strip()
    tag = request.form.get("tag")
    if not tag:  # Apply default only if tag is None or empty
        tag = "miscellaneous"
    tag = tag.strip()
    timestamp = datetime.now()

    if not audio_file:
        return jsonify({"message": "Audio file is missing!"}), 400

    # Generate a dynamic title based on the tag
    title = f"{tag.capitalize()}: {note_name}" if note_name else f"{tag.capitalize()} {timestamp.strftime('%m-%d-%H%M')}"

    # Save the audio file locally
    safe_note_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else "_" for c in title).strip()
    file_path = os.path.join(AUDIO_DIR, f"{safe_note_name}.wav")
    audio_file.save(file_path)

    # Save metadata to the database
    conn = sqlite3.connect("journal_entries.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO journal_entries (title, content, tag, additional_info, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, "", tag, f"Audio saved at {file_path}", timestamp, timestamp))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Audio file uploaded successfully!",
        "file_path": file_path,
        "title": title,
        "tag": tag
    })



@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    file_path = data.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "Invalid file path!"}), 400

    try:
        # Perform transcription
        transcription_text = transcribe_audio(file_path)
        if not transcription_text:
            return jsonify({"message": "Transcription failed!"}), 500

        # Delete the audio file after transcription
        os.remove(file_path)

        # Update the corresponding database entry
        title = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now()
        conn = sqlite3.connect("journal_entries.db")
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE journal_entries
            SET content = ?, updated_at = ?
            WHERE title = ?
        ''', (transcription_text, timestamp, title))
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Transcription successful!",
            "transcription": transcription_text
        })
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"message": "An error occurred during transcription!"}), 500


@app.route("/entries", methods=["GET"])
def entries():
    try:
        # Get query parameters for filtering and searching
        tag_filter = request.args.get("tag", "").strip()
        search_query = request.args.get("search", "").strip()

        # Connect to the database
        conn = sqlite3.connect("journal_entries.db")
        cursor = conn.cursor()

        # Base query
        sql_query = "SELECT title, content, tag, additional_info, created_at FROM journal_entries"
        conditions = []
        params = []

        # Apply tag filter
        if tag_filter:
            conditions.append("tag = ?")
            params.append(tag_filter)

        # Apply search filter (search in title and content)
        if search_query:
            conditions.append("(title LIKE ? OR content LIKE ?)")
            params.append(f"%{search_query}%")
            params.append(f"%{search_query}%")

        # Add conditions to the query
        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)

        # Order by creation date
        sql_query += " ORDER BY created_at DESC"

        # Execute the query
        cursor.execute(sql_query, params)
        entries = [
            {
                "note_name": row[0],
                "transcription": row[1],
                "tag": row[2],
                "additional_info": row[3],
                "date_created": row[4]
            }
            for row in cursor.fetchall()
        ]
        conn.close()

        # Render the entries page with the filtered entries
        return render_template("entries.html", entries=entries, tag_filter=tag_filter, search_query=search_query)

    except Exception as e:
        print(f"Error loading entries: {e}")
        return jsonify({"message": "An error occurred while loading entries!"}), 500


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    note_name = data.get('note_name')

    if not note_name:
        return jsonify({'error': 'Note name is required'}), 400

    try:
        # Fetch transcription text from the database
        conn = sqlite3.connect("journal_entries.db")
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM journal_entries WHERE title = ?", (note_name,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return jsonify({'error': 'Note not found'}), 404

        text = result[0]
        if not text:
            return jsonify({'error': 'No transcription available for this note'}), 400

        # Extract keywords and summary
        result = extract_keywords_and_summary(text)
        return jsonify(result)

    except Exception as e:
        print(f"Error summarizing note: {e}")
        return jsonify({'error': 'An error occurred while summarizing'}), 500

@app.route('/topics', methods=['POST'])
def topics():
    data = request.get_json()
    note_name = data.get('note_name')

    if not note_name:
        return jsonify({'error': 'Note name is required'}), 400

    try:
        print(f"Fetching content for note: {note_name}")  # Debug log
        # Fetch transcription text from the database
        conn = sqlite3.connect("journal_entries.db")
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM journal_entries WHERE title = ?", (note_name,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return jsonify({'error': 'Note not found'}), 404

        text = result[0]
        if not text:
            return jsonify({'error': 'No transcription available for this note'}), 400

    except Exception as e:
        print(f"Error extracting topics: {e}")
        return jsonify({'error': 'An error occurred while extracting topics'}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=("ssl-certificates/cert.pem", "ssl-certificates/key.pem"), debug=True)