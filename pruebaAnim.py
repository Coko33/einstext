import cv2
import os
import time

def escalar_frame(frame, ancho_max=800, alto_max=600):
    alto, ancho = frame.shape[:2]
    factor_escala = min(ancho_max / ancho, alto_max / alto, 1.0)  # No escala hacia arriba
    nuevo_ancho = int(ancho * factor_escala)
    nuevo_alto = int(alto * factor_escala)
    return cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

def reproducir_animacion_opencv(carpeta_frames, duracion_por_frame=100, repeticiones=2):
    archivos = sorted([
        f for f in os.listdir(carpeta_frames)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])

    if not archivos:
        print("❌ No se encontraron imágenes en la carpeta.")
        return

    # Cargar todos los frames de una vez (opcional pero mejora la fluidez)
    frames = []
    for archivo in archivos:
        ruta = os.path.join(carpeta_frames, archivo)
        frame = cv2.imread(ruta)
        if frame is not None:
            frames.append(frame)
        else:
            print(f"⚠️ No se pudo cargar {ruta}")

    if not frames:
        print("❌ No se pudo cargar ningún frame.")
        return

    cv2.namedWindow("🗣️ Animación", cv2.WINDOW_AUTOSIZE)

    for _ in range(repeticiones):
        for frame in frames:
            frame_escalado = escalar_frame(frame)
            cv2.imshow("🗣️ Animación", frame_escalado)
            key = cv2.waitKey(duracion_por_frame)
            if key == 27:  # ESC
                break

    cv2.destroyAllWindows()

# Llamada de prueba
reproducir_animacion_opencv("./frames", duracion_por_frame=150, repeticiones=2)
