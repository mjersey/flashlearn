import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import time


def open_dashboard():
    root.destroy()
    subprocess.run(["python", "dashboard.py"])


def open_sign_up():
    root.destroy()
    subprocess.run(["python", "sign_up.py"])


def open_forgot_password():
    root.withdraw()  # Hide the sign-in window instead of destroying it
    try:
        # Import the forgot_password module
        import forgot_password
        # Create an instance of the ForgotPasswordApp class
        fp = forgot_password.ForgotPasswordApp(root)
        # Run the application
        fp.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open forgot password window: {str(e)}")
        root.deiconify()  # Show the sign-in window again if there's an error


def update_lock_timer():
    """Update the lock timer display"""
    global lock_end_time

    if lock_end_time > 0:
        remaining = max(0, lock_end_time - time.time())
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)

        if remaining <= 0:
            # Time's up, reset everything
            reset_attempts()
        else:
            # Update the timer display
            attempt_label.config(text=f"Account locked. Try again in {minutes}:{seconds:02d}")
            # Schedule the next update
            root.after(1000, update_lock_timer)


def reset_attempts():
    """Reset the login attempts counter after a delay"""
    global login_attempts, lock_end_time

    login_attempts = 0
    lock_end_time = 0
    sign_in_btn.config(state="normal", bg="#003366")
    attempt_label.config(text="")

    # Re-enable the entry fields
    username_entry.config(state="normal")
    password_entry.config(state="normal")


def check_credentials(username, password):
    """Check if the credentials are valid and handle login attempts"""
    global login_attempts, lock_end_time

    # Ensure users.txt exists before reading
    if not os.path.exists("users.txt"):
        messagebox.showerror("Error", "No users found. Please sign up first.")
        return False

    with open("users.txt", "r") as file:
        users = file.readlines()
        found = False  # Flag to track if username is found

        for user in users:
            user_data = user.strip().split(",")
            user_data = [field.strip() for field in user_data if field.strip()]

            if len(user_data) < 3:
                continue

            stored_username, stored_email, stored_password = user_data[:3]

            if username.lower() == stored_username.strip().lower():
                found = True
                if password == stored_password:
                    # Check if the profile picture file exists for this user
                    profile_picture_path = ""  # Default profile picture if none set
                    profile_picture_file = f"profile_pictures/{username}.jpg"
                    if os.path.exists(profile_picture_file):
                        profile_picture_path = profile_picture_file

                    # Save logged-in user's credentials to current_user.txt
                    with open("current_user.txt", "w") as user_file:
                        user_file.write(f"{stored_username},{stored_email},{stored_password},{profile_picture_path}")

                    # Reset attempts on successful login
                    login_attempts = 0
                    return True
                else:
                    # Incorrect password
                    login_attempts += 1
                    remaining = 3 - login_attempts

                    if remaining > 0:
                        attempt_label.config(text=f"Attempts remaining: {remaining}")
                        messagebox.showerror("Error", f"Incorrect password. {remaining} attempts remaining.")
                    else:
                        # Lock the account for 30 seconds
                        lock_end_time = time.time() + 30  # 30 seconds from now

                        # Disable the sign-in button and entry fields
                        sign_in_btn.config(state="disabled", bg="#999999")
                        username_entry.config(state="disabled")
                        password_entry.config(state="disabled")

                        messagebox.showerror("Error", "Too many failed attempts. Account temporarily locked.")

                        # Start the timer
                        update_lock_timer()

                    return False

        # Username not found
        if not found:
            login_attempts += 1
            remaining = 3 - login_attempts

            if remaining > 0:
                attempt_label.config(text=f"Attempts remaining: {remaining}")
                messagebox.showerror("Error", f"Username not found. {remaining} attempts remaining.")
            else:
                # Lock the account for 30 seconds
                lock_end_time = time.time() + 30  # 30 seconds from now

                # Disable the sign-in button and entry fields
                sign_in_btn.config(state="disabled", bg="#999999")
                username_entry.config(state="disabled")
                password_entry.config(state="disabled")

                messagebox.showerror("Error", "Too many failed attempts. Account temporarily locked.")

                # Start the timer
                update_lock_timer()

            return False


def sign_in(event=None):
    """Handle sign-in process"""
    global lock_end_time

    # If account is locked, don't process sign-in
    if lock_end_time > time.time():
        return

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    # Ensure both fields are filled
    if not username or not password:
        messagebox.showerror("Error", "Both fields are required!")
        return

    # Check credentials - this function handles login attempts
    if check_credentials(username, password):
        open_dashboard()  # Open dashboard on successful login


def toggle_password():
    if show_password_var.get():
        password_entry.config(show="")  # Show password
    else:
        password_entry.config(show="*")  # Hide password


# Initialize variables
login_attempts = 0
lock_end_time = 0  # Unix timestamp when the lock ends

# Main window setup
root = tk.Tk()
root.title("FlashLearn - Sign In")

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set the window size
window_width = 900
window_height = 600

