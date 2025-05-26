import cv2
import os
import textwrap

def escalar_frame(frame, ancho_max=800, alto_max=600):
    alto, ancho = frame.shape[:2]
    factor_escala = min(ancho_max / ancho, alto_max / alto, 1.0)  # No escala hacia arriba
    nuevo_ancho = int(ancho * factor_escala)
    nuevo_alto = int(alto * factor_escala)
    return cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

def dibujar_texto(frame, texto, margen=10, alto_caja=100):
    ancho = frame.shape[1]
    alto = frame.shape[0]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, alto - alto_caja), (ancho, alto), (0, 0, 0), -1)
    alpha = 0.6
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    color = (255, 255, 255)
    thickness = 1
    max_line_width = 80
    wrapped_text = textwrap.wrap(texto, width=max_line_width)

    for i, linea in enumerate(wrapped_text[:4]):
        y = alto - alto_caja + margen + (i + 1) * 22
        cv2.putText(frame, linea, (margen, y), font, font_scale, color, thickness, cv2.LINE_AA)

    return frame

def mostrar_imagen_fija(ruta_frame, texto=""):
    cv2.namedWindow("🗣️ Animación", cv2.WINDOW_AUTOSIZE)  # 🔧 Solo una vez
    frame = cv2.imread(ruta_frame)
    if frame is None:
        print(f"❌ No se pudo cargar la imagen: {ruta_frame}")
        return

    frame_escalado = escalar_frame(frame)
    frame_con_texto = dibujar_texto(frame_escalado, texto)
    cv2.imshow("🗣️ Animación", frame_con_texto)
    cv2.waitKey(1)

def reproducir_animacion_opencv(carpeta_frames, duracion_por_frame=100, repeticiones=1, texto=""):
    archivos = sorted([f for f in os.listdir(carpeta_frames) if f.endswith(".jpg")])
    
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

    for _ in range(repeticiones):
        for frame in frames:
            frame_escalado = escalar_frame(frame)
            frame_con_texto = dibujar_texto(frame_escalado, texto)
            cv2.imshow("🗣️ Animación", frame_con_texto)
            key = cv2.waitKey(duracion_por_frame)
            if key == 27:  # ESC
                cv2.destroyAllWindows()
                return

    # Mostrar el primer frame como cierre
    frame_final = dibujar_texto(escalar_frame(frames[0]), texto)
    cv2.imshow("🗣️ Animación", frame_final)
    print("⏹️ Esperando cierre (ESC)...")
    while True:
        key = cv2.waitKey(100)
        if key == 27:
            break

    cv2.destroyAllWindows()
