# YouTube Transcript Extractor with Timestamps: A 6-Hour Blueprint

This project aims to create a Python program that extracts transcripts with timestamps from YouTube videos, suitable for processing by Large Language Models (LLMs).  The program will prioritize efficiency, scalability, and ethical data handling.  This blueprint outlines a 6-hour sprint focused on core functionality.  Failure to complete all steps within this timeframe is acceptable; focus on building a robust foundation.  " *The way you learn how to make something is you build it and you use it* " (01-07-2025 13:37:22).

**Project Goal:**  Create a Python script that takes YouTube video links as input, extracts audio, transcribes it using Whisper, generates a timestamped transcript, and stores the data in an SQLite3 database.  This data, including metadata for ethical citation, should be easily searchable and accessible to LLMs.  " *I want to be able to speak to my phone, hit that, and then boom, it gives me a to-do list.* " (01-07-2025 09:13:57) -  This project is a crucial step towards that larger goal.

**Sprint Goals (6-hour timeframe):**

1. **YouTube Data Acquisition and Audio Extraction (1 hour):**
    * **Goal:**  Write a function to fetch YouTube video metadata (title, channel info, etc.) and extract the audio stream without downloading the full video.
    * **Plan:** Use the `pytube` library to interact with the YouTube API.  This avoids rate limits associated with direct download.  Extract only the audio stream using the appropriate methods provided by `pytube`.  " *There's so many apps out there... But my issue is I don't want to spend time learning someone's app... if that person can't make their app better anymore... I'm left in the dark.* " (01-07-2025 13:33:39) -  Building your own avoids this dependency.
    * **Code Example:**
    ```python
    from pytube import YouTube

    def get_youtube_audio(youtube_url):
        try:
            yt = YouTube(youtube_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(filename='temp_audio.mp3') #Download to temporary file
            return yt.title, yt.author, 'temp_audio.mp3' # Return metadata and path to temporary file
        except Exception as e:
            print(f"Error processing YouTube URL: {e}")
            return None, None, None
    ```
2. **Audio Transcription with Whisper (2 hours):**
    * **Goal:**  Transcribe the audio using the `whisper` library, generating a transcript with timestamps.
    * **Plan:** Use the `whisper` library's `transcribe` function.  Experiment with different model sizes to balance speed and accuracy.  Whisper's output contains timestamps.  " *I want to do something where I'm going to build a little device that it gets stored on that little device... I've just glued a bunch of things that exist in a way that it's mine.* " (01-07-2025 13:37:22) - This is gluing together existing libraries.
    * **Code Example:**
    ```python
    import whisper

    def transcribe_audio(audio_path):
        model = whisper.load_model("base") # Choose model size (base, small, medium, large)
        result = model.transcribe(audio_path)
        return result["segments"]  # List of dictionaries, each with "start", "end", and "text"
    ```
3. **Data Storage and Database Setup (1 hour):**
    * **Goal:**  Create an SQLite3 database to store transcripts and metadata efficiently.
    * **Plan:** Use the `sqlite3` library. Design a database schema to store: video ID (from YouTube URL), video title, channel name, transcript segments (start, end, text), and other relevant metadata.  " *How can I search through all of the entries for different keywords? ... Can I do recommendation systems on my own journal entries?* " (01-07-2025 10:25:12) -  This database will enable these features.
    * **Code Example:**
    ```python
    import sqlite3

    def create_db_and_table():
        conn = sqlite3.connect('youtube_transcripts.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcripts (
                video_id TEXT PRIMARY KEY,
                video_title TEXT,
                channel_name TEXT,
                segment_start REAL,
                segment_end REAL,
                segment_text TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def insert_transcript(video_id, video_title, channel_name, segments):
        conn = sqlite3.connect('youtube_transcripts.db')
        cursor = conn.cursor()
        for segment in segments:
            cursor.execute('''
                INSERT INTO transcripts (video_id, video_title, channel_name, segment_start, segment_end, segment_text)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (video_id, video_title, channel_name, segment["start"], segment["end"], segment["text"]))
        conn.commit()
        conn.close()

    ```

