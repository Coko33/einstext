from sentence_transformers import SentenceTransformer, util

#prod
#model = SentenceTransformer('./modelos/models--sentence-transformers--all-MiniLM-L6-v2')

#dev
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./modelos/')
#model = SentenceTransformer('all-mpnet-base-v2', cache_folder='./modelos/')

def find_best_match_sentence_transformers(user_question, entradas):
    
    input_embedding = model.encode(user_question, convert_to_tensor=True)
    best_match = None
    best_score = -1

    for entrada in entradas:
        contenido = " ".join(entrada["tags"]) + " " + entrada.get("texto", "")
        entry_embedding = model.encode(contenido, convert_to_tensor=True)

        similarity = util.cos_sim(input_embedding, entry_embedding).item()

        if similarity > best_score:
            best_score = similarity
            best_match = entrada
    return best_match
