import subprocess
import os
import json
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk, ImageDraw

# Constants
SETTINGS_FOLDER = "user_settings"
PROFILE_PICTURE_FOLDER = "profile_pictures"
os.makedirs(SETTINGS_FOLDER, exist_ok=True)
os.makedirs(PROFILE_PICTURE_FOLDER, exist_ok=True)

# Default settings
DEFAULT_SETTINGS = {
    "theme": "light",
    "card_order": "sequential",
    "auto_reveal_time": 0,  # 0 means disabled
    "font_size": "medium",
    "notifications_enabled": True,
    "sound_enabled": True,
    "backup_frequency": "weekly",
    "auto_save": True
}

# Theme colors
THEMES = {
    "light": {
        "bg": "white",
        "sidebar_bg": "white",
        "fg": "black",
        "button_bg": "#003366",
        "button_fg": "white",
        "highlight": "#FFF47F",  # This exact yellow color is crucial
        "highlight_fg": "black",  # Text color for highlighted items
        "shadow": "#D3D3D3",
        "card_bg": "#F0F0F0",
        "success_bg": "#4CAF50",
        "error_bg": "#f44336",
        "warning_bg": "#FFEB3B",
        "info_bg": "#2196F3",
        "border": "#D3D3D3"  # Border color
    },
    "dark": {
        "bg": "#222222",  # Dark background
        "sidebar_bg": "#1E1E1E",  # Slightly darker for sidebar
        "fg": "#E0E0E0",  # Light text color
        "button_bg": "#003366",  # Blue button
        "button_fg": "#E0E0E0",  # Light text on buttons
        "highlight": "#FFF47F",  # Same yellow highlight
        "highlight_fg": "black",  # Text color for highlighted items
        "shadow": "#333333",
        "card_bg": "#2D2D2D",  # Slightly lighter than bg for cards
        "success_bg": "#388E3C",
        "error_bg": "#D32F2F",
        "warning_bg": "#FFA000",
        "info_bg": "#1976D2",
        "border": "#333333"  # Border color
    }
}

# Font sizes
FONT_SIZES = {
    "small": {
        "title": ("Poppins", 14, "bold"),
        "subtitle": ("Poppins", 12, "bold"),
        "regular": ("Poppins", 9),
        "button": ("Poppins", 9),
        "small": ("Poppins", 8)
    },
    "medium": {
        "title": ("Poppins", 16, "bold"),
        "subtitle": ("Poppins", 14, "bold"),
        "regular": ("Poppins", 10),
        "button": ("Poppins", 10),
        "small": ("Poppins", 9)
    },
    "large": {
        "title": ("Poppins", 18, "bold"),
        "subtitle": ("Poppins", 16, "bold"),
        "regular": ("Poppins", 12),
        "button": ("Poppins", 12),
        "small": ("Poppins", 10)
    }
}


def get_current_settings():
    """Get settings for the current user"""
    username = get_logged_in_user()[0]
    return get_user_settings(username)


def get_logged_in_user():
    """Get the currently logged in user"""
    try:
        with open("current_user.txt", "r") as user_file:
            data = user_file.read().strip().split(",")
            return (data + [None])[:4]  # Ensure four elements (username, email, password, profile_pic)
    except FileNotFoundError:
        return "Guest", "No Email", "No Password", None


