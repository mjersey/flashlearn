import tkinter as tk
import os
import subprocess
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from tkinter import ttk
import shutil

# Import settings module functionality
from settings import get_user_settings, THEMES, FONT_SIZES, apply_theme, apply_font_size

PROFILE_PICTURE_FOLDER = "profile_pictures"

# Ensure the profile picture directory exists
if not os.path.exists(PROFILE_PICTURE_FOLDER):
    os.makedirs(PROFILE_PICTURE_FOLDER)


# Function to save user data and update the profile page
def save_user_data(username, email, password, profile_picture_path):
    # First, update current_user.txt
    with open("current_user.txt", "w") as file:
        file.write(f"{username},{email},{password},{profile_picture_path}")

    # Then, update users.txt to ensure persistence
    if os.path.exists("users.txt"):
        # Read all users
        with open("users.txt", "r") as file:
            users = file.readlines()

        # Find and update the current user
        found = False
        with open("users.txt", "w") as file:
            for user in users:
                user_data = user.strip().split(",")
                if len(user_data) >= 3:
                    stored_username, stored_email, stored_password = user_data[:3]

                    # Check if this is the user we're updating (match by email)
                    if stored_email.lower() == logged_in_email.lower():
                        # Write updated user data
                        file.write(f"{username},{email},{password},{profile_picture_path}\n")
                        found = True
                    else:
                        # Keep original user data
                        file.write(user)
                else:
                    # Keep malformed lines as they are
                    file.write(user)

            # If user wasn't found (shouldn't happen, but just in case)
            if not found:
                file.write(f"{username},{email},{password},{profile_picture_path}\n")
    else:
        # If users.txt doesn't exist, create it
        with open("users.txt", "w") as file:
            file.write(f"{username},{email},{password},{profile_picture_path}\n")

    # Now, update the profile UI
    update_profile(username, email, password, profile_picture_path)


# Function to get logged-in user
def get_logged_in_user():
    try:
        with open("current_user.txt", "r") as user_file:
            data = user_file.read().strip().split(",")
            if len(data) >= 4:  # Ensure username, email, password, and profile picture path exist
                return data[0], data[1], data[2], data[3]  # (username, email, password, profile_pic)
            elif len(data) == 3:
                return data[0], data[1], data[2], None  # No profile picture saved
    except FileNotFoundError:
        return "Guest", "No Email", "No Password", None

    return "Guest", "No Email", "No Password", None


# Function to update the profile UI dynamically
def update_profile(username, email, password, profile_picture_path):
    # Update the UI components with new data
    username_entry.delete(0, tk.END)
    username_entry.insert(0, username)

    email_entry.delete(0, tk.END)
    email_entry.insert(0, email)

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

    display_profile_picture(profile_picture_path)


# Function to check if username or email already exists (for other users)
def check_duplicate_credentials(new_username, new_email, current_email):
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as file:
            for line in file:
                user_data = line.strip().split(",")
                if len(user_data) >= 3:
                    username, email, _ = user_data[:3]
                    # Skip checking the current user
                    if email.lower() == current_email.lower():
                        continue
                    # Check for duplicate username or email
                    if username.lower() == new_username.lower():
                        return True, "Username already exists. Please choose another."
                    if email.lower() == new_email.lower():
                        return True, "Email already exists. Please use another email."
    return False, ""


# Function to save changes with confirmation
def save_changes():
    global logged_in_username, logged_in_email, logged_in_password, profile_picture_path

    new_username = username_entry.get().strip()
    new_email = email_entry.get().strip()
    new_password = password_entry.get().strip()

    if not new_username or not new_email or not new_password:
        messagebox.showerror("Error", "All fields are required!")
        return

    # Check for duplicate username or email (only if changing)
    if new_username.lower() != logged_in_username.lower() or new_email.lower() != logged_in_email.lower():
        is_duplicate, error_message = check_duplicate_credentials(new_username, new_email, logged_in_email)
        if is_duplicate:
            messagebox.showerror("Error", error_message)
            return

    # Update current_user.txt with new details and keep profile picture path
    with open("current_user.txt", "w") as user_file:
        user_file.write(f"{new_username},{new_email},{new_password},{profile_picture_path}")

    # Update users.txt to ensure persistence
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as file:
            users = file.readlines()

        with open("users.txt", "w") as file:
            for user in users:
                user_data = user.strip().split(",")
                if len(user_data) >= 3:
                    stored_username, stored_email, stored_password = user_data[:3]
                    stored_profile_pic = user_data[3] if len(user_data) > 3 else ""
                    if stored_email.lower() == logged_in_email.lower():  # Identify the user by email
                        file.write(f"{new_username},{new_email},{new_password},{profile_picture_path}\n")
                    else:
                        file.write(user)  # Keep other users unchanged

    # Update the logged-in user's details in the global variables
    logged_in_username = new_username
    logged_in_email = new_email
    logged_in_password = new_password

    messagebox.showinfo("Success", "Profile updated successfully!")

    # Update the UI with new information
    username_entry.delete(0, tk.END)
    username_entry.insert(0, logged_in_username)

    email_entry.delete(0, tk.END)
    email_entry.insert(0, logged_in_email)

    password_entry.delete(0, tk.END)
    password_entry.insert(0, logged_in_password)


