import sqlite3

def get_connection():
    return sqlite3.connect("sentinel.db")

ALLOWED_STATUSES = ["New", "Investigated", "Contained", "Resolved", "Closed"]

def change_status(user_id, role, incident_id, new_status):

    connection = get_connection()
    cursor = connection.cursor()

    print("Updating incident status...")

    if role != "investigator":
        print("Access denied. Only investigators can change incident status.")
        connection.close()
        return False

    cursor.execute("""
    SELECT status
    FROM Incident
    WHERE incident_id = ?
    """,
    (incident_id,))

    incident = cursor.fetchone()

    if not incident:
        print("Incident not found.")
        connection.close()
        return False

    old_status = incident[0]

    if new_status not in ALLOWED_STATUSES:
        print("Invalid status.")
        connection.close()
        return False

    # reopen exception: Closed can always go back to Investigated
    is_reopen = (old_status == "Closed" and new_status == "Investigated")

    if not is_reopen:

        old_index = ALLOWED_STATUSES.index(old_status)
        new_index = ALLOWED_STATUSES.index(new_status)

        if new_index != old_index + 1:
            print(f"Invalid move: cannot go from {old_status} to {new_status}.")
            connection.close()
            return False

    cursor.execute("""
    UPDATE Incident
    SET status = ?
    WHERE incident_id = ?
    """,
    (
        new_status,
        incident_id
    ))

    cursor.execute("""
    INSERT INTO StatusChange
    (old_status, new_status, changed_by, incident_id)

    VALUES (?, ?, ?, ?)
    """,
    (
        old_status,
        new_status,
        user_id,
        incident_id
    ))

    connection.commit()

    print("Status updated successfully!")

    connection.close()

    return True

def get_status_history(incident_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT change_id, old_status, new_status, changed_at, changed_by
    FROM StatusChange
    WHERE incident_id = ?
    ORDER BY changed_at DESC
    """,
    (incident_id,))

    history = cursor.fetchall()

    connection.close()

    return history


if __name__ == "__main__":
    result = change_status(2, "investigator", 1, "Investigated")
    print(result)