def get_user_settings(username):
    """Get settings for a specific user"""
    settings_file = os.path.join(SETTINGS_FOLDER, f"{username}_settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()


def save_user_settings(username, settings_data):
    """Save settings for a specific user"""
    settings_file = os.path.join(SETTINGS_FOLDER, f"{username}_settings.json")
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def apply_theme(widget, theme_name="light", widget_type="main"):
    """Apply the selected theme to a widget"""
    theme = THEMES.get(theme_name, THEMES["light"])

    try:
        if widget_type == "main":
            widget.configure(bg=theme["bg"])
            try:
                widget.configure(fg=theme["fg"])
            except:
                pass  # Some widgets don't support fg
        elif widget_type == "sidebar":
            widget.configure(bg=theme["sidebar_bg"])
            try:
                widget.configure(fg=theme["fg"])
            except:
                pass  # Some widgets don't support fg
        elif widget_type == "button":
            widget.configure(bg=theme["button_bg"])
            try:
                widget.configure(fg=theme["button_fg"])
            except:
                pass  # Some widgets don't support fg
        elif widget_type == "highlight":
            widget.configure(bg=theme["highlight"])
            try:
                widget.configure(fg=theme["highlight_fg"])  # Use highlight_fg for highlighted items
            except:
                pass  # Some widgets don't support fg
        elif widget_type == "card":
            widget.configure(bg=theme["card_bg"])
            try:
                widget.configure(fg=theme["fg"])
            except:
                pass  # Some widgets don't support fg
    except:
        # Some widgets might not support bg either
        pass

    # Apply theme to all child widgets
    if hasattr(widget, 'winfo_children'):
        for child in widget.winfo_children():
            if widget_type == "sidebar":
                apply_theme(child, theme_name, "sidebar")
            elif widget_type == "card":
                apply_theme(child, theme_name, "card")
            else:
                apply_theme(child, theme_name, "main")


def apply_font_size(widget, size="medium", text_type="regular"):
    """Apply the selected font size to a widget"""
    fonts = FONT_SIZES.get(size, FONT_SIZES["medium"])

    if text_type in fonts:
        try:
            widget.configure(font=fonts[text_type])
        except:
            pass  # Some widgets don't support font

    # Apply font to all child widgets
    if hasattr(widget, 'winfo_children'):
        for child in widget.winfo_children():
            apply_font_size(child, size, text_type)


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


def open_page(page):
    """Open another page and close the current one"""
    root.destroy()
    subprocess.run(["python", f"{page}.py"])


def sign_out():
    """Sign out the current user"""
    if os.path.exists("current_user.txt"):
        os.remove("current_user.txt")
    root.destroy()
    import sign_in


def export_settings():
    """Export user settings to a file"""
    username, _, _, _ = get_logged_in_user()
    settings = get_user_settings(username)

    # Ask user for save location
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile=f"{username}_settings.json"
    )

    if file_path:
        try:
            with open(file_path, 'w') as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Success", "Settings exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings: {str(e)}")


def import_settings():
    """Import user settings from a file"""
    # Ask user for file location
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")]
    )

    if file_path:
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)

            # Validate imported settings
            for key in DEFAULT_SETTINGS:
                if key not in imported_settings:
                    imported_settings[key] = DEFAULT_SETTINGS[key]

            # Save the imported settings
            username, _, _, _ = get_logged_in_user()
            if save_user_settings(username, imported_settings):
                messagebox.showinfo("Success",
                                    "Settings imported successfully! Please restart the application for changes to take effect.")
                # Apply settings immediately
                apply_imported_settings(imported_settings)
            else:
                messagebox.showerror("Error", "Failed to save imported settings.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings: {str(e)}")


def apply_imported_settings(settings):
    """Apply imported settings immediately"""
    # Update theme variables
    theme_var.set(settings["theme"])
    font_var.set(settings["font_size"])
    order_var.set(settings["card_order"])
    reveal_var.set(settings["auto_reveal_time"])
    notif_var.set(settings["notifications_enabled"])
    sound_var.set(settings["sound_enabled"])

    # Apply theme to the entire application
    apply_theme(root, settings["theme"])

    # Update preview text with new font sizes
    update_preview_text()

    # Make sure to reapply the highlight to the Settings button
    select_menu("⚙️ Settings")


def reset_settings():
    """Reset user settings to default"""
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to default?"):
        username, _, _, _ = get_logged_in_user()
        if save_user_settings(username, DEFAULT_SETTINGS.copy()):
            messagebox.showinfo("Success",
                                "Settings reset to default! Please restart the application for changes to take effect.")
            # Apply default settings immediately
            apply_imported_settings(DEFAULT_SETTINGS.copy())
        else:
            messagebox.showerror("Error", "Failed to reset settings.")


