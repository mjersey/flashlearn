import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import threading
import re  # Regular expression for validating OTP input

from PIL import Image, ImageTk
from otp_sender import generate_otp, send_otp_email  # Import OTP functions


def open_sign_in(verify_window):
    """Opens the dashboard and closes OTP verification."""
    verify_window.withdraw()
    os.system('python sign_in.py')


def setup_verification(email, otp, username, password, signup_window):
    """Sets up OTP verification window."""
    if signup_window:
        signup_window.withdraw()

    verify_window = tk.Toplevel()
    verify_window.title("OTP Verification")
    verify_window.geometry("900x600")
    verify_window.configure(bg="white")
    verify_window.resizable(False, False)

    # --- LEFT FRAME (Yellow background + Image + Text) ---
    left_frame = tk.Frame(verify_window, width=400, height=600, bg="#FFF47F")
    left_frame.pack(side="left", fill="both")

    # Vertically center the content of the left frame
    left_frame.grid_rowconfigure(0, weight=1)
    left_frame.grid_rowconfigure(1, weight=1)
    left_frame.grid_rowconfigure(2, weight=1)

    # Title with adjusted padding
    ttk.Label(left_frame, text="FlashLearn", font=("Poppins", 30, "bold"),
              background="#FFF47F").grid(row=0, pady=(70, 5))

    # Load and display image
    try:
        img = Image.open(r"C:\Users\MJ\PycharmProjects\pythonProject\FlashLearn\images\Sign In.png")
        img = img.resize((450, 450), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        img_label = tk.Label(left_frame, image=img_tk, bg="#FFF47F")
        img_label.image = img_tk  # Keep a reference to avoid garbage collection
        img_label.grid(row=2, pady=20)
    except Exception as e:
        print(f"Image loading error: {e}")
        ttk.Label(left_frame, text="(Image Not Found)", font=("Poppins", 14, "italic"),
                  background="#FFF47F", foreground="red").grid(row=2, pady=20)

    # --- RIGHT FRAME (White background + OTP Entry + Buttons) ---
    right_frame = tk.Frame(verify_window, width=400, height=600, bg="white")
    right_frame.pack(side="right", fill="both", expand=True)
    right_frame.pack_propagate(False)

    # Title
    ttk.Label(right_frame, text="OTP Code", font=("Poppins", 20, "bold"),
              background="white").pack(pady=(80, 5))

    ttk.Label(right_frame, text="Check your email for 6-digit verification code.",
              font=("Poppins", 12), background="white").pack()

    # Enter Code Label
    ttk.Label(right_frame, text="Enter Code:", font=("Poppins", 12), background="white").pack(anchor="w", padx=60,
                                                                                              pady=(25, 0))

    # OTP Entry with validation (limit to 6 digits)
    otp_var = tk.StringVar()

    # Validate function to allow only 6 digits
    def validate_input(new_input):
        if len(new_input) > 6:
            return False
        return bool(re.match(r'^\d*$', new_input))  # Only allow digits

    validate_command = (verify_window.register(validate_input), '%P')  # Validate against new input
    otp_entry = ttk.Entry(right_frame, width=32, font=("Poppins", 12),
                          textvariable=otp_var, validate="key", validatecommand=validate_command, justify="center")
    otp_entry.pack(ipady=6, padx=60, pady=10)

    def verify_otp():
        """Verifies OTP and opens dashboard if correct."""
        entered_otp = otp_var.get().strip()
        if entered_otp == otp:
            messagebox.showinfo("Success", "OTP Verified! Your account is now active.")
            with open("users.txt", "a") as file:
                file.write(f"{username},{email},{password}\n")
            open_sign_in(verify_window)
        else:
            messagebox.showerror("Error", "Incorrect OTP. Please try again.")

    # Timer and Button Frame
    button_frame = tk.Frame(right_frame, bg="white")
    button_frame.pack(pady=10)

    # Timer Label (now placed under the text field)
    timer_label = ttk.Label(
        button_frame, text="Resend in: 120s", font=("Poppins", 10),
        background="white", foreground="red"
    )
    timer_label.pack(pady=(10, 10))

    # Verify Button
    verify_btn = tk.Button(
        button_frame, text="Verify", font=("Poppins", 12, "bold"),
        bg="#003366", fg="white", width=15, command=verify_otp
    )
    verify_btn.pack(pady=10)

    # Resend Button
    resend_btn = tk.Button(
        button_frame, text="Resend", font=("Poppins", 12, "bold"),
        bg="white", fg="gray", width=15, command=lambda: resend_otp()
    )
    resend_btn.pack(pady=5)

    def resend_otp():
        """Resends OTP and starts cooldown timer."""
        nonlocal otp
        otp = generate_otp()
        send_otp_email(email, otp)
        messagebox.showinfo("Resent", "A new OTP has been sent to your email.")

        # Disable Resend button and reset style
        resend_btn.config(state="disabled", fg="gray")
        countdown(120)

    def countdown(seconds):
        """Handles cooldown timer for the resend button."""

        def update_timer():
            for sec in range(seconds, 0, -1):
                time.sleep(1)
                if not timer_label.winfo_exists():
                    return
                timer_label.config(text=f"Resend in: {sec}s")

            if timer_label.winfo_exists():
                timer_label.config(text="Resend")
                resend_btn.config(state="normal", fg="black")

        threading.Thread(target=update_timer, daemon=True).start()

    # Initially disable Resend button, start countdown
    resend_btn.config(state="disabled", fg="gray")
    countdown(120)

    verify_window.mainloop()
