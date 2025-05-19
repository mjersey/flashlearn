import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import ttk
import re
from otp_sender import generate_otp, send_otp_email
import verify

def open_sign_in():
    root.destroy()
    import sign_in

def open_verify(email, otp, username, password):
    """Opens OTP verification and hides sign-up window."""
    root.withdraw()  # Hide sign-up window
    verify.setup_verification(email, otp, username, password, root)

# Password validation
def strong_password(password):
    """Checks if the password meets the strong password criteria."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):  # At least one uppercase letter
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):  # At least one lowercase letter
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):  # At least one digit
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Special character
        return False, "Password must contain at least one special character."
    if len(password) > 50:
        return False, "Password must not exceed 50 characters."
    return True, ""

# Username validation
def is_valid_username(username):
    """Checks if the username is valid."""
    if len(username) > 25:
        return False, "Username must not exceed 25 characters."
    if not username.isalnum():  # Only letters and digits, no special characters
        return False, "Username must not contain special characters."
    return True, ""

def sign_up():
    """Handles sign-up logic, sends OTP, and opens verification."""
    username = username_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    # Validate username
    is_valid, username_message = is_valid_username(username)
    if not is_valid:
        messagebox.showerror("Error", username_message)
        return

    # Validate email
    if len(email) > 50:
        messagebox.showerror("Error", "Email must not exceed 50 characters.")
        return

    # Validate password
    is_strong, password_message = strong_password(password)
    if not is_strong:
        messagebox.showerror("Error", password_message)
        return

    # Check for existing username or email
    with open("users.txt", "r") as file:
        existing_users = file.readlines()

    # Check for duplicates (both username and email)
    for user in existing_users:
        user_data = user.strip().split(",")  # Split by commas
        if len(user_data) == 3:  # Only proceed if there are exactly 3 values (username, email, password)
            stored_username, stored_email, _ = user_data
            if username == stored_username:
                messagebox.showerror("Error", "Username already exists! Please choose another.")
                return
            if email == stored_email:
                messagebox.showerror("Error", "Email already registered! Please use a different email.")
                return
        else:
            print(f"Skipping malformed line: {user.strip()}")  # Optional: log invalid lines

    # If everything is valid, generate OTP and send it via email
    otp = generate_otp()
    send_otp_email(email, otp, username)

    messagebox.showinfo("Success", "Account created! Check your email for the OTP.")
    open_verify(email, otp, username, password)

def open_verify(email, otp, username, password):
    """Opens OTP verification and hides sign-up window."""
    root.withdraw()  # Hide sign-up window
    verify.setup_verification(email, otp, username, password, root)

def toggle_password():
    """Toggles password visibility."""
    password_entry.config(show="" if show_password_var.get() else "*")

root = tk.Tk()
root.title("FlashLearn - Sign Up")

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Window size and position
window_width, window_height = 900, 600
position_top = int((screen_height - window_height) / 2) - 50
position_right = int((screen_width - window_width) / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

root.configure(bg="white")
root.resizable(False, False)

# Left panel
left_frame = tk.Frame(root, width=400, height=600, bg="#FFF47F")
left_frame.pack(side="left", fill="both")

# FlashLearn Title
ttk.Label(left_frame, text="FlashLearn", font=("Poppins", 30, "bold"), background="#FFF47F").pack(pady=(80, 5))

# Subtitle
ttk.Label(left_frame, text="A Smart Flashcard System for Effective Studying",
          font=("Poppins", 12), background="#FFF47F", wraplength=350, justify="center").pack(pady=(0, 50))

# Load and display image
img = Image.open(r"C:\Users\MJ\PycharmProjects\pythonProject\FlashLearn\images\Sign In.png")
img = img.resize((480, 480), Image.Resampling.LANCZOS)
img_tk = ImageTk.PhotoImage(img)
tk.Label(left_frame, image=img_tk, bg="#FFF47F").pack(side="bottom", pady=20)

# Right panel
right_frame = tk.Frame(root, width=400, height=600, bg="white")
right_frame.pack(side="right", fill="both", expand=True)
right_frame.pack_propagate(False)

# Sign Up UI
ttk.Label(right_frame, text="Sign Up", font=("Poppins", 20, "bold"), background="white").pack(pady=(80, 5))
ttk.Label(right_frame, text="Please enter your details below.", font=("Poppins", 12), background="white").pack()

# Username
ttk.Label(right_frame, text="Username:", font=("Poppins", 12), background="white").pack(anchor="w", padx=60, pady=(25, 0))
username_entry = ttk.Entry(right_frame, width=32, font=("Poppins", 12))
username_entry.pack(ipady=6, padx=60)

# Email
ttk.Label(right_frame, text="Email:", font=("Poppins", 12), background="white").pack(anchor="w", padx=60, pady=(25, 0))
email_entry = ttk.Entry(right_frame, width=32, font=("Poppins", 12))
email_entry.pack(ipady=6, padx=60)

# Password
ttk.Label(right_frame, text="Password:", font=("Poppins", 12), background="white").pack(anchor="w", padx=60, pady=(15, 0))
password_entry = ttk.Entry(right_frame, width=32, font=("Poppins", 12), show="*")
password_entry.pack(ipady=6, padx=60)

# Show/Hide Password
show_password_var = tk.BooleanVar()
ttk.Checkbutton(right_frame, text="Show Password", variable=show_password_var, command=toggle_password).pack(anchor="w", padx=60, pady=(5, 0))

# Sign Up Button
tk.Button(right_frame, text="Sign Up", font=("Poppins", 12, "bold"),
          width=20, height=2, bg="#003366", fg="white", bd=0, cursor="hand2", command=sign_up).pack(pady=(20, 20))

# Sign In Option
signin_frame = tk.Frame(right_frame, bg="white")
signin_frame.pack()
tk.Label(signin_frame, text="Already have an account?", font=("Poppins", 12), background="white").pack(side="left", padx=(0, 5))
signin_label = tk.Label(signin_frame, text="Sign In", font=("Poppins", 12, "underline"),
                         background="white", foreground="blue", cursor="hand2")
signin_label.pack(side="left")
signin_label.bind("<Button-1>", lambda e: open_sign_in())

root.mainloop()
