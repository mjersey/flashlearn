import subprocess
import tkinter as tk
from tkinter import ttk
import os
import json
import time
import datetime
import math
from PIL import Image, ImageTk, ImageDraw
from settings import get_current_settings, apply_theme, apply_font_size

# Constants
PROGRESS_FOLDER = "user_progress"
DECKS_FOLDER = "user_decks"
os.makedirs(PROGRESS_FOLDER, exist_ok=True)
os.makedirs(DECKS_FOLDER, exist_ok=True)


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
    root.destroy()
    subprocess.run(["python", f"{page}.py"])


def sign_out():
    if os.path.exists("current_user.txt"):
        os.remove("current_user.txt")
    root.destroy()
    import sign_in


def get_logged_in_user():
    try:
        with open("current_user.txt", "r") as user_file:
            data = user_file.read().strip().split(",")
            return (data + [None])[:4]  # Ensure four elements (username, email, password, profile_pic)
    except FileNotFoundError:
        return "Guest", "No Email", "No Password", None


def get_user_decks(username):
    """Load saved decks from file for the current user"""
    decks_file = os.path.join(DECKS_FOLDER, f"{username}_decks.json")
    if os.path.exists(decks_file):
        try:
            with open(decks_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading decks: {e}")
    return []


def get_user_progress(username):
    """Get progress data for the user"""
    progress_file = os.path.join(PROGRESS_FOLDER, f"{username}_progress.json")
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading progress: {e}")
    return {}


def calculate_weekly_streak():
    """Calculate cards studied per day for the last week"""
    username = get_logged_in_user()[0]
    progress_data = get_user_progress(username)

    # Initialize daily counts for the last 7 days
    today = datetime.datetime.now()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    daily_counts = {day: 0 for day in days}

    # Go through all deck progress
    for deck_title, deck_progress in progress_data.items():
        if 'last_viewed' in deck_progress:
            try:
                # Parse the last viewed timestamp
                last_viewed = datetime.datetime.strptime(deck_progress['last_viewed'], "%Y-%m-%d %H:%M:%S")

                # Check if it's within the last 7 days
                days_ago = (today - last_viewed).days
                if 0 <= days_ago < 7:
                    # Get the day of week (0 = Monday, 6 = Sunday)
                    day_of_week = last_viewed.weekday()
                    day_name = days[day_of_week]

                    # Add the cards viewed on that day
                    daily_counts[day_name] += deck_progress.get('cards_viewed', 0)
            except Exception as e:
                print(f"Error parsing date: {e}")

    return daily_counts


def calculate_overall_progress():
    """Calculate overall progress across all decks"""
    username = get_logged_in_user()[0]
    progress_data = get_user_progress(username)
    decks = get_user_decks(username)

    total_cards = 0
    mastered_cards = 0

    for deck in decks:
        deck_title = deck.get('title', '')
        card_count = deck.get('card_count', 0)
        total_cards += card_count

        # Get progress for this deck
        deck_progress = progress_data.get(deck_title, {})
        correct_answers = deck_progress.get('correct_answers', 0)

        # Count cards as mastered if they've been answered correctly
        mastered_cards += min(correct_answers, card_count)

    # Calculate percentage
    percentage = (mastered_cards / total_cards * 100) if total_cards > 0 else 0

    return {
        'total_cards': total_cards,
        'mastered_cards': mastered_cards,
        'percentage': percentage
    }


def get_deck_progress():
    """Get progress for individual decks"""
    username = get_logged_in_user()[0]
    progress_data = get_user_progress(username)
    decks = get_user_decks(username)

    deck_progress = []

    for deck in decks:
        deck_title = deck.get('title', '')
        card_count = deck.get('card_count', 0)

        # Get progress for this deck
        progress = progress_data.get(deck_title, {})
        correct_answers = progress.get('correct_answers', 0)

        # Calculate percentage
        percentage = (correct_answers / card_count * 100) if card_count > 0 else 0

        deck_progress.append({
            'title': deck_title,
            'card_count': card_count,
            'correct_answers': correct_answers,
            'percentage': percentage
        })

    # Sort by percentage (highest first)
    deck_progress.sort(key=lambda x: x['percentage'], reverse=True)

    return deck_progress


def create_circular_progress(canvas, percentage, size=100, line_width=10):
    """Create a circular progress indicator on a canvas"""
    # Calculate coordinates
    x0 = y0 = line_width // 2
    x1 = y1 = size - line_width // 2

    # Draw background circle
    canvas.create_oval(x0, y0, x1, y1, outline="#E0E0E0", width=line_width, fill="white")

    # Draw progress arc
    start_angle = 90  # Start from top (90 degrees)
    extent_angle = 3.6 * percentage  # 3.6 degrees per percentage point (360 / 100)
    canvas.create_arc(x0, y0, x1, y1, start=start_angle, extent=extent_angle,
                      outline="#FFD700", width=line_width, style="arc")

    # Add percentage text in the center - rounded to whole number
    canvas.create_text(size // 2, size // 2, text=f"{int(percentage)}%",
                       font=("Arial", 14, "bold"))


def create_progress_bar(parent, percentage, width=400, height=20):
    """Create a progress bar with the given percentage"""
    # Create a frame to hold the progress bar
    frame = tk.Frame(parent, width=width, height=height, bg="#E0E0E0")
    frame.pack_propagate(False)

    # Create the progress indicator
    progress_width = int(width * percentage / 100)
    progress = tk.Frame(frame, width=progress_width, height=height, bg="#76c442")

    # Pack the frames
    frame.pack(fill="x", expand=True)
    progress.pack(side="left", fill="y")

    return frame


def get_progress_rating(percentage):
    """Get a rating based on the progress percentage"""
    if percentage >= 90:
        return "Excellent!"
    elif percentage >= 75:
        return "Great Job!"
    elif percentage >= 50:
        return "Good Progress!"
    elif percentage >= 25:
        return "Keep Going!"
    else:
        return "Just Starting!"


if __name__ == "__main__":
    root = tk.Tk()
    root.title("FlashLearn - Progress")

    # Set the window size
    window_width = 1000
    window_height = 700

    # Center the main window
    center_window(root, window_width, window_height)

    # Get user data
    logged_in_username, logged_in_email, logged_in_password, profile_picture_path = get_logged_in_user()

    # Get user settings
    settings = get_current_settings()
    theme = settings["theme"]
    font_size = settings["font_size"]

    # Apply theme to root window
    apply_theme(root, theme)
    root.resizable(False, False)


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
    sidebar = tk.Frame(root, width=220, height=600, highlightthickness=0 if theme == "dark" else 2)
    apply_theme(sidebar, theme, "sidebar")
    sidebar.pack_propagate(False)  # Prevent resizing
    sidebar.pack(side="left", fill="y")

    # FlashLearn Title
    title_label = tk.Label(sidebar, text="FlashLearn")
    apply_theme(title_label, theme, "sidebar")
    apply_font_size(title_label, font_size, "title")
    title_label.pack(pady=20)

    # Sidebar Buttons Configuration
    menu_items = {
        "⚫ Profile": "profile",
        "📖 My Cards": "dashboard",
        "🔥 Progress": None,
        "⚙️ Settings": "settings"
    }

    buttons = {}


    def select_menu(selected):
        """ Highlights the selected menu item and resets others """
        for btn_text, (btn, page) in buttons.items():
            if btn_text == selected:
                apply_theme(btn, theme, "highlight")
                apply_font_size(btn, font_size, "subtitle")
            else:
                apply_theme(btn, theme, "sidebar")
                apply_font_size(btn, font_size, "regular")


    # Create Sidebar Buttons with Navigation
    for text, page in menu_items.items():
        btn = tk.Button(
            sidebar, text=text, bd=0,
            anchor="w", padx=20, width=20,
            command=lambda t=text, p=page: open_page(p) if p else select_menu(t)
        )
        apply_theme(btn, theme, "sidebar")
        apply_font_size(btn, font_size, "regular")
        btn.pack(pady=5)
        buttons[text] = (btn, page)  # Store button references

    # Default: Select "Progress"
    select_menu("🔥 Progress")

    # Sign Out Button
    sign_out_btn = tk.Button(sidebar, text="↩ Sign Out", bd=0,
                             anchor="w", padx=20, width=20, command=sign_out)
    apply_theme(sign_out_btn, theme, "sidebar")
    apply_font_size(sign_out_btn, font_size, "regular")
    sign_out_btn.pack(pady=30, side="bottom")

    # Main Content Frame
    content_frame = tk.Frame(root, width=680, height=600)
    apply_theme(content_frame, theme)
    content_frame.pack(side="right", fill="both", expand=True)

    # Progress Title
    progress_label = tk.Label(content_frame, text="Progress")
    apply_theme(progress_label, theme)
    apply_font_size(progress_label, font_size, "title")
    progress_label.pack(pady=20)

    # Profile Icon Section (Upper Right)
    profile_icon_label = tk.Label(root)
    apply_theme(profile_icon_label, theme)
    profile_icon_label.place(x=window_width - 60, y=10)  # Place icon 10px from the top-right corner

    # Call the function to display the profile icon
    display_profile_icon()

    # Get overall progress
    overall_progress = calculate_overall_progress()
    percentage = overall_progress['percentage']
    mastered_cards = overall_progress['mastered_cards']
    total_cards = overall_progress['total_cards']

    # Main progress section
    main_progress_frame = tk.Frame(content_frame, bg="white", bd=1, relief="solid", padx=20, pady=20)
    main_progress_frame.pack(fill="x", padx=20, pady=10)

    # Progress rating
    rating_text = get_progress_rating(percentage)
    rating_label = tk.Label(main_progress_frame, text=rating_text, font=("Arial", 18, "bold"), bg="white")
    rating_label.pack(anchor="w")

    # Progress percentage - rounded to whole number
    percentage_label = tk.Label(main_progress_frame, text=f"{int(percentage)}%", font=("Arial", 14), bg="white")
    percentage_label.pack(anchor="w", pady=(5, 10))

    # Progress bar
    progress_bar = create_progress_bar(main_progress_frame, percentage, width=600)

    # Progress text
    progress_text = tk.Label(main_progress_frame,
                             text=f"You've mastered {mastered_cards}/{total_cards} cards. Keep up the good work!",
                             font=("Arial", 12), bg="white")
    progress_text.pack(anchor="w", pady=(10, 0))

    # Weekly streak section
    weekly_frame = tk.Frame(content_frame, bg="white", padx=20, pady=10)
    weekly_frame.pack(fill="x", padx=20, pady=10)

    # Header with title and details button
    weekly_header = tk.Frame(weekly_frame, bg="white")
    weekly_header.pack(fill="x")

    weekly_title = tk.Label(weekly_header, text="Weekly Streak", font=("Arial", 14, "bold"), bg="white")
    weekly_title.pack(side="left")

    details_btn = tk.Button(weekly_header, text="Details", font=("Arial", 10),
                            bg="#EEEEEE", relief="flat", padx=10, pady=2)
    details_btn.pack(side="right")

    # Weekly chart frame
    chart_frame = tk.Frame(weekly_frame, bg="white", height=150, pady=10)
    chart_frame.pack(fill="x", pady=10)

    # Get weekly streak data
    weekly_data = calculate_weekly_streak()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Find the maximum value for scaling
    max_value = max(weekly_data.values()) if weekly_data.values() else 1
    if max_value == 0:
        max_value = 1  # Avoid division by zero

    # Create bars for each day
    bar_width = 50
    bar_spacing = 20
    bar_max_height = 120

    for i, day in enumerate(days):
        # Create a frame for this day
        day_frame = tk.Frame(chart_frame, bg="white")
        day_frame.pack(side="left", padx=bar_spacing // 2)

        # Calculate bar height based on value
        value = weekly_data[day]
        bar_height = int((value / max_value) * bar_max_height)
        if bar_height < 5 and value > 0:
            bar_height = 5  # Minimum visible height if there's any activity

        # Create the bar
        bar = tk.Frame(day_frame, width=bar_width, height=bar_height, bg="#FFA500")
        bar.pack(side="top")

        # Add spacing to align bars at the bottom
        spacer = tk.Frame(day_frame, width=bar_width, height=bar_max_height - bar_height, bg="white")
        spacer.pack(side="top")

        # Add day label
        day_label = tk.Label(day_frame, text=day, bg="white")
        day_label.pack(side="top", pady=(5, 0))

    # Individual deck progress section
    deck_progress_data = get_deck_progress()

    # Show the top performing deck
    if deck_progress_data:
        top_deck = deck_progress_data[0]

        deck_frame = tk.Frame(content_frame, bg="white", bd=1, relief="solid", padx=20, pady=15)
        deck_frame.pack(fill="x", padx=20, pady=10)

        # Deck title
        deck_title = tk.Label(deck_frame, text=top_deck['title'],
                              font=("Arial", 14, "bold"), bg="white")
        deck_title.pack(anchor="w")

        # Deck progress - just show text, no circular progress
        deck_progress_text = tk.Label(deck_frame,
                                      text=f"{top_deck['correct_answers']}/{top_deck['card_count']} cards",
                                      font=("Arial", 12), bg="white", fg="#666666")
        deck_progress_text.pack(anchor="w", pady=(5, 0))

    # Run the application
    root.mainloop()