4. **Initial Script Integration and Testing (1 hour):**
    * **Goal:** Combine functions and test on a sample YouTube video.  Ensure proper audio extraction, transcription, and database insertion.
    * **Plan:** Create a main function that takes YouTube URLs as input, calls the functions from steps 1–3, and handles errors gracefully. Test the script with a short YouTube video (e.g., a brief course preview).  " *I've gotten to the point where this thing, the problem it's supposed to solve is so specific to me that I need to make it from scratch because I want every little letter that's in the thing to be the way I want it.* " (01-07-2025 13:33:39) - Test rigorously to ensure it meets your needs.
    * **Code Example (Main Function):**
    ```python
    import os
    import re
    from pytube import YouTube

    # ... (get_youtube_audio and transcribe_audio functions from previous steps) ...
    # ... (create_db_and_table and insert_transcript functions from previous steps) ...

    def main():
        create_db_and_table()
        video_urls = ["YOUR_YOUTUBE_URLS_HERE"] # Replace with your video URLs

        for url in video_urls:
            video_id = re.findall(r"v=(.+)", url)[0] # Extract video ID from the URL
            title, author, audio_path = get_youtube_audio(url)
            if (title and author and audio_path):
                segments = transcribe_audio(audio_path)
                insert_transcript(video_id, title, author, segments)
                os.remove(audio_path) # Delete temporary file


    if __name__ == "__main__":
        main()

    ```

5.  **Further Considerations:**
    * **Error Handling:** Implement robust error handling (e.g., using `try-except` blocks) to handle network issues, YouTube API errors, and transcription failures.
    * **Progress Monitoring:** Add progress indicators or logging to track the script's execution.
    * **Video Filtering:** Incorporate a video analysis step (using libraries like `moviepy`) to assess if a video contains primarily spoken content before proceeding with transcription. This will help avoid unnecessary processing of videos with little spoken content.
    * **LLM Integration:** Develop a function to query the database and provide formatted data to LLMs. Consider using a library like `openai` to interface with specific language models. 

**Technology Choices:**

* **`pytube`:**  For efficient and ethical YouTube data access and audio extraction. It avoids downloading the full video which would consume excessive storage.
* **`whisper`:** Open-source speech-to-text model, offering a balance between accuracy and speed. It natively provides timestamps.
* **`sqlite3`:**  Lightweight, embedded database solution for efficient transcript storage and retrieval within the Python environment.  This is suitable for the initial sprint goal and easily scalable.
* **`re` (regular expressions):**  For extracting video IDs from YouTube URLs reliably.
* **`os`:** For file management operations (deleting temporary files).


**Data Structure (SQLite3):**

The SQLite3 database stores transcripts in a structured format.  Each row represents a segment of the transcript. The `segment_start` and `segment_end` columns store the start and end timestamps (in seconds) of the segment, enabling precise referencing.


**Scalability and Integration:**

This design is scalable. The SQLite database can handle a large number of transcripts.  The modular design allows for easy integration with other projects.  LLMs can query the database using the `video_id` and access timestamped segments via SQL queries.

**Next Steps (Beyond 6-hour sprint):**

* **Improved Error Handling:** More sophisticated error handling, including retry mechanisms for transient network problems.
* **Video Filtering:** Integrate video analysis for content assessment before transcription.
* **Advanced Search:** Implement advanced search functionalities within the database (using full-text search).
* **LLM Interface:** Create a streamlined interface to deliver formatted data to LLMs.
* **Deployment:** Consider deploying the application to a server for broader accessibility.


This blueprint provides a structured approach. Remember to break down tasks into smaller, manageable steps, iterate, and test frequently. Your success hinges on consistent action, even in small increments. " *I'm in it for the long run.* " (01-09-2025 08:58:16).
