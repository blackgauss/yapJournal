from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

class ActionableStepsExtraction(BaseModel):
    steps: list[str]  # List of actionable steps

# Function to process journal content and extract actionable steps
def extract_actionable_steps(journal_content):
    """
    Extract actionable steps from journal content.
    
    :param journal_content: The raw journal text.
    :return: A list of actionable steps.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",  # Use the appropriate OpenAI model
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert assistant for productivity. "
                        "You will analyze journal entries and extract actionable steps the user can take. "
                        "The steps should be clear, concise, and prioritized."
                    )
                },
                {
                    "role": "user", 
                    "content": journal_content
                }
            ],
            response_format=ActionableStepsExtraction,
        )
        
        # Extract and return the actionable steps
        actionable_steps = response.choices[0].message.parsed.steps
        return actionable_steps

    except Exception as e:
        print(f"Error extracting actionable steps: {e}")
        return None

# Example Usage
if __name__ == "__main__":
    journal_entry = """
     Man, there's so many cool things that I want to learn in life. I don't know how to learn them all. I want to learn blender so I can make like 3D art. I want to learn kinda cool videos, like YouTube videos. I want to learn how to play the piano or like mechanically. The keyboard or the guitar as well. I want to know how computers work. Like I want to know how software works. I want to know how to make things secure. I make applications secure. And I don't know how I'm gonna learn all these things. I just gotta start doing them. I want to fill my time with learning all these things. And I want to get better at math. I still want to get better at math. Holy shit, how do I do this all?
    """
    actionable_steps = extract_actionable_steps(journal_entry)
    if actionable_steps:
        print("Actionable Steps:")
        for i, step in enumerate(actionable_steps, 1):
            print(f"{i}. {step}")
    else:
        print("Failed to extract actionable steps.")
