import sqlite3
import os
from datetime import datetime


def init_db(bank_db):
    created = not os.path.exists(bank_db)
    conn = sqlite3.connect(bank_db)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        date TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        product_id INTEGER,
        name TEXT,
        price REAL,
        qty INTEGER
    )
    ''')
    conn.commit()
    conn.close()
    return created


def add_product(bank_db, name, price):
    conn = sqlite3.connect(bank_db)
    c = conn.cursor()
    c.execute('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
    conn.commit()
    conn.close()


def update_product(bank_db, product_id, name, price):
    conn = sqlite3.connect(bank_db)
    c = conn.cursor()
    c.execute('UPDATE products SET name = ?, price = ? WHERE id = ?', (name, price, product_id))
    conn.commit()
    conn.close()


def get_product(bank_db, product_id):
    conn = sqlite3.connect(bank_db)
    c = conn.cursor()
    c.execute('SELECT id, name, price FROM products WHERE id = ?', (product_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_products(bank_db):
    conn = sqlite3.connect(bank_db)
    c = conn.cursor()
    c.execute('SELECT id, name, price FROM products ORDER BY id')
    rows = c.fetchall()
    conn.close()
    return rows


def add_invoice(bank_db, customer, items):
    conn = sqlite3.connect(bank_db)
    c = conn.cursor()
    date = datetime.now().isoformat()
    c.execute('INSERT INTO invoices (customer, date) VALUES (?, ?)', (customer, date))
    invoice_id = c.lastrowid
    for it in items:
        c.execute('INSERT INTO invoice_items (invoice_id, product_id, name, price, qty) VALUES (?, ?, ?, ?, ?)',
                  (invoice_id, it.get('pid'), it.get('name'), it.get('price'), it.get('qty')))
    conn.commit()
    conn.close()
    return invoice_id
