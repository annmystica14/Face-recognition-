import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import cv2
import face_recognition
import pickle
import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox
import numpy as np
from attendance.attendance_utils import mark_attendance


def on_face_recognition(face_encoding, name, ax):
    subject_code = get_current_subject_code()
    if subject_code:
        mark_attendance(name, subject_code)
        ax.text(50, 50, f"Attendance marked for {name} in {subject_code}", color='white', fontsize=12, bbox=dict(facecolor='black', alpha=0.5))


def get_current_subject_code():
    from datetime import datetime
    now = datetime.now()
    hour = now.hour
    if 9 <= hour < 10:
        return "MATH101"
    elif 10 <= hour < 11:
        return "PHY102"
    elif 11 <= hour < 12:
        return "CHEM103"
    else:
        return "GEN000"


def init_db():
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS people
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT,
                       section TEXT,
                       department TEXT)''')
    conn.commit()
    conn.close()


def update_profile(old_name, new_name, section, department):
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE people SET name=?, section=?, department=? WHERE name=?", (new_name, section, department, old_name))
    conn.commit()
    conn.close()


def remove_profile(name):
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM people WHERE name=?", (name,))
    conn.commit()
    conn.close()


def add_profile(name, section, department):
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people (name, section, department) VALUES (?, ?, ?)", (name, section, department))
    conn.commit()
    conn.close()


def get_profile(name):
    conn = sqlite3.connect('database/faces.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, section, department FROM people WHERE name=?", (name,))
    profile = cursor.fetchone()
    conn.close()
    return profile


def load_encodings():
    try:
        with open('encodings.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def save_encodings(encodings):
    with open('encodings.pkl', 'wb') as f:
        pickle.dump(encodings, f)


def register_action(event):
    root = tk.Tk()
    root.withdraw()

    name = simpledialog.askstring("Register Profile", "Enter name:")
    if not name:
        messagebox.showinfo("No Name", "No name entered!")
        return

    section = simpledialog.askstring("Register Profile", "Enter section:")
    department = simpledialog.askstring("Register Profile", "Enter department:")

    add_profile(name, section, department)

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        messagebox.showinfo("Error", "Failed to capture image from camera.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_frame)
    encodings_in_frame = face_recognition.face_encodings(rgb_frame, boxes)

    if encodings_in_frame:
        encodings = load_encodings()
        encodings[name] = encodings_in_frame[0]
        save_encodings(encodings)
        messagebox.showinfo("Profile Registered", f"Profile for {name} registered successfully!")
    else:
        messagebox.showinfo("Error", "No face detected. Try again.")


def edit_remove_profile(event):
    root = tk.Tk()
    root.withdraw()

    name_to_edit = simpledialog.askstring("Edit/Remove Profile", "Enter name to edit/remove:")
    if not name_to_edit:
        messagebox.showinfo("No Name", "No name entered!")
        return

    conn = sqlite3.connect("database/faces.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM people WHERE name=?", (name_to_edit,))
    profile = cursor.fetchone()
    conn.close()

    if not profile:
        messagebox.showinfo("Profile Not Found", f"No profile found for {name_to_edit}.")
        return

    action = simpledialog.askstring("Edit/Remove Profile", f"Would you like to edit or remove {name_to_edit}? (edit/remove)")

    if action == 'edit':
        new_name = simpledialog.askstring("Edit Profile", f"Enter new name for {name_to_edit}:")
        section = simpledialog.askstring("Edit Profile", "Enter section:")
        department = simpledialog.askstring("Edit Profile", "Enter department:")
        update_profile(name_to_edit, new_name, section, department)
        messagebox.showinfo("Success", f"Profile for {name_to_edit} updated to {new_name}.")
    elif action == 'remove':
        remove_profile(name_to_edit)
        encodings = load_encodings()
        if name_to_edit in encodings:
            del encodings[name_to_edit]
            save_encodings(encodings)
        messagebox.showinfo("Success", f"Profile for {name_to_edit} removed.")
    else:
        messagebox.showinfo("Invalid Action", "Please enter 'edit' or 'remove'.")


def view_profile_action(event):
    name_to_view = simpledialog.askstring("View Profile", "Enter the name of the person to view the profile:")
    if name_to_view:
        profile = get_profile(name_to_view)
        if profile:
            name, section, department = profile
            messagebox.showinfo("Profile Info", f"Name: {name}\nSection: {section}\nDepartment: {department}")
        else:
            messagebox.showinfo("Profile Not Found", f"No profile found for {name_to_view}.")


def mark_attendance_button_action(event):
    global frame, known_encodings, known_names

    subject_code = get_current_subject_code()
    if not subject_code:
        tk.Tk().withdraw()
        messagebox.showinfo("Non-working Hour", "Attendance cannot be marked outside of class hours.")
        return

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    marked_anyone = False
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else -1

        if best_match_index >= 0 and matches[best_match_index]:
            name = known_names[best_match_index]
            mark_attendance(name, subject_code)
            marked_anyone = True

    if marked_anyone:
        tk.Tk().withdraw()
        messagebox.showinfo("Success", f"Attendance marked for recognized faces in {subject_code}.")
    else:
        tk.Tk().withdraw()
        messagebox.showinfo("No Match", "No known faces were recognized.")


def close_program(event):
    global running
    running = False


init_db()

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.45)

register_button_ax = fig.add_axes([0.72, 0.05, 0.25, 0.05])
edit_remove_button_ax = fig.add_axes([0.72, 0.12, 0.25, 0.05])
view_profile_button_ax = fig.add_axes([0.72, 0.19, 0.25, 0.05])
mark_attendance_button_ax = fig.add_axes([0.72, 0.26, 0.25, 0.05])
close_button_ax = fig.add_axes([0.72, 0.33, 0.25, 0.05])

register_button = Button(register_button_ax, 'Register', color='lightgoldenrodyellow', hovercolor='orange')
edit_remove_button = Button(edit_remove_button_ax, 'Edit/Remove', color='lightblue', hovercolor='skyblue')
view_profile_button = Button(view_profile_button_ax, 'View Profile', color='lightgreen', hovercolor='lime')
mark_attendance_button = Button(mark_attendance_button_ax, 'Mark Attendance', color='lightpink', hovercolor='pink')
close_button = Button(close_button_ax, 'Close', color='lightcoral', hovercolor='red')

register_button.on_clicked(register_action)
edit_remove_button.on_clicked(edit_remove_profile)
view_profile_button.on_clicked(view_profile_action)
mark_attendance_button.on_clicked(mark_attendance_button_action)
close_button.on_clicked(close_program)

cap = cv2.VideoCapture(0)
encodings = load_encodings()
known_names = list(encodings.keys())
known_encodings = list(encodings.values())

clicked_position = None
running = True
frame = None

def on_click(event):
    global clicked_position
    if event.xdata and event.ydata:
        clicked_position = (int(event.xdata), int(event.ydata))

fig.canvas.mpl_connect('button_press_event', on_click)

while running:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    ax.clear()
    ax.imshow(rgb)
    ax.axis('off')

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else -1
        if best_match_index >= 0 and matches[best_match_index]:
            name = known_names[best_match_index]

        color = 'green' if name != "Unknown" else 'red'
        ax.add_patch(plt.Rectangle((left, top), right - left, bottom - top, fill=False, color=color, linewidth=2))

        show_data = False
        if clicked_position:
            x, y = clicked_position
            if left <= x <= right and top <= y <= bottom:
                show_data = True

        if show_data and name != "Unknown":
            profile = get_profile(name)
            if profile:
                name, section, department = profile
                label = f"{name}, {section}, {department}"
            else:
                label = name
            ax.text(left, top - 10, label, color=color, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        elif show_data:
            ax.text(left, top - 10, name, color=color, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

    clicked_position = None
    plt.pause(0.1)

cap.release()
plt.close(fig)