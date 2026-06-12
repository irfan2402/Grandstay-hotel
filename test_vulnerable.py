# test_vulnerable.py - VULNERABLE CODE FOR TESTING ONLY
import os
import sqlite3
import subprocess
import hashlib

# B101 - Use of assert
def check_admin(user):
    assert user == "admin", "Not admin"

# B105 - Hardcoded password
PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret-key-12345"
DATABASE_PASSWORD = "password123"

# B106 - Hardcoded password in function
def connect_db():
    password = "supersecret"
    return password

# B107 - Hardcoded password in function argument
def login(username, password="admin123"):
    return username

# B201 - Flask debug mode (shows bad practice)
DEBUG = True

# B301 - Pickle usage (insecure deserialization)
import pickle
def load_data(data):
    return pickle.loads(data)

# B307 - Use of eval
def calculate(expression):
    return eval(expression)

# B311 - Standard pseudo-random generators
import random
def generate_token():
    return random.randint(1000, 9999)

# B324 - Use of weak MD5 hash
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# B501 - SSL disabled
import ssl
def create_connection():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

# B602 - subprocess with shell=True
def run_command(cmd):
    subprocess.call(cmd, shell=True)

# B603 - subprocess without shell
def run_command2(cmd):
    subprocess.Popen(cmd)

# B608 - SQL injection
def get_user(username):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()