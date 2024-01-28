# OBS: Alguns dados foram documentados para consultas futuras
import time
import pyfirmata
from pynput import keyboard
import cv2
import mediapipe as mp


# const int enPin=8
# const int stepXPin = 2 # X.STEP
# const int dirXPin = 5 # X.DIR
stepYPin = 3 # Y.STEP
dirYPin = 6 # Y.DIR
# const int stepZPin = 4 # Z.STEP
# const int dirZPin = 7 # Z.DIR

stepPin=stepYPin
dirPin=dirYPin

board = pyfirmata.Arduino('COM10')

print('Running')

# Configurações =======================
engine = board.get_pin('d:6:p')
engineDigitalPin = board.digital[stepPin]
# =====================================
mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
mp_drawing_styles=mp.solutions.hands
# =====================================

def screwInDeg(degs):
    steps = (degs * 800) / 360
    HEIGH = True
    LOW = False
    delay = 0
    # board.digital[stepPin].write(HEIGH)

    if degs < 0:
        engine.write(HEIGH)
    else:
        engine.write(LOW)

    for i in range(abs(int(steps))):
        engineDigitalPin.write(HEIGH)
        time.sleep(delay)
        engineDigitalPin.write(LOW)
        time.sleep(delay)


# def on_press(key):
#     # Based on the key press we handle the way the key gets logged to the in memory string.
#     # Read more on the different keys that can be logged here:
#     # https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard
#     degsStep = 100
#     if key == keyboard.KeyCode.from_char('s'):
#         screwInDeg(degsStep)
#     elif key == keyboard.KeyCode.from_char('d'):
#         screwInDeg(-degsStep)

# with keyboard.Listener(on_press=on_press) as listener:
#     listener.join()

# while True:
#     screwInDeg(-180)
#     # time.sleep(0.2)
#     screwInDeg(180)
        

def draw_square_around_hand(image, landmarks):
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0

    for landmark in landmarks.landmark:
        x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    # Calcula o centro da mão
    center_x, center_y = (min_x + max_x) // 2, (min_y + max_y) // 2

    # Calcula o tamanho do lado do quadrado (o máximo entre a largura e altura)
    side_length = max(max_x - min_x, max_y - min_y)

    # Calcula as novas coordenadas para desenhar um quadrado ao redor da mão
    new_min_x, new_min_y = center_x - side_length // 2, center_y - side_length // 2
    new_max_x, new_max_y = center_x + side_length // 2, center_y + side_length // 2

    cv2.rectangle(image, (new_min_x, new_min_y), (new_max_x, new_max_y), (0, 255, 0), 2)


def boundary_limits_and_move_engine(image, landmarks):
    min_hand_x, min_hand_y, max_hand_x, max_hand_y = float('inf'), float('inf'), 0, 0
    image_height, image_width, _ = img.shape
    padding_limit = 100
    engine_steps = 10

    # Normalmente é azul, mas será vermelho se o limite for quebrado pelo limite da mão
    square_color = (255, 0, 0)

    for landmark in landmarks.landmark:
        x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
        min_hand_x = min(min_hand_x, x)
        min_hand_y = min(min_hand_y, y)
        max_hand_x = max(max_hand_x, x)
        max_hand_y = max(max_hand_y, y)


    hand_is_left_boundary = min_hand_x <= padding_limit
    hand_is_right_boundary = max_hand_x >= image_width - padding_limit

    if(hand_is_left_boundary or hand_is_right_boundary):
        square_color = (0, 0, 255)

    cv2.rectangle(image, (padding_limit, padding_limit), (image_width - padding_limit, image_height - padding_limit), square_color, 2)

    if hand_is_left_boundary:
        screwInDeg(-engine_steps)
    elif hand_is_right_boundary:
        screwInDeg(engine_steps)


webcam = cv2.VideoCapture(0)
hands = mp_hands.Hands()
while webcam.isOpened():
    success, img = webcam.read()

    # Aplica o trackeamento ao modelo
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Desenhos e ações
    if results.multi_hand_landmarks:
       for hand_landmarks in results.multi_hand_landmarks:
           draw_square_around_hand(img, hand_landmarks)
           boundary_limits_and_move_engine(img, hand_landmarks)
           #mp_drawing.draw_landmarks(img,hand_landmarks,connections=mp_hands.HAND_CONNECTIONS)
    

    cv2.imshow('Tracker', img)
    if cv2.waitKey(5) & 0xFF == ord("q"):
        break
webcam.release()
cv2.destroyAllWindows()