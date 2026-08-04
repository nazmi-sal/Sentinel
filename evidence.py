import sqlite3
import os

# connects to Sentinel database
def get_connection():
    return sqlite3.connect("sentinel.db")

# adds evidence to an incident
def add_evidence(incident_id, uploaded_by, file_name, file_path, notes):

    connection = get_connection()
    cursor = connection.cursor()

    file_path = file_path.strip().strip('"')

    # checks incident exists
    cursor.execute("""
    SELECT incident_id
    FROM Incident
    WHERE incident_id = ?
    """,
    (incident_id,))

    if not cursor.fetchone():
        print("Incident not found.")
        connection.close()
        return False

    # gets file type
    file_type = os.path.splitext(file_path)[1].replace(".", "").lower()

    if file_type == "":
        print("File has no extension.")
        connection.close()
        return False

    # validation checks
    if file_name == "":
        print("File name cannot be empty.")
        connection.close()
        return False

    if file_path == "":
        print("File path cannot be empty.")
        connection.close()
        return False

    allowed_types = [
        "jpg",
        "jpeg",
        "png",
        "pdf",
        "txt"
    ]

    if file_type not in allowed_types:
        print("File type not allowed.")
        connection.close()
        return False

    max_size = 8 * 1024 * 1024

    if not os.path.exists(file_path):
        print("File does not exist.")
        connection.close()
        return False

    if os.path.getsize(file_path) > max_size:
        print("File is too large. Maximum size is 8MB.")
        connection.close()
        return False

    cursor.execute("""
    INSERT INTO Evidence
    (file_name, file_type, file_path, notes, uploaded_by, incident_id)

    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        file_name,
        file_type,
        file_path,
        notes,
        uploaded_by,
        incident_id
    ))

    connection.commit()

    connection.close()

    print("Evidence added successfully!")

    return True

# gets all evidence attached to an incident
def get_evidence(incident_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT evidence_id, file_name, file_type, file_path, notes, uploaded_at, uploaded_by
    FROM Evidence
    WHERE incident_id = ?
    ORDER BY uploaded_at DESC
    """,
    (incident_id,))

    evidence_list = cursor.fetchall()

    connection.close()

    return evidence_list

# gets all evidence uploaded by a specific user
def get_evidence_by_uploader(uploaded_by):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT evidence_id, file_name, file_type, file_path, notes, uploaded_at, incident_id
    FROM Evidence
    WHERE uploaded_by = ?
    ORDER BY uploaded_at DESC
    """,
    (uploaded_by,))

    evidence_list = cursor.fetchall()

    connection.close()

    return evidence_list