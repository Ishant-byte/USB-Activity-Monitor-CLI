import mysql.connector
import bcrypt
import getpass
import subprocess
import os

# Database connection details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""  # Change if needed
DB_NAME = "usbtracker"
TOOL_SCRIPT = "try3.py"  # Path to the actual tool

def connect_to_db():
    """Connect to MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as e:
        print(f"⚠ Database Connection Error: {e}")
        return None

def hash_password(password):
    """Hash the password securely."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_password, entered_password):
    """Verify the entered password against stored hash."""
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8'))

def register_user():
    """Register a new user."""
    username = input("Enter a new username: ").strip()
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("⚠ Passwords do not match. Registration failed.")
        return

    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if the username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                print("⚠ Username already exists. Choose another one.")
            else:
                # Insert new user with hashed password
                hashed_pw = hash_password(password).decode('utf-8')
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
                conn.commit()
                print("✅ Registration successful.")

        except mysql.connector.Error as e:
            print(f"⚠ Database Error: {e}")
        finally:
            cursor.close()
            conn.close()

def authenticate_user():
    """Authenticate a user and redirect to the main tool (try3.py)."""
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")

    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password(user[0], password):
                print(f"✅ Login successful. Welcome, {username}!")

                # Redirect to try3.py
                if os.path.exists(TOOL_SCRIPT):
                    subprocess.run(["python3", TOOL_SCRIPT])
                else:
                    print(f"⚠ Error: {TOOL_SCRIPT} not found. Make sure the script is in the same directory.")
            else:
                print("⚠ Invalid username or password.")

        except mysql.connector.Error as e:
            print(f"⚠ Database Error: {e}")
        finally:
            cursor.close()
            conn.close()

def main():
    """User menu for authentication."""
    while True:
        print("\n🔑 User Authentication")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            authenticate_user()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("⚠ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
