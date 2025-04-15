import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
import random
import time

# Mediapipe тохиргоо
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

# Хуруу тоолох функц
def count_fingers(hand_landmarks, hand_label):
    count = 0
    tips = [8, 12, 16, 20]
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    if hand_label == "Right":
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            count += 1
    else:
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
            count += 1
    return count

# UI хэсэг 
root = tk.Tk()
root.title("Гарын дохиогоор тоо сурах")
root.attributes('-fullscreen', True)
root.configure(bg="lightpink")

# Дээд хэсэг (Оноо, Түвшин)
top_frame = tk.Frame(root, bg = "lightpink")
top_frame.pack(side="top", fill="x", pady=10)

label_score = tk.Label(top_frame, text="Оноо: 0", font=("Cambria", 20), bg="lightpink")
label_score.pack(side="right", padx=20)

label_level = tk.Label(top_frame, text="Түвшин: 1", font=("Cambria", 20), bg="lightpink")
label_level.pack(side="right")

# Асуулт, хариу
label_question = tk.Label(root, text="", font=("Cambria", 36, "bold"), bg="lightpink")
label_question.pack(pady=20)

label_feedback = tk.Label(root, text="", font=("Cambria", 28), fg="blue", bg="lightpink")
label_feedback.pack(pady=10)

# Камерын дүрс
canvas = tk.Label(root, bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

# Хурууны тоо ба секунд
label_real_time = tk.Label(
    root, text="Баруун гар: 0  Зүүн гар: 0  ⏳ Үлдсэн: 5 сек",
    font=("Cambria", 20), bg="lightpink", fg="darkblue"
)
label_real_time.pack(pady=20)

# Тоглоомын хувьсагчид
current_answer = 0
score = 0
level = 1
start_time = time.time()
already_answered = False

def clear_feedback():
    label_feedback.config(text="", fg="blue")

def generate_question():
    global current_answer, level, start_time, already_answered
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    current_answer = a + b
    label_question.config(text=f"{a} + {b} = ?")
    level = score // 5 + 1
    label_score.config(text=f"Оноо: {score}")
    label_level.config(text=f"Түвшин: {level}")
    start_time = time.time()
    already_answered = False

    if level > 1 and score % 5 == 0:
        label_feedback.config(text=f"Түвшин {level} ахив!", fg="orange")
        root.after(2000, clear_feedback)
    else:
        clear_feedback()

def update_frame():
    global score, already_answered
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    hand1_fingers = 0
    hand2_fingers = 0
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label
            if label == "Right":
                hand1_fingers = count_fingers(hand_landmarks, label)
            elif label == "Left":
                hand2_fingers = count_fingers(hand_landmarks, label)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Үлдсэн хугацаа
    elapsed_time = time.time() - start_time
    remaining = max(0, int(5 - elapsed_time))
    label_real_time.config(
        text=f"Баруун гар: {hand1_fingers}  Зүүн гар: {hand2_fingers}   Хугацаа: {remaining} сек"
    )

    # Хариулт шалгах
    if not already_answered:
        if hand1_fingers + hand2_fingers == current_answer and elapsed_time <= 5:
            label_feedback.config(text="Зөв хариулт! ", fg="green")
            score += 1
            already_answered = True
            root.after(1500, generate_question)
        elif elapsed_time > 5:
            label_feedback.config(text="Буруу хариулт! ", fg="red")
            score = max(0, score - 1)
            already_answered = True
            root.after(1500, generate_question)

    # Камерын дүрсийг харуулах
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.imgtk = imgtk
    canvas.configure(image=imgtk)

    root.after(30, update_frame)

# Тоглоом эхлүүлэх
generate_question()
update_frame()
root.mainloop()
cap.release()
