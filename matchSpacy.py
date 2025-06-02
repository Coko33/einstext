import spacy
nlp = spacy.load("es_core_news_md")

def find_best_match(user_question, entries):
    user_doc = nlp(user_question)
    best_match = None
    max_similarity = 0
    for entry in entries:
        for tag in entry["tags"]:
            tag_doc = nlp(tag)
            similarity = user_doc.similarity(tag_doc)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = entry
    return best_match