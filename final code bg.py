import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import time
import os
from datetime import datetime
import re # Added for regex in prompt window
import webbrowser # <<< ADDED for opening QP links
from PIL import Image, ImageTk
from tkcalendar import DateEntry

# =========================================================================
# Aesthetic and Styling Definitions (Light Theme)
# =========================================================================

# Light Theme Color Palette and Fonts
BG_PRIMARY = "#f0f0f0"  # Light gray background
GLASS_BG = "#e9e9e9"  # A light, semi-transparent background for the main frame
GLASS_ALPHA = 0.6
GLASS_BORDER = "#d1d1d1" # Lighter border color
TEXT_DARK = "#333333"  # Dark text color for contrast
TEXT_LIGHT = "#555555" # A slightly lighter dark gray
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_INPUT = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 13, "bold")
FONT_LINK = ("Segoe UI", 10, "underline")
FONT_SMALL = ("Segoe UI", 9)

# Dashboard Color Palette and Fonts (Light Theme)
DASH_BG = "#f0f0f0"
DASH_HEADER_BG = "#d9d9d9"
DASH_TEXT_COLOR = "#333333"
LOGO_COLOR = "#0056b3" # A deep blue for the logo

# A new selection of colors for the cards that work well on a light background
CARD_COLORS = ["#1e88e5", "#00acc1", "#ff7043", "#7e57c2", "#ffca28", "#42a5f5", "#ef5350", "#2ecc71"]
CARD_TEXT_COLOR = "#ffffff"
CARD_PLUS_COLOR = "#ffffff"
CARD_FONT = ("Times New Roman", 18, "bold")

# Button colors - adjusted for a light theme
BTN_NORMAL = "#007bff"
BTN_HOVER = "#0056b3"
BTN_DANGER = "#dc3545"
BTN_DANGER_HOVER = "#c82333"

# =========================================================================
# Global variables to manage application state
# =========================================================================
main_window = None
dashboard_window = None
entry_username = None
entry_password = None
entry_grade = None
entry_section = None
cards_container = None
# List to hold the Tkinter variables for the class checkboxes
checkbox_vars = []
# Global variable to hold the card data for the current user, used for responsive rendering
current_cards_data = []

# Global vars to handle data of records being deleted
student_checkbox_vars = [] # Global list to hold student deletion checkbox data
ROMAN_MAP = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'}
TILE_WIDTH = 10 
TILE_HEIGHT = 5
TILE_BG = "#d9d9d9"
TILE_FG = "#333333"
# Admin specific dashboard cards
ADMIN_CARDS = [
    {"text": "Add Student", "color": CARD_COLORS[0], "icon": "➕", "command": lambda: add_student_window()},
    {"text": "Create Class", "color": CARD_COLORS[1], "icon": "📚", "command": lambda: create_class_window()},
    {"text": "View Class Details", "color": CARD_COLORS[7], "icon": "📖", "command": lambda: view_class_details_window()},
    {"text": "Enter Attendance", "color": CARD_COLORS[2], "icon": "📝", "command": lambda: enter_attendance_window()},
    {"text": "Update Question Paper", "color": CARD_COLORS[4], "icon": "❓", "command": lambda: upload_question_paper_window()},
    {"text": "View Question Papers", "color": CARD_COLORS[5], "icon": "📄", "command": lambda: view_all_question_papers_window()},
    {"text": "Update Circular", "color": CARD_COLORS[4], "icon": "🎟", "command": lambda: update_circular_window()},
    {"text": "Remove student", "color": CARD_COLORS[6], "icon": "❌", "command": lambda: remove_class_window()},
    {"text": "Remove class", "color": CARD_COLORS[2], "icon": "✂", "command": lambda: delete_entire_class_selector()},
]

# Student specific dashboard cards
STUDENT_CARDS = [
    # Updated command to call the new attendance function with the student's ID
    {"text": "View Attendance", "color": CARD_COLORS[0], "icon": "📝", "command": lambda student_id: view_student_attendance_window(student_id)},
    {"text": "View Question Papers", "color": CARD_COLORS[2], "icon": "📄", "command": lambda student_id: view_student_question_papers_window(student_id)},
    {"text": "View Circular", "color": CARD_COLORS[3], "icon": "📢", "command": lambda student_id: view_student_circular_window(student_id)},
]

# CRITICAL: Holds the background image object to prevent garbage collection
global bg_image_ref 
bg_image_ref = None 

# The image item ID on the canvas (can reuse the old 'gif_item' for this)
gif_item = None
# =========================================================================
# Helper Functions
# =========================================================================
def on_enter(e):
    if e.widget.cget('bg') == BTN_NORMAL:
        e.widget['background'] = BTN_HOVER
    elif e.widget.cget('bg') == BTN_DANGER:
        e.widget['background'] = BTN_DANGER_HOVER

def on_leave(e):
    if e.widget.cget('bg') == BTN_HOVER:
        e.widget['background'] = BTN_NORMAL
    elif e.widget.cget('bg') == BTN_DANGER_HOVER:
        # Correctly return to the base danger color
        e.widget['background'] = BTN_DANGER

def get_db_connection():
    """
    Establishes and returns a MySQL database connection.
    NOTE: The password is set to 'root' as requested by the user.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root", # <<< UPDATED PASSWORD HERE
        database="main",
        ssl_disabled=True
    )

def center_window(window):
    """Centers the given window on the screen."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draws a rounded rectangle on a canvas."""
    points = [x1 + radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def open_link(url, title):
    """Opens a URL in the default web browser."""
    # Ensure URL is not empty and starts with a protocol for security and functionality
    if url and (url.startswith("http://") or url.startswith("https://")):
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("Web Browser Error", f"Could not open the link for {title}. Error: {e}")
    elif url:
         messagebox.showwarning("Link Error", f"The link for {title} appears invalid (must start with http:// or https://).")
    else:
        messagebox.showwarning("Link Error", f"No link available for {title}.")

# =========================================================================
# Login Window Functions
# =========================================================================
def show_login_window():
    """Displays the login window with a DYNAMICALLY RESIZING background image."""
    global main_window, dashboard_window, entry_username, entry_password, bg_image_ref, gif_item
    # We need a separate global to hold the raw PIL image (before converting to Tkinter)
    global raw_pil_image 
    
    if dashboard_window:
        dashboard_window.destroy()

    if not main_window:
        main_window = tk.Tk()
        main_window.title("School Management System")
        try:
            main_window.state('zoomed')
        except:
            main_window.attributes('-fullscreen', True)
        main_window.resizable(True, True)

    for widget in main_window.winfo_children():
        widget.destroy()

    main_window.title("Admin Login")

    # Canvas
    main_canvas = tk.Canvas(main_window, bg="black", highlightthickness=0)
    main_canvas.pack(fill="both", expand=True)

    # ---------------------------------------------------------------------
    # 🖼️ DYNAMIC BACKGROUND IMAGE LOGIC (Requires Pillow)
    # ---------------------------------------------------------------------
    image_filename = r"C:\Users\KB KRISHNA\Desktop\krishna\dell-krishna\12th\csproj\primebg.png"
    raw_pil_image = None # Reset

    if os.path.exists(image_filename):
        try:
            # Load the image using PIL (Pillow)
            raw_pil_image = Image.open(image_filename)
        except Exception as e:
            print(f"❌ Pillow Error: {e}")
    else:
        print("⚠️ Warning: Image file not found.")
    # ---------------------------------------------------------------------

    # Login Frame (Hidden initially)
    login_frame = tk.Frame(main_window, bg=GLASS_BG)
    
    tk.Label(login_frame, text="Log in", font=FONT_TITLE, bg=GLASS_BG, fg=TEXT_DARK).pack(pady=(20, 10))

    username_frame = tk.Frame(login_frame, bg=GLASS_BG); username_frame.pack(fill="x", padx=20, pady=5)
    tk.Label(username_frame, text="Username:", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).pack(side="left")
    entry_username = tk.Entry(username_frame, font=FONT_INPUT, bg=BG_PRIMARY, fg=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1); entry_username.pack(side="right", fill="x", expand=True, padx=(5, 0))

    password_frame = tk.Frame(login_frame, bg=GLASS_BG); password_frame.pack(fill="x", padx=20, pady=5)
    tk.Label(password_frame, text="Password:", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).pack(side="left")
    entry_password = tk.Entry(password_frame, show="*", font=FONT_INPUT, bg=BG_PRIMARY, fg=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1); entry_password.pack(side="right", fill="x", expand=True, padx=(5, 0))

    login_btn = tk.Button(login_frame, text="Log in", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=TEXT_DARK,
                          activebackground=BTN_HOVER, activeforeground=TEXT_DARK,
                          relief="flat", bd=0, width=20, pady=10,
                          command=check_login); login_btn.pack(pady=(20, 5))
    login_btn.bind("<Enter>", on_enter); login_btn.bind("<Leave>", on_leave)

    # --- DYNAMIC RESIZE FUNCTION ---
    def resize_content(event):
        global bg_image_ref, gif_item
        
        w = event.width
        h = event.height
        cx = w / 2
        cy = h / 2
        
        # 1. Dynamically Resize Background using Pillow
        if raw_pil_image:
            try:
                # Resize the PIL image to match the window size exactly
                resized_pil = raw_pil_image.resize((w, h), Image.Resampling.LANCZOS)
                
                # Convert back to Tkinter image
                new_bg_image = ImageTk.PhotoImage(resized_pil)
                
                # Save reference and update canvas
                bg_image_ref = new_bg_image 
                main_canvas.create_image(0, 0, image=bg_image_ref, anchor="nw")
            except Exception as e:
                pass

        # 2. Redraw Glass Panel
        rect_w, rect_h = 400, 300
        main_canvas.delete("glass_rect")
        draw_rounded_rectangle(main_canvas, cx - rect_w/2, cy - rect_h/2, cx + rect_w/2, cy + rect_h/2, 20, fill=GLASS_BG, outline=GLASS_BORDER, tags="glass_rect")
        
        # 3. Center Login Frame
        login_frame.place(relx=0.5, rely=0.5, anchor="center", width=360, height=260)

    # Bind resize event
    main_canvas.bind("<Configure>", resize_content)

    main_window.lift()
    main_window.attributes('-topmost', True)
    main_window.after_idle(main_window.attributes, '-topmost', False)

def check_login():
    """Handles the login logic, checks credentials against the database. (REVERTED TO STRING PASSWORD)"""
    global entry_username, entry_password
    username = entry_username.get().strip()
    password = entry_password.get().strip() # Password is now a plain string
    
    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    try:
        # User ID must still be an integer
        userid = int(username)
        # The password remains a string (password)
    except ValueError:
        messagebox.showerror("Input Error", "User ID must be an integer.")
        return

    try:
        db = get_db_connection()
        cursor = db.cursor()
        # The query uses the plain string password
        query = "SELECT role FROM login WHERE userid = %s AND password = %s"
        cursor.execute(query, (userid, password))
        result = cursor.fetchone()

        if result:
            role = result[0]
            messagebox.showinfo("Login Successful", f"Welcome, {username}! Role: {role.capitalize()}")
            main_window.withdraw()
            show_dashboard_window(username, role)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
        
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# =========================================================================
# Dashboard Window Functions
# =========================================================================
def create_card(parent_frame, card_text, card_color, icon_text, command, **kwargs):
    """
    Creates a stylized card that zooms when hovered, with guaranteed centered contents.
    """
    # Parent frame acts as the container
    card_frame = tk.Frame(parent_frame, bg=card_color)
    
    # The canvas draws the content
    card_canvas = tk.Canvas(card_frame, bg=card_color, highlightthickness=0, cursor="hand2")
    card_canvas.pack(fill="both", expand=True, padx=5, pady=5)

    # Card dimensions are roughly 220px wide (110 is the center X)
    CENTER_X = 140
    TEXT_WRAP_WIDTH = 200 # Ensures text stays within the card boundaries

    # 1. Icon/Illustration (ID 1) - Positioned slightly higher
    card_canvas.create_text(
        CENTER_X, 85, # Adjusted Y position up from 85 to 75
        text=icon_text,
        font=("Times New Roman", 60),
        fill=CARD_TEXT_COLOR,
        justify="center",
        anchor="center" # Essential for horizontal centering
    )

    # 2. Card Text (ID 2) - Positioned lower to balance the icon
    card_canvas.create_text(
        CENTER_X, 160,
        text=card_text,
        font=("Times New Roman", 18, "bold"),
        fill=CARD_TEXT_COLOR,
        justify="center",
        anchor="center", # Essential for horizontal centering
        width=TEXT_WRAP_WIDTH # Ensures text wraps correctly, helping alignment
    )
    
    # --- BINDINGS FOR ANIMATION ---
    card_canvas.bind("<Enter>", lambda e: animate_card(card_canvas, True))
    card_canvas.bind("<Leave>", lambda e: animate_card(card_canvas, False))

    # --- CLICK HANDLING ---
    if 'student_id' in kwargs:
        card_canvas.bind("<Button-1>", lambda e: command(kwargs['student_id']))
    else:
        card_canvas.bind("<Button-1>", lambda e: command()) 
        
    return card_frame

def show_dashboard_window(username, role):
    """
    Creates and displays the main dashboard UI in full screen (maximized).
    """
    global dashboard_window, cards_container, current_cards_data
    dashboard_window = tk.Toplevel(main_window)
    dashboard_window.title(f"{role.capitalize()} Dashboard")
    
    # --- FULL SCREEN LOGIC START ---
    try:
        # Windows/Linux maximize
        dashboard_window.state('zoomed')
    except:
        # Fallback for systems that don't support 'zoomed'
        dashboard_window.attributes('-fullscreen', True)
    # --- FULL SCREEN LOGIC END ---
    
    dashboard_window.configure(bg=DASH_BG)
    dashboard_window.lift()
    dashboard_window.grab_set()

    # Main frame for the dashboard content
    main_frame = tk.Frame(dashboard_window, bg=DASH_BG)
    main_frame.pack(fill="both", expand=True, padx=40, pady=40)

    # --- Header with User ID and Logout Button ---
    header_frame = tk.Frame(main_frame, bg=DASH_BG)
    header_frame.pack(fill="x", pady=(0, 20))

    # User Welcome/ID Label (Left)
    welcome_text = f"Welcome, {role.capitalize()} (ID: {username})"
    tk.Label(header_frame, text=welcome_text, font=("Arial", 24, "bold"), fg=LOGO_COLOR, bg=DASH_BG).pack(side="left", padx=10)

    # Logout button (Right)
    logout_btn = tk.Button(header_frame, text="Logout", font=FONT_BUTTON,
                           bg=BTN_DANGER, fg=CARD_TEXT_COLOR, # White text for better contrast
                           activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                           relief="flat", bd=0, width=10, pady=5,
                           command=logout)
    logout_btn.pack(side="right", padx=10)
    logout_btn.bind("<Enter>", on_enter)
    logout_btn.bind("<Leave>", on_leave)
    
    # Set WM_DELETE_WINDOW protocol to logout function
    dashboard_window.protocol("WM_DELETE_WINDOW", logout)
    # -----------------------------------------------------

    # --- Scrollable Card Container Setup ---
    # Create a canvas and scrollbar
    card_canvas = tk.Canvas(main_frame, bg=DASH_BG, highlightthickness=0)
    card_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=card_canvas.yview)

    # Pack canvas and scrollbar
    # Canvas takes all remaining space, scrollbar is on the right
    card_canvas.pack(side="left", fill="both", expand=True)
    card_scrollbar.pack(side="right", fill="y")

    # Configure the canvas to use the scrollbar
    card_canvas.configure(yscrollcommand=card_scrollbar.set)

    # Create the frame *inside* the canvas where the cards will live
    cards_container = tk.Frame(card_canvas, bg=DASH_BG)
    # Place the frame at (0, 0) inside the canvas
    canvas_frame_id = card_canvas.create_window((0, 0), window=cards_container, anchor="nw")

    # This is crucial: update the scroll region whenever the inner frame size changes
    def update_scroll_region(event):
        # Set the container width to match the canvas width, ensuring symmetry and proper expansion
        card_canvas.itemconfigure(canvas_frame_id, width=event.width)
        # Update the scroll region based on the content size
        card_canvas.configure(scrollregion=card_canvas.bbox("all"))

    cards_container.bind("<Configure>", update_scroll_region)
    # Bind resize event on the Canvas itself to manage the internal frame's width when the window resizes
    card_canvas.bind('<Configure>', update_scroll_region)
    # ---------------------------------------

    if role == 'admin' or role == 'teacher':
        current_cards_data = ADMIN_CARDS
    elif role == 'student':
        current_cards_data = STUDENT_CARDS
    else:
        current_cards_data = [] # No cards for unrecognized roles

    # Now we render the cards once in the fixed grid.
    # The 'after' call ensures the main_frame has rendered and has a proper width before calculating the grid.
    dashboard_window.after(100, lambda: render_cards(current_cards_data, role, username))


