import sounddevice as sd
import vosk
import queue
import json
import os
from rapidfuzz import process

# Configuración
MODEL_PATH = "modelos/vosk-model-small-es-0.42"
TEXTO_PATH = "dataTexto.txt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en {MODEL_PATH}")

model = vosk.Model(MODEL_PATH)
q = queue.Queue()

with open(TEXTO_PATH, "r", encoding="utf-8") as f:
    lineas_texto = f.readlines()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def recognize_and_match():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        print("🎤 Escuchando... (Ctrl+C para salir)")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                voz_texto = result.get("text", "")
                if voz_texto:
                    buscar_fragmento(voz_texto)

# def buscar_fragmento(texto_voz):
#     mejor_match, score, idx = process.extractOne(texto_voz, lineas_texto)
#     print(f"\nEntrada de voz: {texto_voz}")
#     print(f"🎯 Mejor coincidencia: {mejor_match.strip()}")
#     print(f"Similaridad: {score:.2f}%\n")


def buscar_fragmento(texto_voz):
    mejor_match, score, idx = process.extractOne(texto_voz, lineas_texto)
    parrafo = encontrar_parrafo(mejor_match)
    print(f"\nEntrada de voz: {texto_voz}")
    print(f"🎯 Párrafo encontrado:\n{parrafo.strip()}")
    print(f"Similaridad: {score:.2f}%\n")

def encontrar_parrafo(linea_encontrada):
    with open(TEXTO_PATH, "r", encoding="utf-8") as f:
        texto_completo = f.read()

    parrafos = texto_completo.split('\n\n')  # Separar por párrafos

    for parrafo in parrafos:
        if linea_encontrada.strip() in parrafo:
            return parrafo

    return "❌ Párrafo no encontrado."

if __name__ == "__main__":
    try:
        recognize_and_match()
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")


# 💡 Tecnologías adicionales recomendadas
#     • rapidfuzz (mejor que fuzzywuzzy, más rápido) → para hacer coincidencias de texto por similitud.
#     • (Opcional) NLP básico con spaCy o NLTK si quisieras hacer búsquedas más "inteligentes" en el futuro.