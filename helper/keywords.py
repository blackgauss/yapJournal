from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re

# List of filler words and phrases to remove
FILLER_WORDS = {
    "you know", "um", "yeah", "like", "uh", "so", "well", "actually", "basically", "right",
    "I mean", "kind of", "sort of", "you see", "just"
}

def preprocess_text(text):
    """
    Preprocess the text by:
    1. Removing filler words and phrases.
    2. Cleaning up punctuation after filler word removal.
    3. Normalizing spaces, tabs, and newlines.
    """
    # Remove filler words and phrases
    for filler in FILLER_WORDS:
        text = re.sub(rf"\b{re.escape(filler)}\b[,\.]?", "", text, flags=re.IGNORECASE)

    # Remove redundant spaces around punctuation (e.g., " ,", " .")
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

def extract_keywords_and_summary(text, num_keywords=5, num_sentences=3):
    """
    Extract keywords and summary from the given text.
    """
    # Preprocess the text
    text = preprocess_text(text)
    stop_words = set(stopwords.words('english'))

    # Tokenize and remove stopwords
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in stop_words]

    # Count word frequencies
    word_freq = Counter(words)

    # Extract keywords
    keywords = [word for word, freq in word_freq.most_common(num_keywords)]

    # Summarize using top sentences
    sentences = sent_tokenize(text)
    sentence_scores = {}
    for sentence in sentences:
        for word in keywords:
            if word in sentence.lower():
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_freq[word]

    # Select top sentences
    summary = ' '.join(sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences])

    return {'keywords': keywords, 'summary': summary}
