import mysql.connector
from mysql.connector import Error
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'qhotels_user'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'qhotels_db')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_settings():
    conn = get_db_connection()
    settings = {}
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT setting_key, setting_value FROM settings")
            rows = cursor.fetchall()
            for row in rows:
                settings[row['setting_key']] = row['setting_value']
        finally:
            cursor.close()
            conn.close()
    return settings

def ensure_admin_user(username, password):
    if not username or not password:
        return False

    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM admin_users LIMIT 1")
        existing_admin = cursor.fetchone()
        if existing_admin:
            return True

        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error ensuring admin user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def verify_admin_credentials(username, password):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT password_hash FROM admin_users WHERE username = %s LIMIT 1",
            (username,)
        )
        admin = cursor.fetchone()
        if not admin:
            return False
        return check_password_hash(admin['password_hash'], password)
    except Error as e:
        print(f"Error verifying admin credentials: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
