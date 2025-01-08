import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re
from sentence_transformers import SentenceTransformer, util

# Preload NLTK stopwords
stopwords.words('english')

# Filler words for cleanup
FILLER_WORDS = {
    "you know", "um", "yeah", "like", "uh", "so", "well", "actually", "basically", "right",
    "I mean", "kind of", "sort of", "you see", "just"
}

# SentenceTransformer Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Topic hierarchy
topics_hierarchy = {
    "App Development": ["Feature Prioritization", "Custom UI/UX", "Searchable Databases"],
    "Self-Reflection": ["Journaling as Self-Discovery", "Purpose and Creativity"],
    "Technology and Tools": ["OpenAI API", "AI-Powered Insights", "Lightweight NLP Models"],
    "Learning and Skill Building": ["JavaScript for Frontend", "LaTeX and Math Documentation"],
    "Meta-Level Observations": ["Design Thinking", "User-Centered Development"],
}

def preprocess_text(text):
    """
    Remove filler words and normalize text.
    """
    for filler in FILLER_WORDS:
        text = re.sub(rf"\b{re.escape(filler)}\b[,\.]?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_keywords_and_summary(text, num_keywords=5, num_sentences=3):
    """
    Extract keywords and summary from text.
    """
    text = preprocess_text(text)
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in stop_words]
    word_freq = Counter(words)
    keywords = [word for word, freq in word_freq.most_common(num_keywords)]
    sentences = sent_tokenize(text)
    sentence_scores = {}
    for sentence in sentences:
        for word in keywords:
            if word in sentence.lower():
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_freq[word]
    summary = ' '.join(sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences])
    return {'keywords': keywords, 'summary': summary}

def hierarchical_topic_matching(text, top_broad_n=1, top_sub_n=3):
    """
    Match broad topics and subtopics for the text.
    """
    broad_topics = list(topics_hierarchy.keys())
    text_embedding = model.encode(text, convert_to_tensor=True)
    broad_embeddings = model.encode(broad_topics, convert_to_tensor=True)
    broad_similarities = util.cos_sim(text_embedding, broad_embeddings)
    broad_scores = [(broad_topics[i], float(broad_similarities[0][i])) for i in range(len(broad_topics))]
    broad_scores = sorted(broad_scores, key=lambda x: x[1], reverse=True)
    top_broad_topics = broad_scores[:top_broad_n]
    results = {}
    for broad_topic, broad_score in top_broad_topics:
        subtopics = topics_hierarchy[broad_topic]
        sub_embeddings = model.encode(subtopics, convert_to_tensor=True)
        sub_similarities = util.cos_sim(text_embedding, sub_embeddings)
        sub_scores = [(subtopics[i], float(sub_similarities[0][i])) for i in range(len(subtopics))]
        sub_scores = sorted(sub_scores, key=lambda x: x[1], reverse=True)
        top_subtopics = sub_scores[:top_sub_n]
        results[broad_topic] = {"broad_score": broad_score, "subtopics": top_subtopics}
    return results

def update_entries():
    """
    Update all entries in the database with summary, keywords, and topics.
    """
    conn = sqlite3.connect("journal_entries.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM journal_entries")
    entries = cursor.fetchall()

    for entry_id, content in entries:
        if not content:
            continue
        # Extract summary and keywords
        result = extract_keywords_and_summary(content)
        summary = result['summary']
        keywords = ', '.join(result['keywords'])
        # Extract topics
        topics = hierarchical_topic_matching(content)
        topics_str = ', '.join([f"{broad}: {', '.join([sub[0] for sub in details['subtopics']])}" for broad, details in topics.items()])

        # Update the database
        cursor.execute("""
            UPDATE journal_entries
            SET summary = ?, keywords = ?, topics = ?
            WHERE id = ?
        """, (summary, keywords, topics_str, entry_id))

    conn.commit()
    conn.close()
    print("Entries updated successfully!")

if __name__ == "__main__":
    update_entries()
