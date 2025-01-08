from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re

def extract_keywords_and_summary(text, num_keywords=5, num_sentences=3):
    # Preprocess the text
    text = re.sub(r'\s+', ' ', text)
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
