from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List, Optional

# Load environment variables from a .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

class FilteredIdea(BaseModel):
    probability_of_thousand_in_week: float # probability of making $1000 in the next week
    overall_ranking: str  # Overall ranking score for the idea
    description: str  # Detailed explanation of the idea
    time_needed: List[float]  # Time required over 1 day, 1 week, 1 month, 1 year
    earnings_forecast: List[float]  # Earnings forecast for [1 week, 1 month, 1 year]
    how_realistic: str  # How realistic the idea is
    description_of_earning_streams: str # Explaination of where earnings are coming from
    skills: List[str]  # List of skills required
    man_hours: List[float]  # Man hours needed for beginner, intermediate, and expert levels
    novelty_score: float  # Score for how novel the idea is
    difficulty_score: float  # Score for the difficulty of the idea
    location: List[str]  # Contains country and state
    audience: str  # Demographic or target audience
    additional_resources: str  # Resources required to implement the idea
    additional_data_needed: str  # Additional data needed for the idea
    suitability_to_user: str  # Explanation of how well suited this idea is to the user
    passive_income: bool # Whether the idea generates passive income
    user_competiveness: str # How competitive the user is in this niche (In two sentences)
class FilteredIdeaExtraction(BaseModel):
    ideas: List[FilteredIdea]

class Step(BaseModel):
    probability_of_thousand_in_week: float # probability of making $1000 in the next week
    category: str  # e.g., 'Coding Projects', 'Ideas', etc.
    description: str  # Detailed explanation of the step
    relation_to_user: str  # How the step relates to the user's goals
    actionable_details: str  # Specific tools, platforms, or resources to use
    expected_outcome: str  # What the user should achieve
    timeline: str  # When the user should complete the step
    additional_info_request: str  # Additional details required for refining the step
    time_commitment: str  # Time required to complete the step, e.g., '2 hours/week'
    earnings_forecast: List[float]  # Earnings forecast for [1 week, 1 month, 1 year]
    description_of_earning_streams: str # Explaination of where earnings are coming from
    best_season: str  # Season when this works best, e.g., 'Spring', 'Summer'
    next_contact: str  # Who to talk to next to move forward, e.g., 'Mentor', 'Colleague'
    passive_income: bool # Whether the idea generates passive income

class ActionableStepsExtraction(BaseModel):
    steps: List[Step]


def gpt_prompt(system_prompt:str, user_prompt:str, model:str, response_format:BaseModel):
    """
    Generate a response from the GPT-3 model based on the system and user prompts.

    :param system_prompt: The system prompt to provide context.
    :param user_prompt: The user prompt to generate a response.
    :param model: The GPT-3 model to use.
    :param response_format: The Pydantic model to use for parsing the response.
    :return: An instance of the response_format model containing the generated response.
    """
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format=response_format,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

if __name__ == "__main__":
    # Example Usage
    response:ActionableStepsExtraction = gpt_prompt("Hi I am testing this out", "I am testing this out", "gpt-4o-mini", ActionableStepsExtraction)
    response
    print(response)
    
