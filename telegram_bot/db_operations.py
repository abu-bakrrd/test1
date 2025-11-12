import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()


def get_db_connection():
    """Creates database connection"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        if 'sslmode=' not in database_url:
            database_url = database_url + ('&' if '?' in database_url else '?') + 'sslmode=require'
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        conn = psycopg2.connect(
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT', '5432'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            database=os.getenv('PGDATABASE'),
            sslmode='require',
            cursor_factory=RealDictCursor
        )
    return conn


def get_categories_from_config():
    """
    Gets categories from settingsbot.json file
    
    Returns:
        list: Array of category dictionaries or empty array if error
    """
    try:
        config_path = Path(__file__).parent / 'settingsbot.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('categories', [])
    except FileNotFoundError:
        print("⚠️ Файл settingsbot.json не найден.")
        return []
    except Exception as e:
        print(f"❌ Ошибка загрузки категорий: {e}")
        return []


def add_product(name, description, price, images, category_id=None):
    """
    Adds new product to database
    
    Parameters:
        name (str): Product name
        description (str): Product description
        price (int): Product price in cents
        images (list): Array of image URLs
        category_id (str, optional): Category ID (must match category ID from config)
    
    Returns:
        dict: Dictionary with created product data or None if error
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO products (name, description, price, images, category_id) VALUES (%s, %s, %s, %s, %s) RETURNING *',
            (name, description, price, images, category_id)
        )
        product = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return product
    except Exception as e:
        print(f"Error adding product: {e}")
        return None


def delete_product(product_id):
    """
    Deletes product from database
    
    Parameters:
        product_id (str): Product ID to delete
    
    Returns:
        bool: True if product deleted, False if error
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM products WHERE id = %s', (product_id,))
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return deleted_count > 0
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False


def get_all_products(category_id=None):
    """
    Gets all products from database (with optional category filter)
    
    Parameters:
        category_id (str, optional): Category ID for filtering
    
    Returns:
        list: Array of product dictionaries or empty array if error
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if category_id:
            cur.execute('SELECT * FROM products WHERE category_id = %s', (category_id,))
        else:
            cur.execute('SELECT * FROM products')
        
        products = cur.fetchall()
        cur.close()
        conn.close()
        return products
    except Exception as e:
        print(f"Error getting products: {e}")
        return []


def get_product_by_id(product_id):
    """
    Gets product by ID
    
    Parameters:
        product_id (str): Product ID
    
    Returns:
        dict: Dictionary with product data or None if not found
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
        product = cur.fetchone()
        cur.close()
        conn.close()
        return product
    except Exception as e:
        print(f"Error getting product: {e}")
        return None


def find_products_by_name(name):
    """
    Searches products by name (partial match)
    
    Parameters:
        name (str): Product name or part of name
    
    Returns:
        list: Array of product dictionaries or empty array
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products WHERE name ILIKE %s', (f'%{name}%',))
        products = cur.fetchall()
        cur.close()
        conn.close()
        return products
    except Exception as e:
        print(f"Error searching products: {e}")
        return []
