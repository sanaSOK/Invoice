from db import init_db, add_product, get_products
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'bank_db.db')


def seed():
    init_db(DB_PATH)
    existing = get_products(DB_PATH)
    if existing:
        print('DB already has products, skipping seed')
        return
    samples = [
        ('Apple', 0.50),
        ('Banana', 0.30),
        ('Orange Juice 1L', 2.50),
        ('Notebook A5', 1.20),
        ('Pen Blue', 0.20),
    ]
    for name, price in samples:
        add_product(DB_PATH, name, price)
    print('Seeded sample products')


if __name__ == '__main__':
    seed()
