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

class GoodQuestion(BaseModel):
    text: str  # The actual question text
    is_clear: bool  # Is the question clear and unambiguous?
    is_falsifiable: bool  # Can the question be tested or proven true/false?
    falsifiable_experiment: str # Experiment to test the falsifiability
    is_actionable: bool  # Does the question lead to a path for solving it?
    relevance_score: float  # Relevance to personal goals/interests (0-1)
    ingenuity_score: float  # Ingenuity level (1-10)
    importance_score: float  # Importance of the question (1-10)
    has_static_target: bool  # Does it aim at a well-defined outcome?
    is_consistent: bool  # Is it consistent with existing knowledge?
    is_unbiased: bool  # Is it free from personal/cultural biases?
    is_experimentable: bool  # Can it be tested/experimented with?
    is_mathematical:bool # Does the problem benefit from the user's mathematical skills?
    skills_used: str  # List of skills required to solve the question
    boringness_score: float  # Boringness level (1-10)
    blooms_taxonomy: str  # Bloom's taxonomy level of the question

class QuestionList(BaseModel):
    questions: List[GoodQuestion]

def identify_problems(journal_content):
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
                        "Your task is to analyze the user's journal entries and generate 15 excellent questions and individually unique. "
                        "Each question must meet the following criteria: "
                        "1. Be clear and unambiguous. "
                        "2. Be falsifiable (testable or provable true/false). The phrasing should not be open ended unless prompting a solution."
                        "3. Be actionable (lead to a path for exploration). "
                        "4. Have a well-defined target. "
                        "5. Be relevant, important, and consistent with existing knowledge. "
                        "6. Be experimentable (can be interacted with practically)."
                        "As a bonus, decide if the problem will benefit from the users uniquem mathematical skills and abilities."
                        "Each problem should be phrased as an intesting intellecutal and technical challenge."
                        "Incentivee questions that require the user to think critically and creatively."
                        "Each question should be scalable. The solution should be relevant to other people as well."
                        "Each question should adress curiosity, issue, or problem that the user is facing. that is relevant to humans."
                        "Focus on problems that AI and LLMs would be useful for."
                    )

                },
                {
                    "role": "user",
                    "content": journal_content
                }
            ],
            response_format=QuestionList,
                top_p=1.0,  # Include more diverse possibilities
                temperature=1.0 # Control the randomness of the output
        )

        # Extract and return the filtered ideas
        filtered_ideas = response.choices[0].message.parsed
        return filtered_ideas
    except Exception as e:
        print(f"Error filtering ideas: {e}")
        return None
    
def save_questions_to_md(question_list: QuestionList, output_file: str = "good_questions.md"):
    """
    Save a list of good questions to a Markdown file.
    :param question_list: An instance of QuestionList containing GoodQuestion objects.
    :param output_file: The name of the output Markdown file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as md_file:
            md_file.write("# Good Questions\n\n")
            md_file.write("This document contains a list of questions extracted and evaluated based on your journal entries.\n\n")

            for idx, question in enumerate(question_list.questions, 1):
                md_file.write(f"## Question {idx}: {question.text}\n\n")
                md_file.write(f"- **Blooms Taxonomy Level**: {question.blooms_taxonomy}\n")
                md_file.write(f"- **Is Clear**: {'Yes' if question.is_clear else 'No'}\n")
                md_file.write(f"- **Is Falsifiable**: {'Yes' if question.is_falsifiable else 'No'}\n")
                md_file.write(f"- **Is Actionable**: {'Yes' if question.is_actionable else 'No'}\n")
                md_file.write(f"- **Relevance Score**: {question.relevance_score:.2f} (out of 1.0)\n")
                md_file.write(f"- **Ingenuity Score**: {question.ingenuity_score:.1f} (out of 10)\n")
                md_file.write(f"- **Importance Score**: {question.importance_score:.1f} (out of 10)\n")
                md_file.write(f"- **Has Static Target**: {'Yes' if question.has_static_target else 'No'}\n")
                md_file.write(f"- **Is Consistent**: {'Yes' if question.is_consistent else 'No'}\n")
                md_file.write(f"- **Is Unbiased**: {'Yes' if question.is_unbiased else 'No'}\n")
                md_file.write(f"- **Is Experimentable**: {'Yes' if question.is_experimentable else 'No'}\n")
                md_file.write(f"- **Is Mathematical**: {'Yes' if question.is_mathematical else 'No'}\n")
                md_file.write(f"- **Falsifiable Experiment**: {question.falsifiable_experiment}\n\n")
                md_file.write(f"- **Skills Used**: {question.skills_used}\n")
                md_file.write(f"- **Boringness Score**: {question.boringness_score:.1f} (out of 10)\n\n")
                md_file.write("\n---\n\n")

        print(f"Questions successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving questions to Markdown: {e}")

if __name__ == "__main__":
    # Fetch journal entries
     # Read all journal entries
    with open("journal_entries_recent.txt", "r", encoding="utf-8") as file:
        journal_content = file.read()
    problems_md = identify_problems(journal_content)
    # print(data)
    save_questions_to_md(problems_md)