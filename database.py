import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = 'listings_history.db'

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Table for tracking all generated runs/sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                phone_number TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                service_type TEXT NOT NULL,
                requested_count INTEGER NOT NULL,
                generated_count INTEGER NOT NULL
            )
        ''')

        # Table for tracking used business names
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS used_business_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                first_used_run_id INTEGER,
                times_used INTEGER DEFAULT 1,
                FOREIGN KEY (first_used_run_id) REFERENCES runs(id)
            )
        ''')

        # Table for tracking used commercial addresses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS used_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                first_used_run_id INTEGER,
                times_used INTEGER DEFAULT 1,
                UNIQUE(latitude, longitude),
                FOREIGN KEY (first_used_run_id) REFERENCES runs(id)
            )
        ''')

        # Table for all generated listings (complete history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                business_name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            )
        ''')

        # Create indexes for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_business_names
            ON used_business_names(name)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_addresses_coords
            ON used_addresses(latitude, longitude)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_addresses_location
            ON used_addresses(city, state)
        ''')

def create_run(phone_number, city, state, service_type, requested_count, generated_count):
    """Create a new run record and return its ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO runs (phone_number, city, state, service_type, requested_count, generated_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (phone_number, city, state, service_type, requested_count, generated_count))
        return cursor.lastrowid

def is_business_name_used(name):
    """Check if a business name has been used before"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM used_business_names WHERE name = ?', (name,))
        return cursor.fetchone() is not None

def is_address_used(latitude, longitude):
    """Check if an address (by coordinates) has been used before"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM used_addresses
            WHERE latitude = ? AND longitude = ?
        ''', (latitude, longitude))
        return cursor.fetchone() is not None

def is_address_used_by_text(address, city, state):
    """Check if an address (by text) has been used before"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM used_addresses
            WHERE address = ? AND city = ? AND state = ?
        ''', (address, city, state))
        return cursor.fetchone() is not None

def add_business_name(name, run_id):
    """Add a business name to the used names list"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO used_business_names (name, first_used_run_id)
                VALUES (?, ?)
            ''', (name, run_id))
        except sqlite3.IntegrityError:
            # Name already exists, increment usage count
            cursor.execute('''
                UPDATE used_business_names
                SET times_used = times_used + 1
                WHERE name = ?
            ''', (name,))

def add_address(address, latitude, longitude, city, state, run_id):
    """Add an address to the used addresses list"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO used_addresses
                (address, latitude, longitude, city, state, first_used_run_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (address, latitude, longitude, city, state, run_id))
        except sqlite3.IntegrityError:
            # Address already exists, increment usage count
            cursor.execute('''
                UPDATE used_addresses
                SET times_used = times_used + 1
                WHERE latitude = ? AND longitude = ?
            ''', (latitude, longitude))

def save_listing(run_id, business_name, address, phone_number, latitude, longitude):
    """Save a complete listing to the database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generated_listings
            (run_id, business_name, address, phone_number, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (run_id, business_name, address, phone_number, latitude, longitude))

def get_all_runs():
    """Get all previous runs with summary information"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                id,
                timestamp,
                phone_number,
                city,
                state,
                requested_count,
                generated_count
            FROM runs
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_run_details(run_id):
    """Get detailed information about a specific run including all listings"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get run information
        cursor.execute('SELECT * FROM runs WHERE id = ?', (run_id,))
        run = cursor.fetchone()

        if not run:
            return None

        # Get all listings for this run
        cursor.execute('''
            SELECT
                business_name,
                address,
                phone_number,
                latitude,
                longitude,
                timestamp
            FROM generated_listings
            WHERE run_id = ?
            ORDER BY id
        ''', (run_id,))

        listings = [dict(row) for row in cursor.fetchall()]

        return {
            'run': dict(run),
            'listings': listings
        }

def get_statistics():
    """Get overall statistics about the database"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Total runs
        cursor.execute('SELECT COUNT(*) as count FROM runs')
        total_runs = cursor.fetchone()['count']

        # Total unique business names
        cursor.execute('SELECT COUNT(*) as count FROM used_business_names')
        total_business_names = cursor.fetchone()['count']

        # Total unique addresses
        cursor.execute('SELECT COUNT(*) as count FROM used_addresses')
        total_addresses = cursor.fetchone()['count']

        # Total listings generated
        cursor.execute('SELECT COUNT(*) as count FROM generated_listings')
        total_listings = cursor.fetchone()['count']

        # Most recent run
        cursor.execute('''
            SELECT timestamp, city, state, service_type, generated_count
            FROM runs
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        recent_run = cursor.fetchone()

        return {
            'total_runs': total_runs,
            'total_unique_business_names': total_business_names,
            'total_unique_addresses': total_addresses,
            'total_listings_generated': total_listings,
            'most_recent_run': dict(recent_run) if recent_run else None
        }

def get_used_addresses_for_city(city, state):
    """Get all addresses that have been used for a specific city"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT address, latitude, longitude, times_used
            FROM used_addresses
            WHERE city = ? AND state = ?
        ''', (city, state))
        return [dict(row) for row in cursor.fetchall()]

def clear_all_data():
    """Clear all data from the database (use with caution!)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM generated_listings')
        cursor.execute('DELETE FROM used_addresses')
        cursor.execute('DELETE FROM used_business_names')
        cursor.execute('DELETE FROM runs')
