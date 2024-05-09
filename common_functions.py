import pymssql
import os
from dotenv import load_dotenv
from flask import flash
from app_configuration import get_password_policy
from flask_mail import Message

load_dotenv()
password = os.getenv('MSSQL_SA_PASSWORD')

conn = pymssql.connect("172.17.0.1", "sa", password, "CommunicationLTD")


def get_user_data_from_db(username=None, password=None):
    with conn.cursor(as_dict=True) as cursor:
        if username and password:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        else:
            cursor.execute(f"SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()


def get_all_sectors_names_from_db():
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT sector_name FROM sectors")
        sectors = cursor.fetchall()
        sectors = [sector['sector_name'] for sector in sectors]
    return sectors


def get_user_by_username(username):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
    return user


def check_if_user_exists_using_email(email: str) -> bool:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s ", (email,))
        if cursor.fetchone():  # todo: check if this condition works
            return True
        return False


def insert_new_user_to_db(new_username, new_password, new_email, internet_package_type, user_salt):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute("INSERT INTO users (username, password, email, package_id,salt) VALUES (%s, %s, %s, %s, %s)",
                       (new_username, new_password, new_email, internet_package_type, user_salt))


def insert_user_sectors_selected_to_db(publish_sectors, user_id):
    with conn.cursor(as_dict=True) as cursor:
        for sector in publish_sectors:
            cursor.execute("SELECT sector_id FROM sectors WHERE sector_name = %s", (sector,))
            sector_id = cursor.fetchone()['sector_id']
            cursor.execute("INSERT INTO user_sectors (user_id, sector_id) VALUES (%s, %s)",
                           (user_id, sector_id))
    conn.commit()


def validate_password(password):
    password_policy, _ = get_password_policy()
    with open(os.path.abspath('passwords.txt'), 'r') as common_passwords_file:
        for common_pwd in common_passwords_file:
            if password == common_pwd.strip():
                flash('Password is a known password.')
                return False
    if len(password_policy.test(password)) > 0:
        flash('The Password does not meet the minimum requirements ', 'error')
        for missing_requirement in password_policy.test(password):
            match str(missing_requirement):
                case 'Length(10)':
                    flash('Please enter a password with at least 10 characters', 'error')
                case 'Uppercase(2)':
                    flash('Please enter a password with at least 2 Uppercase Letters', 'error')
                case 'Numbers(1)':
                    flash('Please enter a password with at least 1 Number', 'error')
                case 'Special(1)':
                    flash('Please enter a password with at least 1 Special String', 'error')
                case 'NonLetters(1)':
                    flash('Please enter a password with at least 10 characters', 'error')
        return False
    else:
        return True

def create_password_reset_table():
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS PasswordReset (
                          user_id INT PRIMARY KEY,
                          email NVARCHAR(100) UNIQUE,
                          hash_code VARBINARY(100) UNIQUE
                          )''')
        conn.commit()


def insert_password_reset(email, hash_code):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute('''SELECT email FROM PasswordReset WHERE email = %s''', (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            cursor.execute('''UPDATE PasswordReset SET hash_code = %s WHERE email = %s''', (hash_code, email))
        else:
            cursor.execute('''INSERT INTO PasswordReset (email, hash_code) VALUES (%s, %s)''', (email, hash_code))
        conn.commit()


def send_email(mail, recipient, hash_code):
    msg = Message('Confirm Password Change', sender='compsec2024@gmail.com', recipients=[recipient])
    msg.body = "Hello,\nWe've received a request to reset your password. If you want to reset your password, " \
               "click the link below and enter your new password\n http://localhost:5000/" + hash_code
    mail.send(msg)

def change_user_password(email, new_password):
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute('''UPDATE users SET password = %s WHERE email = %s''', (new_password, email))
        conn.commit()
