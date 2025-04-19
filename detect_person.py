from ultralytics import YOLO
import cv2
import mediapipe as mp
import math
import mysql.connector
from datetime import datetime
import uuid
import time
import random
import tkinter as tk
import threading
import pygame
import os
import glob
from PIL import Image, ImageDraw, ImageFont

# Generate a unique session ID
session_id = str(uuid.uuid4())[:8]

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Mediapipe face mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5)

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="activity_logs"
)
cursor = conn.cursor()

# Open webcam
cap = cv2.VideoCapture(0)

# Joke messages for yawning and roasting messages for phone use
joke_messages = [
"That yawn had more effort than your entire day.",
"You're exhausting to watch... and you’re not even moving.",
"Yawning again? You contribute less than background noise.",
"I’ve seen screensavers do more work than you.",
"Your energy is so low it’s in negative.",
"You look like ambition gave up on you.",
"That wasn’t a yawn, that was a cry for help.",
"Even your coffee is asking for a refund.",
"Your presence is as dynamic as a paused YouTube video.",
"One more yawn and we’re submitting your resignation.",
"Every time you yawn, your goals move further away.",
"You’re in a competition with a potato—and losing.",
"I’d say ‘rise and grind,’ but clearly you chose ‘slump and whine.’",
"Your dedication is giving ‘bare minimum’ a bad name.",
"Blink once for motivation. Never mind, too late."

]

roast_messages = [
    "Put the phone down, influencer. No one's watching.",
    "Your productivity just left the chat.",
    "Instagram won't pay your rent.",
    "Unlock purpose, not your phone.",
    "Was that scroll worth it?"
]

meme_captions = [
"That yawn worked harder than I did all day.",
"Official mascot of Monday motivation — failure.",
"Peak performance right here, folks.",
"Grinding… but only my teeth during naps.",
"This is what dreams (and deadlines missed) look like.",
"When effort exits the body.",
"Running on 1 bar of energy and 0 shame.",
"Employee of the yawn.",
"Just here so I don’t get fined… or fired.",
"This is my ‘do not disturb’ face.",
"Still buffering… like my career.",
"Corporate burnout? I call it lifestyle.",
"This meeting could’ve been a nap.",
"Productivity called — I let it go to voicemail.",
"Please direct all questions to my empty gaze.",
"Daydreaming of a job I don’t have to do.",
"Woke up, showed up, zoned out.",
"Delivering yawn vibes since 9:01 AM.",
"This is what overachieving laziness looks like.",
"Working hard… hardly working… barely awake."
    
]

# Sound setup
pygame.mixer.init()
def play_sound(sound_path="ding.mp3"):
    try:
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Sound error: {e}")

# Popup notification
def popup_message(title, message, sound_path="ding.mp3"):
    def show():
        play_sound(sound_path)
        win = tk.Tk()
        win.title(title)
        win.geometry("500x120+500+300")
        win.configure(bg="#fff8f0")
        win.overrideredirect(True)
        label_title = tk.Label(win, text=title, font=("Helvetica", 16, "bold"), bg="#fff8f0", fg="#e63946")
        label_msg = tk.Label(win, text=message, font=("Segoe UI", 12), wraplength=480, justify="center", bg="#fff8f0", fg="#1d3557")
        label_title.pack(pady=(20, 5))
        label_msg.pack(pady=(0, 20))
        win.lift()
        win.attributes('-topmost', True)
        win.after(3000, win.destroy)
        win.mainloop()
    threading.Thread(target=show).start()

def trigger_joke():
    popup_message("😴 Yawn Joke Incoming!", random.choice(joke_messages), sound_path="joke.mp3")

def trigger_roast():
    popup_message("📱 Phone Roast Alert!", random.choice(roast_messages), sound_path="roast.mp3")

def euclidean(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def is_yawning(landmarks):
    upper_lip = landmarks[13]
    lower_lip = landmarks[14]
    return euclidean(upper_lip, lower_lip) > 0.05

user_status = {
    'yawn_count': 0,
    'joke_sent': False,
    'phone_start': None,
    'roast_sent': False
}

yawn_start_time = None
snapshot_dir = "snapshots"
os.makedirs(snapshot_dir, exist_ok=True)

# Add meme caption to image
def save_yawn_snapshot(frame):
    meme_text = random.choice(meme_captions)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{snapshot_dir}/yawn_{timestamp}.jpg"
    
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, 32)
    except:
        font = ImageFont.load_default()
    text_position = (20, 20)
    draw.text(text_position, meme_text, font=font, fill=(255, 0, 0))
    image.save(filepath)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_mp = face_mesh.process(frame_rgb)
    results_yolo = model(frame)[0]

    yawning_now = False
    phone_count = 0

    phones = []
    persons = []
    for box in results_yolo.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if label == 'cell phone':
            phones.append((x1, y1, x2, y2))
        if label == 'person':
            persons.append((x1, y1, x2, y2))

    # Check phone usage based on overlap with persons
    for px1, py1, px2, py2 in persons:
        for fx1, fy1, fx2, fy2 in phones:
            if fx1 < px2 and fx2 > px1 and fy1 < py2 and fy2 > py1:
                phone_count = 1
                break

    if results_mp.multi_face_landmarks:
        for face_landmarks in results_mp.multi_face_landmarks:
            if is_yawning(face_landmarks.landmark):
                if yawn_start_time is None:
                    yawn_start_time = time.time()
                elif 2 <= (time.time() - yawn_start_time):
                    yawning_now = True
                    save_yawn_snapshot(frame)
            else:
                yawn_start_time = None

    yawning_count = 1 if yawning_now else 0

    if yawning_count > 0:
        user_status['yawn_count'] += 1
        if user_status['yawn_count'] >= 1 and not user_status['joke_sent']:
            trigger_joke()
            user_status['joke_sent'] = True
    else:
        user_status['yawn_count'] = 0
        user_status['joke_sent'] = False

    if phone_count > 0:
        if user_status['phone_start'] is None:
            user_status['phone_start'] = time.time()
        elif not user_status['roast_sent'] and (time.time() - user_status['phone_start']) >= 2:
            trigger_roast()
            user_status['roast_sent'] = True
    else:
        user_status['phone_start'] = None
        user_status['roast_sent'] = False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO detections (timestamp, phone_users, yawning_users, session_id) VALUES (%s, %s, %s, %s)",
        (now, phone_count, yawning_count, session_id)
    )
    conn.commit()

    cv2.putText(frame, f"😴 Yawning: {yawning_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
    cv2.putText(frame, f"📱 Phone Detected: {phone_count}", (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    cv2.imshow("Real-Time Detection", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()