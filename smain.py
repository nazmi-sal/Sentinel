import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from userfunctions import login_user, create_user, get_investigators
from incidents import create_incident, get_all_incidents
from statuschanges import get_status_history, change_status
from reports import create_report

# ============================================================
# GUI SETTINGS
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# CONSTANTS
WINDOW_SIZE = "500x650"

TITLE_FONT = ("Arial", 18, "bold")
HEADING_FONT = ("Arial", 18, "bold")
NORMAL_FONT = ("Arial", 12)

BACKGROUND = "#c9d6f2"
CARD = "#1e293b"
ACCENT = "#38bdf8"
TEXT = "#f8fafc"

# verification code for investigators
INVESTIGATOR_CODE = "ENVaSES.2026!" 


# ============================================================
# LOGO:

LOGO_PATH = r"C:\Users\administrator\Downloads\vw5h7j3y.png"

try:

    original_logo = Image.open(LOGO_PATH)

    logo_image = ctk.CTkImage(
        light_image=original_logo,
        dark_image=original_logo,
        size=(220,50)
    )

except:

    logo_image = None


# ============================================================
# MAIN WINDOW:
window = ctk.CTk()

window.title("Incident Management System")
window.geometry(WINDOW_SIZE)

password_visible = False
register_password_visible = False
investigator_code_visible = False
confirm_password_visible = False
current_user = {"id": None, "username": None, "role": None}

# ============================================================
# FUNCTIONS:

# Password for login

def toggle_password():
    global password_visible


    if password_visible:

        password_entry.configure(show="*")
        eye_button.configure(text="🔒")
        password_visible = False


    else:

        password_entry.configure(show="")
        eye_button.configure(text="🔓")
        password_visible = True

def toggle_register_password():
    global register_password_visible

    if register_password_visible:

        register_password_entry.configure(show="*")
        register_eye_button.configure(text="🔒")
        register_password_visible = False

    else:

        register_password_entry.configure(show="")
        register_eye_button.configure(text="🔓")
        register_password_visible = True

def toggle_confirm_password():
    global confirm_password_visible

    if confirm_password_visible:

        confirm_password_entry.configure(show="*")
        confirm_password_eye_button.configure(text="🔒")
        confirm_password_visible = False

    else:

        confirm_password_entry.configure(show="")
        confirm_password_eye_button.configure(text="🔓")
        confirm_password_visible = True

def toggle_investigator_code():
    global investigator_code_visible

    if investigator_code_visible:

        investigator_code_entry.configure(show="*")
        investigator_code_eye_button.configure(text="🔒")
        investigator_code_visible = False

    else:

        investigator_code_entry.configure(show="")
        investigator_code_eye_button.configure(text="🔓")
        investigator_code_visible = True

# ------------------------
# Login

def login():
    email = email_entry.get()
    password = password_entry.get()

    user = login_user(
        email,
        password
    )

    if user:

        user_id = user[0]
        username = user[1]
        role = user[2]

        messagebox.showinfo(
            "Login Successful",
            f"Welcome {username}!"
        )

        open_dashboard(
            user_id,
            username,
            role
        )

    else:

        messagebox.showerror(
            "Error", 
            "Invalid username or password, please try again."
        )


# ------------------------
# Register

def register():
    username = username_entry.get()
    email = register_email_entry.get()
    role = role_var.get()
    password = register_password_entry.get()
    confirm_password = confirm_password_entry.get()

    investigator_code = investigator_code_entry.get()

    if password != confirm_password:

        messagebox.showerror(
            "Error",
            "Passwords do not match."
        )

        return

    # checks investigator verification
    if role == "investigator":

        if investigator_code != INVESTIGATOR_CODE:

            messagebox.showerror(
                "Error",
                "Invalid verification code."
            )

            return

    result = create_user(
        username,
        email,
        role,
        password
    )

    if result == True:

        messagebox.showinfo(
            "Success",
            "Account created successfully!"
        )

        back_to_login()

    else:

        messagebox.showerror(
            "Error",
            result
        )

# ------------------------
# Navigation

def open_register():
    login_frame.pack_forget()

    window.geometry("500x650")

    register_frame.pack(
        pady=75
    )

def back_to_login():
    register_frame.pack_forget()

    window.geometry("500x650")

    login_frame.pack(
        pady=40
    )

# ------------------------
# Dashboard