# Calculate the position to center the window
position_top = int((screen_height - window_height) / 2) - 50
position_right = int((screen_width - window_width) / 2)

# Set the geometry with the calculated position
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

root.configure(bg="white")
root.resizable(False, False)

# Left panel
left_frame = tk.Frame(root, width=400, height=600, bg="#FFF47F")
left_frame.pack(side="left", fill="both")

# FlashLearn Title
title_label = ttk.Label(left_frame, text="FlashLearn", font=("Poppins", 30, "bold"), background="#FFF47F")
title_label.pack(pady=(80, 5))

# Subtitle (Smaller)
subtitle_label = ttk.Label(
    left_frame, text="A Smart Flashcard System for Effective Studying",
    font=("Poppins", 12), background="#FFF47F", wraplength=350, justify="center"
)
subtitle_label.pack(pady=(0, 50))

# Display Image
try:
    img_path = "images/Sign In.png"
    if not os.path.exists(img_path):
        # Create a placeholder image if the file doesn't exist
        img = Image.new('RGB', (480, 480), color='#FFF47F')
    else:
        img = Image.open(img_path)

    img = img.resize((480, 480), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)

    img_label = tk.Label(left_frame, image=img_tk, bg="#FFF47F")
    img_label.image = img_tk  # Keep a reference
    img_label.pack(side="bottom", pady=20)
except Exception as e:
    print(f"Error loading image: {e}")
    # Create a placeholder label if image loading fails
    placeholder = tk.Label(left_frame, text="[Image Placeholder]",
                           font=("Poppins", 14), bg="#FFF47F", width=30, height=15)
    placeholder.pack(side="bottom", pady=20)

# Right Panel
right_frame = tk.Frame(root, width=400, height=600, bg="white")
right_frame.pack(side="right", fill="both", expand=True)
right_frame.pack_propagate(False)

# Sign In Title
sign_in_label = ttk.Label(right_frame, text="Sign In", font=("Poppins", 20, "bold"), background="white")
sign_in_label.pack(pady=(80, 5))

desc_label = ttk.Label(right_frame, text="Please enter your details below.", font=("Poppins", 12), background="white")
desc_label.pack()

# Username Label & Entry
username_label = ttk.Label(right_frame, text="Username:", font=("Poppins", 12), background="white")
username_label.pack(anchor="w", padx=60, pady=(25, 0))  # Align left
username_entry = ttk.Entry(right_frame, width=32, font=("Poppins", 12))
username_entry.pack(ipady=6, padx=60)
# Bind Enter key to sign_in function for username entry
username_entry.bind("<Return>", sign_in)

# Password Label & Entry
password_label = ttk.Label(right_frame, text="Password:", font=("Poppins", 12), background="white")
password_label.pack(anchor="w", padx=60, pady=(15, 0))  # Align left
password_entry = ttk.Entry(right_frame, width=32, font=("Poppins", 12), show="*")
password_entry.pack(ipady=6, padx=60)
# Bind Enter key to sign_in function for password entry
password_entry.bind("<Return>", sign_in)

# Show/Hide Password Checkbox
show_password_var = tk.BooleanVar()
show_password_checkbox = ttk.Checkbutton(
    right_frame, text="Show Password", variable=show_password_var, command=toggle_password
)
show_password_checkbox.pack(anchor="w", padx=60, pady=(5, 0))

# Forgot Password Link (Aligned with Text Fields)
forgot_password = ttk.Label(
    right_frame, text="Forgot Password?", font=("Poppins", 9, "underline"),
    foreground="blue", background="white", cursor="hand2"
)
forgot_password.pack(anchor="e", padx=60, pady=(5, 10))  # Right align
forgot_password.bind("<Button-1>", lambda e: open_forgot_password())  # Make it clickable

# Attempts remaining label
attempt_label = ttk.Label(right_frame, text="", font=("Poppins", 10), foreground="red", background="white")
attempt_label.pack(pady=(0, 10))

# Sign In Button
sign_in_btn = tk.Button(
    right_frame, text="Sign In", font=("Poppins", 12, "bold"),
    width=20, height=2, bg="#003366", fg="white", bd=0, cursor="hand2", command=sign_in
)
sign_in_btn.pack(pady=(5, 20))

# Sign Up Text (Non-clickable) & Clickable "Sign Up"
signup_frame = tk.Frame(right_frame, bg="white")
signup_frame.pack()

signup_text = tk.Label(signup_frame, text="Don't have an account?", font=("Poppins", 12), background="white")
signup_text.pack(side="left", padx=(0, 5))

signup_label = tk.Label(
    signup_frame, text="Sign Up", font=("Poppins", 12, "underline"),
    background="white", foreground="blue", cursor="hand2"
)
signup_label.pack(side="left")
signup_label.bind("<Button-1>", lambda e: open_sign_up())  # Clickable "Sign Up"

# Set focus to username entry when the application starts
username_entry.focus()

# Run the application
if __name__ == "__main__":
    root.mainloop()