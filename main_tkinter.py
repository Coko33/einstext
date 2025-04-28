import tkinter as tk
from tkinter import scrolledtext
import sounddevice as sd
import vosk
import queue
import threading
import json
import os
from rapidfuzz import process

# ---------------- Configuración ----------------
MODEL_PATH = "modelos/vosk-model-small-es-0.42"
TEXTO_PATH = "dataTexto.txt"

# Verificar modelo
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en {MODEL_PATH}")

# Cargar modelo Vosk
model = vosk.Model(MODEL_PATH)
q = queue.Queue()

# Cargar texto extenso
with open(TEXTO_PATH, "r", encoding="utf-8") as f:
    lineas_texto = f.readlines()

# Función de audio
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# Hilo de reconocimiento
def recognize_and_match():
    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, 16000)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    voz_texto = result.get("text", "")
                    if voz_texto:
                        ventana.after(0, buscar_fragmento, voz_texto)
    except Exception as e:
        print("Error en reconocimiento:", e)

# Buscar fragmento de texto que más matchee
def buscar_fragmento(texto_voz):
    try:
        mejor_match, score, idx = process.extractOne(texto_voz, lineas_texto)
        mostrar_fragmento(mejor_match, score)
    except Exception as e:
        print("Error al buscar fragmento:", e)

def mostrar_fragmento(fragmento, score):
    texto_area.delete('1.0', tk.END)
    texto_area.insert(tk.END, f"🎯 Mejor coincidencia:\n\n{fragmento}\n\n(Similaridad: {score:.2f}%)")

# Iniciar hilo de reconocimiento
def iniciar_reconocimiento():
    threading.Thread(target=recognize_and_match, daemon=True).start()

# ---------------- Interfaz Tkinter ----------------
ventana = tk.Tk()
ventana.title("Búsqueda por voz")
ventana.geometry("600x400")

boton_iniciar = tk.Button(ventana, text="Iniciar reconocimiento", command=iniciar_reconocimiento)
boton_iniciar.pack(pady=10)

texto_area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD)
texto_area.pack(expand=True, fill='both', padx=10, pady=10)

ventana.mainloop()
