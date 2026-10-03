import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image

import reports
from userfunctions import login_user, create_user, get_investigators, get_user_name
from incidents import create_incident, get_all_incidents, get_incidents_by_reporter, search_incidents
from statuschanges import get_status_history, change_status, undo_last_status_change
from reports import create_report, get_reports
from evidence import add_evidence, get_evidence_by_uploader

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
INVESTIGATOR_CODE = "EnvasesWork{78}" 

# ============================================================
# LOGO:

LOGO_PATH = r"C:\Users\nzsal\Downloads\envases.png"

try:

    original_logo = Image.open(LOGO_PATH)

    logo_image = ctk.CTkImage(
        light_image=original_logo,
        dark_image=original_logo,
        size=(190,120)
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

    if role == "user":

        create_incident_button.pack(
            pady=5
        )

        evidence_button.pack(
            pady=5
        )

        my_evidence_button.pack(
            pady=5
        )

    view_incidents_button.pack(
        pady=5
    )

    if role == "investigator":

        report_button.pack(
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
kanban_column_bounds = {}
last_moved_incident = {"id": None}

def open_kanban_board():

    window.geometry("950x650")

    dashboard_frame.pack_forget()
    incident_frame.pack_forget()

    clear_filters(rebuild=False)

    build_kanban_board()

    kanban_frame.pack(
        pady=20
    )

    window.lift()
    window.focus_force()

# ------------------------
# Search / Filter

def get_filtered_incidents():

    status = filter_status_var.get()
    category = filter_category_var.get()
    severity = filter_severity_var.get()
    date_from = filter_date_from_entry.get().strip()
    date_to = filter_date_to_entry.get().strip()

    status = None if status == "All Statuses" else status
    category = None if category == "All Categories" else category
    severity = None if severity == "All Severities" else severity
    date_from = date_from if date_from else None
    date_to = date_to if date_to else None

    if date_from:
        date_from = date_from + " 00:00:00"

    if date_to:
        date_to = date_to + " 23:59:59"

    if not any([status, category, severity, date_from, date_to]):

        return get_all_incidents()

    return search_incidents(
        status=status,
        category=category,
        severity=severity,
        date_from=date_from,
        date_to=date_to
    )

def apply_filters():

    build_kanban_board()

def clear_filters(rebuild=True):

    filter_status_var.set("All Statuses")
    filter_category_var.set("All Categories")
    filter_severity_var.set("All Severities")
    filter_date_from_entry.delete(0, "end")
    filter_date_to_entry.delete(0, "end")

    if rebuild:
        build_kanban_board()

# ------------------------
# allowing drag and drop of cards between columns
drag_state = {"card": None, "float_win": None, "start_x": 0, "start_y": 0}

def on_card_press(event, card):

    drag_state["card"] = card
    drag_state["start_x"] = event.x_root
    drag_state["start_y"] = event.y_root

    float_win = ctk.CTkToplevel(window)
    float_win.overrideredirect(True)
    float_win.attributes("-alpha", 0.85)
    float_win.geometry(f"150x50+{event.x_root - 75}+{event.y_root - 25}")

    ctk.CTkLabel(
        float_win,
        text=card.cget("text"),
        fg_color=ACCENT,
        corner_radius=6
    ).pack(
        fill="both",
        expand=True
    )

    drag_state["float_win"] = float_win

def on_card_motion(event, card):

    float_win = drag_state["float_win"]

    if float_win is None:
        return

    float_win.geometry(f"+{event.x_root - 75}+{event.y_root - 25}")

def on_card_release(event, card):

    if drag_state["card"] is None:
        return

    float_win = drag_state["float_win"]

    if float_win is not None:

        float_win.destroy()
        drag_state["float_win"] = None

    dx = abs(event.x_root - drag_state["start_x"])
    dy = abs(event.y_root - drag_state["start_y"])

    drag_state["card"] = None

    if dx < 6 and dy < 6:

        open_incident_detail(card.incident_id)

        return

    drop_x = event.x_root
    drop_y = event.y_root

    window.update_idletasks()

    target_status = None

    for status_name, column in kanban_column_bounds.items():

        col_x = column.winfo_rootx()
        col_y = column.winfo_rooty()
        col_width = column.winfo_width()
        col_height = column.winfo_height()

        if col_x <= drop_x <= col_x + col_width and col_y <= drop_y <= col_y + col_height:

            target_status = status_name
            break

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

        last_moved_incident["id"] = card.incident_id

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

    incidents = get_filtered_incidents()

    for incident in incidents:

        incident_id = incident[0]
        title = incident[1]
        category = incident[2]
        severity = incident[3]
        status = incident[6]
        reporter_id = incident[9]

        column = kanban_columns.get(status)

        if column is None:
            continue

        reporter_name = get_user_name(reporter_id)

        card = ctk.CTkButton(
            column,
            text=f"{title}\nReported by: {reporter_name}",
            anchor="w"
        )

        card.pack(
            pady=5,
            padx=5,
            fill="x"
        )

        card.incident_id = incident_id
        card.origin_status = status

        card.bind("<ButtonPress-1>", lambda e, c=card: on_card_press(e, c))
        card.bind("<B1-Motion>", lambda e, c=card: on_card_motion(e, c))
        card.bind("<ButtonRelease-1>", lambda e, c=card: on_card_release(e, c))

def open_incident_evidence(incident_id, incident_title):

    from evidence import get_evidence

    evidence_window = ctk.CTkToplevel(window)
    evidence_window.title(f"Evidence - {incident_title}")
    evidence_window.geometry("350x450")
    evidence_window.transient(window)
    evidence_window.attributes("-topmost", True)
    evidence_window.lift()
    evidence_window.focus_force()

    ctk.CTkLabel(
        evidence_window,
        text="Evidence",
        font=TITLE_FONT
    ).pack(
        pady=10
    )

    scroll_area = ctk.CTkScrollableFrame(
        evidence_window,
        width=310,
        height=350
    )

    scroll_area.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    evidence_list = get_evidence(incident_id)

    if not evidence_list:

        ctk.CTkLabel(
            scroll_area,
            text="No evidence uploaded yet."
        ).pack(
            pady=10
        )

        return

    image_types = ["jpg", "jpeg", "png"]

    for evidence_id, file_name, file_type, file_path, notes, uploaded_at, uploaded_by in evidence_list:

        entry_frame = ctk.CTkFrame(
            scroll_area,
            fg_color="gray20",
            corner_radius=6
        )

        entry_frame.pack(
            fill="x",
            padx=5,
            pady=5
        )

        if file_type in image_types:

            try:

                img = Image.open(file_path)

                thumbnail = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(150, 150)
                )

                ctk.CTkLabel(
                    entry_frame,
                    text="",
                    image=thumbnail
                ).pack(
                    pady=5
                )

            except:

                ctk.CTkLabel(
                    entry_frame,
                    text="(Image could not be loaded)"
                ).pack(
                    pady=5
                )

        else:

            ctk.CTkLabel(
                entry_frame,
                text=f"📄 {file_type.upper()} file"
            ).pack(
                pady=5
            )

        ctk.CTkLabel(
            entry_frame,
            text=f"File: {file_name}\nUploaded: {uploaded_at}\nNotes: {notes if notes else 'None'}",
            justify="left",
            wraplength=270
        ).pack(
            pady=(0,5),
            padx=5
        )

def open_reassign_popup(incident_id, current_investigator_id):

    reassign_window = ctk.CTkToplevel(window)
    reassign_window.title("Reassign Investigator")
    reassign_window.geometry("300x220")
    reassign_window.transient(window)
    reassign_window.attributes("-topmost", True)
    reassign_window.lift()
    reassign_window.focus_force()

    ctk.CTkLabel(
        reassign_window,
        text="Reassign Investigator",
        font=HEADING_FONT
    ).pack(
        pady=15
    )

    investigators = get_investigators()

    reassign_lookup = {}
    names = []

    for investigator_id, investigator_name in investigators:

        reassign_lookup[investigator_name] = investigator_id
        names.append(investigator_name)

    if not names:

        names = ["No investigators available"]

    reassign_var = ctk.StringVar(value=names[0])

    ctk.CTkOptionMenu(
        reassign_window,
        values=names,
        variable=reassign_var
    ).pack(
        pady=10
    )

    def confirm_reassign():

        selected_name = reassign_var.get()
        new_investigator_id = reassign_lookup.get(selected_name)

        if new_investigator_id is None:

            messagebox.showerror(
                "Error",
                "Please select a valid investigator."
            )

            return

        from userfunctions import reassign_investigator

        result = reassign_investigator(incident_id, new_investigator_id)

        if result:

            messagebox.showinfo(
                "Success",
                "Investigator reassigned successfully!"
            )

            reassign_window.destroy()
            build_kanban_board()

        else:

            messagebox.showerror(
                "Error",
                "Could not reassign investigator."
            )

    ctk.CTkButton(
        reassign_window,
        text="Confirm",
        command=confirm_reassign
    ).pack(
        pady=15
    )

def open_incident_detail(incident_id):

    from incidents import get_incident
    from reports import get_reports

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

    detail_window.geometry(f"350x500+{main_x + 550}+{main_y + 50}")
    detail_window.lift()
    detail_window.focus_force()
    detail_window.transient(window)
    detail_window.attributes("-topmost", True)

    ctk.CTkLabel(
        detail_window,
        text=title,
        font=TITLE_FONT
    ).pack(
        pady=10
    )

    button_row = ctk.CTkFrame(
        detail_window,
        fg_color="transparent"
    )

    button_row.pack(
        pady=5
    )

    ctk.CTkButton(
        button_row,
        text="Close",
        width=100,
        command=detail_window.destroy
    ).pack(
        side="left",
        padx=5
    )

    ctk.CTkButton(
        button_row,
        text="Evidence",
        width=100,
        command=lambda: open_incident_evidence(incident_id, title)
    ).pack(
        side="left",
        padx=5
    )

    if current_user["role"] == "investigator":

        ctk.CTkButton(
            button_row,
            text="Reassign",
            width=100,
            command=lambda: open_reassign_popup(incident_id, investigator_id)
        ).pack(
            side="left",
            padx=5
        )

    scroll_area = ctk.CTkScrollableFrame(
        detail_window,
        width=310,
        height=380
    )

    scroll_area.pack(
        fill="both",
        expand=True,
        padx=10,
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
        scroll_area,
        text=info_text,
        justify="left",
        wraplength=280
    ).pack(
        pady=10,
        padx=10,
        anchor="w"
    )

    ctk.CTkLabel(
        scroll_area,
        text="Status history",
        font=HEADING_FONT
    ).pack(
        pady=(20,5),
        anchor="w"
    )

    history = get_status_history(incident_id)

    if history:

        for change_id, old_status, new_status, changed_at, changed_by in history:

            ctk.CTkLabel(
                scroll_area,
                text=f"{old_status} → {new_status}  ({changed_at})",
                font=NORMAL_FONT
            ).pack(
                anchor="w",
                padx=10
            )

    else:

        ctk.CTkLabel(
            scroll_area,
            text="No status changes yet.",
            font=NORMAL_FONT
        ).pack(
            anchor="w",
            padx=10
        )

    reports = get_reports(incident_id)

    if reports:

        ctk.CTkLabel(
            scroll_area,
            text="Generated Reports",
            font=HEADING_FONT
        ).pack(
            pady=(20,5),
            anchor="w"
        )

        for report_id, summary, generated_at, generated_by in reports:

            ctk.CTkLabel(
                scroll_area,
                text=f"Report ({generated_at}):\n{summary}",
                justify="left",
                wraplength=280,
                font=NORMAL_FONT
            ).pack(
                anchor="w",
                padx=10,
                pady=5
            )

# undo button as a function
def undo_last_move():

    if last_moved_incident["id"] is None:

        messagebox.showerror(
            "Error",
            "No recent move to undo."
        )

        return

    if current_user["role"] != "investigator":

        messagebox.showerror(
            "Access Denied",
            "Only investigators can undo status changes."
        )

        return

    result = undo_last_status_change(
        current_user["id"],
        current_user["role"],
        last_moved_incident["id"]
    )

    if result:

        last_moved_incident["id"] = None

        build_kanban_board()

    else:

        messagebox.showerror(
            "Error",
            "Nothing to undo."
        )

# ------------------------
# Generate Report screen

report_incident_lookup = {}

def open_report_screen():

    window.geometry("500x500")

    dashboard_frame.pack_forget()

    refresh_report_dropdown()

    report_frame.pack(
        pady=40
    )

def refresh_report_dropdown():

    incidents = get_all_incidents()

    report_incident_lookup.clear()

    eligible = []

    for incident in incidents:

        incident_id = incident[0]
        title = incident[1]
        status = incident[6]

        if status in ["Resolved", "Closed"]:

            label = f"#{incident_id} - {title}"
            report_incident_lookup[label] = incident_id
            eligible.append(label)

    if not eligible:

        report_menu.configure(values=["No eligible incidents"])
        report_var.set("No eligible incidents")

        return

    report_menu.configure(values=eligible)
    report_var.set(eligible[0])

def generate_report_from_screen():

    selected = report_var.get()
    incident_id = report_incident_lookup.get(selected)

    if incident_id is None:

        messagebox.showerror(
            "Error",
            "Please select a valid incident."
        )

        return

    notes = report_notes_entry.get("1.0", "end").strip()

    summary = create_report(
        current_user["id"],
        current_user["role"],
        incident_id,
        notes
    )

    if summary:

        messagebox.showinfo(
            "Report Generated",
            summary
        )

        report_notes_entry.delete("1.0", "end")

    else:

        messagebox.showerror(
            "Error",
            "Could not generate report."
        )

# ------------------------
# Evidence upload screen

evidence_incident_lookup = {}
selected_file_path = {"path": None}

def open_evidence_screen():

    window.geometry("500x600")

    dashboard_frame.pack_forget()

    refresh_evidence_dropdown()

    selected_file_path["path"] = None
    file_label.configure(text="No file selected")

    evidence_frame.pack(
        pady=40
    )

def refresh_evidence_dropdown():

    incidents = get_incidents_by_reporter(current_user["id"])

    evidence_incident_lookup.clear()

    labels = []

    for incident in incidents:

        incident_id = incident[0]
        title = incident[1]
        status = incident[6]

        if status in ["Resolved", "Closed"]:
            continue

        label = f"#{incident_id} - {title}"
        evidence_incident_lookup[label] = incident_id
        labels.append(label)

    if not labels:

        evidence_menu.configure(values=["No eligible incidents"])
        evidence_var.set("No eligible incidents")

        return

    evidence_menu.configure(values=labels)
    evidence_var.set(labels[0])

def browse_file():

    path = filedialog.askopenfilename(
        title="Select evidence file",
        filetypes=[
            ("Allowed files", "*.jpg *.jpeg *.png *.pdf *.txt")
        ]
    )

    if path:

        selected_file_path["path"] = path

        file_name = path.split("/")[-1]

        file_label.configure(text=file_name)

def submit_evidence():

    selected = evidence_var.get()
    incident_id = evidence_incident_lookup.get(selected)

    if incident_id is None:

        messagebox.showerror(
            "Error",
            "Please select a valid incident."
        )

        return

    file_path = selected_file_path["path"]

    if not file_path:

        messagebox.showerror(
            "Error",
            "Please select a file to upload."
        )

        return

    file_name = file_path.split("/")[-1]
    notes = evidence_notes_entry.get("1.0", "end").strip()

    result = add_evidence(
        incident_id,
        current_user["id"],
        file_name,
        file_path,
        notes
    )

    if result:

        messagebox.showinfo(
            "Success",
            "Evidence uploaded successfully!"
        )

        selected_file_path["path"] = None
        file_label.configure(text="No file selected")
        evidence_notes_entry.delete("1.0", "end")

    else:

        messagebox.showerror(
            "Error",
            "Could not upload evidence. Check the file type and size."
        )

# ------------------------
# View My Evidence screen

def open_my_evidence_screen():

    window.geometry("500x600")

    dashboard_frame.pack_forget()

    build_my_evidence_list()

    my_evidence_frame.pack(
        pady=20
    )

def build_my_evidence_list():

    for widget in my_evidence_list_area.winfo_children():

        widget.destroy()

    evidence_list = get_evidence_by_uploader(current_user["id"])

    if not evidence_list:

        ctk.CTkLabel(
            my_evidence_list_area,
            text="You haven't uploaded any evidence yet."
        ).pack(
            pady=10
        )

        return

    for evidence_id, file_name, file_type, file_path, notes, uploaded_at, incident_id in evidence_list:

        entry_text = (
            f"File: {file_name}\n"
            f"Incident: #{incident_id}\n"
            f"Uploaded: {uploaded_at}\n"
            f"Notes: {notes if notes else 'None'}"
        )

        ctk.CTkLabel(
            my_evidence_list_area,
            text=entry_text,
            justify="left",
            wraplength=280,
            fg_color="gray20",
            corner_radius=6
        ).pack(
            fill="x",
            padx=10,
            pady=5
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
# GENERATE REPORT PAGE

report_frame = ctk.CTkFrame(
    window,
    width=350,
    height=500
)

report_frame.pack_propagate(False)

ctk.CTkLabel(
    report_frame,
    text="Generate Report",
    font=TITLE_FONT
).pack(
    pady=20
)

ctk.CTkLabel(
    report_frame,
    text="Select Incident"
).pack(
    anchor="w",
    padx=50
)

report_var = ctk.StringVar(
    value=""
)

report_menu = ctk.CTkOptionMenu(
    report_frame,
    values=["No eligible incidents"],
    variable=report_var
)

report_menu.pack(
    pady=5,
    padx=50,
    anchor="w"
)

ctk.CTkLabel(
    report_frame,
    text="Notes & Recommendations: (optional)"
).pack(
    anchor="w",
    padx=50,
    pady=(15,0)
)

report_notes_entry = ctk.CTkTextbox(
    report_frame,
    width=250,
    height=80,
    wrap="word"
)

report_notes_entry.pack(
    pady=5
)

ctk.CTkButton(
    report_frame,
    text="Generate Report",
    command=generate_report_from_screen,
    width=250
).pack(
    pady=20
)

ctk.CTkButton(
    report_frame,
    text="Back",
    command=lambda: (
        window.geometry("500x650"),
        report_frame.pack_forget(),
        dashboard_frame.pack(pady=60)
    ),
    width=250
).pack(
    pady=10
)

# ============================================================
# EVIDENCE UPLOAD PAGE

evidence_frame = ctk.CTkFrame(
    window,
    width=350,
    height=550
)

evidence_frame.pack_propagate(False)

ctk.CTkLabel(
    evidence_frame,
    text="Upload Evidence",
    font=TITLE_FONT
).pack(
    pady=20
)

ctk.CTkLabel(
    evidence_frame,
    text="Select Incident"
).pack(
    anchor="w",
    padx=50
)

evidence_var = ctk.StringVar(
    value=""
)

evidence_menu = ctk.CTkOptionMenu(
    evidence_frame,
    values=["No incidents found"],
    variable=evidence_var
)

evidence_menu.pack(
    pady=5,
    padx=50,
    anchor="w"
)

ctk.CTkButton(
    evidence_frame,
    text="Browse File",
    command=browse_file,
    width=250
).pack(
    pady=(15,5)
)

file_label = ctk.CTkLabel(
    evidence_frame,
    text="No file selected"
)

file_label.pack(
    pady=5
)

ctk.CTkLabel(
    evidence_frame,
    text="Notes"
).pack(
    anchor="w",
    padx=50,
    pady=(15,0)
)

evidence_notes_entry = ctk.CTkTextbox(
    evidence_frame,
    width=250,
    height=80,
    wrap="word"
)

evidence_notes_entry.pack(
    pady=5
)

ctk.CTkButton(
    evidence_frame,
    text="Submit Evidence",
    command=submit_evidence,
    width=250
).pack(
    pady=15
)

ctk.CTkButton(
    evidence_frame,
    text="Back",
    command=lambda: (
        window.geometry("500x650"),
        evidence_frame.pack_forget(),
        dashboard_frame.pack(pady=60)
    ),
    width=250
).pack(
    pady=10
)

# ============================================================
# VIEW MY EVIDENCE PAGE

my_evidence_frame = ctk.CTkFrame(
    window,
    width=350,
    height=550
)

my_evidence_frame.pack_propagate(False)

ctk.CTkLabel(
    my_evidence_frame,
    text="My Evidence",
    font=TITLE_FONT
).pack(
    pady=20
)

my_evidence_list_area = ctk.CTkScrollableFrame(
    my_evidence_frame,
    width=310,
    height=380
)

my_evidence_list_area.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

ctk.CTkButton(
    my_evidence_frame,
    text="Back",
    command=lambda: (
        window.geometry("500x650"),
        my_evidence_frame.pack_forget(),
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
    height=620
)

kanban_frame.pack_propagate(False)

kanban_top_row = ctk.CTkFrame(
    kanban_frame,
    fg_color="transparent"
)

kanban_top_row.pack(
    pady=5
)

ctk.CTkButton(
    kanban_top_row,
    text="↩",
    command=undo_last_move,
    width=50,
    fg_color="gray30"
).pack(
    side="left",
    padx=5
)

ctk.CTkButton(
    kanban_top_row,
    text="Back",
    command=lambda: (
        window.geometry("500x650"),
        kanban_frame.pack_forget(),
        dashboard_frame.pack(pady=60)
    ),
    width=150
).pack(
    side="left",
    padx=5
)

# ------------------------
# Filter row

kanban_filter_row = ctk.CTkFrame(
    kanban_frame,
    fg_color="transparent"
)

kanban_filter_row.pack(
    pady=(0,5)
)

filter_status_var = ctk.StringVar(value="All Statuses")

ctk.CTkOptionMenu(
    kanban_filter_row,
    values=["All Statuses"] + KANBAN_STATUSES,
    variable=filter_status_var,
    width=130
).pack(
    side="left",
    padx=3
)

filter_category_var = ctk.StringVar(value="All Categories")

ctk.CTkOptionMenu(
    kanban_filter_row,
    values=["All Categories", "Cyber", "Security", "Theft", "Damage", "Other"],
    variable=filter_category_var,
    width=130
).pack(
    side="left",
    padx=3
)

filter_severity_var = ctk.StringVar(value="All Severities")

ctk.CTkOptionMenu(
    kanban_filter_row,
    values=["All Severities", "Low", "Medium", "High", "Critical"],
    variable=filter_severity_var,
    width=130
).pack(
    side="left",
    padx=3
)

filter_date_from_entry = ctk.CTkEntry(
    kanban_filter_row,
    placeholder_text="From (YYYY-MM-DD)",
    width=130
)

filter_date_from_entry.pack(
    side="left",
    padx=3
)

filter_date_to_entry = ctk.CTkEntry(
    kanban_filter_row,
    placeholder_text="To (YYYY-MM-DD)",
    width=130
)

filter_date_to_entry.pack(
    side="left",
    padx=3
)

ctk.CTkButton(
    kanban_filter_row,
    text="Apply",
    command=apply_filters,
    width=70
).pack(
    side="left",
    padx=3
)

ctk.CTkButton(
    kanban_filter_row,
    text="Clear",
    command=clear_filters,
    width=70,
    fg_color="gray30"
).pack(
    side="left",
    padx=3
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
    kanban_column_bounds[status] = column_container
    
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

view_incidents_button = ctk.CTkButton(
    dashboard_frame,
    text="View Incidents",
    command=open_kanban_board
)

report_button = ctk.CTkButton(
    dashboard_frame,
    text="Generate Report",
    command=open_report_screen
)

evidence_button = ctk.CTkButton(
    dashboard_frame,
    text="Upload Evidence",
    command=open_evidence_screen
)

my_evidence_button = ctk.CTkButton(
    dashboard_frame,
    text="My Evidence",
    command=open_my_evidence_screen
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