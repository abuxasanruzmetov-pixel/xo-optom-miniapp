import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "shop.db")

def get_db():
      conn = sqlite3.connect(DB_PATH)
      conn.row_factory = sqlite3.Row
      return conn

def init_db():
      conn = get_db()
      c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                            emoji TEXT DEFAULT '',
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                        )''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                            name TEXT NOT NULL,
                                    description TEXT DEFAULT '',
                                            price REAL NOT NULL,
                                                    old_price REAL DEFAULT 0,
                                                            stock INTEGER DEFAULT 0,
                                                                    image_url TEXT DEFAULT '',
                                                                            is_active INTEGER DEFAULT 1,
                                                                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                                            FOREIGN KEY (category_id) REFERENCES categories(id)
                                                                                                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE,
                            first_name TEXT,
                                    last_name TEXT,
                                            username TEXT,
                                                    phone TEXT,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                                                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                            total_price REAL,
                                    status TEXT DEFAULT 'new',
                                            address TEXT DEFAULT '',
                                                    phone TEXT DEFAULT '',
                                                            promo_code TEXT DEFAULT '',
                                                                    discount REAL DEFAULT 0,
                                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                                                    FOREIGN KEY (user_id) REFERENCES users(id)
                                                                                        )''')

    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                            product_id INTEGER,
                                    quantity INTEGER DEFAULT 1,
                                            price REAL,
                                                    FOREIGN KEY (order_id) REFERENCES orders(id),
                                                            FOREIGN KEY (product_id) REFERENCES products(id)
                                                                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                            product_id INTEGER,
                                    quantity INTEGER DEFAULT 1,
                                            FOREIGN KEY (user_id) REFERENCES users(id),
                                                    FOREIGN KEY (product_id) REFERENCES products(id)
                                                        )''')

    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                            product_id INTEGER,
                                    FOREIGN KEY (user_id) REFERENCES users(id),
                                            FOREIGN KEY (product_id) REFERENCES products(id)
                                                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE,
                            discount_percent REAL DEFAULT 0,
                                    is_active INTEGER DEFAULT 1,
                                            usage_limit INTEGER DEFAULT 100,
                                                    used_count INTEGER DEFAULT 0
                                                        )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
      init_db()
      print("Database initialized!")
  
