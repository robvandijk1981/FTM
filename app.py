from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
import datetime
import os
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from urllib.parse import urlparse
import re

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Environment configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///task_manager.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Database setup
DATABASE = 'task_manager.db'
IS_POSTGRESQL = DATABASE_URL.startswith('postgresql://')

def init_db():
    """Initialize database with tables and sample data"""
    # Define table schemas for both SQLite and PostgreSQL
    if IS_POSTGRESQL:
        # PostgreSQL table creation
        users_table = '''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        tracks_table = '''
            CREATE TABLE IF NOT EXISTS tracks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                color VARCHAR(7) DEFAULT '#3B82F6',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        '''
        
        goals_table = '''
            CREATE TABLE IF NOT EXISTS goals (
                id SERIAL PRIMARY KEY,
                track_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                target_value INTEGER DEFAULT 1,
                current_value INTEGER DEFAULT 0,
                unit VARCHAR(50) DEFAULT 'times',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks (id) ON DELETE CASCADE
            )
        '''
        
        tasks_table = '''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                goal_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE CASCADE
            )
        '''
    else:
        # SQLite table creation
        users_table = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        tracks_table = '''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#3B82F6',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        '''
        
        goals_table = '''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_value INTEGER DEFAULT 1,
                current_value INTEGER DEFAULT 0,
                unit TEXT DEFAULT 'times',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        '''
        
        tasks_table = '''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals (id)
            )
        '''
    
    # Create tables
    execute_query(users_table)
    execute_query(tracks_table)
    execute_query(goals_table)
    execute_query(tasks_table)
    
    # Check if Rob van Dijk exists
    user = execute_query('SELECT id FROM users WHERE email = %s' if IS_POSTGRESQL else 'SELECT id FROM users WHERE email = ?', 
                        ('rob.vandijk@example.com',), fetch_one=True)
    
    if not user:
        # Create Rob van Dijk user with bcrypt password hashing
        password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if IS_POSTGRESQL:
            user_id = execute_query(
                'INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s) RETURNING id',
                ('rob.vandijk@example.com', password_hash, 'Rob van Dijk')
            )['id']
        else:
            execute_query(
                'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
                ('rob.vandijk@example.com', password_hash, 'Rob van Dijk')
            )
            user_id = execute_query('SELECT last_insert_rowid()', fetch_one=True)[0]
        
        # Create sample tracks, goals, and tasks
        tracks_data = [
            ('Morning Routine', 'Daily morning activities', '#10B981'),
            ('Exercise & Health', 'Physical fitness and wellness', '#EF4444'),
            ('Work Productivity', 'Professional tasks and goals', '#3B82F6'),
            ('Learning & Growth', 'Personal development', '#8B5CF6'),
            ('Social Connections', 'Relationships and networking', '#F59E0B'),
            ('Creative Projects', 'Artistic and creative pursuits', '#EC4899'),
            ('Evening Wind-down', 'End of day routines', '#6366F1')
        ]
        
        for track_name, track_desc, track_color in tracks_data:
            if IS_POSTGRESQL:
                track_id = execute_query(
                    'INSERT INTO tracks (user_id, name, description, color) VALUES (%s, %s, %s, %s) RETURNING id',
                    (user_id, track_name, track_desc, track_color)
                )['id']
            else:
                execute_query(
                    'INSERT INTO tracks (user_id, name, description, color) VALUES (?, ?, ?, ?)',
                    (user_id, track_name, track_desc, track_color)
                )
                track_id = execute_query('SELECT last_insert_rowid()', fetch_one=True)[0]
            
            # Add sample goals and tasks for each track
            if track_name == 'Morning Routine':
                if IS_POSTGRESQL:
                    goal_id = execute_query(
                        'INSERT INTO goals (track_id, title, description, target_value, unit) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                        (track_id, 'Wake up early', 'Consistent 6 AM wake-up time', 7, 'days per week')
                    )['id']
                else:
                    execute_query(
                        'INSERT INTO goals (track_id, title, description, target_value, unit) VALUES (?, ?, ?, ?, ?)',
                        (track_id, 'Wake up early', 'Consistent 6 AM wake-up time', 7, 'days per week')
                    )
                    goal_id = execute_query('SELECT last_insert_rowid()', fetch_one=True)[0]
                
                tasks = [
                    ('Set alarm for 6 AM', 'Use consistent alarm time'),
                    ('Get out of bed immediately', 'No snoozing allowed'),
                    ('Drink water first thing', 'Hydrate upon waking')
                ]
                for task_title, task_desc in tasks:
                    if IS_POSTGRESQL:
                        execute_query(
                            'INSERT INTO tasks (goal_id, title, description) VALUES (%s, %s, %s)',
                            (goal_id, task_title, task_desc)
                        )
                    else:
                        execute_query(
                            'INSERT INTO tasks (goal_id, title, description) VALUES (?, ?, ?)',
                            (goal_id, task_title, task_desc)
                        )
    
    print("Database initialized successfully")

