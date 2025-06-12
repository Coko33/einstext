from sentence_transformers import SentenceTransformer

# Esto descargará el modelo completo en cache_folder y lo guardará en forma usable.
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder="./modelos")

print("✅ Modelo descargado y listo en './modelos/sentence-transformers_all-MiniLM-L6-v2'")