def open_dashboard(user_id, username, role):

    current_user["id"] = user_id
    current_user["username"] = username
    current_user["role"] = role

    login_frame.pack_forget()

    dashboard_frame.pack(
        pady=60
    )

    welcome_label.configure(
        text=f"Welcome {username}\nRole: {role}"
    )

    if role == "investigator":

        report_button.pack(
            pady=5
        )

    elif role == "user":

        create_incident_button.pack(
            pady=5
        )

        evidence_button.pack(
            pady=5
        )

    view_incidents_button.pack(
        pady=5
    )

# ------------------------
# Investigator code function

def role_changed():

    if role_var.get() == "investigator":

        investigator_code_frame.pack(
            pady=10,
            before=register_password_frame
)

    else:

        investigator_code_frame.pack_forget()


# ------------------------
# Create Incident Page
def open_create_incident():

    window.geometry("500x750")

    refresh_investigator_dropdown()

    dashboard_frame.pack_forget()

    incident_frame.pack(
        pady=40
    )

# ------------------------
# Kanban board

KANBAN_STATUSES = ["New", "Investigated", "Contained", "Resolved", "Closed"]

kanban_columns = {}

def open_kanban_board():

    window.geometry("950x600")

    dashboard_frame.pack_forget()
    incident_frame.pack_forget()

    build_kanban_board()

    kanban_frame.pack(
        pady=20
    )

# ------------------------
# allowing drag and drop of cards between columns
drag_state = {"card": None, "start_x": 0, "start_y": 0}

def on_card_press(event):

    card = event.widget

    drag_state["card"] = card
    drag_state["start_x"] = event.x_root
    drag_state["start_y"] = event.y_root

def on_card_drag(event):

    card = drag_state["card"]

    if card is None:
        return

    dx = event.x_root - drag_state["start_x"]
    dy = event.y_root - drag_state["start_y"]

def on_card_release(event):

    card = drag_state["card"]

    if card is None:
        return

    drop_x = event.x_root
    drop_y = event.y_root

    target_status = None

    for status_name, column in kanban_columns.items():

        col_x = column.winfo_rootx()
        col_y = column.winfo_rooty()
        col_width = column.winfo_width()
        col_height = column.winfo_height()

        if col_x <= drop_x <= col_x + col_width and col_y <= drop_y <= col_y + col_height:

            target_status = status_name
            break

    drag_state["card"] = None

    if target_status is None or target_status == card.origin_status:
        return

    if current_user["role"] != "investigator":

        messagebox.showerror(
            "Access Denied",
            "Only investigators can change incident status."
        )

        return

    result = change_status(
        current_user["id"],
        current_user["role"],
        card.incident_id,
        target_status
    )

    if result:

        build_kanban_board()

    else:

        messagebox.showerror(
            "Invalid Move",
            f"Cannot move this incident to {target_status}."
        )

# ------------------------
# Kanban board
def build_kanban_board():

    # clears existing cards from each column
    for status in KANBAN_STATUSES:

        for widget in kanban_columns[status].winfo_children():

            widget.destroy()

    investigators = get_investigators()

    investigator_names = {}

    for investigator_id, investigator_name in investigators:

        investigator_names[investigator_id] = investigator_name

    incidents = get_all_incidents()

    for incident in incidents:

        incident_id = incident[0]
        title = incident[1]
        category = incident[2]
        severity = incident[3]
        status = incident[6]
        investigator_id = incident[10]

        column = kanban_columns.get(status)

        if column is None:
            continue

        investigator_name = investigator_names.get(investigator_id, "Unassigned")

        card = ctk.CTkButton(
            column,
            text=f"{title}\n{severity} | {category}\n{investigator_name}",
            anchor="w",
            command=lambda i=incident_id: open_incident_detail(i)
        )

        card.pack(
            pady=5,
            padx=5,
            fill="x"
        )

        card.incident_id = incident_id
        card.origin_status = status

        card.bind("<ButtonPress-1>", on_card_press)
        card.bind("<B1-Motion>", on_card_drag)
        card.bind("<ButtonRelease-1>", on_card_release)

