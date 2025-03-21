from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps
from pocketbase import PocketBase
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['DATABASE'] = '../data/HomesteadTO Grow Veggies Textbook_2025 Edition.db'
app.config['POCKETBASE_URL'] = 'http://127.0.0.1:8090'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize PocketBase client
pb = PocketBase(app.config['POCKETBASE_URL'])

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email=None, name=None):
        self.id = id
        self.username = username
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    try:
        # Get user from PocketBase
        user_data = pb.collection('users').get_one(user_id)
        return User(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email if hasattr(user_data, 'email') else None,
            name=user_data.name if hasattr(user_data, 'name') else None
        )
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Authenticate with PocketBase
            auth_data = pb.collection('users').auth_with_password(username, password)
            user_data = auth_data.record
            
            # Create user object for Flask-Login
            user = User(
                id=user_data.id,
                username=user_data.username,
                email=user_data.email if hasattr(user_data, 'email') else None,
                name=user_data.name if hasattr(user_data, 'name') else None
            )
            
            # Login user with Flask-Login
            login_user(user)
            
            # Store PocketBase token in session
            session['pb_token'] = auth_data.token
            
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Login failed: Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name', '')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        try:
            # Create user in PocketBase
            user_data = {
                "username": username,
                "password": password,
                "passwordConfirm": confirm_password,
                "name": name
            }
            
            result = pb.collection('users').create(user_data)
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            error_msg = str(e)
            if 'username' in error_msg and 'already exists' in error_msg:
                flash('Username already exists')
            else:
                flash(f'Registration failed: {error_msg}')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    # Clear PocketBase token from session
    session.pop('pb_token', None)
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    # Get unique section names for filters
    sections = conn.execute('SELECT DISTINCT section_name FROM pdf_pages WHERE section_name IS NOT NULL ORDER BY section_name').fetchall()
    conn.close()
    return render_template('dashboard.html', sections=sections)

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    section = request.args.get('section', '')
    
    conn = get_db_connection()
    
    if query and section:
        # Search with both query and section filter
        results = conn.execute('''
            SELECT id, page_number, section_name, page_text 
            FROM pdf_pages_fts 
            WHERE pdf_pages_fts MATCH ? AND section_name = ?
            ORDER BY page_number
            LIMIT 50
        ''', (query, section)).fetchall()
    elif query:
        # Search with just query
        results = conn.execute('''
            SELECT id, page_number, section_name, page_text 
            FROM pdf_pages_fts 
            WHERE pdf_pages_fts MATCH ?
            ORDER BY page_number
            LIMIT 50
        ''', (query,)).fetchall()
    elif section:
        # Filter by section only
        results = conn.execute('''
            SELECT id, page_number, section_name, page_text 
            FROM pdf_pages 
            WHERE section_name = ?
            ORDER BY page_number
            LIMIT 50
        ''', (section,)).fetchall()
    else:
        # No filters, return recent entries
        results = conn.execute('''
            SELECT id, page_number, section_name, page_text 
            FROM pdf_pages 
            ORDER BY page_number
            LIMIT 20
        ''').fetchall()
    
    conn.close()
    
    return render_template('_search_results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