def backup_data():
    """Backup all user data"""
    username, _, _, _ = get_logged_in_user()

    # Ask user for backup directory
    backup_dir = filedialog.askdirectory(title="Select Backup Directory")

    if not backup_dir:
        return

    # Create a backup folder with timestamp
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(backup_dir, f"{username}_backup_{timestamp}")

    try:
        os.makedirs(backup_folder, exist_ok=True)

        # Backup settings
        settings_file = os.path.join(SETTINGS_FOLDER, f"{username}_settings.json")
        if os.path.exists(settings_file):
            import shutil
            shutil.copy2(settings_file, os.path.join(backup_folder, f"{username}_settings.json"))

        # Backup decks
        decks_file = os.path.join("user_decks", f"{username}_decks.json")
        if os.path.exists(decks_file):
            import shutil
            shutil.copy2(decks_file, os.path.join(backup_folder, f"{username}_decks.json"))

        # Backup progress
        progress_file = os.path.join("user_progress", f"{username}_progress.json")
        if os.path.exists(progress_file):
            import shutil
            shutil.copy2(progress_file, os.path.join(backup_folder, f"{username}_progress.json"))

        messagebox.showinfo("Success", f"Data backed up successfully to:\n{backup_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to backup data: {str(e)}")


def restore_data():
    """Restore user data from backup"""
    # Ask user for backup file location
    backup_dir = filedialog.askdirectory(title="Select Backup Directory")

    if not backup_dir:
        return

    username, _, _, _ = get_logged_in_user()

    try:
        # Check if backup files exist
        settings_backup = os.path.join(backup_dir, f"{username}_settings.json")
        decks_backup = os.path.join(backup_dir, f"{username}_decks.json")
        progress_backup = os.path.join(backup_dir, f"{username}_progress.json")

        files_restored = 0

        # Restore settings
        if os.path.exists(settings_backup):
            import shutil
            settings_file = os.path.join(SETTINGS_FOLDER, f"{username}_settings.json")
            shutil.copy2(settings_backup, settings_file)
            files_restored += 1

            # Apply restored settings immediately
            with open(settings_file, 'r') as f:
                restored_settings = json.load(f)
            apply_imported_settings(restored_settings)

        # Restore decks
        if os.path.exists(decks_backup):
            import shutil
            decks_file = os.path.join("user_decks", f"{username}_decks.json")
            shutil.copy2(decks_backup, decks_file)
            files_restored += 1

        # Restore progress
        if os.path.exists(progress_backup):
            import shutil
            progress_file = os.path.join("user_progress", f"{username}_progress.json")
            shutil.copy2(progress_backup, progress_file)
            files_restored += 1

        if files_restored > 0:
            messagebox.showinfo("Success",
                                f"Restored {files_restored} data files. Some changes will take effect immediately, others after restarting the application.")
        else:
            messagebox.showwarning("Warning", "No backup files found for the current user.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restore data: {str(e)}")


def update_preview_text():
    """Update the preview text with the selected font size"""
    current_font_size = font_var.get()
    current_theme = theme_var.get()

    # Update preview labels with new font sizes
    preview_title.config(font=FONT_SIZES[current_font_size]["title"])
    preview_subtitle.config(font=FONT_SIZES[current_font_size]["subtitle"])
    preview_body.config(font=FONT_SIZES[current_font_size]["regular"])

    # Update colors based on theme
    theme_colors = THEMES[current_theme]
    preview_frame.config(bg=theme_colors["bg"], fg=theme_colors["fg"])
    preview_title.config(bg=theme_colors["bg"], fg=theme_colors["fg"])
    preview_subtitle.config(bg=theme_colors["bg"], fg=theme_colors["fg"])
    preview_body.config(bg=theme_colors["bg"], fg=theme_colors["fg"])


def apply_theme_change(*args):
    """Apply theme changes when the theme is changed"""
    current_theme = theme_var.get()

    # Apply theme to the entire application
    apply_theme(root, current_theme)
    update_preview_text()

    # First, update the sidebar itself
    sidebar.config(bg=THEMES[current_theme]["sidebar_bg"])

    # Then update all buttons in the sidebar with the correct theme
    for btn_text, (btn, page) in buttons.items():
        if btn_text == "⚙️ Settings":  # Keep the Settings button highlighted
            btn.config(bg=THEMES[current_theme]["highlight"], fg="black")
            btn.config(font=FONT_SIZES[user_settings["font_size"]]["subtitle"])
        else:
            # Apply the sidebar background and text color directly
            btn.config(bg=THEMES[current_theme]["sidebar_bg"], fg=THEMES[current_theme]["fg"])
            btn.config(font=FONT_SIZES[user_settings["font_size"]]["regular"])

    # Update the title and sign out button
    title_label.config(bg=THEMES[current_theme]["sidebar_bg"], fg=THEMES[current_theme]["fg"])
    sign_out_btn.config(bg=THEMES[current_theme]["sidebar_bg"], fg=THEMES[current_theme]["fg"])

    # Update all other buttons with the button_bg color
    update_button_colors(current_theme)


