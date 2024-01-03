import cv2
import numpy as np
from picamera2 import Picamera2
import time

fpsCounter = 0

# Inicializar Picamera2
picam2 = Picamera2()

# Configuraciones de la cámara
camera_config = picam2.create_video_configuration(main={"format": "BGR888", "size": (900, 900)}, raw={"format": "SRGGB10", "size": (1332, 990)})
#camera_config = picam2.create_video_configuration()
picam2.configure(camera_config)
# Establecer el framerate
picam2.set_controls({"FrameRate": 120})


# Iniciar la cámara
picam2.start()

prev_time = 0

startTime = time.time()


while True:
    # Capturar el frame
    frame = picam2.capture_array("main")
    #frameLowRes = picam2.capture_array("lores")

    # Convertir a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicar umbral para encontrar áreas con alta intensidad de luz
    _, thresholded = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)

    # Encontrar contornos en la imagen umbralizada
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        # Obtener el centro de los contornos
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            print(cx, cy)
            # Dibujar un círculo en el punto luminoso
            #cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    # Tiempo actual
    current_time = time.time()

    # Calcular el framerate
    if prev_time != 0:
        fps = 1 / (current_time - prev_time)
        fpsCounter += 1
        print(fpsCounter/(current_time-startTime))
        #cv2.putText(frame, f'FPS: {fps:.2f}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    prev_time = current_time

    # Mostrar el frame
    #cv2.imshow('FrameLowRes', frameLowRes)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cerrar todas las ventanas
cv2.destroyAllWindows()
picam2.stop()