from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def find_best_match_sentence_transformers(user_question, entradas):
    
    input_embedding = model.encode(user_question, convert_to_tensor=True)
    best_match = None
    best_score = -1

    for entrada in entradas:
        tags_text = " ".join(entrada["texto"])
        entry_embedding = model.encode(tags_text, convert_to_tensor=True)
    
        similarity = util.cos_sim(input_embedding, entry_embedding).item()
    
        if similarity > best_score:
            best_score = similarity
            best_match = entrada
        return best_match
