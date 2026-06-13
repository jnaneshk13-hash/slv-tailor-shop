import sqlite3
import os
from flask import g
from utils.auth import hash_password

DATABASE = 'database/slv_tailor.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

def init_db():
    os.makedirs('database', exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS dress_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL CHECK(gender IN ('men','women','unisex')),
            description TEXT,
            image_url TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS design_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            description TEXT,
            image_url TEXT,
            featured INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES dress_categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS price_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            stitch_type TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES dress_categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS customer_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            age TEXT,
            address TEXT,
            dress_type TEXT NOT NULL,
            measurements TEXT,
            booking_date TEXT,
            delivery_date TEXT,
            remarks TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT UNIQUE NOT NULL,
            order_id INTEGER,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            age TEXT,
            address TEXT,
            dress_type TEXT NOT NULL,
            measurements TEXT,
            booking_date TEXT,
            delivery_date TEXT,
            advance_amount REAL DEFAULT 0,
            final_amount REAL NOT NULL,
            balance_amount REAL DEFAULT 0,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES customer_orders(id)
        );
    ''')
    db.commit()

    # Seed admin user
    existing = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not existing:
        db.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                   ('admin', hash_password('admin@slv2024'), 'admin'))
        db.commit()

    # Seed categories
    existing_cats = db.execute("SELECT COUNT(*) FROM dress_categories").fetchone()[0]
    if existing_cats == 0:
        seed_cats = [
            ('Shirt', 'men', 'Classic and casual shirts'),
            ('Pant', 'men', 'Formal and casual pants'),
            ('Suit', 'men', 'Complete suits and blazers'),
            ('Kurtha', 'men', 'Traditional kurtha styles'),
            ('Saree Blouse', 'women', 'All blouse designs'),
            ('Churidar', 'women', 'Churidar and salwar suits'),
            ('Lehenga', 'women', 'Lehenga and skirt designs'),
            ('Kurtha Neck Designs', 'women', 'Neck design gallery for kurthas'),
            ('Frock', 'women', 'Kids and ladies frocks'),
            ('Pyjama Set', 'unisex', 'Comfortable night wear'),
        ]
        for cat in seed_cats:
            db.execute("INSERT INTO dress_categories (name, gender, description, active) VALUES (?,?,?,1)", cat)

        # Seed prices
        db.commit()
        cats_db = db.execute("SELECT id, name FROM dress_categories").fetchall()
        price_map = {
            'Shirt': [('Regular Fit', 350), ('Slim Fit', 400), ('Designer', 500)],
            'Pant': [('Regular', 400), ('Formal', 500), ('Jeans Style', 550)],
            'Suit': [('2-Piece', 1200), ('3-Piece', 1500)],
            'Kurtha': [('Simple', 300), ('Designer', 450)],
            'Saree Blouse': [('Plain', 200), ('Designer', 350), ('Embroidery', 500)],
            'Churidar': [('Simple', 400), ('Designer', 600)],
            'Lehenga': [('Simple', 700), ('Designer', 1200)],
            'Frock': [('Kids', 250), ('Ladies', 400)],
            'Pyjama Set': [('Simple', 300)],
        }
        for cat in cats_db:
            if cat['name'] in price_map:
                for stype, price in price_map[cat['name']]:
                    db.execute("INSERT INTO price_list (category_id, stitch_type, price) VALUES (?,?,?)",
                               (cat['id'], stype, price))
        db.commit()

    db.close()
