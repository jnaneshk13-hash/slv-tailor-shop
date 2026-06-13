import hashlib
import os
from functools import wraps
from flask import session, redirect, url_for

def hash_password(password):
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def check_password(password, password_hash):
    try:
        salt, hashed = password_hash.split(':')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except:
        return False

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated
