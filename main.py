import sounddevice as sd
import vosk
import queue
import json
import os
import cv2
from datos import entradas
from animacion import reproducir_animacion_opencv, mostrar_imagen_fija
#from matchSpacy import find_best_match
from matchSentenceTransformers import find_best_match_sentence_transformers
import textwrap
import random

MODEL_PATH = "modelos/vosk-model-small-es-0.42"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en {MODEL_PATH}")

model = vosk.Model(MODEL_PATH)
q = queue.Queue()
primer_frame = os.path.join("frames/einstein", sorted(os.listdir("frames/einstein"))[0])
color_amarillo = (255, 204, 31, 255)
entradas_leidas = set()

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

        def fragmentar_entrada(entrada_actual):
            lineas_fragmentadas = textwrap.wrap(entrada_actual, width=90)
            ultima_linea = lineas_fragmentadas[-1]
            indice_fragmento = 0
            fragmento_lineas = lineas_fragmentadas[indice_fragmento:indice_fragmento + lineas_por_fragmento]
            if fragmento_lineas[-1] == ultima_linea:
                fragmento = "\n".join(fragmento_lineas)
            else:
                fragmento = "\n".join(fragmento_lineas) + "...(continúa)"
            return fragmento, ultima_linea
        
        def entrada_random():
            global entradas_leidas
            if len(entradas_leidas) == len(entradas):
                entradas_leidas = set()
            disponibles = [e for e in entradas if e["id"] not in entradas_leidas]
            entrada = random.choice(disponibles)
            entradas_leidas.add(entrada["id"])
            return entrada["texto"]

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                texto = result.get("text", "").lower()
                if not texto:
                    continue
                print("🦜", texto)
                if modo == "pregunta":
                    #entrada_encontrada = find_best_match(texto, entradas)
                    entrada_encontrada = find_best_match_sentence_transformers(texto, entradas)
                    if entrada_encontrada:
                        entrada_actual = entrada_encontrada["texto"]
                        fragmento, ultima_linea = fragmentar_entrada(entrada_actual)
                        reproducir_animacion_opencv("./frames/einstein/" if entrada_encontrada["perso"] == "Einstein" else "./frames/lugones/", repeticiones=20, texto=fragmento)
                        print("🟢 Coincidencia encontrada:")
                        print(fragmento)
                        entradas_leidas.add(entrada_encontrada["id"])
                        modo = "comando"
                    else:
                        mostrar_imagen_fija(primer_frame, texto="No entendí tu pregunta. \n¿Podrias repetirla?", color_texto=color_amarillo)
                        print("🔴 No se encontró coincidencia.")
                elif modo == "comando":
                    if "cualquier" in texto or "tema" in texto:
                        entrada_actual = entrada_random()
                        fragmento, ultima_linea = fragmentar_entrada(entrada_actual)
                        reproducir_animacion_opencv("./frames/einstein/" if entrada_encontrada["perso"] == "Einstein" else "./frames/lugones/", repeticiones=20, texto=fragmento)
                    elif "otra" in texto or "pregunta" in texto:
                        mostrar_imagen_fija(primer_frame, texto="Preguntá lo que quieras sobre la visita de Einstein a la Argentina", color_texto=color_amarillo)
                        print("🔁 Nueva pregunta")
                        modo = "pregunta"
                    elif "continuar" in texto:
                        if entrada_actual:
                            indice_fragmento += lineas_por_fragmento
                            if indice_fragmento < len(lineas_fragmentadas):
                                fragmento_lineas = lineas_fragmentadas[indice_fragmento:indice_fragmento + lineas_por_fragmento]
                                if fragmento_lineas[-1] == ultima_linea:
                                    fragmento = "\n".join(fragmento_lineas)
                                else:
                                    fragmento = "\n".join(fragmento_lineas) + "...(continúa)"
                                reproducir_animacion_opencv("./frames/einstein/" if entrada_encontrada["perso"] == "Einstein" else "./frames/lugones/", repeticiones=10, texto=fragmento)
                                print("⏩ Continuando...")
                            else:
                                mostrar_imagen_fija(primer_frame, texto="Eso es todo! Preguntá lo que quieras sobre la visita de Einstein a la Argentina", color_texto=color_amarillo)
                                print("🔚 Fin del contenido.")
                                modo = "pregunta"
                        else:
                            print("⚠️ No hay contenido previo para continuar.")              
                    elif "salir" in texto:
                        print("👋 Saliendo por comando de voz.")
                        break
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
