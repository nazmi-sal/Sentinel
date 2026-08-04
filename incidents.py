import sqlite3

# connects to the Sentinel database
def get_connection():
    return sqlite3.connect("sentinel.db")

# creates an incident
def create_incident(title, category, severity, description, location, reporter_id, investigator_id):

    connection = get_connection()
    cursor = connection.cursor()

    # validation checks
    if title == "":
        print("Title cannot be empty.")
        connection.close()
        return False

    if category == "":
        print("Category cannot be empty.")
        connection.close()
        return False

    if description == "":
        print("Description cannot be empty.")
        connection.close()
        return False

    if severity not in ["Low", "Medium", "High", "Critical"]:
        print("Invalid severity.")
        connection.close()
        return False

    # checks reporter exists
    cursor.execute("""
    SELECT user_id
    FROM User
    WHERE user_id = ?
    """,
    (reporter_id,))

    if not cursor.fetchone():
        print("Reporter not found.")
        connection.close()
        return False

    # checks investigator exists
    cursor.execute("""
    SELECT user_id
    FROM User
    WHERE user_id = ? AND role = 'investigator'
    """,
    (investigator_id,))

    investigator = cursor.fetchone()

    if not investigator:
        print("Investigator not found.")
        connection.close()
        return False

    # inserts incident
    cursor.execute("""
    INSERT INTO Incident
    (title, category, severity, description, location, reporter_id, investigator_id)

    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        title,
        category,
        severity,
        description,
        location,
        reporter_id,
        investigator_id
    ))

    connection.commit()

    print("Incident created successfully!")

    connection.close()

    return True

# gets a single incident by id
def get_incident(incident_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT incident_id, title, category, severity, description, location,
           status, created_at, closed_at, reporter_id, investigator_id
    FROM Incident
    WHERE incident_id = ?
    """,
    (incident_id,))

    incident = cursor.fetchone()

    connection.close()

    return incident

# gets all incidents
def get_all_incidents():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT incident_id, title, category, severity, description, location,
           status, created_at, closed_at, reporter_id, investigator_id
    FROM Incident
    ORDER BY created_at DESC
    """)

    incidents = cursor.fetchall()

    connection.close()

    return incidents

# gets all incidents reported by a specific user
def get_incidents_by_reporter(reporter_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT incident_id, title, category, severity, description, location,
           status, created_at, closed_at, reporter_id, investigator_id
    FROM Incident
    WHERE reporter_id = ?
    ORDER BY created_at DESC
    """,
    (reporter_id,))

    incidents = cursor.fetchall()

    connection.close()

    return incidents

# searches/filters incidents by status, category, severity, and date range
def search_incidents(status=None, category=None, severity=None, date_from=None, date_to=None):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT incident_id, title, category, severity, description, location,
           status, created_at, closed_at, reporter_id, investigator_id
    FROM Incident
    WHERE 1=1
    """

    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if category:
        query += " AND category = ?"
        params.append(category)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if date_from:
        query += " AND created_at >= ?"
        params.append(date_from)

    if date_to:
        query += " AND created_at <= ?"
        params.append(date_to)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)

    incidents = cursor.fetchall()

    connection.close()

    return incidents