import spacy

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    """
    Extract keywords (nouns + proper nouns) from resume/job description.
    """
    doc = nlp(text)
    keywords = [token.text.lower() for token in doc if token.pos_ in ("NOUN", "PROPN")]
    return list(set(keywords))  # remove duplicates
