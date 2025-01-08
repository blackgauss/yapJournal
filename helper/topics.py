from sentence_transformers import SentenceTransformer, util

# Define hierarchical topics
topics_hierarchy = {
    "App Development": [
        "Feature Prioritization",
        "Custom UI/UX",
        "Searchable Databases",
        "Speech-to-Text Conversion",
        "Modular App Design",
        "Transcription Accuracy",
    ],
    "Self-Reflection": [
        "Journaling as Self-Discovery",
        "Purpose and Creativity",
        "Productivity and Motivation",
        "Oral Tradition",
        "Behavioral Change",
    ],
    "Technology and Tools": [
        "OpenAI API",
        "AI-Powered Insights",
        "Lightweight NLP Models",
        "Recommendation Algorithms",
        "Personal Cloud Storage",
        "Raspberry Pi Devices",
    ],
    "Learning and Skill Building": [
        "JavaScript for Frontend",
        "LaTeX and Math Documentation",
        "Python Projects",
        "Problem Solving through Coding",
        "Iterative Learning",
    ],
    "Meta-Level Observations": [
        "Design Thinking",
        "User-Centered Development",
        "Data-Driven Creativity",
        "Offline and Online Systems",
    ],
}

# Load the sentence transformer model
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    raise


def hierarchical_topic_matching(text, topics_hierarchy, top_broad_n=1, top_sub_n=3):
    """
    Match broad topics first, then match subtopics within the top broad topic(s).

    :param text: Input text to analyze.
    :param topics_hierarchy: Dictionary mapping broad topics to their subtopics.
    :param top_broad_n: Number of top broad topics to return.
    :param top_sub_n: Number of top subtopics per broad topic to return.
    :return: Dictionary with matched broad topics and their subtopics.
    """
    try:
        # Validate input
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string.")

        print("Step 1: Starting broad topic matching...")
        broad_topics = list(topics_hierarchy.keys())
        text_embedding = model.encode(text, convert_to_tensor=True)
        broad_embeddings = model.encode(broad_topics, convert_to_tensor=True)

        # Compute similarities for broad topics
        broad_similarities = util.cos_sim(text_embedding, broad_embeddings)
        broad_scores = [(broad_topics[i], float(broad_similarities[0][i])) for i in range(len(broad_topics))]
        broad_scores = sorted(broad_scores, key=lambda x: x[1], reverse=True)
        top_broad_topics = broad_scores[:top_broad_n]
        print(f"Step 2: Broad topic matches: {top_broad_topics}")

        # Step 2: Match Subtopics within Top Broad Topics
        results = {}
        for broad_topic, broad_score in top_broad_topics:
            print(f"Step 3: Matching subtopics for broad topic: {broad_topic}")
            subtopics = topics_hierarchy[broad_topic]
            sub_embeddings = model.encode(subtopics, convert_to_tensor=True)

            # Compute similarities for subtopics
            sub_similarities = util.cos_sim(text_embedding, sub_embeddings)
            sub_scores = [(subtopics[i], float(sub_similarities[0][i])) for i in range(len(subtopics))]
            sub_scores = sorted(sub_scores, key=lambda x: x[1], reverse=True)
            top_subtopics = sub_scores[:top_sub_n]

            results[broad_topic] = {
                "broad_score": broad_score,
                "subtopics": top_subtopics,
            }

        print(f"Step 4: Final results: {results}")
        return results

    except Exception as e:
        print(f"Error in hierarchical topic matching: {e}")
        return {"error": str(e)}