def render_cards(card_data, role, username):
    """Renders the cards in a fixed, symmetrical 4-column grid."""
    global cards_container
    # Clear existing cards
    for widget in cards_container.winfo_children():
        widget.destroy()

    # Fixed number of columns as requested
    num_cols = 4
    row = 0
    col = 0

    # Ensure the columns are symmetrically weighted
    for i in range(num_cols):
        cards_container.grid_columnconfigure(i, weight=1)

    for data in card_data:
        # Check the role and pass the student_id if applicable
        if role == 'student':
            # Note: We pass the student ID (which is the username) to the command
            card = create_card(cards_container, data["text"], data["color"], data["icon"], data["command"], student_id=username)
        else:
            card = create_card(cards_container, data["text"], data["color"], data["icon"], data["command"])
        
        # Place the card in the grid
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Increment column and wrap to the next row if the limit is reached
        col += 1
        if col >= num_cols:
            col = 0
            row += 1

    # Ensure all used rows have weight for vertical expansion (though less critical for fixed height cards)
    for i in range(row + 1):
        cards_container.grid_rowconfigure(i, weight=1)
    
    # Crucial: Explicitly update the scroll region after rendering all widgets
    # This prevents the scrollbar from being empty initially.
    cards_container.update_idletasks()
    cards_container.master.configure(scrollregion=cards_container.master.bbox("all"))


def logout():
    """Logs out the user and returns to the login window."""
    global dashboard_window
    dashboard_window.destroy()
    show_login_window()

# =========================================================================
# Card Animation Functions (Zoom Effect)
# =========================================================================
def animate_card(canvas, is_hovering):
    """
    Animates the card contents to create a zoom/resize effect.
    ID 1 = Icon, ID 2 = Text
    """
    if is_hovering:
        # ZOOM IN: Increase font size and add border
        canvas.itemconfig(1, font=("Times New Roman", 70)) # Icon grows
        canvas.itemconfig(2, font=("Times New Roman", 20, "bold")) # Text grows
        canvas.config(highlightthickness=4, highlightbackground="#ffffff")
    else:
        # ZOOM OUT: Reset to original size and remove border
        canvas.itemconfig(1, font=("Times New Roman", 60)) # Original Icon size
        canvas.itemconfig(2, font=("Times New Roman", 18, "bold")) # Original Text size
        canvas.config(highlightthickness=0)