def update_button_colors(theme_name):
    """Update all buttons with the button_bg color from the theme"""
    theme_colors = THEMES[theme_name]

    # Update all buttons in the application
    for widget in root.winfo_children():
        update_button_colors_recursive(widget, theme_colors)


def update_button_colors_recursive(widget, theme_colors):
    """Recursively update button colors"""
    if isinstance(widget, tk.Button):
        # Skip sidebar buttons which have special handling
        if widget.master != sidebar:
            widget.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])

    # Process children
    if hasattr(widget, 'winfo_children'):
        for child in widget.winfo_children():
            update_button_colors_recursive(child, theme_colors)


def apply_font_change(*args):
    """Apply font changes when the font size is changed"""
    current_font_size = font_var.get()

    # Update preview text with new font sizes
    update_preview_text()

    # Update sidebar buttons with new font sizes
    for btn_text, (btn, page) in buttons.items():
        if btn_text == "⚙️ Settings":  # Currently selected
            btn.config(font=FONT_SIZES[current_font_size]["subtitle"])
        else:
            btn.config(font=FONT_SIZES[current_font_size]["regular"])

    # Update other key elements
    title_label.config(font=FONT_SIZES[current_font_size]["title"])
    settings_label.config(font=FONT_SIZES[current_font_size]["title"])
    sign_out_btn.config(font=FONT_SIZES[current_font_size]["regular"])


# Fix the select_menu function to properly highlight the selected menu item
# Replace the current select_menu function with this one:

