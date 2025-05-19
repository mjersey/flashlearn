import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
import threading
import time
from PIL import Image, ImageTk
from otp_sender import generate_otp, send_otp_email


class ForgotPasswordApp:
    def __init__(self, root=None):
        # If root is provided, this is being called from another window
        self.parent_window = root

        # Create a new window if not called from another window
        if not root:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel(root)

        self.window.title("FlashLearn - Forgot Password")
        self.window.configure(bg="white")

        # Set window size and position
        window_width = 900
        window_height = 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        position_top = int((screen_height - window_height) / 2) - 50
        position_right = int((screen_width - window_width) / 2)
        self.window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.window.resizable(False, False)

        # Variables to store user data
        self.email_var = tk.StringVar()
        self.username = ""
        self.otp = ""
        self.otp_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        # Current step in the password reset process
        self.current_step = 1  # 1: Email entry, 2: OTP verification, 3: New password

        # Create the UI
        self.create_ui()

    def create_ui(self):
        # Left panel (same for all steps)
        self.left_frame = tk.Frame(self.window, width=400, height=600, bg="#FFF47F")
        self.left_frame.pack(side="left", fill="both")
        self.left_frame.pack_propagate(False)

        # FlashLearn Title
        title_label = ttk.Label(self.left_frame, text="FlashLearn", font=("Poppins", 30, "bold"), background="#FFF47F")
        title_label.pack(pady=(80, 5))

        # Subtitle
        subtitle_label = ttk.Label(
            self.left_frame, text="A Smart Flashcard System for Effective Studying",
            font=("Poppins", 12), background="#FFF47F", wraplength=350, justify="center"
        )
        subtitle_label.pack(pady=(0, 50))

        # Display Image (try to load the image, use placeholder if not found)
        try:
            img_path = "images/Sign In.png"
            if not os.path.exists(img_path):
                # Use a default image or create a placeholder
                img = Image.new('RGB', (480, 480), color='#FFF47F')
            else:
                img = Image.open(img_path)

            img = img.resize((480, 480), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(self.left_frame, image=img_tk, bg="#FFF47F")
            img_label.image = img_tk  # Keep a reference
            img_label.pack(side="bottom", pady=20)
        except Exception as e:
            print(f"Error loading image: {e}")
            # Create a placeholder label if image loading fails
            placeholder = tk.Label(self.left_frame, text="[Image Placeholder]",
                                   font=("Poppins", 14), bg="#FFF47F", width=30, height=15)
            placeholder.pack(side="bottom", pady=20)

        # Right panel (changes based on step)
        self.right_frame = tk.Frame(self.window, width=500, height=600, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)
        self.right_frame.pack_propagate(False)

        # Show the first step (email entry)
        self.show_email_step()

    def show_email_step(self):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Title
        title_label = ttk.Label(self.right_frame, text="Forgot Password", font=("Poppins", 20, "bold"),
                                background="white")
        title_label.pack(pady=(80, 5))

        # Description
        desc_label = ttk.Label(self.right_frame, text="Enter your email to reset your password.",
                               font=("Poppins", 12), background="white")
        desc_label.pack(pady=(0, 20))

        # Email Label & Entry
        email_label = ttk.Label(self.right_frame, text="Email:", font=("Poppins", 12), background="white")
        email_label.pack(anchor="w", padx=60, pady=(25, 0))

        email_entry = ttk.Entry(self.right_frame, width=32, font=("Poppins", 12), textvariable=self.email_var)
        email_entry.pack(ipady=6, padx=60)

        # Continue Button
        continue_btn = tk.Button(
            self.right_frame, text="Continue", font=("Poppins", 12, "bold"),
            width=20, height=2, bg="#003366", fg="white", bd=0, cursor="hand2",
            command=self.verify_email
        )
        continue_btn.pack(pady=(30, 20))

        # Back to Sign In Button
        back_btn = tk.Button(
            self.right_frame, text="Back to Sign In", font=("Poppins", 10),
            bg="white", fg="#003366", bd=0, cursor="hand2",
            command=self.back_to_sign_in
        )
        back_btn.pack()

    def show_otp_step(self):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Title
        title_label = ttk.Label(self.right_frame, text="Verify OTP", font=("Poppins", 20, "bold"), background="white")
        title_label.pack(pady=(80, 5))

        # Description
        desc_label = ttk.Label(self.right_frame,
                               text=f"A 6-digit code has been sent to {self.email_var.get()}",
                               font=("Poppins", 12), background="white", wraplength=400)
        desc_label.pack(pady=(0, 20))

        # OTP Entry
        otp_label = ttk.Label(self.right_frame, text="Enter OTP:", font=("Poppins", 12), background="white")
        otp_label.pack(anchor="w", padx=60, pady=(25, 0))

        # Validate function to allow only 6 digits
        def validate_input(new_input):
            if len(new_input) > 6:
                return False
            return bool(re.match(r'^\d*$', new_input))  # Only allow digits

        validate_command = (self.window.register(validate_input), '%P')
        otp_entry = ttk.Entry(self.right_frame, width=32, font=("Poppins", 12),
                              textvariable=self.otp_var, validate="key",
                              validatecommand=validate_command, justify="center")
        otp_entry.pack(ipady=6, padx=60, pady=10)

        # Timer and Button Frame
        button_frame = tk.Frame(self.right_frame, bg="white")
        button_frame.pack(pady=10)

        # Timer Label
        self.timer_label = ttk.Label(
            button_frame, text="Resend in: 120s", font=("Poppins", 10),
            background="white", foreground="red"
        )
        self.timer_label.pack(pady=(10, 10))

        # Verify Button
        verify_btn = tk.Button(
            button_frame, text="Verify OTP", font=("Poppins", 12, "bold"),
            bg="#003366", fg="white", width=15, command=self.verify_otp
        )
        verify_btn.pack(pady=10)

        # Resend Button
        self.resend_btn = tk.Button(
            button_frame, text="Resend OTP", font=("Poppins", 12, "bold"),
            bg="white", fg="gray", width=15, command=self.resend_otp,
            state="disabled"
        )
        self.resend_btn.pack(pady=5)

        # Back Button
        back_btn = tk.Button(
            self.right_frame, text="Back", font=("Poppins", 10),
            bg="white", fg="#003366", bd=0, cursor="hand2",
            command=self.show_email_step
        )
        back_btn.pack(pady=(20, 0))

        # Start the countdown
        self.countdown(120)

    def show_new_password_step(self):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Title
        title_label = ttk.Label(self.right_frame, text="Reset Password", font=("Poppins", 20, "bold"),
                                background="white")
        title_label.pack(pady=(80, 5))

        # Description
        desc_label = ttk.Label(self.right_frame, text="Create a new password for your account.",
                               font=("Poppins", 12), background="white")
        desc_label.pack(pady=(0, 20))

        # New Password Label & Entry
        new_password_label = ttk.Label(self.right_frame, text="New Password:", font=("Poppins", 12), background="white")
        new_password_label.pack(anchor="w", padx=60, pady=(25, 0))

        new_password_entry = ttk.Entry(self.right_frame, width=32, font=("Poppins", 12),
                                       textvariable=self.new_password_var, show="*")
        new_password_entry.pack(ipady=6, padx=60)

        # Confirm Password Label & Entry
        confirm_password_label = ttk.Label(self.right_frame, text="Confirm Password:",
                                           font=("Poppins", 12), background="white")
        confirm_password_label.pack(anchor="w", padx=60, pady=(15, 0))

        confirm_password_entry = ttk.Entry(self.right_frame, width=32, font=("Poppins", 12),
                                           textvariable=self.confirm_password_var, show="*")
        confirm_password_entry.pack(ipady=6, padx=60)

        # Show/Hide Password Checkbox
        show_password_var = tk.BooleanVar()

        def toggle_password():
            if show_password_var.get():
                new_password_entry.config(show="")
                confirm_password_entry.config(show="")
            else:
                new_password_entry.config(show="*")
                confirm_password_entry.config(show="*")

        show_password_checkbox = ttk.Checkbutton(
            self.right_frame, text="Show Password", variable=show_password_var, command=toggle_password
        )
        show_password_checkbox.pack(anchor="w", padx=60, pady=(5, 0))

        # Password requirements info
        password_info = ttk.Label(
            self.right_frame,
            text="Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character.",
            font=("Poppins", 8), background="white", wraplength=400, foreground="gray"
        )
        password_info.pack(padx=60, pady=(5, 0))

        # Reset Password Button
        reset_btn = tk.Button(
            self.right_frame, text="Reset Password", font=("Poppins", 12, "bold"),
            width=20, height=2, bg="#003366", fg="white", bd=0, cursor="hand2",
            command=self.reset_password
        )
        reset_btn.pack(pady=(20, 20))

    def verify_email(self):
        email = self.email_var.get().strip()

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        # Check if email exists in users.txt
        if not os.path.exists("users.txt"):
            messagebox.showerror("Error", "No users found. Please sign up first.")
            return

        found = False
        with open("users.txt", "r") as file:
            for line in file:
                user_data = line.strip().split(",")
                if len(user_data) >= 3:
                    username, stored_email, password = user_data[:3]
                    if email.lower() == stored_email.lower():
                        found = True
                        self.username = username
                        break

        if not found:
            messagebox.showerror("Error", "Email not found. Please check your email or sign up.")
            return

        # Generate and send OTP
        self.otp = generate_otp()
        try:
            send_otp_email(email, self.otp, self.username)
            messagebox.showinfo("OTP Sent", f"A verification code has been sent to {email}.")
            self.current_step = 2
            self.show_otp_step()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")

    def verify_otp(self):
        entered_otp = self.otp_var.get().strip()

        if not entered_otp:
            messagebox.showerror("Error", "Please enter the OTP.")
            return

        if entered_otp == self.otp:
            messagebox.showinfo("Success", "OTP verified successfully.")
            self.current_step = 3
            self.show_new_password_step()
        else:
            messagebox.showerror("Error", "Incorrect OTP. Please try again.")

    # Password validation function
    def strong_password(self, password):
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

    def reset_password(self):
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()

        # Validate passwords
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please enter both passwords.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Check password strength
        is_strong, password_message = self.strong_password(new_password)
        if not is_strong:
            messagebox.showerror("Error", password_message)
            return

        # Update password in users.txt
        if not os.path.exists("users.txt"):
            messagebox.showerror("Error", "User database not found.")
            return

        email = self.email_var.get().strip()
        updated = False

        # Read all users
        with open("users.txt", "r") as file:
            users = file.readlines()

        # Update the specific user's password
        with open("users.txt", "w") as file:
            for user in users:
                user_data = user.strip().split(",")
                if len(user_data) >= 3:
                    username, stored_email, password = user_data[:3]

                    if email.lower() == stored_email.lower():
                        # Update password
                        file.write(f"{username},{stored_email},{new_password}")
                        if len(user_data) > 3:
                            # Preserve any additional data
                            file.write(f",{','.join(user_data[3:])}")
                        file.write("\n")
                        updated = True
                    else:
                        # Keep the original line
                        file.write(user)
                else:
                    # Keep the original line if it doesn't have enough data
                    file.write(user)

        if updated:
            messagebox.showinfo("Success", "Password reset successfully. You can now sign in with your new password.")
            self.back_to_sign_in()
        else:
            messagebox.showerror("Error", "Failed to update password. Please try again.")

    def resend_otp(self):
        email = self.email_var.get().strip()
        self.otp = generate_otp()

        try:
            send_otp_email(email, self.otp, self.username)
            messagebox.showinfo("OTP Resent", f"A new verification code has been sent to {email}.")

            # Disable Resend button and reset timer
            self.resend_btn.config(state="disabled", fg="gray")
            self.countdown(120)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resend OTP: {str(e)}")

    def countdown(self, seconds):
        """Handles cooldown timer for the resend button."""

        def update_timer():
            for sec in range(seconds, 0, -1):
                time.sleep(1)
                if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
                    return
                self.timer_label.config(text=f"Resend in: {sec}s")

            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text="Resend available")
                self.resend_btn.config(state="normal", fg="black")

        threading.Thread(target=update_timer, daemon=True).start()

    def back_to_sign_in(self):
        self.window.destroy()
        if not self.parent_window:
            import subprocess
            subprocess.run(["python", "sign_in.py"])

    def run(self):
        self.window.mainloop()


# Run the application if executed directly
if __name__ == "__main__":
    app = ForgotPasswordApp()
    app.run()