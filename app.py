import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from database import create_db, add_flashcard, get_flashcards, get_random_flashcard

# Initialize database when the app starts
create_db()

# Function to show random flashcard
def show_random_flashcard():
    flashcard = get_random_flashcard()
    if flashcard:
        question, answer = flashcard[1], flashcard[2]
        question_label.config(text=question)
        answer_label.config(text="Answer: " + answer)

# Function to add new flashcard
def add_new_flashcard():
    question = question_entry.get()
    answer = answer_entry.get()
    if question and answer:
        add_flashcard(question, answer)
        messagebox.showinfo("Success", "Flashcard added!")
    else:
        messagebox.showwarning("Input Error", "Please provide both question and answer.")

# Tkinter GUI setup
root = tk.Tk()
root.title("FlashLearn - Flashcard System")
root.geometry("600x400")

# Flashcard Question Label
question_label = ttk.Label(root, text="Question will appear here", font=("Arial", 14))
question_label.pack(pady=20)

# Flashcard Answer Label (hidden until shown)
answer_label = ttk.Label(root, text="Answer will appear here", font=("Arial", 12))
answer_label.pack(pady=10)

# Show random flashcard button
show_btn = ttk.Button(root, text="Show Random Flashcard", command=show_random_flashcard)
show_btn.pack(pady=10)

# Inputs for adding new flashcards
question_entry = ttk.Entry(root, width=50, font=("Arial", 12))
question_entry.pack(pady=5)

answer_entry = ttk.Entry(root, width=50, font=("Arial", 12))
answer_entry.pack(pady=5)

# Add flashcard button
add_btn = ttk.Button(root, text="Add Flashcard", command=add_new_flashcard)
add_btn.pack(pady=20)

root.mainloop()