# =========================================================================
# Sub-window Functions
# =========================================================================
def create_new_window(title, message):
    """A generic function to create a new window for any button."""
    new_window = tk.Toplevel(dashboard_window)
    new_window.title(title)
    new_window.geometry("400x300")
    new_window.configure(bg=DASH_BG)
    new_window.transient(dashboard_window)
    new_window.grab_set()

    frame = tk.Frame(new_window, bg=DASH_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text=title, font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(20, 10))
    tk.Label(frame, text=message, font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack(pady=10)

    # Close button
    close_btn = tk.Button(frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=new_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

def create_class_window():
    """
    Creates a new window for entering class details using a grid layout.
    """
    global entry_grade, entry_section
    class_window = tk.Toplevel(dashboard_window)
    class_window.title("Create New Class")
    class_window.geometry("400x300")
    class_window.configure(bg=DASH_BG)
    class_window.transient(dashboard_window)
    # We call center_window immediately to ensure the window has a size
    center_window(class_window)

    main_frame = tk.Frame(class_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both")

    # Header
    tk.Label(main_frame, text="Create Class", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).grid(row=0, column=0, columnspan=2, pady=(20, 10))

    # Grade Input
    tk.Label(main_frame, text="Grade:", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_grade = tk.Entry(main_frame, font=FONT_INPUT, bg=GLASS_BG, fg=TEXT_DARK, insertbackground=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1)
    entry_grade.grid(row=1, column=1, padx=5, pady=5)

    # Section Input
    tk.Label(main_frame, text="Section:", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_section = tk.Entry(main_frame, font=FONT_INPUT, bg=GLASS_BG, fg=TEXT_DARK, insertbackground=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1)
    entry_section.grid(row=2, column=1, padx=5, pady=5)

    # Configure grid columns to center the content
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)

    # Save button
    save_btn = tk.Button(main_frame, text="Save Class", font=FONT_BUTTON,
                         bg=BTN_NORMAL, fg=DASH_TEXT_COLOR,
                         activebackground=BTN_HOVER, activeforeground=DASH_TEXT_COLOR,
                         relief="flat", bd=0, pady=10, width=15,
                         command=lambda: save_class(class_window))
    save_btn.grid(row=3, column=0, columnspan=2, pady=(20, 5))
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    # Place the grab_set call at the very end to ensure the window is viewable.
    class_window.grab_set()

def save_class(parent_window):
    """Saves a new class record to the database with a new, relatable class_id."""
    global entry_grade, entry_section
    grade_str = entry_grade.get().strip()
    section = entry_section.get().strip().upper()  # Ensure section is uppercase for consistency

    if not grade_str or not section:
        messagebox.showwarning("Input Error", "Please enter both Grade and Section.")
        return
    if not section.isalpha() or len(section) != 1:
        messagebox.showwarning("Input Error", "Section must be a single letter.")
        return
    try:
        grade = int(grade_str)
    except ValueError:
        messagebox.showwarning("Input Error", "Grade must be an integer.")
        return

    try:
        db = get_db_connection()
        cursor = db.cursor()

        # New logic: Generate a class_id based on grade and section
        # Convert section letter to its alphabetical position (A=1, B=2, ...)
        section_position = ord(section) - ord('A') + 1
        class_id = f"{grade_str}{section_position}"

        # Check for existing class_id to avoid collisions
        check_query = "SELECT class_id FROM class WHERE class_id = %s"
        cursor.execute(check_query, (class_id,))
        if cursor.fetchone():
            messagebox.showwarning("Duplicate Entry", f"Class ID {class_id} already exists. Please choose a different section.")
            return

        # Check if a class with the same grade and section already exists
        check_duplicate_query = "SELECT * FROM class WHERE grade = %s AND section = %s"
        cursor.execute(check_duplicate_query, (grade, section))
        if cursor.fetchone():
            messagebox.showwarning("Duplicate Entry", "A class with this grade and section already exists.")
            return

        insert_query = "INSERT INTO class (class_id, grade, section) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (class_id, grade, section))
        db.commit()
        messagebox.showinfo("Success", f"Class with ID {class_id} added successfully!")
        parent_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        db.rollback()
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def refresh_class_list(scrollable_frame, button_frame):
    """Recents the list of classes displayed in the remove class window."""
    global checkbox_vars
    # Clear existing widgets from the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    checkbox_vars.clear()

    # Re-fetch and display classes from the database
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT grade, section FROM class ORDER BY grade, section")
        classes = cursor.fetchall()

        if not classes:
            tk.Label(scrollable_frame, text="No classes found.", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).pack(pady=20, padx=20)
            button_frame.pack_forget() # Hide the button frame if no classes exist
        else:
            for grade, section in classes:
                class_entry_frame = tk.Frame(scrollable_frame, bg=GLASS_BG)
                class_entry_frame.pack(fill="x", pady=2, padx=5)
                var = tk.IntVar(value=0)
                checkbox_vars.append({"var": var, "grade": grade, "section": section})
                chk = tk.Checkbutton(class_entry_frame, text=f"Grade {grade} - Section {section}",
                                     variable=var, font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK,
                                     activebackground=GLASS_BG, selectcolor=GLASS_BG)
                chk.pack(side="left", padx=5)
            button_frame.pack(pady=10) # Ensure the button frame is visible

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching classes: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()


def to_roman(num):
    """Converts a number (1-12) to its Roman numeral representation."""
    return ROMAN_MAP.get(num, str(num))

def get_all_classes():
    """Fetches all distinct class grades and sections from the database."""
    classes = []
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # Fetch Grade and Section, ordered by Grade (numeric) and then Section (alphabetic)
        # Using the 'class' table as per the user's schema
        cursor.execute("SELECT DISTINCT grade, section FROM class ORDER BY grade ASC, section ASC")
        classes = cursor.fetchall()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching classes: {err}")
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()
    return classes

def delete_selected_students(student_ids_to_delete, grade, section, student_list_frame, student_canvas):
    """
    Deletes the selected students and all their associated records from the database.
    Performs cascading delete from attendance, login, and studentrec tables.
    """
    if not student_ids_to_delete:
        messagebox.showwarning("No Selection", "Please select at least one student to delete.")
        return

    # Prepare for SQL IN clause. Ensure all items in the tuple are integers.
    placeholders = ', '.join(['%s'] * len(student_ids_to_delete))
    id_tuple = tuple(int(id) for id in student_ids_to_delete)
    
    confirm_msg = f"Are you sure you want to permanently delete {len(id_tuple)} student(s) from class {grade}{section}? This will also delete their **login credentials and attendance records**."
    if not messagebox.askyesno("Confirm Deletion", confirm_msg):
        return

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # 1. Delete Attendance Records (dependent on student_id)
        # The same student_ids are used for all three tables
        delete_attendance_query = f"DELETE FROM attendance WHERE student_id IN ({placeholders})"
        cursor.execute(delete_attendance_query, id_tuple)
        
        # 2. Delete Login Records (dependent on student_id/userid)
        delete_login_query = f"DELETE FROM login WHERE userid IN ({placeholders})"
        cursor.execute(delete_login_query, id_tuple)
        
        # 3. Delete Student Record (the main record)
        delete_studentrec_query = f"DELETE FROM studentrec WHERE student_id IN ({placeholders})"
        cursor.execute(delete_studentrec_query, id_tuple)
        
        db.commit()
        messagebox.showinfo("Deletion Complete", f"Successfully deleted {len(id_tuple)} student(s) and all associated records.")
        
        # Refresh the student list (by destroying the old window and creating a new one)
        # To simplify refresh, we'll just destroy the student list frame content and call reload
        for widget in student_list_frame.winfo_children():
            widget.destroy()
        
        # Reload the remaining students by calling the function again
        student_list_frame.winfo_toplevel().destroy() # Close the student window
        show_students_for_deletion(grade, section, dashboard_window) # Reopen with fresh data

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error deleting students: {err}")
        if db:
            db.rollback()
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()


def show_students_for_deletion(grade, section, parent_window):
    """
    Creates a new window to display all students in a class with checkboxes for deletion.
    """
    global student_checkbox_vars
    student_checkbox_vars = [] # Reset global list for new window

    student_window = tk.Toplevel(parent_window)
    student_window.title(f"Manage Students: Class {to_roman(grade)}-{section}")
    student_window.geometry("800x600")
    student_window.configure(bg=DASH_BG)
    student_window.transient(parent_window)
    center_window(student_window)

    # Main frame setup
    main_frame = tk.Frame(student_window, bg=DASH_BG)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    title_text = f"Select Students in Class {to_roman(grade)}{section} for Deletion"
    tk.Label(main_frame, text=title_text, font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))

    # Frame for list and scrollbar
    list_container_frame = tk.Frame(main_frame, bg=GLASS_BG)
    list_container_frame.pack(fill="both", expand=True, pady=10, padx=10)

    # Canvas and Scrollbar setup
    student_canvas = tk.Canvas(list_container_frame, bg=GLASS_BG, highlightthickness=0)
    student_scrollbar = ttk.Scrollbar(list_container_frame, orient="vertical", command=student_canvas.yview)
    student_list_frame = tk.Frame(student_canvas, bg=GLASS_BG) # This is the scrollable content frame

    student_list_frame.bind(
        "<Configure>",
        lambda e: student_canvas.configure(
            scrollregion=student_canvas.bbox("all")
        )
    )

    student_canvas.create_window((0, 0), window=student_list_frame, anchor="nw")
    student_canvas.configure(yscrollcommand=student_scrollbar.set)
    student_canvas.pack(side="left", fill="both", expand=True)
    student_scrollbar.pack(side="right", fill="y")
    
    # Header Row
    header_font = ("Segoe UI", 12, "bold")
    col_config = [
        ("Select", 5), ("ID", 5), ("Name", 30), ("Phone", 15), ("Email", 30), ("DOB", 15)
    ]
    
    # Create header labels
    for i, (text, width) in enumerate(col_config):
        tk.Label(student_list_frame, text=text, font=header_font, bg=DASH_BG, fg=LOGO_COLOR, width=width, anchor="w", relief="flat").grid(row=0, column=i, padx=5, pady=5, sticky="w")
    
    # Fetch and display students
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT student_id, name, phone_number, email, date_of_birth FROM studentrec WHERE class = %s AND section = %s ORDER BY student_id ASC"
        cursor.execute(query, (grade, section))
        students = cursor.fetchall()
        
        if not students:
            tk.Label(student_list_frame, text="No students found in this class.", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_LIGHT).grid(row=1, column=0, columnspan=6, pady=20)
        
        # Data rows
        for i, student in enumerate(students):
            student_id, name, phone, email, dob = student
            row = i + 1
            
            var = tk.IntVar()
            student_checkbox_vars.append({
                'id': student_id,
                'var': var
            })

            # 0. Checkbox
            tk.Checkbutton(student_list_frame, variable=var, bg=GLASS_BG, activebackground=GLASS_BG).grid(row=row, column=0, sticky="w", padx=5)

            # 1. ID
            tk.Label(student_list_frame, text=student_id, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=5).grid(row=row, column=1, sticky="w", padx=5)

            # 2. Name
            tk.Label(student_list_frame, text=name, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=30).grid(row=row, column=2, sticky="w", padx=5)
            
            # 3. Phone
            tk.Label(student_list_frame, text=phone, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=15).grid(row=row, column=3, sticky="w", padx=5)

            # 4. Email
            tk.Label(student_list_frame, text=email, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=30).grid(row=row, column=4, sticky="w", padx=5)

            # 5. DOB
            tk.Label(student_list_frame, text=dob, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=15).grid(row=row, column=5, sticky="w", padx=5)
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching students: {err}")
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()
            
    # Button Frame
    button_frame = tk.Frame(main_frame, bg=DASH_BG)
    button_frame.pack(pady=10)

    # Delete Student Button
    def get_selected_student_ids():
        ids = [data['id'] for data in student_checkbox_vars if data['var'].get() == 1]
        return ids
    
    delete_btn = tk.Button(button_frame, text="Delete Selected Students", font=FONT_BUTTON,
                           bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                           activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                           relief="flat", bd=0, pady=10, width=25,
                           command=lambda: delete_selected_students(get_selected_student_ids(), grade, section, student_list_frame, student_canvas))
    delete_btn.pack(side="left", padx=10)
    delete_btn.bind("<Enter>", on_enter)
    delete_btn.bind("<Leave>", on_leave)

    # Close button
    close_btn = tk.Button(button_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=student_window.destroy)
    close_btn.pack(side="right", padx=10)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    student_window.grab_set()


def remove_class_window():
    """
    (MODIFIED) Creates the initial window to display classes in a tiled view, 
    cycling through the global CARD_COLORS list.
    """
    # NOTE: CARD_COLORS is assumed to be defined in your global scope.
    
    if not dashboard_window:
        messagebox.showerror("System Error", "Dashboard window not initialized. Cannot open manager.")
        return

    remove_window = tk.Toplevel(dashboard_window)
    remove_window.title("Manage Student Deletion by Class")
    remove_window.geometry("700x700")
    remove_window.configure(bg=DASH_BG)
    remove_window.transient(dashboard_window)
    center_window(remove_window)

    main_frame = tk.Frame(remove_window, bg=DASH_BG)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    tk.Label(main_frame, text="Select a Class to Manage Students", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 20))

    class_grid_frame = tk.Frame(main_frame, bg=DASH_BG)
    class_grid_frame.pack(pady=10)
    
    classes = get_all_classes()
    
    if not classes:
        tk.Label(class_grid_frame, text="No classes found in the database.", font=FONT_LABEL, bg=DASH_BG, fg=TEXT_LIGHT).pack(pady=50)
        
    COLUMNS = 5
    
    for i, (grade, section) in enumerate(classes):
        row = i // COLUMNS
        col = i % COLUMNS
        
        roman_grade = to_roman(grade) 
        display_text = f"Class\n{roman_grade}-{section}"
        
        # --- KEY CHANGE: Use CARD_COLORS for cycling ---
        # The length of CARD_COLORS is 8, ensuring a variety of colors.
        tile_color = CARD_COLORS[i % len(CARD_COLORS)]
        # --- ---------------------------------------- ---

        class_tile_btn = tk.Button(class_grid_frame, 
                                   text=display_text, 
                                   font=("Segoe UI", 16, "bold"),
                                   bg=tile_color,
                                   fg=CARD_TEXT_COLOR, # Use white text for contrast on dark colors
                                   activebackground=tile_color, 
                                   relief="raised", bd=2, 
                                   width=TILE_WIDTH, height=TILE_HEIGHT,
                                   wraplength=100,
                                   command=lambda g=grade, s=section: show_students_for_deletion(g, s, remove_window))
                                   
        class_tile_btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=remove_window.destroy)
    close_btn.pack(pady=(30, 10))
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    remove_window.grab_set()

def add_student_window():
    """
    Creates a new window to add a new student to the database.
    Updated to include input constraints and a calendar selector for DOB.
    """
    add_student_window = tk.Toplevel(dashboard_window)
    add_student_window.title("Add New Student")
    add_student_window.geometry("500x470") # Adjusted window size slightly
    add_student_window.configure(bg=DASH_BG)
    add_student_window.transient(dashboard_window)
    center_window(add_student_window)

    main_frame = tk.Frame(add_student_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both")

    tk.Label(main_frame, text="Add New Student", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(20, 10))

    # Form frame using grid for cleaner layout
    form_frame = tk.Frame(main_frame, bg=DASH_BG)
    form_frame.pack(padx=20, pady=10)

    # Dictionary to hold entry widgets for easy access
    student_entries = {}
    
    # Static fields (Entry widgets)
    labels_and_fields = [
        ("Student Name:", "entry_name", False),
        ("Password:", "entry_password", True),
        ("Class (Grade):", "entry_class", False),
        ("Section:", "entry_section", False),
        ("Phone Number (10-digit):", "entry_phone", False),
        ("Email ID:", "entry_email", False),
    ]
    for i, (label_text, entry_key, is_password) in enumerate(labels_and_fields):
        tk.Label(form_frame, text=label_text, font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        
        show_char = "*" if is_password else ""
        entry = tk.Entry(form_frame, show=show_char, font=FONT_INPUT, bg=GLASS_BG, fg=TEXT_DARK, 
                         insertbackground=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1)
        
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        student_entries[entry_key] = entry
    
    # Date of Birth field using DateEntry (Calendar Picker)
    dob_row = len(labels_and_fields)
    tk.Label(form_frame, text="Date of Birth:", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=dob_row, column=0, padx=5, pady=5, sticky="w")
    
    try:
        # DateEntry (Calendar Picker) setup
        dob_entry = DateEntry(form_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, 
                              date_pattern='yyyy-mm-dd', # Ensures correct database format
                              font=FONT_INPUT, selectbackground=LOGO_COLOR)
        dob_entry.grid(row=dob_row, column=1, padx=5, pady=5, sticky="ew")
        student_entries["entry_dob"] = dob_entry
    except NameError:
        # Fallback if tkcalendar is not available (i.e., DateEntry causes NameError)
        tk.Label(form_frame, text="[Install tkcalendar]", font=FONT_SMALL, bg=DASH_BG, fg=BTN_DANGER).grid(row=dob_row, column=1, sticky="w")
        dob_entry_fallback = tk.Entry(form_frame, font=FONT_INPUT, bg=GLASS_BG, fg=TEXT_DARK, 
                                      insertbackground=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1)
        dob_entry_fallback.insert(0, "YYYY-MM-DD")
        dob_entry_fallback.grid(row=dob_row, column=1, padx=5, pady=5, sticky="ew")
        student_entries["entry_dob"] = dob_entry_fallback
        messagebox.showwarning("Missing Library", "The Date of Birth calendar feature requires 'tkcalendar'. Please install it using 'pip install tkcalendar'.")

    form_frame.grid_columnconfigure(1, weight=1)

    # Save button
    save_btn = tk.Button(main_frame, text="Save Student", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=DASH_TEXT_COLOR,
                          activebackground=BTN_HOVER, activeforeground=DASH_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=lambda: save_student(add_student_window, student_entries))
    save_btn.pack(pady=20)
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    add_student_window.grab_set()

def save_student(parent_window, entries):
    """
    Saves a new student record to the database after performing data validation.
    """
    # Retrieve and sanitize data from entry widgets
    student_name = entries["entry_name"].get().strip()
    password_str = entries["entry_password"].get().strip()
    class_grade_str = entries["entry_class"].get().strip()
    section_name = entries["entry_section"].get().strip().upper()
    phone_number = entries["entry_phone"].get().strip()
    email = entries["entry_email"].get().strip()
    
    try:
        # Get the date string from the DateEntry widget
        dob = entries["entry_dob"].get() 
    except AttributeError:
        # Fallback for standard Entry
        dob = entries["entry_dob"].get().strip() 


    # --- PYTHON CONSTRAINTS / VALIDATION ---
    
    # 1. Check for required fields
    if not all([student_name, password_str, class_grade_str, section_name, phone_number, email, dob]):
        messagebox.showwarning("Input Error", "All fields are required.")
        return
    
    # 2. Validate Class Grade
    try:
        class_grade = int(class_grade_str)
        if not (1 <= class_grade <= 12): # Assuming standard school grades
            messagebox.showwarning("Input Error", "Class grade must be an integer between 1 and 12.")
            return
    except ValueError:
        messagebox.showwarning("Input Error", "Class grade must be an integer.")
        return
    
    # 3. Validate Phone Number (Strictly 10 digits)
    phone_pattern = re.compile(r'^\d{10}$')
    if not phone_pattern.match(phone_number):
        messagebox.showwarning("Input Error", "Phone number must be exactly 10 digits (no spaces or dashes).")
        return

    # 4. Validate Email ID
    # This is a standard, robust email regex
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if not email_pattern.match(email):
        messagebox.showwarning("Input Error", "Please enter a valid email address (e.g., user@domain.com).")
        return

    # 5. Validate Date of Birth (YYYY-MM-DD format)
    try:
        datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Input Error", "Date of Birth must be in the YYYY-MM-DD format.")
        return
        
    # --- END VALIDATION ---

    # Database logic remains the same
    try:
        db = get_db_connection()
        cursor = db.cursor()

        db.start_transaction()

        # Step 1: Find the class_id from the class and section.
        class_query = "SELECT class_id FROM class WHERE grade = %s AND section = %s"
        cursor.execute(class_query, (class_grade, section_name))
        class_result = cursor.fetchone()

        if not class_result:
            messagebox.showwarning("Invalid Class", f"Class {class_grade} Section {section_name} does not exist. Please create it first.")
            return
        
        class_id = class_result[0]

        # Step 2: Insert the new student record into the 'studentrec' table.
        insert_student_query = """
            INSERT INTO studentrec (name, class, section, class_id, phone_number, email, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_student_query, (student_name, class_grade, section_name, class_id, phone_number, email, dob))

        new_student_id = cursor.lastrowid

        # Step 3: Use the new student_id to create an entry in the 'login' table.
        insert_login_query = "INSERT INTO login (userid, password, role) VALUES (%s, %s, %s)"
        cursor.execute(insert_login_query, (new_student_id, password_str, 'student'))

        db.commit()
        messagebox.showinfo("Success", f"Student {student_name} added successfully! The Student ID is {new_student_id}.")
        parent_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        db.rollback()
    finally:
        if 'db' in locals() and db and db.is_connected():
            cursor.close()
            db.close()

def view_class_details_window():
    """
    Creates a new window to view all created classes in a table.
    Clicking a row will open another window with student details.
    """
    view_window = tk.Toplevel(dashboard_window)
    view_window.title("View All Classes")
    view_window.geometry("600x400")
    view_window.configure(bg=DASH_BG)
    view_window.transient(dashboard_window)
    center_window(view_window)

    main_frame = tk.Frame(view_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    tk.Label(main_frame, text="Click on a Class to View Students", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))

    # Treeview to display the table
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame, columns=("Class ID", "Grade", "Section"), show="headings")
    tree.heading("Class ID", text="Class ID")
    tree.heading("Grade", text="Grade")
    tree.heading("Section", text="Section")

    tree.column("Class ID", width=100, anchor="center")
    tree.column("Grade", width=100, anchor="center")
    tree.column("Section", width=100, anchor="center")

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(fill="both", expand=True)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT class_id, grade, section FROM class ORDER BY grade, section")
        classes = cursor.fetchall()

        if classes:
            for item in classes:
                tree.insert("", "end", values=item)
        else:
            tree.insert("", "end", values=("", "No classes found.", ""))

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching classes: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

    # Bind a function to the Treeview row click event
    def on_class_select(event):
        selected_item = tree.focus()
        if selected_item:
            item_data = tree.item(selected_item, "values")
            class_id = item_data[0] # The class_id is the first value in the tuple
            show_student_details_window(class_id)
            
    tree.bind("<<TreeviewSelect>>", on_class_select)

    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=view_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    view_window.grab_set()

def show_student_details_window(class_id):
    """
    Creates a new window to display all student records for a given class_id.
    Updated to display phone number, email, and DOB.
    """
    student_window = tk.Toplevel(dashboard_window)
    student_window.title(f"Students in Class ID: {class_id}")
    student_window.geometry("1000x500") # Adjusted window size for new columns
    student_window.configure(bg=DASH_BG)
    student_window.transient(dashboard_window)
    center_window(student_window)

    main_frame = tk.Frame(student_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    tk.Label(main_frame, text=f"Student Details for Class ID: {class_id}", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))

    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame, columns=("Student ID", "Name", "Class", "Section", "Phone", "Email", "DOB"), show="headings")
    
    tree.heading("Student ID", text="Student ID")
    tree.heading("Name", text="Name")
    tree.heading("Class", text="Class")
    tree.heading("Section", text="Section")
    tree.heading("Phone", text="Phone Number")
    tree.heading("Email", text="Email ID")
    tree.heading("DOB", text="Date of Birth")

    tree.column("Student ID", width=80, anchor="center")
    tree.column("Name", width=150)
    tree.column("Class", width=60, anchor="center")
    tree.column("Section", width=60, anchor="center")
    tree.column("Phone", width=100, anchor="center")
    tree.column("Email", width=200, anchor="center")
    tree.column("DOB", width=100, anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(fill="both", expand=True)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        # Updated query to select all student fields
        query = """
        SELECT student_id, name, class, section, phone_number, email, date_of_birth 
        FROM studentrec 
        WHERE class_id = %s 
        ORDER BY student_id
        """
        cursor.execute(query, (class_id,))
        students = cursor.fetchall()

        if students:
            for student in students:
                tree.insert("", "end", values=student)
        else:
            tree.insert("", "end", values=("", "No students found in this class.", "", "", "", "", ""))

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching student details: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
            
    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=student_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    student_window.grab_set()


# =========================================================================
# Attendance Window Functions
# =========================================================================
'''
def get_classes():
    """Fetches and returns a list of all classes from the database."""
    classes = []
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT class_id, grade, section FROM class ORDER BY grade, section")
        classes = cursor.fetchall()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching classes: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
    return classes

def enter_attendance_window():
    """
    Creates a window for teachers/admins to take attendance.
    It first prompts for the class and date, then loads the student list.
    """
    attendance_window = tk.Toplevel(dashboard_window)
    attendance_window.title("Enter Attendance")
    attendance_window.geometry("700x300")
    attendance_window.configure(bg=DASH_BG)
    attendance_window.transient(dashboard_window)
    center_window(attendance_window)

    # Main frame for the window content
    main_frame = tk.Frame(attendance_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    tk.Label(main_frame, text="Enter Attendance", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))

    # Form to select class and date
    form_frame = tk.Frame(main_frame, bg=DASH_BG)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Select Class:", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack(side="left", padx=5)
    
    # Get the list of classes for the dropdown
    classes = get_classes()
    class_names = [f"Grade {c[1]} - Section {c[2]}" for c in classes]
    class_ids = [c[0] for c in classes]

    selected_class = tk.StringVar()
    if class_names:
        selected_class.set(class_names[0])  # Set a default value
    
    class_dropdown = ttk.Combobox(form_frame, textvariable=selected_class, values=class_names, state="readonly", font=FONT_INPUT)
    class_dropdown.pack(side="left", padx=5)

    tk.Label(form_frame, text="Date (YYYY-MM-DD):", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack(side="left", padx=5)
    date_entry = tk.Entry(form_frame, font=FONT_INPUT, bg=GLASS_BG, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Pre-populate with current date
    date_entry.pack(side="left", padx=5)

    def load_students_for_attendance():
        """Loads students based on the selected class and date."""
        try:
            # Check if a class is actually selected
            if not selected_class.get():
                messagebox.showwarning("Input Error", "Please select a class.")
                return

            selected_class_name = selected_class.get()
            class_index = class_names.index(selected_class_name)
            class_id = class_ids[class_index]
            attendance_date = date_entry.get().strip()
            
            # Validate date format
            try:
                datetime.strptime(attendance_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

            # Check for existing attendance record to prevent duplicates
            db = get_db_connection()
            cursor = db.cursor()
            check_query = "SELECT COUNT(*) FROM attendance WHERE class_id = %s AND date = %s"
            cursor.execute(check_query, (class_id, attendance_date))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Duplicate Entry", "Attendance for this class on this date has already been recorded.")
                return
            
            load_students(attendance_window, class_id, attendance_date)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if 'db' in locals() and db.is_connected():
                cursor.close()
                db.close()

    load_btn = tk.Button(main_frame, text="Load Students", font=FONT_BUTTON,
                         bg=BTN_NORMAL, fg=DASH_TEXT_COLOR,
                         activebackground=BTN_HOVER, activeforeground=DASH_TEXT_COLOR,
                         relief="flat", bd=0, pady=5, padx=10,
                         command=load_students_for_attendance)
    load_btn.pack(pady=10)

    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=attendance_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    attendance_window.grab_set()

def load_students(parent_window, class_id, attendance_date):
    """
    Creates a new window to display students for attendance marking.
    This function is called after the class and date have been selected.
    """
    student_window = tk.Toplevel(parent_window)
    student_window.title("Mark Attendance")
    student_window.geometry("500x600")
    student_window.configure(bg=DASH_BG)
    student_window.transient(parent_window)
    center_window(student_window)

    main_frame = tk.Frame(student_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    tk.Label(main_frame, text="Mark Attendance", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))
    tk.Label(main_frame, text=f"Class ID: {class_id}, Date: {attendance_date}", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack()

    # Frame to hold the list of students, with a scrollbar
    student_list_frame = tk.Frame(main_frame, bg=GLASS_BG)
    student_list_frame.pack(fill="both", expand=True, pady=10)

    student_canvas = tk.Canvas(student_list_frame, bg=GLASS_BG, highlightthickness=0)
    student_scrollbar = ttk.Scrollbar(student_list_frame, orient="vertical", command=student_canvas.yview)
    scrollable_frame = tk.Frame(student_canvas, bg=GLASS_BG)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: student_canvas.configure(
            scrollregion=student_canvas.bbox("all")
        )
    )

    student_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    student_canvas.configure(yscrollcommand=student_scrollbar.set)
    student_canvas.pack(side="left", fill="both", expand=True)
    student_scrollbar.pack(side="right", fill="y")
    
    # List to hold the Tkinter variables for the radio buttons
    student_vars = []

    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT student_id, name FROM studentrec WHERE class_id = %s ORDER BY name"
        cursor.execute(query, (class_id,))
        students = cursor.fetchall()

        if not students:
            tk.Label(scrollable_frame, text="No students found in this class.", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).pack(pady=20, padx=20)
        else:
            for student_id, student_name in students:
                student_frame = tk.Frame(scrollable_frame, bg=GLASS_BG, bd=1, relief="solid")
                student_frame.pack(fill="x", padx=10, pady=5)
                
                # Use a StringVar to manage the selected status for each student
                # Set the default value to 'Present' as requested.
                status_var = tk.StringVar(value="Present")
                student_vars.append({"id": student_id, "var": status_var})
                
                tk.Label(student_frame, text=f"{student_id} - {student_name}", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).pack(side="left", padx=10, pady=5)
                
                present_rb = tk.Radiobutton(student_frame, text="Present", variable=status_var, value="Present",
                                            font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK, activebackground=GLASS_BG,
                                            selectcolor=GLASS_BG)
                absent_rb = tk.Radiobutton(student_frame, text="Absent", variable=status_var, value="Absent",
                                           font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK, activebackground=GLASS_BG,
                                           selectcolor=GLASS_BG)
                
                absent_rb.pack(side="right", padx=5, pady=5)
                present_rb.pack(side="right", padx=5, pady=5)
    
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching student list: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

    # Save button
    save_btn = tk.Button(main_frame, text="Save Attendance", font=FONT_BUTTON,
                         bg=BTN_NORMAL, fg=DASH_TEXT_COLOR,
                         activebackground=BTN_HOVER, activeforeground=DASH_TEXT_COLOR,
                         relief="flat", bd=0, pady=10, width=15,
                         command=lambda: save_attendance(student_window, student_vars, class_id, attendance_date))
    save_btn.pack(pady=20)
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    student_window.grab_set()

def save_attendance(parent_window, student_vars, class_id, attendance_date):
    """
    Saves the attendance records to the database.
    """
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        insert_query = "INSERT INTO attendance (student_id, class_id, date, status) VALUES (%s, %s, %s, %s)"
        
        for data in student_vars:
            student_id = data['id']
            status = data['var'].get()
            
            cursor.execute(insert_query, (student_id, class_id, attendance_date, status))
        
        db.commit()
        messagebox.showinfo("Success", "Attendance saved successfully!")
        parent_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving attendance: {err}")
        db.rollback()
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()
'''

# --- 1. User's get_classes (Replaced) ---

def get_classes():
    """Fetches and returns a list of all classes from the database."""
    classes = []
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # Returns (class_id, grade, section)
        cursor.execute("SELECT class_id, grade, section FROM class ORDER BY grade, section")
        classes = cursor.fetchall()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching classes: {err}")
    finally:
        if 'db' in locals() and db and db.is_connected():
            cursor.close()
            db.close()
    return classes

# --- 2. User's enter_attendance_window (MODIFIED) ---

def enter_attendance_window():
    """
    Creates a window for teachers/admins to take attendance.
    It now includes a button to view/modify existing attendance.
    """
    attendance_window = tk.Toplevel(dashboard_window)
    attendance_window.title("Enter Attendance")
    attendance_window.geometry("700x300")
    attendance_window.configure(bg=DASH_BG)
    attendance_window.transient(dashboard_window)
    center_window(attendance_window)

    # Main frame for the window content
    main_frame = tk.Frame(attendance_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    tk.Label(main_frame, text="Enter Attendance", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))

    # Form to select class and date
    form_frame = tk.Frame(main_frame, bg=DASH_BG)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Select Class:", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack(side="left", padx=5)
    
    # Get the list of classes for the dropdown
    classes = get_classes()
    class_names = [f"Grade {c[1]} - Section {c[2]}" for c in classes]
    class_ids = [c[0] for c in classes]

    selected_class = tk.StringVar()
    if class_names:
        selected_class.set(class_names[0])  # Set a default value
    
    class_dropdown = ttk.Combobox(form_frame, textvariable=selected_class, values=class_names, state="readonly", font=FONT_INPUT)
    class_dropdown.pack(side="left", padx=5)

    tk.Label(form_frame, text="Date (YYYY-MM-DD):", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack(side="left", padx=5)
    date_entry = tk.Entry(form_frame, font=FONT_INPUT, bg=GLASS_BG, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Pre-populate with current date
    date_entry.pack(side="left", padx=5)

    def load_students_for_attendance():
        """Loads students based on the selected class and date."""
        try:
            if not selected_class.get():
                messagebox.showwarning("Input Error", "Please select a class.")
                return

            selected_class_name = selected_class.get()
            class_index = class_names.index(selected_class_name)
            class_id = class_ids[class_index]
            attendance_date = date_entry.get().strip()
            
            # Validate date format
            try:
                datetime.strptime(attendance_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

            # Check for existing attendance record to prevent duplicates
            db = get_db_connection()
            cursor = db.cursor()
            # The check should verify attendance records for ANY student in that class
            check_query = """
            SELECT COUNT(a.attendance_id) 
            FROM attendance a 
            JOIN studentrec s ON a.student_id = s.student_id 
            WHERE s.class_id = %s AND a.date = %s
            """
            cursor.execute(check_query, (class_id, attendance_date))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Duplicate Entry", "Attendance for this class on this date has already been recorded. Use 'View & Modify Attendance' instead.")
                return
            
            load_students(attendance_window, class_id, attendance_date)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            if 'db' in locals() and db and db.is_connected():
                cursor.close()
                db.close()

    # --- START MODIFICATION ---
    # Frame for buttons (Load Students and View/Modify)
    button_frame = tk.Frame(main_frame, bg=DASH_BG)
    button_frame.pack(pady=10)

    load_btn = tk.Button(button_frame, text="Load Students", font=FONT_BUTTON,
                         bg=BTN_NORMAL, fg=DASH_TEXT_COLOR,
                         activebackground=BTN_HOVER, activeforeground=DASH_TEXT_COLOR,
                         relief="flat", bd=0, pady=5, padx=10,
                         command=load_students_for_attendance)
    load_btn.pack(side="left", padx=10)

    # NEW BUTTON: View & Modify Attendance
    view_modify_btn = tk.Button(button_frame, text="View & Modify Attendance", font=FONT_BUTTON,
                                bg=LOGO_COLOR, fg=CARD_TEXT_COLOR,
                                activebackground="#0056b3", activeforeground=CARD_TEXT_COLOR,
                                relief="flat", bd=0, pady=5, padx=10,
                                command=view_modify_attendance_class_selector)
    view_modify_btn.pack(side="left", padx=10)
    view_modify_btn.bind("<Enter>", on_enter)
    view_modify_btn.bind("<Leave>", on_leave)
    # --- END MODIFICATION ---

    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=attendance_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    attendance_window.grab_set()

# --- 3. User's load_students (Replaced) ---

def load_students(parent_window, class_id, attendance_date):
    """
    Creates a new window to display students for attendance marking.
    This function is called after the class and date have been selected.
    """
    student_window = tk.Toplevel(parent_window)
    student_window.title("Mark Attendance")
    student_window.geometry("500x600")
    student_window.configure(bg=DASH_BG)
    student_window.transient(parent_window)
    center_window(student_window)

    main_frame = tk.Frame(student_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    tk.Label(main_frame, text="Mark Attendance", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))
    tk.Label(main_frame, text=f"Class ID: {class_id}, Date: {attendance_date}", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack()

    # Frame to hold the list of students, with a scrollbar
    student_list_frame = tk.Frame(main_frame, bg=GLASS_BG)
    student_list_frame.pack(fill="both", expand=True, pady=10)

    student_canvas = tk.Canvas(student_list_frame, bg=GLASS_BG, highlightthickness=0)
    student_scrollbar = ttk.Scrollbar(student_list_frame, orient="vertical", command=student_canvas.yview)
    scrollable_frame = tk.Frame(student_canvas, bg=GLASS_BG)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: student_canvas.configure(
            scrollregion=student_canvas.bbox("all")
        )
    )

    student_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    student_canvas.configure(yscrollcommand=student_scrollbar.set)
    student_canvas.pack(side="left", fill="both", expand=True)
    student_scrollbar.pack(side="right", fill="y")
    
    # List to hold the Tkinter variables for the radio buttons
    student_vars = []

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT student_id, name FROM studentrec WHERE class_id = %s ORDER BY name"
        cursor.execute(query, (class_id,))
        students = cursor.fetchall()

        if not students:
            tk.Label(scrollable_frame, text="No students found in this class.", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).pack(pady=20, padx=20)
        else:
            # Header Row
            tk.Label(scrollable_frame, text="Student Name", font=("Segoe UI", 12, "bold"), bg=DASH_HEADER_BG, fg=LOGO_COLOR, anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            tk.Label(scrollable_frame, text="Status", font=("Segoe UI", 12, "bold"), bg=DASH_HEADER_BG, fg=LOGO_COLOR, anchor="e").grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="e")

            for i, (student_id, student_name) in enumerate(students):
                row = i + 1
                
                # Use a StringVar to manage the selected status for each student
                status_var = tk.StringVar(value="Present")
                student_vars.append({"id": student_id, "var": status_var})
                
                tk.Label(scrollable_frame, text=f"{student_id} - {student_name}", font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK).grid(row=row, column=0, padx=10, pady=5, sticky="w")
                
                present_rb = tk.Radiobutton(scrollable_frame, text="Present", variable=status_var, value="Present",
                                             font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK, activebackground=GLASS_BG,
                                             selectcolor=GLASS_BG)
                absent_rb = tk.Radiobutton(scrollable_frame, text="Absent", variable=status_var, value="Absent",
                                           font=FONT_LABEL, bg=GLASS_BG, fg=TEXT_DARK, activebackground=GLASS_BG,
                                           selectcolor=GLASS_BG)
                
                absent_rb.grid(row=row, column=2, padx=5, pady=5, sticky="e")
                present_rb.grid(row=row, column=1, padx=5, pady=5, sticky="e")
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching student list: {err}")
    finally:
        if 'db' in locals() and db and db.is_connected():
            cursor.close()
            db.close()

    # Save button
    save_btn = tk.Button(main_frame, text="Save Attendance", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=DASH_TEXT_COLOR,
                          activebackground=BTN_HOVER, activeforeground=DASH_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=lambda: save_attendance(student_window, student_vars, class_id, attendance_date))
    save_btn.pack(pady=20)
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    student_window.grab_set()

# --- 4. User's save_attendance (Replaced) ---

def save_attendance(parent_window, student_vars, class_id, attendance_date):
    """
    Saves the attendance records to the database.
    """
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        insert_query = "INSERT INTO attendance (student_id, class_id, date, status) VALUES (%s, %s, %s, %s)"
        
        for data in student_vars:
            student_id = data['id']
            status = data['var'].get()
            
            cursor.execute(insert_query, (student_id, class_id, attendance_date, status))
        
        db.commit()
        messagebox.showinfo("Success", "Attendance saved successfully!")
        parent_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving attendance: {err}")
        if 'db' in locals() and db:
            db.rollback()
    finally:
        if 'db' in locals() and db and db.is_connected():
            cursor.close()
            db.close()

# =========================================================================
# NEW FUNCTIONS FOR VIEW & MODIFY ATTENDANCE
# =========================================================================

# --- 5. Class Selector Window ---

def view_modify_attendance_class_selector():
    """
    Opens a window allowing the admin to select a class to view/modify attendance.
    """
    if not dashboard_window:
        messagebox.showerror("System Error", "Dashboard window not initialized. Cannot open manager.")
        return

    class_select_window = tk.Toplevel(dashboard_window)
    class_select_window.title("Select Class to View/Modify Attendance")
    class_select_window.geometry("700x700")
    class_select_window.configure(bg=DASH_BG)
    class_select_window.transient(dashboard_window)
    center_window(class_select_window)

    main_frame = tk.Frame(class_select_window, bg=DASH_BG)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    tk.Label(main_frame, text="Select Class to View/Modify Attendance", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 20))

    class_grid_frame = tk.Frame(main_frame, bg=DASH_BG)
    class_grid_frame.pack(pady=10)
    
    classes = get_classes() # Fetches (class_id, grade, section)
    
    if not classes:
        tk.Label(class_grid_frame, text="No classes found in the database.", font=FONT_LABEL, bg=DASH_BG, fg=TEXT_LIGHT).pack(pady=50)
        
    COLUMNS = 5
    
    for i, (class_id, grade, section) in enumerate(classes):
        row = i // COLUMNS
        col = i % COLUMNS
        
        roman_grade = to_roman(grade) 
        display_text = f"Class\n{roman_grade}-{section}"
        
        tile_color = CARD_COLORS[i % len(CARD_COLORS)]

        class_tile_btn = tk.Button(class_grid_frame, 
                                   text=display_text, 
                                   font=("Segoe UI", 16, "bold"),
                                   bg=tile_color,
                                   fg=CARD_TEXT_COLOR,
                                   activebackground=tile_color, 
                                   relief="raised", bd=2, 
                                   width=TILE_WIDTH, height=TILE_HEIGHT,
                                   wraplength=100,
                                   # Pass all three identifiers to the next step
                                   command=lambda cid=class_id, g=grade, s=section: view_modify_attendance_date_selector(cid, g, s, class_select_window))
                                   
        class_tile_btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=class_select_window.destroy)
    close_btn.pack(pady=(30, 10))
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    class_select_window.grab_set()

# --- 6. Date Selector Window ---

def view_modify_attendance_date_selector(class_id, grade, section, parent_window):
    """
    Opens a window for the admin to select a date for the chosen class.
    """
    date_select_window = tk.Toplevel(parent_window)
    date_select_window.title(f"Select Date: {to_roman(grade)}-{section}")
    date_select_window.geometry("400x300")
    date_select_window.configure(bg=DASH_BG)
    date_select_window.transient(parent_window)
    center_window(date_select_window)

    tk.Label(date_select_window, text=f"Attendance for Class {to_roman(grade)}-{section}", 
             font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=20)
    
    tk.Label(date_select_window, text="Enter Date (YYYY-MM-DD):", 
             font=FONT_LABEL, bg=DASH_BG, fg=TEXT_DARK).pack(pady=(10, 5))

    # Date Entry
    date_entry = ttk.Entry(date_select_window, font=FONT_INPUT, width=15, justify='center')
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    date_entry.pack(pady=5)

    def load_attendance():
        date_str = date_entry.get().strip()
        
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        date_select_window.destroy()
        
        # Call the final modification window
        modify_attendance_window(class_id, grade, section, date_str, parent_window)


    # Load Attendance Button
    load_btn = tk.Button(date_select_window, text="Load Attendance", font=FONT_BUTTON,
                         bg=LOGO_COLOR, fg=CARD_TEXT_COLOR,
                         activebackground="#0056b3", activeforeground=CARD_TEXT_COLOR,
                         relief="flat", bd=0, pady=10, width=20,
                         command=load_attendance)
    load_btn.pack(pady=20)
    load_btn.bind("<Enter>", on_enter)
    load_btn.bind("<Leave>", on_leave)

    date_select_window.grab_set()

# --- 7. Core Modification Window ---

def modify_attendance_window(class_id, grade, section, date_str, parent_of_class_selector):
    """
    Displays the attendance for a specific class and date, allowing modification.
    """
    attendance_modify_window = tk.Toplevel(parent_of_class_selector)
    attendance_modify_window.title(f"Modify Attendance: {to_roman(grade)}-{section} on {date_str}")
    attendance_modify_window.geometry("750x650")
    attendance_modify_window.configure(bg=DASH_BG)
    attendance_modify_window.transient(parent_of_class_selector)
    center_window(attendance_modify_window)

    tk.Label(attendance_modify_window, text=f"Modify Attendance: Class {to_roman(grade)}-{section}", 
             font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(10, 5))
    tk.Label(attendance_modify_window, text=f"Date: {date_str}", 
             font=FONT_LABEL, bg=DASH_BG, fg=TEXT_DARK).pack(pady=(0, 10))

    # Scrollable Frame Setup
    scroll_container = tk.Frame(attendance_modify_window, bg=GLASS_BG)
    scroll_container.pack(fill="both", expand=True, padx=20, pady=10)
    
    canvas = tk.Canvas(scroll_container, bg=GLASS_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
    student_list_frame = tk.Frame(canvas, bg=GLASS_BG) 

    student_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=student_list_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Data structure to hold current statuses and new variables
    attendance_vars = {} # {student_id: (attendance_id, status_var)}
    
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Fetch students and their attendance status for the given date
        # LEFT JOIN ensures all students in the class are listed, even with no record (a.status will be NULL)
        query = """
        SELECT sr.student_id, sr.name, a.attendance_id, a.status 
        FROM studentrec sr
        LEFT JOIN attendance a ON sr.student_id = a.student_id 
            AND a.date = %s
        WHERE sr.class_id = %s
        ORDER BY sr.student_id ASC
        """
        cursor.execute(query, (date_str, class_id))
        students_data = cursor.fetchall()
        
        # Header Row
        header_font = ("Segoe UI", 12, "bold")
        tk.Label(student_list_frame, text="ID", font=header_font, bg=DASH_HEADER_BG, fg=LOGO_COLOR, width=10, anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(student_list_frame, text="Student Name", font=header_font, bg=DASH_HEADER_BG, fg=LOGO_COLOR, width=40, anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Label(student_list_frame, text="Status", font=header_font, bg=DASH_HEADER_BG, fg=LOGO_COLOR, width=15, anchor="w").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # Data Rows
        for i, (student_id, name, attendance_id, status) in enumerate(students_data):
            row = i + 1
            # Default to "N/A" if no attendance record is found
            current_status = status if status else "N/A" 
            
            status_var = tk.StringVar(value=current_status)
            attendance_vars[student_id] = (attendance_id, status_var)
            
            # 1. Student ID and Name
            tk.Label(student_list_frame, text=student_id, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=10).grid(row=row, column=0, sticky="w", padx=5)
            tk.Label(student_list_frame, text=name, font=FONT_SMALL, bg=GLASS_BG, anchor="w", width=40).grid(row=row, column=1, sticky="w", padx=5)
            
            # 2. Status Combobox for Modification
            status_combo = ttk.Combobox(student_list_frame, textvariable=status_var, 
                                        values=["Present", "Absent", "N/A"], state="readonly", width=10)
            status_combo.grid(row=row, column=2, sticky="w", padx=5)
            
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching attendance: {err}")
        return
    finally:
        # Keep DB connection open if needed for saving, but for now, close after fetch
        if db and db.is_connected():
            cursor.close()
            # We will open a new connection in save_changes() to ensure atomic commit/rollback


    # --- Save Logic ---
    def save_changes():
        db_save = None
        try:
            db_save = get_db_connection()
            cursor_save = db_save.cursor()
            
            changes_count = 0
            for student_id, (old_attendance_id, status_var) in attendance_vars.items():
                new_status = status_var.get()
                
                # Case 1: Attendance exists AND status is changed to Present/Absent (UPDATE)
                if old_attendance_id and new_status != "N/A":
                    cursor_save.execute("UPDATE attendance SET status = %s WHERE attendance_id = %s", (new_status, old_attendance_id))
                    changes_count += 1
                
                # Case 2: Attendance exists BUT status changed to N/A (DELETE)
                elif old_attendance_id and new_status == "N/A":
                    cursor_save.execute("DELETE FROM attendance WHERE attendance_id = %s", (old_attendance_id,))
                    changes_count += 1
                
                # Case 3: Attendance doesn't exist AND status changed to Present/Absent (INSERT)
                elif not old_attendance_id and new_status != "N/A":
                    insert_query = "INSERT INTO attendance (student_id, class_id, date, status) VALUES (%s, %s, %s, %s)"
                    cursor_save.execute(insert_query, (student_id, class_id, date_str, new_status))
                    changes_count += 1
                
                # Case 4: Attendance doesn't exist AND status is N/A (NO ACTION)

            db_save.commit()
            messagebox.showinfo("Success", f"Successfully saved {changes_count} attendance modifications.")
            attendance_modify_window.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error saving changes: {err}")
            if db_save:
                db_save.rollback()
        finally:
            if db_save and db_save.is_connected():
                cursor_save.close()
                db_save.close()


    # Button Frame
    button_frame = tk.Frame(attendance_modify_window, bg=DASH_BG)
    button_frame.pack(pady=10)

    # Save Changes Button
    save_btn = tk.Button(button_frame, text="Save Modifications", font=FONT_BUTTON,
                         bg="#2ecc71", fg=CARD_TEXT_COLOR,
                         activebackground="#27ae60", activeforeground=CARD_TEXT_COLOR,
                         relief="flat", bd=0, pady=10, width=20,
                         command=save_changes)
    save_btn.pack(side="left", padx=10)
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    # Close button
    close_btn = tk.Button(button_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=attendance_modify_window.destroy)
    close_btn.pack(side="right", padx=10)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    attendance_modify_window.grab_set()
# =========================================================================
# Student Attendance View Function
# =========================================================================

def view_student_attendance_window(student_id):
    """
    Creates a new window for a student to view their attendance history.
    """
    student_attendance_window = tk.Toplevel(dashboard_window)
    student_attendance_window.title(f"Attendance for Student ID: {student_id}")
    student_attendance_window.geometry("500x500")
    student_attendance_window.configure(bg=DASH_BG)
    student_attendance_window.transient(dashboard_window)
    center_window(student_attendance_window)

    main_frame = tk.Frame(student_attendance_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)

    tk.Label(main_frame, text="Your Attendance Records", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))

    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame, columns=("Date", "Status"), show="headings")
    tree.heading("Date", text="Date")
    tree.heading("Status", text="Status")
    tree.column("Date", width=200, anchor="center")
    tree.column("Status", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(fill="both", expand=True)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT date, status FROM attendance WHERE student_id = %s ORDER BY date DESC"
        cursor.execute(query, (student_id,))
        attendance_records = cursor.fetchall()
        
        if attendance_records:
            for record in attendance_records:
                tree.insert("", "end", values=record)
        else:
            tree.insert("", "end", values=("", "No attendance records found."))
    
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching attendance records: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=student_attendance_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    student_attendance_window.grab_set()

# =========================================================================
# Question Paper Upload/View Functions (Place this entire block in the Sub-window Functions section)
# =========================================================================

def open_qp_link(qp_id, link_type):
    """
    Fetches the specified link (qp_link or answer_key_link) for a given qp_id
    and opens it in the web browser.
    """
    db = None
    link_col_name = 'qp_link' if link_type == 'QP' else 'answer_key_link'
    link_title = 'Question Paper' if link_type == 'QP' else 'Answer Key'
    
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Select the correct link column
        query = f"SELECT {link_col_name}, subject FROM qp WHERE qp_id = %s"
        cursor.execute(query, (qp_id,))
        result = cursor.fetchone()
        
        if result:
            url = result[link_col_name]
            subject = result['subject']
            
            if url:
                webbrowser.open_new_tab(url)
            else:
                messagebox.showwarning("Link Missing", f"No {link_title} link has been uploaded for {subject}.")
        else:
            messagebox.showerror("Error", "Question Paper not found in the database.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error retrieving link: {err}")
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()


def save_question_paper(parent_window, grade_var, qp_type_var, subject_var, max_marks_var, qp_link_var, answer_key_link_var):
    """
    Saves a new question paper record to the 'qp' table with the new schema.
    (This function remains unchanged from the previous working version)
    """
    grade_str = grade_var.get().strip()
    qp_type = qp_type_var.get().strip()
    subject = subject_var.get().strip()
    max_marks_str = max_marks_var.get().strip()
    qp_link = qp_link_var.get().strip()
    answer_key_link = answer_key_link_var.get().strip() # Optional field

    # Validation
    if not all([grade_str, qp_type, subject, max_marks_str, qp_link]):
        messagebox.showwarning("Input Error", "Please fill in all mandatory fields (Grade, QP Type, Subject, Max Marks, QP Link).")
        return
    
    try:
        grade = int(grade_str)
        if not (1 <= grade <= 12):
             messagebox.showwarning("Input Error", "Grade must be between 1 and 12.")
             return
    except ValueError:
        messagebox.showwarning("Input Error", "Grade must be an integer.")
        return

    try:
        max_marks = int(max_marks_str)
        if max_marks <= 0:
             messagebox.showwarning("Input Error", "Max Marks must be a positive integer.")
             return
    except ValueError:
        messagebox.showwarning("Input Error", "Max Marks must be an integer.")
        return

    # Basic URL validation for mandatory link
    if not (qp_link.startswith("http://") or qp_link.startswith("https://")):
         messagebox.showwarning("Input Error", "QP Link must be a valid URL starting with http:// or https://")
         return
    
    # URL validation for optional link (if provided)
    if answer_key_link and not (answer_key_link.startswith("http://") or answer_key_link.startswith("https://")):
         messagebox.showwarning("Input Error", "Answer Key Link, if provided, must be a valid URL starting with http:// or https://")
         return

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        insert_query = """
            INSERT INTO qp (qp_link, qp_type, subject, grade, max_marks, answer_key_link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (qp_link, qp_type, subject, grade, max_marks, answer_key_link if answer_key_link else None))
        db.commit()
        messagebox.showinfo("Success", f"Question Paper ({qp_type} for Grade {grade}, {subject}) uploaded successfully!")
        parent_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error saving question paper: {err}")
        if db:
            db.rollback()
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()

def upload_question_paper_window():
    """
    Creates the GUI window for uploading question paper details, matching the new schema.
    (This function remains unchanged from the previous working version)
    """
    upload_window = tk.Toplevel(dashboard_window)
    upload_window.title("Upload Question Paper")
    upload_window.geometry("550x500")
    upload_window.configure(bg=DASH_BG)
    upload_window.transient(dashboard_window)
    center_window(upload_window)

    # Frame for content
    main_frame = tk.Frame(upload_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=30, pady=30)
    
    # Header
    tk.Label(main_frame, text="Upload Question Paper", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Input Variables
    grade_var = tk.StringVar()
    qp_type_var = tk.StringVar()
    subject_var = tk.StringVar()
    max_marks_var = tk.StringVar()
    qp_link_var = tk.StringVar()
    answer_key_link_var = tk.StringVar()

    # Dropdown Options for QP Type
    qp_types = ["Mid-Term", "Quarterly", "Half-Yearly", "Annual", "Unit Test", "Practice Paper", "Other"]
    qp_type_var.set(qp_types[0]) 

    # Form Fields (Label and Entry/OptionMenu)
    fields = [
        ("Grade (1-12):", grade_var, tk.Entry),
        ("Subject:", subject_var, tk.Entry),
        ("Max Marks:", max_marks_var, tk.Entry),
        ("QP Link (URL):", qp_link_var, tk.Entry),
        ("Answer Key Link (Optional):", answer_key_link_var, tk.Entry),
    ]
    
    row_num = 1
    # Special case for QP Type (Dropdown)
    tk.Label(main_frame, text="QP Type:", font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=row_num, column=0, padx=5, pady=8, sticky="w")
    type_menu = ttk.OptionMenu(main_frame, qp_type_var, qp_type_var.get(), *qp_types)
    type_menu.configure(width=30)
    type_menu.grid(row=row_num, column=1, padx=5, pady=8, sticky="ew")
    row_num += 1

    for label_text, var, widget_type in fields:
        tk.Label(main_frame, text=label_text, font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=row_num, column=0, padx=5, pady=8, sticky="w")
        entry = widget_type(main_frame, textvariable=var, font=FONT_INPUT, bg=GLASS_BG, fg=TEXT_DARK, insertbackground=TEXT_DARK, relief="flat", highlightbackground=GLASS_BORDER, highlightthickness=1, width=35)
        entry.grid(row=row_num, column=1, padx=5, pady=8, sticky="ew")
        row_num += 1

    # Configure grid columns
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=3)
    
    # Save button
    save_btn = tk.Button(main_frame, text="Upload Paper", font=FONT_BUTTON,
                         bg=BTN_NORMAL, fg=CARD_TEXT_COLOR,
                         activebackground=BTN_HOVER, activeforeground=CARD_TEXT_COLOR,
                         relief="flat", bd=0, pady=10, width=20,
                         command=lambda: save_question_paper(upload_window, grade_var, qp_type_var, subject_var, max_marks_var, qp_link_var, answer_key_link_var))
    save_btn.grid(row=row_num, column=0, columnspan=2, pady=(30, 5))
    save_btn.bind("<Enter>", on_enter)
    save_btn.bind("<Leave>", on_leave)

    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_SMALL,
                            bg=BG_PRIMARY, fg=TEXT_DARK,
                            activebackground=GLASS_BG, activeforeground=TEXT_DARK,
                            relief="flat", bd=0, pady=5, width=15,
                            command=upload_window.destroy)
    close_btn.grid(row=row_num + 1, column=0, columnspan=2, pady=(5, 0))

    upload_window.grab_set()

def delete_question_paper(tree, view_window):
    """Deletes the selected question paper from the database.
    (This function remains unchanged from the previous working version)
    """
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a question paper to delete.")
        return

    qp_id = tree.item(selected_item, "values")[0]
    qp_details = f"QP ID: {qp_id}, Subject: {tree.item(selected_item, 'values')[2]}"

    if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the following question paper?\n\n{qp_details}\n\nThis action is permanent."):
        return

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        delete_query = "DELETE FROM qp WHERE qp_id = %s"
        cursor.execute(delete_query, (qp_id,))
        db.commit()
        
        messagebox.showinfo("Success", f"Question Paper ID {qp_id} deleted successfully.")
        # Refresh the Treeview
        # We need to ensure this function is safe to call from both view functions
        if len(tree['columns']) == 8: # Admin View
             load_all_question_papers(tree)
        else: # Student View
             # Cannot easily refresh student view without student_id, so close and tell user to reopen
             view_window.destroy()
             messagebox.showinfo("Refresh", "Please re-open the window to see the updated list.")


    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error deleting question paper: {err}")
        if db:
            db.rollback()
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()


def load_all_question_papers(tree):
    """
    Fetches all question papers from the database and populates the Admin Treeview.
    The links are displayed as clickable text ("QP Link", "Answer Key Link") if present.
    """
    # Clear existing data
    for item in tree.get_children():
        tree.delete(item)

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # CRITICAL: Select all 8 columns including the links
        query = """
            SELECT 
                qp_id, grade, subject, qp_type, max_marks, uploaded_on, qp_link, answer_key_link 
            FROM qp 
            ORDER BY grade, subject, uploaded_on DESC
        """
        cursor.execute(query)
        papers = cursor.fetchall()

        if papers:
            for paper in papers:
                qp_id, grade, subject, qp_type, max_marks, uploaded_on, qp_link, answer_key_link = paper
                
                # Check link presence and display clickable text or placeholder
                qp_display = "[Click to Open]" if qp_link else "---"
                key_display = "[Click to Open]" if answer_key_link else "---"
                
                # Insert the data into the 8 columns
                values = (qp_id, grade, subject, qp_type, max_marks, uploaded_on, qp_display, key_display)
                
                # Use a tag only if there is a link to make it look clickable
                tags = ()
                if qp_link or answer_key_link:
                    tags = ('link_style',)

                tree.insert("", "end", values=values, tags=tags)
        else:
            # Ensure the empty message has 8 values to match the columns
            tree.insert("", "end", values=("", "No question papers found.", "", "", "", "", "", ""), tags=('no_data',))

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching question papers: {err}")
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()


def handle_link_click(event, tree):
    """
    Handles click event on a Treeview row to open the QP link or Answer Key link.
    This replaces all previous click handlers and is robust.
    """
    item = tree.identify_row(event.y)
    column_id = tree.identify_column(event.x)
    
    # Check if a row was clicked
    if not item:
        return

    # Get the QP ID (always index 0 of the values)
    qp_id = tree.item(item, "values")[0]
    
    # Check if the click was in a link column based on column ID
    
    # Admin View Link Columns: #7 (QP Link) and #8 (Answer Key Link)
    if column_id == '#7' and len(tree['columns']) == 8: # Admin QP Link
        # Get the value displayed in the cell to confirm it's clickable
        cell_value = tree.item(item, 'values')[6]
        if cell_value == "[Click to Open]":
            open_qp_link(qp_id, 'QP')
            return
            
    elif column_id == '#8' and len(tree['columns']) == 8: # Admin Answer Key Link
        cell_value = tree.item(item, 'values')[7]
        if cell_value == "[Click to Open]":
            open_qp_link(qp_id, 'KEY')
            return
            
    # Student View Link Column: #5 (QP Link)
    elif column_id == '#5' and len(tree['columns']) == 6: # Student QP Link
        cell_value = tree.item(item, 'values')[4]
        if cell_value == "[Click to Open]":
            open_qp_link(qp_id, 'QP')
            return


def view_all_question_papers_window():
    """
    (Admin/Teacher View) Creates a window to display all question papers with clickable links.
    """
    view_window = tk.Toplevel(dashboard_window)
    view_window.title("View All Question Papers (Admin)")
    view_window.geometry("1400x600") 
    view_window.configure(bg=DASH_BG)
    view_window.transient(dashboard_window)
    center_window(view_window)

    # Define the link style tag for Treeview
    # CRITICAL: This needs to be defined once before the tree is used
    try:
        style = ttk.Style()
        style.configure('Treeview', rowheight=25)
        # Use LOGO_COLOR for link blue
        style.tag_configure('link_style', foreground=LOGO_COLOR, font=FONT_LINK)
    except Exception:
        pass


    main_frame = tk.Frame(view_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    tk.Label(main_frame, text="All Question Papers", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))
    
    # Treeview setup
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    # Columns must match the load_all_question_papers query exactly (8 columns)
    columns = ("QP ID", "Grade", "Subject", "Type", "Max Marks", "Uploaded On", "QP Link", "Answer Key Link")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        # Configure column widths
        if col == "QP ID" or col == "Grade" or col == "Max Marks":
            tree.column(col, width=60, anchor="center")
        elif col == "Uploaded On":
            tree.column(col, width=120, anchor="center")
        elif col == "Subject" or col == "Type":
            tree.column(col, width=150, anchor="w")
        else: # Links are wide
            tree.column(col, width=150, anchor="center")

    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(fill="both", expand=True)

    # Bind the click handler to the Treeview
    tree.bind("<Button-1>", lambda e: handle_link_click(e, tree))

    # Load initial data
    load_all_question_papers(tree)
    
    # Buttons frame
    button_frame = tk.Frame(main_frame, bg=DASH_BG)
    button_frame.pack(pady=10)

    # Delete button
    delete_btn = tk.Button(button_frame, text="Delete Selected Paper", font=FONT_BUTTON,
                           bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                           activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                           relief="flat", bd=0, pady=10, width=20,
                           command=lambda: delete_question_paper(tree, view_window))
    delete_btn.pack(side="left", padx=10)
    delete_btn.bind("<Enter>", on_enter)
    delete_btn.bind("<Leave>", on_leave)

    # Close button
    close_btn = tk.Button(button_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=view_window.destroy)
    close_btn.pack(side="right", padx=10)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    view_window.grab_set()

def view_student_question_papers_window(student_id):
    """
    (Student View) Creates a window to display question papers relevant only to the student's grade, with a clickable link.
    """
    view_window = tk.Toplevel(dashboard_window)
    view_window.title("My Question Papers")
    view_window.geometry("1100x500") 
    view_window.configure(bg=DASH_BG)
    view_window.transient(dashboard_window)
    center_window(view_window)

    # Define the link style tag for Treeview
    try:
        style = ttk.Style()
        style.configure('Treeview', rowheight=25)
        style.tag_configure('link_style', foreground=LOGO_COLOR, font=FONT_LINK)
    except Exception:
        pass


    main_frame = tk.Frame(view_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    student_grade = None
    # 1. Get student's grade
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT class, name FROM studentrec WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        if result:
            student_grade = result[0]
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching student grade: {err}")
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()
    
    if student_grade is None:
        tk.Label(main_frame, text="Could not retrieve your class information.", font=FONT_TITLE, bg=DASH_BG, fg=BTN_DANGER).pack(pady=20)
        return

    tk.Label(main_frame, text=f"Question Papers for Grade {student_grade}", font=FONT_TITLE, bg=DASH_BG, fg=LOGO_COLOR).pack(pady=(0, 10))
    
    # Treeview setup
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    # Columns must match the data selected (6 columns total)
    columns = ("QP ID", "Subject", "Type", "Max Marks", "QP Link", "Uploaded On")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")


    for col in columns:
        tree.heading(col, text=col)
        # Configure column widths
        if col == "QP ID" or col == "Max Marks":
            tree.column(col, width=70, anchor="center")
        elif col == "Uploaded On":
            tree.column(col, width=120, anchor="center")
        elif col == "Subject" or col == "Type":
            tree.column(col, width=200, anchor="w")
        else: # Link column
            tree.column(col, width=150, anchor="center")


    # Add scrollbars
    v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(fill="both", expand=True)

    # Bind the click handler to the Treeview
    tree.bind("<Button-1>", lambda e: handle_link_click(e, tree))


    # 2. Load data filtered by grade
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # CRITICAL: We need to select the actual QP link URL to check if it exists
        query = "SELECT qp_id, subject, qp_type, max_marks, qp_link, uploaded_on FROM qp WHERE grade = %s ORDER BY subject, uploaded_on DESC"
        cursor.execute(query, (student_grade,))
        papers = cursor.fetchall()

        if papers:
            for paper in papers:
                qp_id, subject, qp_type, max_marks, qp_link, uploaded_on = paper
                
                # Display clickable text or placeholder
                qp_display = "[Click to Open]" if qp_link else "---"
                
                # Insert the data: qp_id, subject, qp_type, max_marks, QP LINK DISPLAY, uploaded_on
                values = (qp_id, subject, qp_type, max_marks, qp_display, uploaded_on)
                
                # Use a tag only if there is a link
                tags = ('link_style',) if qp_link else ()
                
                tree.insert("", "end", values=values, tags=tags)
        else:
            # Ensure the empty message has 6 values
            tree.insert("", "end", values=("", "No question papers available for your grade.", "", "", "", ""), tags=('no_data',))

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching question papers: {err}")
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()
    
    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=FONT_BUTTON,
                          bg=BTN_NORMAL, fg=CARD_TEXT_COLOR,
                          activebackground=BTN_HOVER, activeforeground=CARD_TEXT_COLOR,
                          relief="flat", bd=0, pady=10, width=15,
                          command=view_window.destroy)
    close_btn.pack(pady=20)
    close_btn.bind("<Enter>", on_enter)
    close_btn.bind("<Leave>", on_leave)

    view_window.grab_set()
# =========================================================================
# Update circular
# =========================================================================
import tkinter as tk
from tkinter import ttk, messagebox, END
# Ensure you have 'from datetime import datetime' imported for proper date formatting
from datetime import datetime 
import mysql.connector

# --- Helper Functions (Assuming these are defined elsewhere) ---
# def get_db_connection(): ...
# def open_link(url): ...
# DASH_BG, DASH_TEXT_COLOR, FONT_TITLE, FONT_LABEL, LOGO_COLOR, GLASS_BG are assumed to be defined.

def update_circular_window():
    try:
        win = tk.Toplevel(dashboard_window)  # ✅ attach to dashboard properly
    except NameError:
        win = tk.Toplevel()  # fallback if dashboard_window not defined

    win.title("Manage Circulars")
    win.geometry("1000x700")
    win.configure(bg=DASH_BG)
    # win.transient(dashboard_window) # Commented out as dashboard_window may not be defined in testing
    win.grab_set()  # ensures it's active

    # --- Debug print to verify it's opening
    print("✅ Manage Circulars window opened")

    # Title label
    tk.Label(
        win, text="Manage Circulars (Send/Delete)",
        font=("Segoe UI", 20, "bold"), # Used a direct font tuple as placeholders are not defined here
        bg=DASH_BG, fg=DASH_TEXT_COLOR
    ).pack(pady=10)

    # --- Build interface safely ---
    try:
        form_frame = tk.Frame(win, bg=DASH_BG)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Title:", bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=0, column=0, sticky="w", padx=10)
        title_entry = tk.Entry(form_frame, width=50)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Link (URL):", bg=DASH_BG, fg=DASH_TEXT_COLOR).grid(row=1, column=0, sticky="w", padx=10)
        link_entry = tk.Entry(form_frame, width=50)
        link_entry.grid(row=1, column=1, padx=10, pady=5)

        # --- Grade Checkboxes
        grade_frame = tk.LabelFrame(win, text="Select Grades to Send", bg=DASH_BG, fg=DASH_TEXT_COLOR)
        grade_frame.pack(fill="x", padx=20, pady=10)

        grade_names = ["NUR", "LKG", "UKG"] + [str(i) for i in range(1, 13)]
        grade_vars = {}
        for i, g in enumerate(grade_names):
            var = tk.BooleanVar()
            tk.Checkbutton(
                grade_frame, text=g, variable=var,
                bg=DASH_BG, fg=DASH_TEXT_COLOR
            ).grid(row=0, column=i, padx=8, pady=5)
            grade_vars[g] = var

        # --- Scrollable List
        list_frame = tk.Frame(win, bg=DASH_BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(list_frame, bg=DASH_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        circulars_container = tk.Frame(canvas, bg=DASH_BG)

        circulars_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=circulars_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Button to send
        tk.Button(
            win, text="Send Circular", bg=LOGO_COLOR, fg="white", font=("Segoe UI", 12, "bold"),
            command=lambda: send_circular_action(title_entry, link_entry, grade_vars, circulars_container)
        ).pack(pady=10)

        # --- Load data
        refresh_circular_list(circulars_container)

    except Exception as e:
        print("⚠️ Error while building circulars window:", e)
        tk.Label(win, text=f"Error: {e}", bg="red", fg="white").pack(pady=20)


def refresh_circular_list(container):
    """Refreshes and displays the list of all circulars."""
    for widget in container.winfo_children():
        widget.destroy()

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # The query already includes date_posted
        cursor.execute("SELECT circular_id, circular_title, grade, date_posted, circular_link FROM circulars ORDER BY date_posted DESC")
        data = cursor.fetchall()
    except Exception as e:
        print("Error loading circulars:", e)
        data = []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

    headers = ["ID", "Title", "Grade", "Posted On", "Link", "Action"]
    for c, h in enumerate(headers):
        # Using a direct font tuple as a placeholder for FONT_LABEL
        tk.Label(container, text=h, bg=GLASS_BG, fg="black", font=("Segoe UI", 10, "bold"), width=16).grid(row=0, column=c, padx=2, pady=4, sticky="nsew")

    for r, row in enumerate(data, start=1):
        # Unpacking is correct for the 5 columns
        cid, title, grade, date_posted, link = row
        
        # --- Date Formatting Improvement ---
        try:
            # Format the datetime object to a readable string (YYYY-MM-DD HH:MM)
            date_str = date_posted.strftime("%Y-%m-%d %H:%M")
        except AttributeError:
            # Fallback if date_posted is not a datetime object (e.g., a string or None)
            date_str = str(date_posted)

        tk.Label(container, text=cid, bg="white", width=10).grid(row=r, column=0, padx=2, pady=3)
        tk.Label(container, text=title, bg="white", width=20, anchor="w").grid(row=r, column=1, padx=2, pady=3)
        tk.Label(container, text=grade, bg="white", width=8).grid(row=r, column=2, padx=2, pady=3)
        # Using the formatted date string
        tk.Label(container, text=date_str, bg="white", width=20).grid(row=r, column=3, padx=2, pady=3)

        tk.Button(container, text="Open", bg="dodgerblue", fg="white", width=8,
                  command=lambda url=link: open_links(url)).grid(row=r, column=4, padx=4, pady=3)

        tk.Button(container, text="Delete", bg="crimson", fg="white", width=8,
                  command=lambda c=cid: delete_circular(c, container)).grid(row=r, column=5, padx=4, pady=3)


def open_links(url):
    import webbrowser
    if url and (url.startswith("http://") or url.startswith("https://")):
        webbrowser.open(url)
    elif url:
         # Handle cases where URL might be incomplete or local file path if intended
        messagebox.showwarning("Invalid Link", f"Link provided is not a valid web URL: {url}")
    else:
        messagebox.showinfo("No Link", "No link provided for this circular.")


def delete_circular(cid, container):
    """Deletes a circular by its ID and refreshes the list."""
    from tkinter import messagebox
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM circulars WHERE circular_id=%s", (cid,))
        db.commit()
        messagebox.showinfo("Deleted", "Circular removed successfully.")
        refresh_circular_list(container)
    except Exception as e:
        messagebox.showerror("DB Error", f"Failed to delete circular: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


def send_circular_action(title_entry, link_entry, grade_vars, container):
    """Inserts a new circular for all selected grades."""
    title = title_entry.get().strip()
    link = link_entry.get().strip()
    selected_grades = [g for g, var in grade_vars.items() if var.get()]

    if not title:
        messagebox.showwarning("Missing Data", "Please enter the **Title** for the circular.")
        return
    if not selected_grades:
        messagebox.showwarning("Missing Data", "Please **select at least one grade** to send the circular to.")
        return
        
    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # Mapping for special grades
        grade_map = {"NUR": 0, "LKG": -1, "UKG": -2}

        for g in selected_grades:
            grade_val = grade_map.get(g, int(g))
            # The INSERT statement remains correct, as date_posted defaults to CURRENT_TIMESTAMP
            cursor.execute("INSERT INTO circulars (circular_title, circular_link, grade) VALUES (%s, %s, %s)",
                          (title, link, grade_val))
            
        db.commit()

        # Clear form fields on successful send
        title_entry.delete(0, END)
        link_entry.delete(0, END)
        for var in grade_vars.values():
            var.set(False)

        messagebox.showinfo("Success", "Circulars sent successfully.")
        refresh_circular_list(container)
        
    except Exception as e:
        messagebox.showerror("DB Error", f"Failed to send circulars: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def view_student_circular_window(student_id):
    """
    Opens a window showing circulars relevant only to the student's grade 
    using a scrollable frame (non-Treeview).
    """
    try:
        # Tries to attach to the main dashboard window
        student_circular_window = tk.Toplevel(dashboard_window) 
    except NameError:
        # Fallback if running standalone
        student_circular_window = tk.Toplevel()
    
    student_circular_window.title("View Class Circulars")
    student_circular_window.geometry("700x500")
    student_circular_window.configure(bg=DASH_BG)
    student_circular_window.grab_set()

    main_frame = tk.Frame(student_circular_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    # Title Label
    tk.Label(
        main_frame, 
        text="Your Class Circulars", 
        font=FONT_TITLE,
        bg=DASH_BG, 
        fg=LOGO_COLOR
    ).pack(pady=(0, 10))

    # --- Scrollable Frame Setup ---
    list_container = tk.Frame(main_frame, bg=DASH_BG)
    list_container.pack(fill="both", expand=True)

    circular_canvas = tk.Canvas(list_container, bg=DASH_BG, highlightthickness=0)
    circular_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=circular_canvas.yview)
    
    # The inner frame where circulars will be placed
    circular_list_frame = tk.Frame(circular_canvas, bg=GLASS_BG, padx=10, pady=10) 

    circular_list_frame.bind(
        "<Configure>",
        lambda e: circular_canvas.configure(
            scrollregion=circular_canvas.bbox("all")
        )
    )

    circular_canvas.create_window((0, 0), window=circular_list_frame, anchor="nw", width=640)
    circular_canvas.configure(yscrollcommand=circular_scrollbar.set)
    
    circular_canvas.pack(side="left", fill="both", expand=True)
    circular_scrollbar.pack(side="right", fill="y")
    # ------------------------------

    db = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # 1. Get student's grade from studentrec
        grade_query = "SELECT class FROM studentrec WHERE student_id = %s"
        cursor.execute(grade_query, (student_id,))
        grade_result = cursor.fetchone()

        if not grade_result:
            tk.Label(circular_list_frame, text="Error: Could not find your class details.", font=("Segoe UI", 12), fg="red", bg=GLASS_BG).pack(pady=20)
            return

        student_grade = grade_result[0]
        
        # 2. Fetch circulars for the student's grade
        circular_query = "SELECT circular_title, circular_link, date_posted FROM circulars WHERE grade = %s ORDER BY date_posted DESC"
        cursor.execute(circular_query, (student_grade,))
        circulars = cursor.fetchall()

        # Display grade header
        grade_map_reverse = {0: "NUR", -1: "LKG", -2: "UKG"}
        grade_display = grade_map_reverse.get(student_grade, str(student_grade))
        tk.Label(
            circular_list_frame, 
            text=f"Showing Circulars for Grade {grade_display}:", 
            font=("Segoe UI", 12, "bold"), 
            bg=GLASS_BG, 
            fg=DASH_TEXT_COLOR
        ).pack(anchor="w", pady=(0, 10))

        if not circulars:
            tk.Label(circular_list_frame, text="No circulars found for your class yet.", font=("Segoe UI", 12), bg=GLASS_BG).pack(pady=20)
        else:
            for title, link, date_posted in circulars:
                # Individual circular item container
                circular_item_frame = tk.Frame(circular_list_frame, bg=DASH_HEADER_BG, bd=1, relief="solid") 
                circular_item_frame.pack(fill="x", pady=5, ipady=5)
                circular_item_frame.grid_columnconfigure(0, weight=4) # Title Column
                circular_item_frame.grid_columnconfigure(1, weight=1) # Link Column

                # Title Label
                title_text = f"📢 {title}"
                tk.Label(circular_item_frame, text=title_text, font=("Segoe UI", 12, "bold"), 
                         bg=DASH_HEADER_BG, fg=DASH_TEXT_COLOR, anchor="w", wraplength=450
                         ).grid(row=0, column=0, padx=10, pady=2, sticky="ew")

                # Date Label
                date_str = date_posted.strftime("%Y-%m-%d %H:%M")
                tk.Label(circular_item_frame, text=f"Posted: {date_str}", font=("Segoe UI", 9), 
                         bg=DASH_HEADER_BG, fg=DASH_TEXT_COLOR, anchor="w"
                         ).grid(row=1, column=0, padx=10, pady=2, sticky="w")
                
                # Link Button - Correctly calls open_link(url, title)
                if link:
                    link_btn = tk.Button(circular_item_frame, text="Open Link 🔗", font=("Segoe UI", 10, "underline"),
                                         bg=LOGO_COLOR, fg="white", 
                                         activebackground="#0056b3",
                                         relief="flat", bd=0, pady=5, width=12,
                                         command=lambda url=link, t=title: open_link(url, t)) 
                    link_btn.grid(row=0, column=1, rowspan=2, padx=10, sticky="e")
                else:
                    tk.Label(circular_item_frame, text="No Link", font=("Segoe UI", 10), 
                             bg=DASH_HEADER_BG, fg=DASH_TEXT_COLOR
                             ).grid(row=0, column=1, rowspan=2, padx=10, sticky="e")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching circulars: {err}")
    except Exception as e:
        messagebox.showerror("System Error", f"An unexpected error occurred: {e}")
    finally:
        if 'db' in locals() and db and db.is_connected():
            cursor.close()
            db.close()

    # Close button
    close_btn = tk.Button(main_frame, text="Close", font=("Segoe UI", 13, "bold"),
                          bg="#dc3545", fg="white",
                          activebackground="#c82333",
                          relief="flat", bd=0, pady=10, width=15,
                          command=student_circular_window.destroy)
    close_btn.pack(pady=20)

# =========================================================================
# NEW FUNCTIONS FOR PERMANENT CLASS DELETION
# =========================================================================

def delete_entire_class_selector():
    """
    Opens a separate window for the admin to select a class for permanent deletion
    and requires final confirmation before proceeding.
    """
    # Assuming 'dashboard_window' is the main root window for dashboard elements
    class_select_window = tk.Toplevel(dashboard_window) 
    class_select_window.title("Select Class for Permanent Deletion")
    class_select_window.geometry("600x250")
    class_select_window.configure(bg=DASH_BG)
    class_select_window.transient(dashboard_window)
    center_window(class_select_window)

    main_frame = tk.Frame(class_select_window, bg=DASH_BG)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    tk.Label(main_frame, text="⚠️ PERMANENT CLASS DELETION ⚠️", font=FONT_TITLE, bg=DASH_BG, fg=BTN_DANGER).pack(pady=(0, 10))
    tk.Label(main_frame, text="Select the Class to be deleted.\nALL associated student records and attendance will be erased.", 
             font=FONT_LABEL, bg=DASH_BG, fg=DASH_TEXT_COLOR).pack(pady=5)

    # Get the list of classes for the dropdown (Assumes get_classes() is defined)
    classes = get_classes() 
    class_names = [f"Grade {c[1]} - Section {c[2]}" for c in classes]
    class_ids = [c[0] for c in classes]

    if not classes:
        tk.Label(main_frame, text="No classes found to delete.", font=FONT_LABEL, bg=DASH_BG, fg=TEXT_DARK).pack(pady=15)
        return

    selected_class = tk.StringVar()
    selected_class.set(class_names[0])  # Set a default value
    
    # Dropdown frame
    dropdown_frame = tk.Frame(main_frame, bg=DASH_BG)
    dropdown_frame.pack(pady=10)

    class_dropdown = ttk.Combobox(dropdown_frame, textvariable=selected_class, values=class_names, state="readonly", font=FONT_INPUT, width=30)
    class_dropdown.pack(side="left", padx=10)

    def confirm_and_delete_class():
        selected_class_name = selected_class.get()
        class_index = class_names.index(selected_class_name)
        class_id_to_delete = class_ids[class_index]
        grade = classes[class_index][1]
        section = classes[class_index][2]
        
        # Confirmation message is CRITICAL for this severe action
        confirm = messagebox.askyesno(
            "Confirm Permanent Deletion",
            f"Are you ABSOLUTELY SURE you want to permanently delete Class Grade {grade}, Section {section} (ID: {class_id_to_delete})?\n\n"
            "This will delete ALL associated STUDENT RECORDS, ATTENDANCE, and the CLASS ITSELF. This action CANNOT BE UNDONE.",
            icon='error'
        )
        
        if confirm:
            delete_entire_class_permanently(class_id_to_delete, class_select_window)


    delete_btn = tk.Button(dropdown_frame, text="PERMANENTLY DELETE", font=FONT_BUTTON,
                           bg=BTN_DANGER, fg=CARD_TEXT_COLOR,
                           activebackground=BTN_DANGER_HOVER, activeforeground=CARD_TEXT_COLOR,
                           relief="flat", bd=0, pady=5, padx=10,
                           command=confirm_and_delete_class)
    delete_btn.pack(side="right", padx=10)
    delete_btn.bind("<Enter>", on_enter)
    delete_btn.bind("<Leave>", on_leave)

    class_select_window.grab_set()


def delete_entire_class_permanently(class_id_to_delete, parent_window):
    """
    Executes a cascading deletion of all records associated with a class ID.
    This order is required due to database foreign key constraints.
    """
    db = None
    try:
        db = get_db_connection() # Assumes this function is available
        cursor = db.cursor()
        
        db.start_transaction()

        # Step 1: Get all student IDs belonging to the class
        cursor.execute("SELECT student_id FROM studentrec WHERE class_id = %s", (class_id_to_delete,))
        student_ids = [row[0] for row in cursor.fetchall()]
        
        if student_ids:
            student_id_placeholders = ', '.join(['%s'] * len(student_ids))
            
            # Step 2: Delete associated attendance records (must happen before studentrec deletion)
            delete_attendance_query = f"DELETE FROM attendance WHERE student_id IN ({student_id_placeholders})"
            cursor.execute(delete_attendance_query, tuple(student_ids))
            
            # Step 3: Delete associated login records (must happen before studentrec deletion)
            delete_login_query = f"DELETE FROM login WHERE userid IN ({student_id_placeholders}) AND role = 'student'"
            cursor.execute(delete_login_query, tuple(student_ids))
            
            # Step 4: Delete student records
            delete_studentrec_query = f"DELETE FROM studentrec WHERE student_id IN ({student_id_placeholders})"
            cursor.execute(delete_studentrec_query, tuple(student_ids))
        
        # Step 5: Delete the class record itself (final step)
        cursor.execute("DELETE FROM class WHERE class_id = %s", (class_id_to_delete,))

        db.commit()
        messagebox.showinfo("Success", f"Class ID {class_id_to_delete} and all {len(student_ids)} associated records have been PERMANENTLY deleted.")
        parent_window.destroy()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error during permanent class deletion: {err}")
        if db:
            db.rollback()
    except Exception as e:
        messagebox.showerror("System Error", f"An unexpected error occurred: {e}")
        if db:
            db.rollback()
    finally:
        if 'db' in locals() and db and db.is_connected():
            cursor.close()
            db.close()

# =========================================================================
# Main Application Logic
# =========================================================================
if __name__ == "__main__":
    show_login_window()
    tk.mainloop()