def select_menu(selected):
    """ Highlights the selected menu item and resets others """
    current_theme = theme_var.get()  # Get the current theme

    for btn_text, (btn, page) in buttons.items():
        if btn_text == selected:
            # Use the theme's highlight color with black text for highlighted items
            btn.config(bg=THEMES[current_theme]["highlight"], fg="black")
            btn.config(font=FONT_SIZES[user_settings["font_size"]]["subtitle"])
        else:
            # Apply the sidebar background and text color directly
            btn.config(bg=THEMES[current_theme]["sidebar_bg"], fg=THEMES[current_theme]["fg"])
            btn.config(font=FONT_SIZES[user_settings["font_size"]]["regular"])


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("FlashLearn - Settings")

    # Set the window size
    window_width = 1000
    window_height = 700

    # Center the main window
    center_window(root, window_width, window_height)

    # Make window non-resizable
    root.resizable(False, False)

    # Get user data
    logged_in_username, logged_in_email, logged_in_password, profile_picture_path = get_logged_in_user()

    # Get user settings
    user_settings = get_user_settings(logged_in_username)

    # Force dark theme for this implementation
    # Use the user's saved theme preference
    current_theme = user_settings["theme"]
    theme_colors = THEMES[current_theme]


    # Function to load and display the profile icon
    def display_profile_icon():
        if profile_picture_path and os.path.exists(profile_picture_path):
            try:
                img = Image.open(profile_picture_path)
                img = img.resize((50, 50), Image.LANCZOS)

                # Make the image circular
                mask = Image.new('L', (50, 50), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 50, 50), fill=255)
                img_circular = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
                img_circular.paste(img, (0, 0), mask)

                img_tk = ImageTk.PhotoImage(img_circular)
                profile_icon_label.config(image=img_tk)
                profile_icon_label.image = img_tk
            except Exception as e:
                print(f"Error displaying profile icon: {e}")
                default_image = Image.new("RGB", (50, 50), color="#CCCCCC")
                default_image = ImageTk.PhotoImage(default_image)
                profile_icon_label.config(image=default_image)
                profile_icon_label.image = default_image
        else:
            default_image = Image.new("RGB", (50, 50), color="#CCCCCC")
            default_image = ImageTk.PhotoImage(default_image)
            profile_icon_label.config(image=default_image)
            profile_icon_label.image = default_image


    # Sidebar Frame (Fixed Width)
    sidebar = tk.Frame(root, width=220, height=600)
    apply_theme(sidebar, current_theme, "sidebar")
    sidebar.pack_propagate(False)  # Prevent resizing
    sidebar.pack(side="left", fill="y")

    # FlashLearn Title
    title_label = tk.Label(sidebar, text="FlashLearn")
    apply_theme(title_label, current_theme, "sidebar")
    apply_font_size(title_label, user_settings["font_size"], "title")
    title_label.pack(pady=20)

    # Sidebar Buttons Configuration
    menu_items = {
        "⚫ Profile": "profile",
        "📖 My Cards": "dashboard",
        "🔥 Progress": "progress",
        "⚙️ Settings": None  # Current page
    }

    buttons = {}

    # Also fix the buttons creation section by adding this after the buttons dictionary is defined:
    # Create Sidebar Buttons with Navigation
    for text, page in menu_items.items():
        btn = tk.Button(
            sidebar, text=text, bd=0,
            anchor="w", padx=20, width=20,
            command=lambda t=text, p=page: open_page(p) if p else select_menu(t)
        )
        apply_theme(btn, current_theme, "sidebar")
        apply_font_size(btn, user_settings["font_size"], "regular")
        btn.pack(pady=5, fill="x")
        buttons[text] = (btn, page)  # Store button references

    # Modified select_menu function to use direct color setting and black text for highlighted items
    # Default: Select "Settings" - directly set the yellow color with theme-appropriate text
    # for btn_text, (btn, page) in buttons.items():
    #     if btn_text == "⚙️ Settings":
    #         btn.config(bg="#FFF47F", fg=theme_colors["highlight_fg"])  # Yellow highlight with theme-appropriate text
    #         btn.config(font=FONT_SIZES[user_settings["font_size"]]["subtitle"])

    # Sign Out Button (Goes back to sign_in.py)
    sign_out_btn = tk.Button(sidebar, text="↩ Sign Out", bd=0,
                             anchor="w", padx=20, width=20, command=sign_out)
    apply_theme(sign_out_btn, current_theme, "sidebar")
    apply_font_size(sign_out_btn, user_settings["font_size"], "regular")
    sign_out_btn.pack(pady=30, side="bottom", fill="x")

    # Add a thin vertical separator between sidebar and content
    separator = tk.Frame(root, width=1, bg=theme_colors["border"])
    separator.pack(side="left", fill="y")

    # Main Content Frame
    content_frame = tk.Frame(root, width=680, height=600)
    apply_theme(content_frame, current_theme)
    content_frame.pack(side="right", fill="both", expand=True)

    # Settings Title
    settings_label = tk.Label(content_frame, text="Settings")
    apply_theme(settings_label, current_theme)
    apply_font_size(settings_label, user_settings["font_size"], "title")
    settings_label.pack(pady=20)

    # Profile Icon Section (Upper Right)
    profile_icon_label = tk.Label(root)
    apply_theme(profile_icon_label, current_theme)
    profile_icon_label.place(x=window_width - 60, y=10)  # Place icon 10px from the top-right corner

    # Call the function to display the profile icon
    display_profile_icon()

    # Create a notebook (tabbed interface) for settings
    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # Appearance Tab
    appearance_tab = tk.Frame(notebook)
    apply_theme(appearance_tab, current_theme)
    notebook.add(appearance_tab, text="Appearance")

    # Theme setting
    theme_frame = tk.LabelFrame(appearance_tab, text="Theme", bd=1, relief="solid")
    apply_theme(theme_frame, current_theme)
    apply_font_size(theme_frame, user_settings["font_size"], "subtitle")
    theme_frame.pack(fill="x", padx=20, pady=10)

    theme_var = tk.StringVar(value=current_theme)
    theme_var.trace_add("write", apply_theme_change)  # Call apply_theme_change when theme_var changes

    # Theme options
    theme_light = tk.Radiobutton(
        theme_frame,
        text="Light Theme",
        variable=theme_var,
        value="light",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(theme_light, current_theme)
    apply_font_size(theme_light, user_settings["font_size"], "regular")
    theme_light.pack(anchor="w", pady=5, padx=10)

    theme_dark = tk.Radiobutton(
        theme_frame,
        text="Dark Theme",
        variable=theme_var,
        value="dark",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(theme_dark, current_theme)
    apply_font_size(theme_dark, user_settings["font_size"], "regular")
    theme_dark.pack(anchor="w", pady=5, padx=10)

    # Font size setting
    font_frame = tk.LabelFrame(appearance_tab, text="Font Size", bd=1, relief="solid")
    apply_theme(font_frame, current_theme)
    apply_font_size(font_frame, user_settings["font_size"], "subtitle")
    font_frame.pack(fill="x", padx=20, pady=10)

    font_var = tk.StringVar(value=user_settings["font_size"])
    font_var.trace_add("write", apply_font_change)  # Call apply_font_change when font_var changes

    # Font size options
    font_small = tk.Radiobutton(
        font_frame,
        text="Small",
        variable=font_var,
        value="small",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(font_small, current_theme)
    apply_font_size(font_small, user_settings["font_size"], "regular")
    font_small.pack(anchor="w", pady=5, padx=10)

    font_medium = tk.Radiobutton(
        font_frame,
        text="Medium",
        variable=font_var,
        value="medium",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(font_medium, current_theme)
    apply_font_size(font_medium, user_settings["font_size"], "regular")
    font_medium.pack(anchor="w", pady=5, padx=10)

    font_large = tk.Radiobutton(
        font_frame,
        text="Large",
        variable=font_var,
        value="large",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(font_large, current_theme)
    apply_font_size(font_large, user_settings["font_size"], "regular")
    font_large.pack(anchor="w", pady=5, padx=10)

    # Preview section
    preview_frame = tk.LabelFrame(appearance_tab, text="Preview", bd=1, relief="solid")
    apply_theme(preview_frame, current_theme)
    apply_font_size(preview_frame, user_settings["font_size"], "subtitle")
    preview_frame.pack(fill="x", padx=20, pady=10)

    # Preview of different text sizes
    preview_title = tk.Label(preview_frame, text="Title Example")
    apply_theme(preview_title, current_theme)
    apply_font_size(preview_title, user_settings["font_size"], "title")
    preview_title.pack(anchor="w", pady=5, padx=10)

    preview_subtitle = tk.Label(preview_frame, text="Subtitle Example")
    apply_theme(preview_subtitle, current_theme)
    apply_font_size(preview_subtitle, user_settings["font_size"], "subtitle")
    preview_subtitle.pack(anchor="w", pady=5, padx=10)

    preview_body = tk.Label(preview_frame, text="Body text example")
    apply_theme(preview_body, current_theme)
    apply_font_size(preview_body, user_settings["font_size"], "regular")
    preview_body.pack(anchor="w", pady=5, padx=10)

    # Study Preferences Tab
    study_tab = tk.Frame(notebook)
    apply_theme(study_tab, current_theme)
    notebook.add(study_tab, text="Study Preferences")

    # Card order setting
    order_frame = tk.LabelFrame(study_tab, text="Card Order", bd=1, relief="solid")
    apply_theme(order_frame, current_theme)
    apply_font_size(order_frame, user_settings["font_size"], "subtitle")
    order_frame.pack(fill="x", padx=20, pady=10)

    order_var = tk.StringVar(value=user_settings["card_order"])

    # Card order options
    order_sequential = tk.Radiobutton(
        order_frame,
        text="Sequential (Cards shown in order)",
        variable=order_var,
        value="sequential",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(order_sequential, current_theme)
    apply_font_size(order_sequential, user_settings["font_size"], "regular")
    order_sequential.pack(anchor="w", pady=5, padx=10)

    order_random = tk.Radiobutton(
        order_frame,
        text="Random (Cards shown in random order)",
        variable=order_var,
        value="random",
        selectcolor=theme_colors["bg"]
    )
    apply_theme(order_random, current_theme)
    apply_font_size(order_random, user_settings["font_size"], "regular")
    order_random.pack(anchor="w", pady=5, padx=10)

    # Auto reveal setting
    reveal_frame = tk.LabelFrame(study_tab, text="Auto Reveal Answer", bd=1, relief="solid")
    apply_theme(reveal_frame, current_theme)
    apply_font_size(reveal_frame, user_settings["font_size"], "subtitle")
    reveal_frame.pack(fill="x", padx=20, pady=10)

    reveal_var = tk.IntVar(value=user_settings["auto_reveal_time"])

    # Auto reveal description
    reveal_desc = tk.Label(
        reveal_frame,
        text="Set how many seconds to wait before automatically revealing the answer (0 = disabled)",
        wraplength=600,
        justify="left"
    )
    apply_theme(reveal_desc, current_theme)
    apply_font_size(reveal_desc, user_settings["font_size"], "regular")
    reveal_desc.pack(anchor="w", pady=5, padx=10)

    # Auto reveal slider
    reveal_scale = tk.Scale(
        reveal_frame,
        from_=0,
        to=10,
        orient=tk.HORIZONTAL,
        variable=reveal_var,
        length=400,
        troughcolor=theme_colors["card_bg"],
        bg=theme_colors["bg"],
        fg=theme_colors["fg"],
        highlightbackground=theme_colors["bg"]
    )
    apply_theme(reveal_scale, current_theme)
    reveal_scale.pack(anchor="w", pady=5, padx=10)

    # Notifications Tab
    notif_tab = tk.Frame(notebook)
    apply_theme(notif_tab, current_theme)
    notebook.add(notif_tab, text="Notifications")

    # Notifications settings
    notif_frame = tk.LabelFrame(notif_tab, text="Notification Settings", bd=1, relief="solid")
    apply_theme(notif_frame, current_theme)
    apply_font_size(notif_frame, user_settings["font_size"], "subtitle")
    notif_frame.pack(fill="x", padx=20, pady=10)

    notif_var = tk.BooleanVar(value=user_settings["notifications_enabled"])
    sound_var = tk.BooleanVar(value=user_settings["sound_enabled"])

    # Notification options
    notif_check = tk.Checkbutton(
        notif_frame,
        text="Enable Notifications",
        variable=notif_var,
        selectcolor=theme_colors["bg"]
    )
    apply_theme(notif_check, current_theme)
    apply_font_size(notif_check, user_settings["font_size"], "regular")
    notif_check.pack(anchor="w", pady=5, padx=10)

    notif_desc = tk.Label(
        notif_frame,
        text="Receive notifications for study reminders and updates",
        wraplength=600,
        justify="left"
    )
    apply_theme(notif_desc, current_theme)
    apply_font_size(notif_desc, user_settings["font_size"], "small")
    notif_desc.pack(anchor="w", padx=25, pady=(0, 10))

    # Sound options
    sound_check = tk.Checkbutton(
        notif_frame,
        text="Enable Sounds",
        variable=sound_var,
        selectcolor=theme_colors["bg"]
    )
    apply_theme(sound_check, current_theme)
    apply_font_size(sound_check, user_settings["font_size"], "regular")
    sound_check.pack(anchor="w", pady=5, padx=10)

    sound_desc = tk.Label(
        notif_frame,
        text="Play sounds for correct/incorrect answers and notifications",
        wraplength=600,
        justify="left"
    )
    apply_theme(sound_desc, current_theme)
    apply_font_size(sound_desc, user_settings["font_size"], "small")
    sound_desc.pack(anchor="w", padx=25, pady=(0, 10))

    # Data Management Tab
    data_tab = tk.Frame(notebook)
    apply_theme(data_tab, current_theme)
    notebook.add(data_tab, text="Data Management")

    # Backup and restore frame
    backup_frame = tk.LabelFrame(data_tab, text="Backup & Restore", bd=1, relief="solid")
    apply_theme(backup_frame, current_theme)
    apply_font_size(backup_frame, user_settings["font_size"], "subtitle")
    backup_frame.pack(fill="x", padx=20, pady=10)

    # Backup description
    backup_desc = tk.Label(
        backup_frame,
        text="Backup your flashcards, progress, and settings to a file that you can restore later.",
        wraplength=600,
        justify="left"
    )
    apply_theme(backup_desc, current_theme)
    apply_font_size(backup_desc, user_settings["font_size"], "regular")
    backup_desc.pack(anchor="w", pady=5, padx=10)

    # Backup and restore buttons
    backup_btn = tk.Button(
        backup_frame,
        text="Backup Data",
        command=backup_data,
        padx=15,
        pady=5
    )
    backup_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(backup_btn, user_settings["font_size"], "button")
    backup_btn.pack(side=tk.LEFT, padx=15, pady=10)

    restore_btn = tk.Button(
        backup_frame,
        text="Restore from Backup",
        command=restore_data,
        padx=15,
        pady=5
    )
    restore_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(restore_btn, user_settings["font_size"], "button")
    restore_btn.pack(side=tk.LEFT, padx=5, pady=10)

    # Import/Export frame
    import_frame = tk.LabelFrame(data_tab, text="Import & Export Settings", bd=1, relief="solid")
    apply_theme(import_frame, current_theme)
    apply_font_size(import_frame, user_settings["font_size"], "subtitle")
    import_frame.pack(fill="x", padx=20, pady=10)

    # Import/Export description
    import_desc = tk.Label(
        import_frame,
        text="Export your settings to share with others or import settings from another device.",
        wraplength=600,
        justify="left"
    )
    apply_theme(import_desc, current_theme)
    apply_font_size(import_desc, user_settings["font_size"], "regular")
    import_desc.pack(anchor="w", pady=5, padx=10)

    # Import/Export buttons
    export_btn = tk.Button(
        import_frame,
        text="Export Settings",
        command=export_settings,
        padx=15,
        pady=5
    )
    export_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(export_btn, user_settings["font_size"], "button")
    export_btn.pack(side=tk.LEFT, padx=15, pady=10)

    import_btn = tk.Button(
        import_frame,
        text="Import Settings",
        command=import_settings,
        padx=15,
        pady=5
    )
    import_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(import_btn, user_settings["font_size"], "button")
    import_btn.pack(side=tk.LEFT, padx=5, pady=10)

    # Reset frame
    reset_frame = tk.LabelFrame(data_tab, text="Reset Settings", bd=1, relief="solid")
    apply_theme(reset_frame, current_theme)
    apply_font_size(reset_frame, user_settings["font_size"], "subtitle")
    reset_frame.pack(fill="x", padx=20, pady=10)

    # Reset description
    reset_desc = tk.Label(
        reset_frame,
        text="Reset all settings to their default values. This cannot be undone.",
        wraplength=600,
        justify="left"
    )
    apply_theme(reset_desc, current_theme)
    apply_font_size(reset_desc, user_settings["font_size"], "regular")
    reset_desc.pack(anchor="w", pady=5, padx=10)

    # Reset button
    reset_btn = tk.Button(
        reset_frame,
        text="Reset to Default",
        command=reset_settings,
        padx=15,
        pady=5
    )
    reset_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(reset_btn, user_settings["font_size"], "button")
    reset_btn.pack(anchor="w", pady=10, padx=10)

    # Save and Cancel buttons at the bottom
    button_frame = tk.Frame(content_frame)
    apply_theme(button_frame, current_theme)
    button_frame.pack(fill="x", padx=20, pady=20)


    # Function to save all settings
    def save_all_settings():
        # Collect all settings
        new_settings = {
            "theme": theme_var.get(),
            "font_size": font_var.get(),
            "card_order": order_var.get(),
            "auto_reveal_time": reveal_var.get(),
            "notifications_enabled": notif_var.get(),
            "sound_enabled": sound_var.get(),
            "backup_frequency": "weekly",  # Default value
            "auto_save": True  # Default value
        }

        # Save settings
        if save_user_settings(logged_in_username, new_settings):
            messagebox.showinfo("Success",
                                "Settings saved successfully! Changes will be applied to all pages.")
            # Return to dashboard
            open_page("dashboard")
        else:
            messagebox.showerror("Error", "Failed to save settings.")


    # Save button
    save_btn = tk.Button(
        button_frame,
        text="Save Changes",
        command=save_all_settings,
        padx=20,
        pady=10
    )
    save_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(save_btn, user_settings["font_size"], "button")
    save_btn.pack(side=tk.LEFT, padx=5)

    # Cancel button
    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        command=lambda: open_page("dashboard"),
        padx=20,
        pady=10
    )
    cancel_btn.config(bg=theme_colors["button_bg"], fg=theme_colors["button_fg"])
    apply_font_size(cancel_btn, user_settings["font_size"], "button")
    cancel_btn.pack(side=tk.RIGHT, padx=5)

    # Apply theme to all widgets
    apply_theme(root, current_theme)

    # Update all buttons with the button_bg color
    update_button_colors(current_theme)

    # Make sure the Settings button stays highlighted with yellow and black text
    for btn_text, (btn, page) in buttons.items():
        if btn_text == "⚙️ Settings":
            btn.config(bg=THEMES[current_theme]["highlight"], fg="black")  # Force the yellow highlight with black text

    # Run the application
    root.mainloop()
