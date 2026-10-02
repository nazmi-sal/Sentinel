#creates a database
import sqlite3

def create_tables():

    connection = sqlite3.connect("sentinel.db")
    cursor = connection.cursor()

    #create a table for users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User(

        user_id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL

    )
    """)

    connection.commit()

    #create a table for incidents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Incident(

        incident_id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL CHECK (
        severity IN ('Low', 'Medium', 'High', 'Critical')
    ),
        description TEXT,
        location TEXT,
        status TEXT DEFAULT 'New' CHECK (
        status IN ('New', 'Investigated', 'Contained', 'Resolved', 'Closed')
    ),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP, 

        reporter_id INTEGER NOT NULL,
        investigator_id INTEGER,
        FOREIGN KEY (reporter_id) REFERENCES User(user_id),
        FOREIGN KEY (investigator_id) REFERENCES User(user_id)
    )
    """)

    connection.commit()

    #create a table for status change
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS StatusChange(

        change_id INTEGER PRIMARY KEY AUTOINCREMENT,

        old_status TEXT NOT NULL,
        new_status TEXT NOT NULL,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        changed_by INTEGER NOT NULL,
        incident_id INTEGER NOT NULL,

        FOREIGN KEY (changed_by) REFERENCES User(user_id),
        FOREIGN KEY (incident_id) REFERENCES Incident(incident_id)

    )
    """)

    connection.commit()

    #create a table for evidence
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Evidence(

        evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
       
        file_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        notes TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        uploaded_by INTEGER NOT NULL,
        incident_id INTEGER NOT NULL,
        FOREIGN KEY (uploaded_by) REFERENCES User(user_id),
        FOREIGN KEY (incident_id) REFERENCES Incident(incident_id)

    )
    """)

    connection.commit()

    #create a table for summary reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SummaryReport(

        report_id INTEGER PRIMARY KEY AUTOINCREMENT,

        summary TEXT NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        generated_by INTEGER NOT NULL,
        incident_id INTEGER NOT NULL,
        FOREIGN KEY (generated_by) REFERENCES User(user_id),
        FOREIGN KEY (incident_id) REFERENCES Incident(incident_id)
    )
    """)

    connection.commit()
    connection.close()

    print("Database tables ready.")

if __name__ == "__main__":
    create_tables()