def open_incident_detail(incident_id):

    from incidents import get_incident

    incident = get_incident(incident_id)

    if not incident:

        messagebox.showerror(
            "Error",
            "Incident not found."
        )

        return

    (incident_id, title, category, severity, description, location,
     status, created_at, closed_at, reporter_id, investigator_id) = incident

    detail_window = ctk.CTkToplevel(window)
    detail_window.title(title)

    main_x = window.winfo_x()
    main_y = window.winfo_y()

    detail_window.geometry(f"320x400+{main_x + 550}+{main_y + 50}")

    ctk.CTkLabel(
        detail_window,
        text=title,
        font=TITLE_FONT
    ).pack(
        pady=10
    )

    info_text = (
        f"Category: {category}\n"
        f"Severity: {severity}\n"
        f"Status: {status}\n"
        f"Location: {location}\n"
        f"Created: {created_at}\n\n"
        f"Description:\n{description}"
    )

    ctk.CTkLabel(
        detail_window,
        text=info_text,
        justify="left",
        wraplength=350
    ).pack(
        pady=10,
        padx=20
    )

    ctk.CTkLabel(
        detail_window,
        text="Status history",
        font=HEADING_FONT
    ).pack(
        pady=(20,5)
    )

    history = get_status_history(incident_id)

    if history:

        for change_id, old_status, new_status, changed_at, changed_by in history:

            ctk.CTkLabel(
                detail_window,
                text=f"{old_status} → {new_status}  ({changed_at})",
                font=NORMAL_FONT
            ).pack(
                anchor="w",
                padx=20
            )

    else:

        ctk.CTkLabel(
            detail_window,
            text="No status changes yet.",
            font=NORMAL_FONT
        ).pack(
            padx=20
        )

    if current_user["role"] == "investigator" and status in ["Resolved", "Closed"]:

        def generate_report():

            summary = create_report(
                current_user["id"],
                current_user["role"],
                incident_id
            )

            if summary:

                messagebox.showinfo(
                    "Report Generated",
                    summary
                )

            else:

                messagebox.showerror(
                    "Error",
                    "Could not generate report."
                )

        ctk.CTkButton(
            detail_window,
            text="Generate Report",
            command=generate_report
        ).pack(
            pady=15
        )

# ------------------------
# investigator dropdown refresh
def refresh_investigator_dropdown():

    investigators = get_investigators()

    investigator_lookup.clear()

    if not investigators:

        investigator_menu.configure(values=["No investigators found"])
        investigator_var.set("No investigators found")

        return

    names = []

    for investigator_id, investigator_name in investigators:

        investigator_lookup[investigator_name] = investigator_id
        names.append(investigator_name)

    investigator_menu.configure(values=names)
    investigator_var.set(names[0])


# ------------------------
# submitting incident
def submit_incident():

    title = incident_title_entry.get()
    description = incident_description_entry.get("1.0", "end").strip()
    category = category_var.get()
    severity = priority_var.get()
    location = location_entry.get()

    investigator_name = investigator_var.get()
    investigator_id = investigator_lookup.get(investigator_name)

    if investigator_id is None:

        messagebox.showerror(
            "Error",
            "Please select a valid investigator."
        )

        return

    result = create_incident(
        title,
        category,
        severity,
        description,
        location,
        current_user["id"],
        investigator_id
    )

    if result == True:

        messagebox.showinfo(
            "Success",
            "Incident created successfully!"
        )

        incident_title_entry.delete(0, "end")
        incident_description_entry.delete("1.0", "end")
        location_entry.delete(0, "end")

        incident_frame.pack_forget()
        dashboard_frame.pack(pady=60)

    else:

        messagebox.showerror(
            "Error",
            "Could not create incident. Please check all fields are filled in correctly."
        )


# ============================================================
# LOGIN PAGE

# login frame
login_frame = ctk.CTkFrame(
    window,
    width=350,
    height=500
)

login_frame.pack_propagate(False)

login_frame.pack(
    pady=40
)

# ------------------------
# logo & title
if logo_image:

    logo_label = ctk.CTkLabel(
        login_frame,
        text="",
        image=logo_image
    )

    logo_label.pack(
        pady=20
    )

ctk.CTkLabel(
    login_frame,
    text="Incident Management System",
    font=TITLE_FONT
).pack(
    pady=5
)

# ------------------------
# email
ctk.CTkLabel(
    login_frame,
    text="Email"
).pack(
    pady=(20,5)
)

email_entry = ctk.CTkEntry(
    login_frame,
    width=250
)

email_entry.pack()

# ------------------------
# password
ctk.CTkLabel(
    login_frame,
    text="Password"
).pack(
    pady=(15,5)
)

password_frame = ctk.CTkFrame(
    login_frame,
    fg_color="transparent"
)

password_frame.pack()

password_entry = ctk.CTkEntry(
    password_frame,
    width=210,
    show="*"
)

