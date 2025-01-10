from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List, Optional
import sqlite3

# Load environment variables from a .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

class FilteredIdea(BaseModel):
    probability_of_thousand_in_week: float # probability of making $1000 in the next week
    overall_ranking: str  # Overall ranking score for the idea
    description: str  # Detailed explanation of the idea
    time_needed: List[float]  # Time required over 1 day, 1 week, 1 month, 1 year
    bullish_earnings_forecast: List[float]  # Earnings forecast for [1 week, 1 month, 1 year]
    bearish_earnings_forecast: List[float]  # Earnings forecast for [1 week, 1 month, 1 year]
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

def filter_ideas(journal_content):
    """
    Filters journal content to extract only the most important ideas for making money, 
    based on the guidelines provided in Metaobs 01-09-1420.

    :param journal_content: The raw journal text.
    :return: List of FilteredIdea instances.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # Use the appropriate OpenAI model
            messages=[
                {
                    "role": "system",
"content":(
                        "Your task is to extract 30 innovative, actionable ideas for making money based on the user's journal. "
                        "Each idea must include the following attributes, with insightful responses for each field:"
                        "\n- **Probability of $1000/Week**: A float value for the probability of making $1000 in the next week."
                        "\n- **Overall Ranking**: A single string score or rating (e.g., 'High', 'Moderate')."
                        "\n- **Description**: A one paragraph detailed explanation of the idea. This should be formative and technical so as to be an actual blueprint for the idea."
                        "\n- **Time Needed**: A list of time estimates for [1 day, 1 week, 1 month, 1 year]."
                        "\n- **Earnings Forecast**: A list of earnings forecasts for [1 week, 1 month, 1 year]."
                        "\n- **How Realistic**: A brief statement on how achievable the idea is."
                        "\n- **Description of Earning Streams**: A concise explanation of where earnings come from."
                        "\n- **Skills Required**: A list of skills necessary to execute the idea."
                        "\n- **Man Hours**: Estimated hours for beginner, intermediate, and expert levels."
                        "\n- **Novelty Score**: A float score (1-10) for how novel the idea is."
                        "\n- **Difficulty Score**: A float score (1-10) for how challenging the idea is."
                        "\n- **Location**: A list containing [Country, State]."
                        "\n- **Audience**: A brief description of the target demographic."
                        "\n- **Additional Resources**: Resources required to execute the idea."
                        "\n- **Additional Data Needed**: Data needed to refine or execute the idea."
                        "\n- **Suitability to User**: A concise explanation (1-2 sentences) on how well this idea fits the user's skills and goals."
                        "\n- **Passive Income**: A boolean indicating if the idea generates passive income."
                        "\n- **User Competitiveness**: A concise explanation (2 sentences max) of how competitive the user is in this niche."
                        "\nFocus on variety and ensure brevity for each response. Generate exactly 30 ideas in your response."
                    )

                },
                {
                    "role": "user",
                    "content": journal_content
                }
            ],
            response_format=FilteredIdeaExtraction,
                top_p=1.0,  # Include more diverse possibilities
                temperature=0.8 # Control the randomness of the output
        )

        # Extract and return the filtered ideas
        filtered_ideas = response.choices[0].message.parsed
        return filtered_ideas
    except Exception as e:
        print(f"Error filtering ideas: {e}")
        return None
    
# Function to process journal content and extract actionable steps
def extract_actionable_steps(journal_content):
    """
    Extract actionable steps from journal content.
    
    :param journal_content: The raw journal text.
    :return: A list of actionable steps.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # Use the appropriate OpenAI model
            messages=[
                {
                    "role": "system", 
"content": (
    "Your role is to guide an incredibly skilled and driven individual—a version of your younger self—to turn their technical abilities, problem-solving skills, and creativity into wealth. "
    "You understand this person's unique identity and talents, and every piece of advice you provide is custom-tailored to their goals and abilities. "
    "You refuse to give generic advice or solutions. Instead, your guidance reflects the user's potential, ambition, and the insights provided in their journal entries. "
    "Your primary objective is to help this person generate significant income—up to $1 million in one year—by leveraging their skills and the insights in their journal. "
    "To achieve this, you will: "
    "1. Extract actionable ideas from their journal entries, focusing on coding projects, monetizable ideas, and impactful opportunities. "
    "2. Provide a list of **30 actionable steps** with a focus on generating income within **1 week**. "
    "3. Include detailed advice on how each step directly relates to their unique goals, skills, and interests as outlined in their journal. "
    "4. Incorporate any relevant real-time news, opportunities, or trends that align with their location, industry, or context. "
    "5. Clearly state any additional information you need from the user to refine your advice and maximize its relevance and impact. "
    "6. Only choose topics which the user will learn from even if the plan fails."
    "7. Every task should build on their portfoli and continue their brand."
    "For each step, include: "
    "- **Category**: A label. "
    "- **Description**: A concise explanation of the step. "
    "- **How It Relates to the User**: Why this step is perfect for their skills, goals, and situation. "
    "- **Actionable Details**: Specific tools, platforms, or resources to use. "
    "- **Expected Outcome**: What the user should achieve if they follow this step successfully. "
    "- **Timeline**: When the user should complete this step. "
    "- **Time Commitment**: The amount of time the user will need to dedicate to complete this step. "
    "- **Earnings Forecast**: An estimated list of earnings from this step for 1 week, 1 month, and 1 year. "
    "- **Best Season**: The season during which this step will be most effective (e.g., Spring, Summer, Fall, Winter). "
    "- **Next Contact**: The person or role the user should reach out to next to progress on this step. "
    "- **Request For More Information**: Any additional details you need from the user to refine this step. "
    "Make 100 tasks."  
    "Do not provide vague or generalized advice. Ensure every recommendation feels like it was crafted uniquely for the user and aligns with their journal entries."
)
                },
                {
                    "role": "user", 
                    "content": journal_content
                }
            ],
            response_format=ActionableStepsExtraction,
            top_p=1.0  # Include more diverse possibilities
        )
        
        # Extract and return the actionable steps
        actionable_steps = response.choices[0].message.parsed
        return actionable_steps

    except Exception as e:
        print(f"Error extracting actionable steps: {e}")
        return None

