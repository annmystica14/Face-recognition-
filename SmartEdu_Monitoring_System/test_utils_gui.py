# test_utils_gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from utils.db_utils import init_db, add_profile, update_profile, remove_profile, get_profile
from utils.encoding_utils import load_encodings, save_encodings
import numpy as np

# Initialize DB
init_db()

def add_profile_gui():
    name = simpledialog.askstring("Add Profile", "Enter name:")
    if not name: return
    section = simpledialog.askstring("Add Profile", "Enter section:")
    department = simpledialog.askstring("Add Profile", "Enter department:")
    add_profile(name, section, department)
    messagebox.showinfo("Done", f"Profile for {name} added!")

def edit_profile_gui():
    old_name = simpledialog.askstring("Edit Profile", "Enter current name:")
    if not old_name: return
    new_name = simpledialog.askstring("Edit Profile", "Enter new name:")
    section = simpledialog.askstring("Edit Profile", "Enter new section:")
    department = simpledialog.askstring("Edit Profile", "Enter new department:")
    update_profile(old_name, new_name, section, department)
    messagebox.showinfo("Done", f"Updated {old_name} → {new_name}")

def remove_profile_gui():
    name = simpledialog.askstring("Remove Profile", "Enter name to remove:")
    if not name: return
    remove_profile(name)
    messagebox.showinfo("Removed", f"{name} has been removed.")

def view_profile_gui():
    name = simpledialog.askstring("View Profile", "Enter name to search:")
    if not name: return
    profile = get_profile(name)
    if profile:
        messagebox.showinfo("Profile Info", f"Name: {profile[0]}\nSection: {profile[1]}\nDepartment: {profile[2]}")
    else:
        messagebox.showinfo("Not Found", f"No profile found for {name}")

def show_all_encodings_gui():
    encs = load_encodings()
    names = list(encs.keys())
    messagebox.showinfo("Encodings", "\n".join(names) if names else "No encodings found.")

def add_dummy_encoding_gui():
    encs = load_encodings()
    name = simpledialog.askstring("Dummy Encoding", "Enter name to add dummy encoding:")
    if not name: return
    encs[name] = np.random.rand(128)
    save_encodings(encs)
    messagebox.showinfo("Done", f"Dummy encoding added for {name}.")

# Build GUI
root = tk.Tk()
root.title("DB / Encoding Utility")
root.geometry("300x350")

tk.Button(root, text="Add Profile", command=add_profile_gui, width=25).pack(pady=5)
tk.Button(root, text="Edit Profile", command=edit_profile_gui, width=25).pack(pady=5)
tk.Button(root, text="Remove Profile", command=remove_profile_gui, width=25).pack(pady=5)
tk.Button(root, text="View Profile", command=view_profile_gui, width=25).pack(pady=5)

tk.Label(root, text="--- Encoding Tools ---").pack(pady=10)
tk.Button(root, text="Show All Encodings", command=show_all_encodings_gui, width=25).pack(pady=5)
tk.Button(root, text="Add Dummy Encoding", command=add_dummy_encoding_gui, width=25).pack(pady=5)

tk.Button(root, text="Exit", command=root.destroy, width=25, fg="red").pack(pady=20)

root.mainloop()
