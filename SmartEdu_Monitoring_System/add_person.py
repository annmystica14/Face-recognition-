# add_person.py
import face_recognition
import cv2
import sqlite3
import os
import pickle

name = input("Name: ")
section = input("Section: ")
department = input("Department: ")

video = cv2.VideoCapture(0)
print("Capturing face... Press 's' to save.")

while True:
    ret, frame = video.read()
    cv2.imshow("Press S to save", frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
        break

video.release()
cv2.destroyAllWindows()

rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
face_locations = face_recognition.face_locations(rgb)
if face_locations:
    encoding = face_recognition.face_encodings(rgb, face_locations)[0]

    # Save to db
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people (name, section, department) VALUES (?, ?, ?)", (name, section, department))
    conn.commit()
    conn.close()

    # Save encoding
    try:
        with open('encodings/saved_encodings.pkl', 'rb') as f:
            encodings, names, infos = pickle.load(f)
    except:
        encodings, names, infos = [], [], []

    encodings.append(encoding)
    names.append(name)
    infos.append((section, department))

    with open('encodings/saved_encodings.pkl', 'wb') as f:
        pickle.dump((encodings, names, infos), f)

    print("✅ Face saved successfully.")
else:
    print("❌ No face detected!")
