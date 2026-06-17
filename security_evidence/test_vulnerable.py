# test_vulnerable.py
# VULNERABLE CODE — FOR SECURITY TESTING DEMONSTRATION ONLY
# This file demonstrates common security vulnerabilities
# BEFORE hardening/mitigation

import os
import sqlite3
import subprocess
import hashlib
import pickle
import random
import ssl

# ─── B105 — Hardcoded Passwords ───────────────────────────
# Vulnerability: Credentials hardcoded in source code
# Risk: Attacker can read source code and get credentials
PASSWORD = "admin123"
SECRET_KEY = "hardcoded-secret-key-12345"
DATABASE_PASSWORD = "password123"
API_KEY = "sk-1234567890abcdef"

# ─── B106 — Hardcoded password in function ────────────────
# Vulnerability: Password hardcoded as default value
def connect_database():
    password = "supersecret"
    return password

# ─── B107 — Hardcoded password in argument ────────────────
# Vulnerability: Default password in function argument
def login(username, password="admin123"):
    return username

# ─── B101 — Use of assert ────────────────────────────────
# Vulnerability: assert is removed in optimized mode
def check_admin(user):
    assert user == "admin", "Not admin"
    return True

# ─── B307 — Use of eval() ────────────────────────────────
# Vulnerability: eval() can execute arbitrary code
# Attack: eval("__import__('os').system('rm -rf /')")
def calculate(expression):
    return eval(expression)

# ─── B301 — Pickle deserialization ───────────────────────
# Vulnerability: Pickle can execute arbitrary code when loading
# Attack: Send malicious pickle data to execute commands
def load_user_data(data):
    return pickle.loads(data)

# ─── B311 — Weak random number generator ─────────────────
# Vulnerability: random is not cryptographically secure
# Attack: Predict tokens and hijack sessions
def generate_session_token():
    return random.randint(1000, 9999)

def generate_reset_token():
    return str(random.random())

# ─── B324 — Weak MD5 hashing ─────────────────────────────
# Vulnerability: MD5 is broken and easily cracked
# Attack: Rainbow table lookup cracks MD5 passwords instantly
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def hash_token(token):
    return hashlib.md5(token.encode()).hexdigest()

# ─── B501 — SSL verification disabled ────────────────────
# Vulnerability: SSL certificate not verified
# Attack: Man-in-the-middle attack possible
def create_ssl_connection():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

# ─── B602 — subprocess with shell=True ───────────────────
# Vulnerability: Shell injection possible
# Attack: run_command("ls; rm -rf /")
def run_command(cmd):
    subprocess.call(cmd, shell=True)

def execute_system(cmd):
    os.system(cmd)

# ─── B603 — subprocess without shell ─────────────────────
# Vulnerability: Still allows command injection
def run_process(cmd):
    subprocess.Popen(cmd)

# ─── B608 — SQL Injection ────────────────────────────────
# Vulnerability: User input directly concatenated into SQL
# Attack: username = "' OR '1'='1" -- bypass login
def get_user_by_username(username):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    # VULNERABLE: Direct string concatenation
    query = "SELECT * FROM auth_user WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()

def get_user_by_id(user_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    # VULNERABLE: No parameterized query
    query = "SELECT * FROM auth_user WHERE id = " + str(user_id)
    cursor.execute(query)
    return cursor.fetchone()

# ─── B324 — Weak SHA1 hashing ────────────────────────────
# Vulnerability: SHA1 is deprecated and weak
def hash_file(filepath):
    return hashlib.sha1(open(filepath, 'rb').read()).hexdigest()