password_entry.pack(
    side="left"
)

# toggling vision of password
eye_button = ctk.CTkButton(
    password_frame,
    text="🔒",
    width=40,
    command=toggle_password
)

eye_button.pack(
    side="right",
    padx=5
)

# ------------------------
# login button
ctk.CTkButton(
    login_frame,
    text="Login",
    command=login,
    width=250
).pack(
    pady=20
)

# ------------------------
# create account button
ctk.CTkButton(
    login_frame,
    text="Create Account",
    command=open_register,
    width=250
).pack()

# REGISTER PAGE ============================================================

# register frame ------------------------

register_frame = ctk.CTkFrame(
    window,
    width=350,
    height=500
)

register_frame.pack_propagate(False)

# create account title ------------------

ctk.CTkLabel(
    register_frame,
    text="Create Account",
    font=TITLE_FONT
).pack(
    pady=20
)

# username ------------------------------

username_entry = ctk.CTkEntry(
    register_frame,
    placeholder_text="Username",
    width=250
)

username_entry.pack(
    pady=12
)

# ------------------------
# email
register_email_entry = ctk.CTkEntry(
    register_frame,
    placeholder_text="Email",
    width=250
)

register_email_entry.pack(
    pady=12
)

# ------------------------
# investigator/user options
role_var = ctk.StringVar(
    value="user"
)

ctk.CTkRadioButton(
    register_frame,
    text="User",
    variable=role_var,
    value="user",
    command=role_changed
).pack(
    pady=5,
    padx=50,
    anchor="w"
)

role_investigator_button = ctk.CTkRadioButton(
    register_frame,
    text="Investigator",
    variable=role_var,
    value="investigator",
    command=role_changed
)

role_investigator_button.pack(
    pady=5,
    padx=50,
    anchor="w"
)

# ------------------------
# investigator verification

investigator_code_frame = ctk.CTkFrame(
    register_frame,
    fg_color="transparent"
)

investigator_code_entry = ctk.CTkEntry(
    investigator_code_frame,
    placeholder_text="Verification Code",
    show="*",
    width=210
)

investigator_code_entry.pack(
    side="left"
)

investigator_code_eye_button = ctk.CTkButton(
    investigator_code_frame,
    text="🔒",
    width=40,
    command=toggle_investigator_code
)

investigator_code_eye_button.pack(
    side="right",
    padx=5
)

investigator_code_frame.pack_forget()

# ------------------------
# password 

register_password_frame = ctk.CTkFrame(
    register_frame,
    fg_color="transparent"
)

register_password_frame.pack(
    pady=10
)

register_password_entry = ctk.CTkEntry(
    register_password_frame,
    placeholder_text="Password",
    show="*",
    width=210
)

# ------------------------
# confirm password

confirm_password_frame = ctk.CTkFrame(
    register_frame,
    fg_color="transparent"
)

confirm_password_frame.pack(
    pady=10
)

confirm_password_entry = ctk.CTkEntry(
    confirm_password_frame,
    placeholder_text="Confirm Password",
    show="*",
    width=210
)

confirm_password_entry.pack(
    side="left"
)

confirm_password_eye_button = ctk.CTkButton(
    confirm_password_frame,
    text="🔒",
    width=40,
    command=toggle_confirm_password
)

confirm_password_eye_button.pack(
    side="right",
    padx=5
)

register_password_entry.pack(
    side="left"
)

register_eye_button = ctk.CTkButton(
    register_password_frame,
    text="🔒",
    width=40,
    command=toggle_register_password
)

register_eye_button.pack(
    side="right",
    padx=5
)

# ------------------------
# create account button
ctk.CTkButton(
    register_frame,
    text="Create Account",
    command=register,
    width=250
).pack(
    pady=10
)

# ------------------------
# back button
ctk.CTkButton(
    register_frame,
    text="Back",
    command=back_to_login,
    width=250
).pack(
    pady=10
)


# ============================================================
# CREATE INCIDENT PAGE

incident_frame = ctk.CTkScrollableFrame(
    window,
    width=350,
    height=550
)

ctk.CTkLabel(
    incident_frame,
    text="Create Incident",
    font=TITLE_FONT
).pack(
    pady=20
)

# Title

ctk.CTkLabel(
    incident_frame,
    text="Incident Title"
).pack(
    anchor="w",
    padx=50
)

incident_title_entry = ctk.CTkEntry(
    incident_frame,
    width=250
)