def get_db_connection():
    """Get database connection - supports both SQLite and PostgreSQL"""
    if IS_POSTGRESQL:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute database query with proper cursor handling"""
    conn = get_db_connection()
    try:
        if IS_POSTGRESQL:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            # For INSERT operations, return the inserted row or lastrowid
            if IS_POSTGRESQL:
                result = cursor.fetchone() if 'RETURNING' in query.upper() else None
            else:
                result = cursor.lastrowid
        
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise e
    finally:
        conn.close()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text, max_length=255):
    """Sanitize user input"""
    if not text:
        return ""
    # Remove potentially dangerous characters and limit length
    sanitized = re.sub(r'[<>"\']', '', str(text))
    return sanitized[:max_length].strip()

def validate_color(color):
    """Validate hex color format"""
    pattern = r'^#[0-9A-Fa-f]{6}$'
    return re.match(pattern, color) is not None

def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# API Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Sanitize inputs
    email = sanitize_input(email, 255)
    password = sanitize_input(password, 255)
    
    user = execute_query(
        'SELECT * FROM users WHERE email = %s' if IS_POSTGRESQL else 'SELECT * FROM users WHERE email = ?', 
        (email,), fetch_one=True
    )
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password with bcrypt
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name']
        }
    })

@app.route('/api/tracks', methods=['GET'])
@token_required
def get_tracks(current_user_id):
    """Get all tracks for the current user"""
    tracks = execute_query(
        'SELECT * FROM tracks WHERE user_id = %s ORDER BY created_at' if IS_POSTGRESQL else 'SELECT * FROM tracks WHERE user_id = ? ORDER BY created_at',
        (current_user_id,), fetch_all=True
    )
    
    return jsonify([dict(track) for track in tracks])

@app.route('/api/tracks', methods=['POST'])
@token_required
def create_track(current_user_id):
    """Create a new track"""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    color = data.get('color', '#3B82F6')
    
    if not name:
        return jsonify({'error': 'Track name is required'}), 400
    
    # Validate and sanitize inputs
    name = sanitize_input(name, 255)
    description = sanitize_input(description, 1000)
    
    if not validate_color(color):
        color = '#3B82F6'  # Default color if invalid
    
    if IS_POSTGRESQL:
        track = execute_query(
            'INSERT INTO tracks (user_id, name, description, color) VALUES (%s, %s, %s, %s) RETURNING *',
            (current_user_id, name, description, color), fetch_one=True
        )
    else:
        execute_query(
            'INSERT INTO tracks (user_id, name, description, color) VALUES (?, ?, ?, ?)',
            (current_user_id, name, description, color)
        )
        track_id = execute_query('SELECT last_insert_rowid()', fetch_one=True)[0]
        track = execute_query('SELECT * FROM tracks WHERE id = ?', (track_id,), fetch_one=True)
    
    return jsonify(dict(track)), 201

@app.route('/api/goals', methods=['GET'])
@token_required
def get_goals(current_user_id):
    """Get goals for a specific track"""
    track_id = request.args.get('track_id')
    if not track_id:
        return jsonify({'error': 'track_id parameter required'}), 400
    
    # Verify track belongs to user
    track = execute_query(
        'SELECT * FROM tracks WHERE id = %s AND user_id = %s' if IS_POSTGRESQL else 'SELECT * FROM tracks WHERE id = ? AND user_id = ?',
        (track_id, current_user_id), fetch_one=True
    )
    
    if not track:
        return jsonify({'error': 'Track not found'}), 404
    
    goals = execute_query(
        'SELECT * FROM goals WHERE track_id = %s ORDER BY created_at' if IS_POSTGRESQL else 'SELECT * FROM goals WHERE track_id = ? ORDER BY created_at',
        (track_id,), fetch_all=True
    )
    
    return jsonify([dict(goal) for goal in goals])

@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks(current_user_id):
    """Get tasks for a specific goal"""
    goal_id = request.args.get('goal_id')
    if not goal_id:
        return jsonify({'error': 'goal_id parameter required'}), 400
    
    # Verify goal belongs to user (through track)
    goal = execute_query('''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = %s AND t.user_id = %s
    ''' if IS_POSTGRESQL else '''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = ? AND t.user_id = ?
    ''', (goal_id, current_user_id), fetch_one=True)
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    tasks = execute_query(
        'SELECT * FROM tasks WHERE goal_id = %s ORDER BY created_at' if IS_POSTGRESQL else 'SELECT * FROM tasks WHERE goal_id = ? ORDER BY created_at',
        (goal_id,), fetch_all=True
    )
    
    return jsonify([dict(task) for task in tasks])

# Additional CRUD Operations for Tracks
@app.route('/api/tracks/<int:track_id>', methods=['PUT'])
@token_required
def update_track(current_user_id, track_id):
    """Update a track"""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    color = data.get('color', '#3B82F6')
    
    if not name:
        return jsonify({'error': 'Track name is required'}), 400
    
    # Validate and sanitize inputs
    name = sanitize_input(name, 255)
    description = sanitize_input(description, 1000)
    
    if not validate_color(color):
        color = '#3B82F6'  # Default color if invalid
    
    # Verify track belongs to user
    track = execute_query(
        'SELECT * FROM tracks WHERE id = %s AND user_id = %s' if IS_POSTGRESQL else 'SELECT * FROM tracks WHERE id = ? AND user_id = ?',
        (track_id, current_user_id), fetch_one=True
    )
    
    if not track:
        return jsonify({'error': 'Track not found'}), 404
    
    # Update track
    updated_track = execute_query(
        'UPDATE tracks SET name = %s, description = %s, color = %s WHERE id = %s AND user_id = %s RETURNING *' if IS_POSTGRESQL else 'UPDATE tracks SET name = ?, description = ?, color = ? WHERE id = ? AND user_id = ?',
        (name, description, color, track_id, current_user_id), fetch_one=True
    )
    
    if not updated_track:
        return jsonify({'error': 'Failed to update track'}), 500
    
    return jsonify(dict(updated_track))

@app.route('/api/tracks/<int:track_id>', methods=['DELETE'])
@token_required
def delete_track(current_user_id, track_id):
    """Delete a track and all associated goals and tasks"""
    # Verify track belongs to user
    track = execute_query(
        'SELECT * FROM tracks WHERE id = %s AND user_id = %s' if IS_POSTGRESQL else 'SELECT * FROM tracks WHERE id = ? AND user_id = ?',
        (track_id, current_user_id), fetch_one=True
    )
    
    if not track:
        return jsonify({'error': 'Track not found'}), 404
    
    # Delete track (cascade will handle goals and tasks)
    execute_query(
        'DELETE FROM tracks WHERE id = %s AND user_id = %s' if IS_POSTGRESQL else 'DELETE FROM tracks WHERE id = ? AND user_id = ?',
        (track_id, current_user_id)
    )
    
    return jsonify({'message': 'Track deleted successfully'})

# CRUD Operations for Goals
@app.route('/api/goals', methods=['POST'])
@token_required
def create_goal(current_user_id):
    """Create a new goal"""
    data = request.get_json()
    track_id = data.get('track_id')
    title = data.get('title')
    description = data.get('description', '')
    target_value = data.get('target_value', 1)
    unit = data.get('unit', 'times')
    
    if not track_id or not title:
        return jsonify({'error': 'Track ID and title are required'}), 400
    
    # Verify track belongs to user
    track = execute_query(
        'SELECT * FROM tracks WHERE id = %s AND user_id = %s' if IS_POSTGRESQL else 'SELECT * FROM tracks WHERE id = ? AND user_id = ?',
        (track_id, current_user_id), fetch_one=True
    )
    
    if not track:
        return jsonify({'error': 'Track not found'}), 404
    
    # Create goal
    if IS_POSTGRESQL:
        goal = execute_query(
            'INSERT INTO goals (track_id, title, description, target_value, unit) VALUES (%s, %s, %s, %s, %s) RETURNING *',
            (track_id, title, description, target_value, unit), fetch_one=True
        )
    else:
        execute_query(
            'INSERT INTO goals (track_id, title, description, target_value, unit) VALUES (?, ?, ?, ?, ?)',
            (track_id, title, description, target_value, unit)
        )
        goal_id = execute_query('SELECT last_insert_rowid()', fetch_one=True)[0]
        goal = execute_query('SELECT * FROM goals WHERE id = ?', (goal_id,), fetch_one=True)
    
    return jsonify(dict(goal)), 201

@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
@token_required
def update_goal(current_user_id, goal_id):
    """Update a goal"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    target_value = data.get('target_value', 1)
    current_value = data.get('current_value', 0)
    unit = data.get('unit', 'times')
    
    if not title:
        return jsonify({'error': 'Goal title is required'}), 400
    
    # Verify goal belongs to user (through track)
    goal = execute_query('''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = %s AND t.user_id = %s
    ''' if IS_POSTGRESQL else '''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = ? AND t.user_id = ?
    ''', (goal_id, current_user_id), fetch_one=True)
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Update goal
    updated_goal = execute_query(
        'UPDATE goals SET title = %s, description = %s, target_value = %s, current_value = %s, unit = %s WHERE id = %s RETURNING *' if IS_POSTGRESQL else 'UPDATE goals SET title = ?, description = ?, target_value = ?, current_value = ?, unit = ? WHERE id = ?',
        (title, description, target_value, current_value, unit, goal_id), fetch_one=True
    )
    
    if not updated_goal:
        return jsonify({'error': 'Failed to update goal'}), 500
    
    return jsonify(dict(updated_goal))

