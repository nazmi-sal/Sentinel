# links the database
import sqlite3
import hashlib

# connects to Sentinel database
def get_connection():
    return sqlite3.connect("sentinel.db")

# hashes the password using SHA-256
def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

# creates users
def create_user(user_name, email, role, password_hash):

    print("create_user() called")

    connection = get_connection()
    cursor = connection.cursor()

    # validation checks
    if user_name == "":
        connection.close()
        return "Please enter a username."

    if email == "":
        connection.close()
        return "Please enter an email."

    if "@" not in email:
        connection.close()
        return "Please enter a valid email."

    if role not in ["investigator", "user"]:
        print("Invalid role, please enter investigator or user.")
        connection.close()
        return False

    if len(password_hash) < 8:
        connection.close()
        return "Password must be at least 8 characters."

    password_hash = hash_password(password_hash)

    # adds user to database
    try:

        cursor.execute("""
        INSERT INTO User(user_name, email, role, password_hash)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_name,
            email,
            role,
            password_hash
        ))

        connection.commit()

        print("User created successfully!")
        return True

    except sqlite3.IntegrityError as error:

        print(error)
        return str(error)

    finally:

        connection.close()

# logs users in
def login_user(email, password):

    connection = get_connection()
    cursor = connection.cursor()

    hashed_input = hash_password(password)

    cursor.execute("""
    SELECT user_id, user_name, role
    FROM User
    WHERE email = ? AND password_hash = ?
    """,
    (
        email,
        hashed_input
    ))

    user = cursor.fetchone()

    connection.close()

    if user:

        print("Login successful!")
        return user

    else:

        print("Invalid email or password.")
        return None

# gets all investigators (for dropdowns/assignment)
def get_investigators():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT user_id, user_name
    FROM User
    WHERE role = 'investigator'
    ORDER BY user_name
    """)

    investigators = cursor.fetchall()

    connection.close()

    return investigators

# gets all users 
def get_user_name(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT user_name
    FROM User
    WHERE user_id = ?
    """,
    (user_id,))

    row = cursor.fetchone()

    connection.close()

    if row:
        return row[0]

    return "Unknown"

# reassigns an incident to a different investigator
def reassign_investigator(incident_id, new_investigator_id):

    connection = get_connection()
    cursor = connection.cursor()

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

    # checks investigator exists and has correct role
    cursor.execute("""
    SELECT user_id
    FROM User
    WHERE user_id = ? AND role = 'investigator'
    """,
    (new_investigator_id,))

    if not cursor.fetchone():
        print("Investigator not found.")
        connection.close()
        return False

    cursor.execute("""
    UPDATE Incident
    SET investigator_id = ?
    WHERE incident_id = ?
    """,
    (
        new_investigator_id,
        incident_id
    ))

    connection.commit()
    connection.close()

    print("Investigator reassigned successfully!")

    return True