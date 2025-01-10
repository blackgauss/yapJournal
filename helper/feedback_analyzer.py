import sqlite3
from openai import OpenAI
import os
from pydantic import BaseModel

# Load environment variables for OpenAI API
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

class FeedBack(BaseModel):
    likes_feedback:str
    dislikes_feedback:str

def fetch_likes_dislikes_from_db():
    """
    Fetch liked and disliked entries from the jobs.db database.
    """
    try:
        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()

        # Fetch liked entries
        cursor.execute('SELECT * FROM jobs WHERE liked = 1')
        liked_entries = cursor.fetchall()

        # Fetch disliked entries
        cursor.execute('SELECT * FROM jobs WHERE liked = 0')
        disliked_entries = cursor.fetchall()

        conn.close()
        return liked_entries, disliked_entries
    except Exception as e:
        print(f"Error fetching entries: {e}")
        return None, None

def format_entries_to_text(liked_entries, disliked_entries):
    """
    Format liked and disliked entries into text for ChatGPT.
    """
    text = "# Summary of Likes and Dislikes\n\n"

    # Format liked entries
    text += "## Liked Entries\n"
    for entry in liked_entries:
        text += (
            f"- **Category**: {entry[1]}\n"
            f"  - **Description**: {entry[2]}\n"
            f"  - **Relation to User**: {entry[3]}\n"
            f"  - **Actionable Details**: {entry[4]}\n"
            f"  - **Expected Outcome**: {entry[5]}\n"
            f"  - **Timeline**: {entry[6]}\n\n"
        )

    # Format disliked entries
    text += "## Disliked Entries\n"
    for entry in disliked_entries:
        text += (
            f"- **Category**: {entry[1]}\n"
            f"  - **Description**: {entry[2]}\n"
            f"  - **Relation to User**: {entry[3]}\n"
            f"  - **Actionable Details**: {entry[4]}\n"
            f"  - **Expected Outcome**: {entry[5]}\n"
            f"  - **Timeline**: {entry[6]}\n\n"
        )

    return text

def generate_summary_with_chatgpt(text):
    """
    Use ChatGPT to generate a summary of the likes and dislikes.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                "You are an assistant analyzing feedback. Below is a list of liked and disliked entries. "
                "Summarize the key themes and insights for both liked and disliked entries, focusing on patterns, "
                "trends, and actionable recommendations:\n\n"
                f"{text}"
            )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
        )
        return response.choices[0].message
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

if __name__ == "__main__":
    # Fetch liked and disliked entries
    liked_entries, disliked_entries = fetch_likes_dislikes_from_db()

    if liked_entries or disliked_entries:
        # Format entries into text
        formatted_text = format_entries_to_text(liked_entries, disliked_entries)
        
        # Generate summary using ChatGPT
        summary = generate_summary_with_chatgpt(formatted_text)
        
        if summary:
            print("Generated Summary:\n")
            print(summary)
        else:
            print("Failed to generate a summary.")
    else:
        print("No liked or disliked entries found.")
