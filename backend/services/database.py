"""SQLite database service for policy simulator."""

import sqlite3
import json
import re
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy_simulator.db')


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            inputs TEXT NOT NULL,
            results TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inputs TEXT NOT NULL,
            results TEXT NOT NULL,
            model_type TEXT,
            confidence REAL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_training_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT NOT NULL,
            rmse REAL,
            r2_score REAL,
            training_samples INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized")


# --- Scenarios CRUD ---

def save_scenario(name: str, inputs: dict, results: dict) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO scenarios (name, inputs, results) VALUES (?, ?, ?)',
        (name, json.dumps(inputs), json.dumps(results))
    )
    conn.commit()
    scenario_id = cursor.lastrowid
    conn.close()
    return {'id': scenario_id, 'name': name, 'inputs': inputs, 'results': results}


def get_all_scenarios() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scenarios ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row['id'],
            'name': row['name'],
            'inputs': json.loads(row['inputs']),
            'results': json.loads(row['results']),
            'created_at': row['created_at'],
        }
        for row in rows
    ]


def delete_scenario(scenario_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM scenarios WHERE id = ?', (scenario_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# --- Simulation History ---

def save_simulation(inputs: dict, results: dict, model_type: str = None, confidence: float = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO simulation_history (inputs, results, model_type, confidence) VALUES (?, ?, ?, ?)',
        (json.dumps(inputs), json.dumps(results), model_type, confidence)
    )
    conn.commit()
    sim_id = cursor.lastrowid
    conn.close()
    return sim_id


def get_history(limit: int = 50) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM simulation_history ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row['id'],
            'inputs': json.loads(row['inputs']),
            'results': json.loads(row['results']),
            'model_type': row['model_type'],
            'confidence': row['confidence'],
            'timestamp': row['created_at'],
        }
        for row in rows
    ]


# --- Training Log ---

def log_training(model_type: str, rmse: float, r2: float, samples: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO model_training_log (model_type, rmse, r2_score, training_samples) VALUES (?, ?, ?, ?)',
        (model_type, rmse, r2, samples)
    )
    conn.commit()
    conn.close()


# --- User Management ---

def create_user(email: str, password_hash: str, name: str) -> dict:
    """Create a new user. Returns user dict or raises on duplicate."""
    email = email.lower().strip()
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        raise ValueError('Invalid email format')
    if len(name.strip()) < 2:
        raise ValueError('Name must be at least 2 characters')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
            (email, password_hash, name.strip())
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {'id': user_id, 'email': email, 'name': name.strip()}
    except sqlite3.IntegrityError:
        raise ValueError('Email already registered')
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Find a user by email. Returns dict with password_hash or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        'id': row['id'],
        'email': row['email'],
        'password_hash': row['password_hash'],
        'name': row['name'],
        'created_at': row['created_at'],
    }


def get_user_by_id(user_id: int) -> dict | None:
    """Find a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, name, created_at FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        'id': row['id'],
        'email': row['email'],
        'name': row['name'],
        'created_at': row['created_at'],
    }


def update_last_login(user_id: int):
    """Update user's last login timestamp."""
    conn = get_connection()
    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


# Initialize on import
init_db()
