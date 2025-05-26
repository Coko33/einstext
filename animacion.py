import cv2
import os
import textwrap
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import pyautogui

def obtener_dimensiones_pantalla():
    ancho, alto = pyautogui.size()
    return ancho, alto

def escalar_y_centrar_frame(frame, ancho_pantalla, alto_pantalla, alto_caja_texto=100):
    alto_frame_original, ancho_frame_original = frame.shape[:2]

    # El área visible para el frame será el 50% de la pantalla (sin contar el texto aún)
    alto_area_frame = int(alto_pantalla * 0.5)

    # Ajustar relación de aspecto
    factor_escala = min(ancho_pantalla / ancho_frame_original, alto_area_frame / alto_frame_original, 1.0)
    nuevo_ancho = max(1, int(ancho_frame_original * factor_escala))
    nuevo_alto = max(1, int(alto_frame_original * factor_escala))

    print(f"📐 Frame original: {ancho_frame_original}x{alto_frame_original}")
    print(f"📏 Escalado a: {nuevo_ancho}x{nuevo_alto}, escala: {factor_escala:.2f}")

    frame_redimensionado = cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

    # Fondo gris claro
    canvas = np.full((alto_pantalla, ancho_pantalla, 3), fill_value=(246, 246, 245), dtype=np.uint8)

    # Centrado
    x_offset = (ancho_pantalla - nuevo_ancho) // 2
    y_offset = (alto_pantalla - alto_caja_texto - nuevo_alto) // 2
    y_offset = max(0, y_offset)

    print(f"📌 Offsets: x={x_offset}, y={y_offset}")

    canvas[y_offset:y_offset + nuevo_alto, x_offset:x_offset + nuevo_ancho] = frame_redimensionado
    return canvas

def dibujar_texto(canvas, texto, color_texto, margen=20, alto_caja=180):
    alto_canvas, ancho_canvas = canvas.shape[:2]

    # Caja de texto negra semitransparente
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0, alto_canvas - alto_caja), (ancho_canvas, alto_canvas), (0, 0, 0), -1)
    alpha = 0.6
    canvas = cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0)

    # PIL para UTF-8
    img_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    font_path = "DejaVuSans.ttf"
    font_size = 18
    font = ImageFont.truetype(font_path, font_size)

    max_chars_por_linea = ancho_canvas // (font_size // 2)
    wrapped_text = textwrap.wrap(texto, width=max_chars_por_linea)

    for i, linea in enumerate(wrapped_text[:alto_caja // (font_size + 6)]):
        y = alto_canvas - alto_caja + margen + i * (font_size + 6)
        draw.text((margen, y), linea, font=font, fill=color_texto or (255, 255, 255, 255))

    canvas = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return canvas

def mostrar_imagen_fija(ruta_frame, texto="", color_texto=(), alto_caja_texto=180):
    frame = cv2.imread(ruta_frame)
    if frame is None:
        print(f"❌ No se pudo cargar la imagen: {ruta_frame}")
        return

    pantalla_ancho, pantalla_alto = obtener_dimensiones_pantalla()
    print(f"🖥️ Tamaño de pantalla detectado: {pantalla_ancho}x{pantalla_alto}")

    canvas = escalar_y_centrar_frame(frame, pantalla_ancho, pantalla_alto, alto_caja_texto)
    canvas_con_texto = dibujar_texto(canvas, texto, color_texto, alto_caja=alto_caja_texto)
    cv2.imshow("🗣️ Animación", canvas_con_texto)
    cv2.waitKey(1)

def reproducir_animacion_opencv(carpeta_frames, duracion_por_frame=100, repeticiones=1, texto="", alto_caja_texto=180):
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

    pantalla_ancho, pantalla_alto = obtener_dimensiones_pantalla()
    print(f"🖥️ Tamaño de pantalla detectado: {pantalla_ancho}x{pantalla_alto}")

    for _ in range(repeticiones):
        for frame in frames:
            canvas = escalar_y_centrar_frame(frame, pantalla_ancho, pantalla_alto, alto_caja_texto)
            canvas_con_texto = dibujar_texto(canvas, texto, color_texto=(), alto_caja=alto_caja_texto)
            cv2.imshow("🗣️ Animación", canvas_con_texto)
            key = cv2.waitKey(duracion_por_frame)
            if key == 27:
                cv2.destroyAllWindows()
                return

    # Mostrar el primer frame al final, fijo
    frame_final = dibujar_texto(
        escalar_y_centrar_frame(frames[0], pantalla_ancho, pantalla_alto, alto_caja_texto),
        texto,
        color_texto=(),
        alto_caja=alto_caja_texto
    )
    cv2.imshow("🗣️ Animación", frame_final)
    print("⏹️ Esperando cierre (ESC)...")
    while True:
        key = cv2.waitKey(100)
        if key == 27:
            break

    cv2.destroyAllWindows()