def save_filtered_ideas_to_md(entry_metadata, filtered_ideas: FilteredIdeaExtraction, output_file="filtered_ideas.md"):
    """
    Save filtered journal ideas to a .txt file.

    :param entry_metadata: A dictionary containing metadata like title, date, and tag.
    :param filtered_ideas: An instance of FilteredIdeaExtraction containing the ideas.
    :param output_file: The name of the output .txt file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(f"# {entry_metadata['title']}\n\n")
            txt_file.write(f"**Date Created:** {entry_metadata['date_created']}\n")
            txt_file.write(f"**Tag:** {entry_metadata['tag']}\n\n")

            for idx, idea in enumerate(filtered_ideas.ideas, 1):
                txt_file.write(f"## Idea {idx}\n\n")
                txt_file.write(f"**Passive Income:** {idea.passive_income}\n\n")
                txt_file.write(f"**User Competitiveness:** {idea.user_competiveness}\n\n")
                txt_file.write(f"**Realistic:** {idea.how_realistic}\n\n")
                txt_file.write(f"**Description:**\n{idea.description}\n\n")
                txt_file.write("**Time Needed:**\n\n")
                txt_file.write(f"- 1 Day: {idea.time_needed[0]} hours\n")
                txt_file.write(f"- 1 Week: {idea.time_needed[1]} hours\n") 
                txt_file.write(f"- 1 Month: {idea.time_needed[2]} hours\n")
                txt_file.write(f"- 1 Year: {idea.time_needed[3]} hours\n\n")
                txt_file.write(f"**Earnings Source:**\n{idea.description_of_earning_streams}\n\n")
                txt_file.write(f"**Probability Of $1000/Week:**\n{idea.probability_of_thousand_in_week}\n\n")
                txt_file.write("**Bull Earnings Forecast:**\n\n")
                txt_file.write(f"- 1 Week: ${idea.bullish_earnings_forecast[0]:,.2f}\n")
                txt_file.write(f"- 1 Month: ${idea.bullish_earnings_forecast[1]:,.2f}\n")
                txt_file.write(f"- 1 Year: ${idea.bullish_earnings_forecast[2]:,.2f}\n\n")
                txt_file.write("**Bear Earnings Forecast:**\n\n")
                txt_file.write(f"- 1 Week: ${idea.bearish_earnings_forecast[0]:,.2f}\n")
                txt_file.write(f"- 1 Month: ${idea.bearish_earnings_forecast[1]:,.2f}\n")
                txt_file.write(f"- 1 Year: ${idea.bearish_earnings_forecast[2]:,.2f}\n\n")
                txt_file.write(f"**Skills:**\n- {', '.join(idea.skills)}\n\n")
                txt_file.write("**Man Hours:**\n\n")
                txt_file.write(f"- Beginner: {idea.man_hours[0]} hours\n")
                txt_file.write(f"- Intermediate: {idea.man_hours[1]} hours\n")
                txt_file.write(f"- Expert: {idea.man_hours[2]} hours\n\n")
                txt_file.write(f"**Novelty Score:** {idea.novelty_score}\n\n")
                txt_file.write(f"**Difficulty Score:** {idea.difficulty_score}\n\n")
                txt_file.write("**Location:**\n\n")
                txt_file.write(f"- Country: {idea.location[0]}\n")
                txt_file.write(f"- State: {idea.location[1]}\n\n")
                txt_file.write(f"**Audience:**\n{idea.audience}\n\n")
                txt_file.write(f"**Additional Resources:**\n{idea.additional_resources}\n\n")
                txt_file.write(f"**Additional Data Needed:**\n{idea.additional_data_needed}\n\n")
                txt_file.write(f"**Overall Ranking:** {idea.overall_ranking}\n\n")
                txt_file.write(f"**Suitability to User:**\n{idea.suitability_to_user}\n\n")
                txt_file.write("---\n\n")
        print(f"Filtered ideas successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving filtered ideas to .md file: {e}")

        
def save_steps_to_markdown(tasks: ActionableStepsExtraction, output_file: str = 'actionable_steps.md'):
    """
    Save a list of actionable steps to a Markdown file.

    :param tasks: An instance of ActionableStepsExtraction containing the steps.
    :param output_file: The name of the output Markdown file.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write("# Actionable Steps\n\n")

            for idx, step in enumerate(tasks.steps, 1):
                md_file.write(f"## Step {idx}: {step.category}\n\n")
                md_file.write(f"**Description:** {step.description}\n\n")
                md_file.write(f"**Relation to User:** {step.relation_to_user}\n\n")
                md_file.write(f"**Actionable Details:** {step.actionable_details}\n\n")
                md_file.write(f"**Expected Outcome:** {step.expected_outcome}\n\n")
                md_file.write(f"**Timeline:** {step.timeline}\n\n")
                md_file.write(f"**Time Commitment:** {step.time_commitment}\n\n")
                md_file.write(
                    f"**Earnings Forecast:**\n\n- 1 Week: ${step.earnings_forecast[0]:,.2f}\n"
                    f"- 1 Month: ${step.earnings_forecast[1]:,.2f}\n"
                    f"- 1 Year: ${step.earnings_forecast[2]:,.2f}\n\n"
                )
                md_file.write(f"**Best Season:** {step.best_season}\n\n")
                md_file.write(f"**Next Contact:** {step.next_contact}\n\n")
                md_file.write(f"**Additional Info Request:** {step.additional_info_request}\n\n")
                md_file.write("---\n\n")

        print(f"Actionable steps successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving steps to Markdown: {e}")