@app.route('/api/goals/<int:goal_id>', methods=['DELETE'])
@token_required
def delete_goal(current_user_id, goal_id):
    """Delete a goal and all associated tasks"""
    # Verify goal belongs to user (through track)
    goal = execute_query('''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = %s AND t.user_id = %s
    ''' if IS_POSTGRESQL else '''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = ? AND t.user_id = ?
    ''', (goal_id, current_user_id), fetch_one=True)
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Delete goal (cascade will handle tasks)
    execute_query(
        'DELETE FROM goals WHERE id = %s' if IS_POSTGRESQL else 'DELETE FROM goals WHERE id = ?',
        (goal_id,)
    )
    
    return jsonify({'message': 'Goal deleted successfully'})

# CRUD Operations for Tasks
@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task(current_user_id):
    """Create a new task"""
    data = request.get_json()
    goal_id = data.get('goal_id')
    title = data.get('title')
    description = data.get('description', '')
    
    if not goal_id or not title:
        return jsonify({'error': 'Goal ID and title are required'}), 400
    
    # Verify goal belongs to user (through track)
    goal = execute_query('''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = %s AND t.user_id = %s
    ''' if IS_POSTGRESQL else '''
        SELECT g.* FROM goals g
        JOIN tracks t ON g.track_id = t.id
        WHERE g.id = ? AND t.user_id = ?
    ''', (goal_id, current_user_id), fetch_one=True)
    
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Create task
    if IS_POSTGRESQL:
        task = execute_query(
            'INSERT INTO tasks (goal_id, title, description) VALUES (%s, %s, %s) RETURNING *',
            (goal_id, title, description), fetch_one=True
        )
    else:
        execute_query(
            'INSERT INTO tasks (goal_id, title, description) VALUES (?, ?, ?)',
            (goal_id, title, description)
        )
        task_id = execute_query('SELECT last_insert_rowid()', fetch_one=True)[0]
        task = execute_query('SELECT * FROM tasks WHERE id = ?', (task_id,), fetch_one=True)
    
    return jsonify(dict(task)), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user_id, task_id):
    """Update a task"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    completed = data.get('completed', False)
    
    if not title:
        return jsonify({'error': 'Task title is required'}), 400
    
    # Verify task belongs to user (through goal and track)
    task = execute_query('''
        SELECT t.* FROM tasks t
        JOIN goals g ON t.goal_id = g.id
        JOIN tracks tr ON g.track_id = tr.id
        WHERE t.id = %s AND tr.user_id = %s
    ''' if IS_POSTGRESQL else '''
        SELECT t.* FROM tasks t
        JOIN goals g ON t.goal_id = g.id
        JOIN tracks tr ON g.track_id = tr.id
        WHERE t.id = ? AND tr.user_id = ?
    ''', (task_id, current_user_id), fetch_one=True)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Update task
    updated_task = execute_query(
        'UPDATE tasks SET title = %s, description = %s, completed = %s WHERE id = %s RETURNING *' if IS_POSTGRESQL else 'UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?',
        (title, description, completed, task_id), fetch_one=True
    )
    
    if not updated_task:
        return jsonify({'error': 'Failed to update task'}), 500
    
    return jsonify(dict(updated_task))

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user_id, task_id):
    """Delete a task"""
    # Verify task belongs to user (through goal and track)
    task = execute_query('''
        SELECT t.* FROM tasks t
        JOIN goals g ON t.goal_id = g.id
        JOIN tracks tr ON g.track_id = tr.id
        WHERE t.id = %s AND tr.user_id = %s
    ''' if IS_POSTGRESQL else '''
        SELECT t.* FROM tasks t
        JOIN goals g ON t.goal_id = g.id
        JOIN tracks tr ON g.track_id = tr.id
        WHERE t.id = ? AND tr.user_id = ?
    ''', (task_id, current_user_id), fetch_one=True)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Delete task
    execute_query(
        'DELETE FROM tasks WHERE id = %s' if IS_POSTGRESQL else 'DELETE FROM tasks WHERE id = ?',
        (task_id,)
    )
    
    return jsonify({'message': 'Task deleted successfully'})

# Frontend Routes
@app.route('/')
def serve_frontend():
    """Serve the main React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files or fallback to React app for client-side routing"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Fallback to React app for client-side routing
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)

