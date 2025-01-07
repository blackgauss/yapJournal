from flask import Flask, render_template, request, jsonify
import os
from helper.transcribe import transcribe_audio
import json
from datetime import datetime
import markdown

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
    note_name = request.form.get("note_name", "").strip()  # Get the note name from the form
    tag = request.form.get("tag", "miscellaneous").strip()  # Get the tag from the form (default: miscellaneous)

    if not audio_file:
        return jsonify({"message": "Audio file is missing!"}), 400

    # Generate a dynamic title based on the tag
    timestamp = datetime.now().strftime("%m-%d-%H%M")
    title = f"{tag.capitalize()}: {note_name}" if note_name else f"{tag.capitalize()} {timestamp}"

    # Clean the title to make it filesystem-safe
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else "_" for c in title).strip()
    file_path = os.path.join(AUDIO_DIR, f"{safe_title}.wav")

    # Save the audio file
    audio_file.save(file_path)

    # Return the file path and metadata
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
    tag = data.get("tag", "miscellaneous")  # Default to miscellaneous if no tag is provided

    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "Invalid file path!"}), 400

    try:
        # Perform transcription
        transcription_text = transcribe_audio(file_path)
        if not transcription_text:
            return jsonify({"message": "Transcription failed!"}), 500

        # Delete the audio file after transcription
        os.remove(file_path)

        # Save the transcription to a JSON file
        note_name = os.path.splitext(os.path.basename(file_path))[0]  # Extract note name from file path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
        json_data = {
            "note_name": note_name,
            "transcription": transcription_text,
            "date_created": timestamp,
            "tag": tag  # Include the tag in the transcription metadata
        }

        # Save JSON to /transcriptions folder
        json_file_path = os.path.join(TRANSCRIPTIONS_DIR, f"{note_name}.json")
        with open(json_file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        return jsonify({
            "message": "Transcription successful!",
            "transcription": transcription_text,
            "json_file": json_file_path
        })
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"message": "An error occurred during transcription!"}), 500

@app.route("/entries", methods=["GET"])
def entries():
    try:
        # List all JSON files in the /transcriptions folder
        entries = []
        for filename in os.listdir(TRANSCRIPTIONS_DIR):
            if filename.endswith(".json"):
                file_path = os.path.join(TRANSCRIPTIONS_DIR, filename)
                
                # Read and parse the JSON file
                with open(file_path, "r") as json_file:
                    data = json.load(json_file)
                    entries.append({
                        "note_name": data.get("note_name", "Unknown"),
                        "date_created": data.get("date_created", "Unknown"),
                        "transcription": data.get("transcription", "No transcription available"),
                        "tag": data.get("tag", "miscellaneous")  # Include the tag for display
                    })

        # Render the entries page with the entries list
        return render_template("entries.html", entries=entries)
    except Exception as e:
        print(f"Error loading entries: {e}")
        return jsonify({"message": "An error occurred while loading entries!"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=("ssl-certificates/cert.pem", "ssl-certificates/key.pem"), debug=True)