# Function to upload a profile picture
def upload_profile_picture():
    global profile_picture_path, logged_in_username

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        try:
            # Create a unique filename based on username
            filename = f"{logged_in_username}.jpg"
            new_profile_picture_path = os.path.join(PROFILE_PICTURE_FOLDER, filename)

            # Open, resize and save the image
            img = Image.open(file_path)
            img = img.resize((120, 120), Image.LANCZOS)  # Size to match screenshot
            img.save(new_profile_picture_path)  # Save the image

            # Update the profile picture path
            profile_picture_path = new_profile_picture_path

            # Update the profile picture display
            display_profile_picture(profile_picture_path)

            # Update the saved profile picture path in both current_user.txt and users.txt
            save_user_data(logged_in_username, logged_in_email, logged_in_password, profile_picture_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload profile picture: {str(e)}")


# Function to display the profile picture
def display_profile_picture(image_path):
    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((120, 120), Image.LANCZOS)  # Size to match screenshot
            img = ImageTk.PhotoImage(img)
            profile_picture_label.config(image=img)
            profile_picture_label.image = img
        except Exception as e:
            print(f"Error displaying profile picture: {e}")
            # If there's an error, show default image
            default_image = Image.new("RGB", (120, 120), color="#CCCCCC")
            default_image = ImageTk.PhotoImage(default_image)
            profile_picture_label.config(image=default_image)
            profile_picture_label.image = default_image
    else:
        # If the file is missing, show a default placeholder
        default_image = Image.new("RGB", (120, 120), color="#CCCCCC")
        default_image = ImageTk.PhotoImage(default_image)
        profile_picture_label.config(image=default_image)
        profile_picture_label.image = default_image


# Function to sign out
def sign_out():
    if os.path.exists("current_user.txt"):
        os.remove("current_user.txt")  # Clear saved user
    root.destroy()
    import sign_in  # Return to sign-in page


# Function to navigate to other pages
def open_page(page):
    root.destroy()
    subprocess.run(["python", f"{page}.py"])


# Function to center window
def center_window(window, width, height):
    """Center a window on the screen"""
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set window position
    window.geometry(f"{width}x{height}+{x}+{y}")


# Main App Window
root = tk.Tk()
root.title("FlashLearn - Profile")

# Set the window size
window_width = 1000
window_height = 700

# Center the window
center_window(root, window_width, window_height)

# Load User Data
logged_in_username, logged_in_email, logged_in_password, profile_picture_path = get_logged_in_user()

# Get user settings
user_settings = get_user_settings(logged_in_username)

# Force dark theme for consistency
current_theme = "dark"
current_font_size = user_settings["font_size"]  # Use the user's font size setting
theme_colors = THEMES[current_theme]

# Configure root with theme
root.configure(bg=theme_colors["bg"])
root.resizable(False, False)

# Sidebar Frame (Fixed Width) - same as in settings.py
sidebar = tk.Frame(root, width=220, height=window_height, bg=theme_colors["sidebar_bg"])
sidebar.pack_propagate(False)  # Prevent resizing
sidebar.pack(side="left", fill="y")

# FlashLearn Title
title_label = tk.Label(sidebar, text="FlashLearn", bg=theme_colors["sidebar_bg"], fg=theme_colors["fg"])
apply_font_size(title_label, current_font_size, "title")
title_label.pack(pady=20)

# Sidebar Buttons Configuration
menu_items = {
    "⚫ Profile": None,  # Current page
    "📖 My Cards": "dashboard",
    "🔥 Progress": "progress",
    "⚙️ Settings": "settings"
}

buttons = {}

# Function to highlight selected menu item
def select_menu(selected):
    """ Highlights the selected menu item and resets others """
    for btn_text, (btn, page) in buttons.items():
        if btn_text == selected:
            # Use direct color for highlight with black text
            btn.config(bg="#FFF47F", fg="black")  # Yellow highlight with black text
            btn.config(font=FONT_SIZES[current_font_size]["subtitle"])
        else:
            apply_theme(btn, current_theme, "sidebar")
            btn.config(font=FONT_SIZES[current_font_size]["regular"])

# Create Sidebar Buttons with Navigation
for text, page in menu_items.items():
    btn = tk.Button(
        sidebar, text=text, bd=0,
        anchor="w", padx=20, width=20,
        command=lambda t=text, p=page: open_page(p) if p else select_menu(t)
    )
    apply_theme(btn, current_theme, "sidebar")
    apply_font_size(btn, current_font_size, "regular")
    btn.pack(pady=5, fill="x")
    buttons[text] = (btn, page)  # Store button references

# Default: Select "Profile" - directly set the yellow color with black text
select_menu("⚫ Profile")

# Sign Out Button (Goes back to sign_in.py)
sign_out_btn = tk.Button(sidebar, text="↩ Sign Out", bd=0,
                     anchor="w", padx=20, width=20, command=sign_out)
apply_theme(sign_out_btn, current_theme, "sidebar")
apply_font_size(sign_out_btn, current_font_size, "regular")
sign_out_btn.pack(pady=30, side="bottom", fill="x")

# Add a thin vertical separator between sidebar and content
separator = tk.Frame(root, width=1, bg=theme_colors["border"])
separator.pack(side="left", fill="y")

# Main Content
main_content = tk.Frame(root, bg=theme_colors["bg"])
main_content.pack(side="right", fill="both", expand=True)

# Profile Title (centered)
profile_title = tk.Label(main_content, text="Profile", bg=theme_colors["bg"], fg=theme_colors["fg"])
apply_font_size(profile_title, current_font_size, "title")
profile_title.pack(pady=20)

# Profile Picture Section (centered)
profile_picture_frame = tk.Frame(main_content, bg=theme_colors["bg"])
profile_picture_frame.pack(pady=10)

# Default profile picture
default_image = Image.new("RGB", (120, 120), color="#CCCCCC")
default_image = ImageTk.PhotoImage(default_image)

profile_picture_label = tk.Label(profile_picture_frame, image=default_image, bg=theme_colors["bg"])
profile_picture_label.image = default_image
profile_picture_label.pack()

# Upload Picture Button
upload_button = tk.Button(profile_picture_frame, text="Upload Picture",
                       bg=theme_colors["button_bg"], fg=theme_colors["button_fg"],
                       padx=10, pady=5, command=upload_profile_picture)
apply_font_size(upload_button, current_font_size, "button")
upload_button.pack(pady=10)

# "You can edit your credentials below" text
edit_label = tk.Label(main_content, text="You can edit your credentials below:",
                   bg=theme_colors["bg"], fg="gray")
apply_font_size(edit_label, current_font_size, "small")
edit_label.pack(pady=10)

# Form Fields - all centered
form_frame = tk.Frame(main_content, bg=theme_colors["bg"])
form_frame.pack(pady=5)

# Username Field
username_label = tk.Label(form_frame, text="Username:", bg=theme_colors["bg"], fg=theme_colors["fg"])
apply_font_size(username_label, current_font_size, "regular")
username_label.pack(anchor="w")

username_entry = tk.Entry(form_frame, width=30, bg="white", fg="black")
apply_font_size(username_entry, current_font_size, "regular")
username_entry.insert(0, logged_in_username)
username_entry.pack(pady=(0, 10), ipady=5)

# Email Field
email_label = tk.Label(form_frame, text="Email:", bg=theme_colors["bg"], fg=theme_colors["fg"])
apply_font_size(email_label, current_font_size, "regular")
email_label.pack(anchor="w")

email_entry = tk.Entry(form_frame, width=30, bg="white", fg="black")
apply_font_size(email_entry, current_font_size, "regular")
email_entry.insert(0, logged_in_email)
email_entry.pack(pady=(0, 10), ipady=5)

# Password Field
password_label = tk.Label(form_frame, text="Password:", bg=theme_colors["bg"], fg=theme_colors["fg"])
apply_font_size(password_label, current_font_size, "regular")
password_label.pack(anchor="w")

password_entry = tk.Entry(form_frame, width=30, bg="white", fg="black", show="*")
apply_font_size(password_entry, current_font_size, "regular")
password_entry.insert(0, logged_in_password)
password_entry.pack(ipady=5)

# Show Password Checkbox
show_password_var = tk.BooleanVar()
show_password_frame = tk.Frame(form_frame, bg=theme_colors["bg"])
show_password_frame.pack(anchor="w", pady=5)

def toggle_password():
    if show_password_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")

show_password_checkbox = tk.Checkbutton(
    show_password_frame, text="Show Password",
    variable=show_password_var, command=toggle_password,
    bg=theme_colors["bg"], fg=theme_colors["fg"],
    selectcolor=theme_colors["bg"]
)
apply_font_size(show_password_checkbox, current_font_size, "small")
show_password_checkbox.pack(side="left")

# Save Changes Button
save_button_frame = tk.Frame(main_content, bg=theme_colors["bg"])
save_button_frame.pack(pady=20)

save_button = tk.Button(save_button_frame, text="Save Changes",
                     bg=theme_colors["button_bg"], fg=theme_colors["button_fg"],
                     padx=15, pady=5, command=save_changes)
apply_font_size(save_button, current_font_size, "button")
save_button.pack()

# Display the profile picture on app load
display_profile_picture(profile_picture_path)

root.mainloop()