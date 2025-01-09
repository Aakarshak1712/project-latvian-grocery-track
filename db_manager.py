import sqlite3
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='grocery_guru.db'):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Products table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        store TEXT NOT NULL,
                        price REAL NOT NULL,
                        url TEXT,
                        last_updated TIMESTAMP
                    )
                ''')
                
                # Shopping lists table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS shopping_lists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP
                    )
                ''')
                
                # Shopping list items table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS shopping_list_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        list_id INTEGER,
                        product_id INTEGER,
                        quantity INTEGER DEFAULT 1,
                        FOREIGN KEY (list_id) REFERENCES shopping_lists (id),
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # Price history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        price REAL NOT NULL,
                        recorded_at TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logging.error(f"Error setting up database: {str(e)}")
            
    def add_product(self, name: str, store: str, price: float, url: str = None):
        """Add or update a product in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if product exists
                cursor.execute('''
                    SELECT id, price FROM products 
                    WHERE name = ? AND store = ?
                ''', (name, store))
                
                result = cursor.fetchone()
                current_time = datetime.now().isoformat()
                
                if result:
                    product_id, old_price = result
                    # Update existing product
                    cursor.execute('''
                        UPDATE products 
                        SET price = ?, last_updated = ? 
                        WHERE id = ?
                    ''', (price, current_time, product_id))
                    
                    # Add to price history if price changed
                    if old_price != price:
                        cursor.execute('''
                            INSERT INTO price_history (product_id, price, recorded_at)
                            VALUES (?, ?, ?)
                        ''', (product_id, price, current_time))
                else:
                    # Insert new product
                    cursor.execute('''
                        INSERT INTO products (name, store, price, url, last_updated)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, store, price, url, current_time))
                    
                    product_id = cursor.lastrowid
                    # Add first price history entry
                    cursor.execute('''
                        INSERT INTO price_history (product_id, price, recorded_at)
                        VALUES (?, ?, ?)
                    ''', (product_id, price, current_time))
                
                conn.commit()
                return product_id
        except Exception as e:
            logging.error(f"Error adding/updating product: {str(e)}")
            return None
            
    def get_product_price_history(self, product_id: int) -> list:
        """Get price history for a specific product"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT price, recorded_at 
                    FROM price_history 
                    WHERE product_id = ?
                    ORDER BY recorded_at DESC
                ''', (product_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error getting price history: {str(e)}")
            return []
            
    def create_shopping_list(self, name: str) -> int:
        """Create a new shopping list"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO shopping_lists (name, created_at)
                    VALUES (?, ?)
                ''', (name, datetime.now().isoformat()))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error creating shopping list: {str(e)}")
            return None
            
    def add_item_to_list(self, list_id: int, product_id: int, quantity: int = 1):
        """Add an item to a shopping list"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO shopping_list_items (list_id, product_id, quantity)
                    VALUES (?, ?, ?)
                ''', (list_id, product_id, quantity))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding item to shopping list: {str(e)}")
            return False
            
    def get_all_products(self) -> list:
        """Get all products from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT name, store 
                    FROM products 
                    ORDER BY name, store
                ''')
                results = cursor.fetchall()
                return [{'name': name, 'store': store} for name, store in results]
        except Exception as e:
            logging.error(f"Error getting all products: {str(e)}")
            return []
            
    def get_product_price_history_by_name(self, name: str, store: str) -> list:
        """Get price history for a product by name and store"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ph.price, ph.recorded_at
                    FROM price_history ph
                    JOIN products p ON ph.product_id = p.id
                    WHERE p.name = ? AND p.store = ?
                    ORDER BY ph.recorded_at DESC
                ''', (name, store))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error getting price history by name: {str(e)}")
            return []
            
    def get_shopping_list_items(self, list_id: int) -> list:
        """Get all items in a shopping list with their details"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.name, sli.quantity, p.store, p.price
                    FROM shopping_list_items sli
                    JOIN products p ON sli.product_id = p.id
                    WHERE sli.list_id = ?
                ''', (list_id,))
                
                results = cursor.fetchall()
                return [
                    {
                        'name': name,
                        'quantity': quantity,
                        'store': store,
                        'price': price
                    }
                    for name, quantity, store, price in results
                ]
        except Exception as e:
            logging.error(f"Error getting shopping list items: {str(e)}")
            return []
            
    def get_lowest_price(self, product_name: str) -> float:
        """Get the lowest current price for a product across all stores"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT MIN(price)
                    FROM products
                    WHERE name = ?
                ''', (product_name,))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] is not None else None
        except Exception as e:
            logging.error(f"Error getting lowest price: {str(e)}")
            return None
            
    def get_price_alerts(self, max_price_dict: dict) -> list:
        """Get products that are now below their alert price"""
        try:
            alerts = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for product_name, max_price in max_price_dict.items():
                    cursor.execute('''
                        SELECT name, store, price
                        FROM products
                        WHERE name = ? AND price <= ?
                    ''', (product_name, max_price))
                    
                    results = cursor.fetchall()
                    for name, store, price in results:
                        alerts.append({
                            'name': name,
                            'store': store,
                            'price': price,
                            'max_price': max_price
                        })
                        
            return alerts
        except Exception as e:
            logging.error(f"Error checking price alerts: {str(e)}")
            return []
