import sounddevice as sd
import vosk
import queue
import json
import os
import cv2
from rapidfuzz import process
from datos import entradas
from animacion import reproducir_animacion_opencv, mostrar_imagen_fija
from matchSpacy import find_best_match
import textwrap

MODEL_PATH = "modelos/vosk-model-small-es-0.42"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en {MODEL_PATH}")

model = vosk.Model(MODEL_PATH)
q = queue.Queue()
primer_frame = os.path.join("frames", sorted(os.listdir("frames"))[0])
color_amarillo = (255, 204, 31, 255)

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def recognize_and_match():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, 16000)
        print("🎤 Escuchando... (Ctrl+C para salir)")
        modo = "pregunta"
        entrada_actual = None
        lineas_fragmentadas = []
        indice_fragmento = 0
        lineas_por_fragmento = 5

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                texto = result.get("text", "").lower()
                if not texto:
                    continue
                print("🦜", texto)

                if modo == "pregunta":
                    entrada_encontrada = find_best_match(texto, entradas)
                    if entrada_encontrada:
                        entrada_actual = entrada_encontrada["texto"]
                        lineas_fragmentadas = textwrap.wrap(entrada_actual, width=90)
                        indice_fragmento = 0

                        fragmento_lineas = lineas_fragmentadas[indice_fragmento:indice_fragmento + lineas_por_fragmento]
                        fragmento = "\n".join(fragmento_lineas)

                        reproducir_animacion_opencv("./frames", repeticiones=20, texto=fragmento)
                        print("🟢 Coincidencia encontrada:")
                        print(fragmento)
                        modo = "comando"
                        
                    else:
                        mostrar_imagen_fija(primer_frame, texto="No entendí tu pregunta. \n¿Podrias repetirla?", color_texto=color_amarillo)
                        print("🔴 No se encontró coincidencia.")

                elif modo == "comando":
                    if "salir" in texto:
                        print("👋 Saliendo por comando de voz.")
                        break
                    elif "otra" in texto or "pregunta" in texto:
                        print("🔁 Nueva pregunta")
                        modo = "pregunta"
                    elif "continuar" in texto:
                        if entrada_actual:
                            indice_fragmento += lineas_por_fragmento
                            if indice_fragmento < len(lineas_fragmentadas):
                                fragmento_lineas = lineas_fragmentadas[indice_fragmento:indice_fragmento + lineas_por_fragmento]
                                fragmento = "\n".join(fragmento_lineas)
                                reproducir_animacion_opencv("./frames", repeticiones=20, texto=fragmento)
                                print("⏩ Continuando...")
                            else:
                                mostrar_imagen_fija(primer_frame, texto="✅ Ya se mostró todo el contenido.", color_texto=color_amarillo)
                                print("🔚 Fin del contenido.")
                                modo = "pregunta"
                        else:
                            print("⚠️ No hay contenido previo para continuar.")
                    else:
                        print("⚠️ No se reconoció el comando. Intentalo de nuevo.")

if __name__ == "__main__":
    try:
        cv2.namedWindow("🗣️ Animación", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("🗣️ Animación", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        mostrar_imagen_fija(primer_frame, texto="Preguntá lo que quieras sobre la visita de Einstein a la Argentina", color_texto=color_amarillo)
        recognize_and_match()
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")
    finally:
        cv2.destroyAllWindows()
