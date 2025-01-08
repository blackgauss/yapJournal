import spacy

# Load SpaCy's medium-sized English model for semantic understanding
nlp = spacy.load("en_core_web_md")

def get_semantic_topics(text, predefined_topics=None, top_n=3):
    """
    Extract semantic topics based on similarity to predefined topic concepts.
    :param text: Input text for analysis.
    :param predefined_topics: List of predefined topic concepts.
    :param top_n: Number of top topics to return.
    :return: List of relevant topics.
    """
    # Default topics if none are provided
    if predefined_topics is None:
        predefined_topics = [
            "technology",
            "education",
            "healthcare",
            "business",
            "entertainment",
            "sports",
            "science",
            "politics",
        ]

    # Preprocess text and calculate semantic similarity
    doc = nlp(text)
    topic_scores = {}
    for topic in predefined_topics:
        topic_doc = nlp(topic)
        similarity = doc.similarity(topic_doc)
        topic_scores[topic] = similarity

    # Sort topics by relevance
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, score in sorted_topics[:top_n]]
