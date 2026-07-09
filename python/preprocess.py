import re
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))

def preprocess(text):

    text = text.lower()

    tokens = re.findall(r"\b[a-zA-Z0-9]+\b", text)

    tokens = [
        token
        for token in tokens
        if token not in stop_words
    ]

    return tokens