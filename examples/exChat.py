import cv2
import numpy as np
from picamera2 import Picamera2
import time

# Inicializar Picamera2
picam2 = Picamera2()

# Configuraciones de la cámara
mode = picam2.sensor_modes[0]

config = picam2.create_video_configuration(raw={'format': 'SRGGB10', 'size': (1332, 990)})
#config = picam2.create_preview_configuration(sensor={'output_size': (1333,990), 'bit_depth': 10})
picam2.configure(config)
#camera_config = picam2.create_video_configuration(main={"format": "XRGB8888", "size": (1280, 720)})
#picam2.configure(camera_config)

# Iniciar la cámara
picam2.start()

# Establecer el framerate
picam2.set_controls({"FrameRate": 120})

prev_time = 0
while True:
    # Capturar el frame
    frame = picam2.capture_array()

    # # Convertir a escala de grises
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # # Aplicar umbral para encontrar áreas con alta intensidad de luz
    # _, thresholded = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)

    # # Encontrar contornos en la imagen umbralizada
    # contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # for cnt in contours:
    #     # Obtener el centro de los contornos
    #     M = cv2.moments(cnt)
    #     if M['m00'] != 0:
    #         cx = int(M['m10']/M['m00'])
    #         cy = int(M['m01']/M['m00'])
    #         # Dibujar un círculo en el punto luminoso
    #         cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    # Tiempo actual
    current_time = time.time()

    # Calcular el framerate
    if prev_time != 0:
        fps = 1 / (current_time - prev_time)
        #cv2.putText(frame, f'FPS: {fps:.2f}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    prev_time = current_time

    print(fps)

    # Mostrar el frame
    #cv2.imshow('Frame', frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cerrar todas las ventanas
cv2.destroyAllWindows()
picam2.stop()