# Example Usage
def save_and_print():
    try:
        # Read all journal entries
        with open("journal_entries_export.txt", "r", encoding="utf-8") as file:
            journal_content = file.read()

        # Filter ideas
        filtered_ideas = filter_ideas(journal_content)

        if filtered_ideas:
            # Save filtered ideas to a text file
            entry_metadata = {
                "title": "Filtered Journal Ideas", 
                "date_created": str(datetime.now()),
                "tag": "metaObs"
            }
            save_filtered_ideas_to_md(entry_metadata, filtered_ideas)
        else:
            print("Failed to filter ideas.")

        # Read journal entry from file
        with open('./filtered_ideas.md', 'r', encoding='utf-8') as file:
            journal_entry = file.read()
        
        result = extract_actionable_steps(journal_entry)
        if result:
            # Save actionable steps to a Markdown file
            save_steps_to_markdown(result, 'actionable_steps.md')
        else:
            print("Failed to extract actionable steps.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def turn_to_json():
    '''save the list of actionable steps to a json file'''
    try:
        # Read journal entry from file
        with open('./filtered_ideas.md', 'r', encoding='utf-8') as file:
            journal_entry = file.read()
        
        result = extract_actionable_steps(journal_entry)
        if result:
            # Save actionable steps to a JSON file
            with open('actionable_steps.json', 'w') as file:
                file.write(result.json())
        else:
            print("Failed to extract actionable steps.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

def save_to_db():
    """
    Save the list of actionable steps directly to the jobs.db database.
    """
    try:
        # Read journal entry from file
        with open('./filtered_ideas.md', 'r', encoding='utf-8') as file:
            journal_entry = file.read()

        # Extract actionable steps
        result = extract_actionable_steps(journal_entry)
        if result:
            actionable_steps = result.steps  # This is a list of Step objects
            
            # Connect to the jobs.db database
            conn = sqlite3.connect("jobs.db")
            cursor = conn.cursor()
            
            # Insert actionable steps into the jobs table
            for step in actionable_steps:
                cursor.execute('''
                    INSERT INTO jobs (
                        category, 
                        description, 
                        relation_to_user, 
                        actionable_details, 
                        expected_outcome, 
                        timeline, 
                        liked
                    )
                    VALUES (?, ?, ?, ?, ?, ?, NULL)
                ''', (
                    step.category,  # Access attributes directly
                    step.description,
                    step.relation_to_user,
                    step.actionable_details,
                    step.expected_outcome,
                    step.timeline,
                ))

            conn.commit()
            conn.close()

            print(f"Successfully saved {len(actionable_steps)} actionable steps to the database.")
        else:
            print("Failed to extract actionable steps.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Save and print
    #save_and_print()
    for i in range(5):
        save_to_db()