incident_title_entry.pack(
    pady=5
)

# Description

ctk.CTkLabel(
    incident_frame,
    text="Description"
).pack(
    anchor="w",
    padx=50
)

incident_description_entry = ctk.CTkTextbox(
    incident_frame,
    width=250,
    height=100,
    wrap="word"
)

incident_description_entry.pack(
    pady=5
)

# Category

ctk.CTkLabel(
    incident_frame,
    text="Category"
).pack(
    anchor="w",
    padx=50
)

category_var = ctk.StringVar(
    value="Other"
)

ctk.CTkOptionMenu(
    incident_frame,
    values=[
        "Cyber",
        "Security",
        "Theft",
        "Damage",
        "Other"
    ],
    variable=category_var
).pack(
    pady=5,
    padx=50,
    anchor="w"
)

# Priority

ctk.CTkLabel(
    incident_frame,
    text="Priority"
).pack(
    anchor="w",
    padx=50
)

priority_var = ctk.StringVar(
    value="Medium"
)

ctk.CTkOptionMenu(
    incident_frame,
    values=[
        "Low",
        "Medium",
        "High",
        "Critical"
    ],
    variable=priority_var
).pack(
    pady=5,
    padx=50,
    anchor="w"
)

# Location

ctk.CTkLabel(
    incident_frame,
    text="Location"
).pack(
    anchor="w",
    padx=50
)

location_entry = ctk.CTkEntry(
    incident_frame,
    width=250
)

location_entry.pack(
    pady=5
)

# Investigator

ctk.CTkLabel(
    incident_frame,
    text="Assign Investigator"
).pack(
    anchor="w",
    padx=50
)

investigator_lookup = {}

investigator_var = ctk.StringVar(
    value=""
)

investigator_menu = ctk.CTkOptionMenu(
    incident_frame,
    values=["No investigators found"],
    variable=investigator_var
)

investigator_menu.pack(
    pady=5,
    padx=50,
    anchor="w"
)

ctk.CTkButton(
    incident_frame,
    text="Submit Incident",
    command=submit_incident,
    width=250
).pack(
    pady=10
)

# Back

ctk.CTkButton(
    incident_frame,
    text="Back",
    command=lambda: (
        window.geometry("500x650"),
        incident_frame.pack_forget(),
        dashboard_frame.pack(pady=60)
    ),
    width=250
).pack(
    pady=10
)

# ============================================================
# KANBAN BOARD

kanban_frame = ctk.CTkFrame(
    window,
    width=900,
    height=550
)

kanban_frame.pack_propagate(False)

ctk.CTkButton(
    kanban_frame,
    text="Back",
    command=lambda: (
        window.geometry("500x650"),
        kanban_frame.pack_forget(),
        dashboard_frame.pack(pady=60)
    ),
    width=150
).pack(
    pady=5
)

for status in KANBAN_STATUSES:

    column_container = ctk.CTkFrame(
        kanban_frame,
        width=170
    )

    column_container.pack(
        side="left",
        fill="y",
        padx=5,
        pady=5
    )

    ctk.CTkLabel(
        column_container,
        text=status,
        font=HEADING_FONT
    ).pack(
        pady=5
    )

    column_scroll = ctk.CTkScrollableFrame(
        column_container,
        width=150,
        height=430
    )

    column_scroll.pack(
        fill="both",
        expand=True
    )

    kanban_columns[status] = column_scroll
    
# ============================================================
# DASHBOARD

# frame
dashboard_frame = ctk.CTkFrame(
    window,
    width=350,
    height=500
)

dashboard_frame.pack_propagate(False)

# ------------------------
# welcome label
welcome_label = ctk.CTkLabel(
    dashboard_frame,
    text="",
    font=HEADING_FONT
)

welcome_label.pack(
    pady=20
)

# ------------------------
# buttons
create_incident_button = ctk.CTkButton(
    dashboard_frame,
    text="Create Incident",
     command=open_create_incident
)

report_button = ctk.CTkButton(
    dashboard_frame,
    text="Generate Report"
)

view_incidents_button = ctk.CTkButton(
    dashboard_frame,
    text="View Incidents",
    command=open_kanban_board
)

evidence_button = ctk.CTkButton(
    dashboard_frame,
    text="Upload Evidence"
)

ctk.CTkButton(
    dashboard_frame,
    text="Logout",
    command=window.destroy
).pack(
    pady=20
)

# ============================================================
# START PROGRAM

window.mainloop()