import sqlite3


# connects to the Sentinel database
def get_connection():
    return sqlite3.connect("sentinel.db")

# allows investigators to generate reports
def create_report(user_id, role, incident_id):

    connection = get_connection()
    cursor = connection.cursor()

    # checks permission
    if role != "investigator":
        print("Access denied. Only investigators can generate reports.")
        connection.close()
        return False

    # gets incident details
    cursor.execute("""
    SELECT title, category, severity, description, status
    FROM Incident
    WHERE incident_id = ?
    """,
    (incident_id,))

    incident = cursor.fetchone()

    if not incident:
        print("Incident not found.")
        connection.close()
        return False

    title, category, severity, description, status = incident

    # only resolved/closed incidents
    if status not in ["Resolved", "Closed"]:
        print("Reports can only be generated for resolved or closed incidents.")
        connection.close()
        return False

    summary = (
        f"Incident Report\n\n"
        f"Title: {title}\n"
        f"Category: {category}\n"
        f"Severity: {severity}\n"
        f"Status: {status}\n\n"
        f"Description:\n{description}"
    )

    cursor.execute("""
    INSERT INTO SummaryReport
    (summary, generated_by, incident_id)

    VALUES (?, ?, ?)
    """,
    (
        summary,
        user_id,
        incident_id
    ))

    connection.commit()
    connection.close()

    print("Report generated successfully!")

    return summary

# gets all reports generated for an incident
def get_reports(incident_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT report_id, summary, generated_at, generated_by
    FROM SummaryReport
    WHERE incident_id = ?
    ORDER BY generated_at DESC
    """,
    (incident_id,))

    reports = cursor.fetchall()

    connection.close()

    return reports