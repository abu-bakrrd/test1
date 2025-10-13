from flask import Flask, jsonify, request, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import requests
from datetime import datetime

app = Flask(__name__, static_folder='dist/public', static_url_path='')


# Database connection
def get_db_connection():
    # Use DATABASE_URL if available, otherwise build from individual vars
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Add sslmode=require for Neon database
        if 'sslmode=' not in database_url:
            database_url = database_url + ('&' if '?' in database_url else '?') + 'sslmode=require'
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        # Build connection from individual PostgreSQL environment variables
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

# Initialize database tables
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create categories table if not exists
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            icon TEXT NOT NULL
        )
    ''')
    
    # Create products table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            images TEXT[] NOT NULL,
            category_id VARCHAR REFERENCES categories(id)
        )
    ''')
    
    # Create users table if not exists
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            username TEXT,
            password TEXT,
            telegram_id BIGINT UNIQUE,
            first_name TEXT,
            last_name TEXT
        )
    ''')
    
    # Create favorites table (many-to-many: users <-> products)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
            product_id VARCHAR REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(user_id, product_id)
        )
    ''')
    
    # Create cart table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
            product_id VARCHAR REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, product_id)
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

# API Routes

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM categories')
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def create_category():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO categories (name, icon) VALUES (%s, %s) RETURNING *',
            (data['name'], data['icon'])
        )
        category = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(category), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        category_id = request.args.get('category_id')
        conn = get_db_connection()
        cur = conn.cursor()
        
        if category_id:
            cur.execute('SELECT * FROM products WHERE category_id = %s', (category_id,))
        else:
            cur.execute('SELECT * FROM products')
        
        products = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO products (name, description, price, images, category_id) VALUES (%s, %s, %s, %s, %s) RETURNING *',
            (data['name'], data.get('description'), data['price'], data['images'], data.get('category_id'))
        )
        product = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(product), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
        product = cur.fetchone()
        cur.close()
        conn.close()
        
        if product:
            return jsonify(product)
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites/<user_id>', methods=['GET'])
def get_favorites(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT p.* FROM products p
            JOIN favorites f ON p.id = f.product_id
            WHERE f.user_id = %s
        ''', (user_id,))
        favorites = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(favorites)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
def add_to_favorites():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO favorites (user_id, product_id) VALUES (%s, %s) ON CONFLICT (user_id, product_id) DO NOTHING RETURNING *',
            (data['user_id'], data['product_id'])
        )
        favorite = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(favorite), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/favorites/<user_id>/<product_id>', methods=['DELETE'])
def remove_from_favorites(user_id, product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'DELETE FROM favorites WHERE user_id = %s AND product_id = %s',
            (user_id, product_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Removed from favorites'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Telegram Auth
@app.route('/auth/telegram', methods=['POST'])
def telegram_auth():
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        username = data.get('username', '')
        
        if not telegram_id:
            return jsonify({'error': 'telegram_id is required'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
        user = cur.fetchone()
        
        if user:
            # User exists, return user data
            cur.close()
            conn.close()
            return jsonify({'user': user, 'is_new': False})
        else:
            # Create new user
            cur.execute(
                'INSERT INTO users (telegram_id, username, first_name, last_name) VALUES (%s, %s, %s, %s) RETURNING *',
                (telegram_id, username, first_name, last_name)
            )
            new_user = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'user': new_user, 'is_new': True}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cart endpoints
@app.route('/api/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT p.*, c.quantity FROM products p
            JOIN cart c ON p.id = c.product_id
            WHERE c.user_id = %s
        ''', (user_id,))
        cart_items = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(cart_items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO cart (user_id, product_id, quantity) 
               VALUES (%s, %s, %s) 
               ON CONFLICT (user_id, product_id) 
               DO UPDATE SET quantity = cart.quantity + EXCLUDED.quantity
               RETURNING *''',
            (data['user_id'], data['product_id'], data.get('quantity', 1))
        )
        cart_item = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(cart_item), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart', methods=['PUT'])
def update_cart_quantity():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s RETURNING *',
            (data['quantity'], data['user_id'], data['product_id'])
        )
        cart_item = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if cart_item:
            return jsonify(cart_item)
        return jsonify({'error': 'Cart item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/<user_id>/<product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'DELETE FROM cart WHERE user_id = %s AND product_id = %s',
            (user_id, product_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Removed from cart'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/<user_id>', methods=['DELETE'])
def clear_cart(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Cart cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Telegram notification function
def send_telegram_notification(user_info, cart_items, total):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Telegram credentials not configured")
        return False
    
    # Format the order message
    user_name = user_info.get('first_name', '') + ' ' + user_info.get('last_name', '')
    user_name = user_name.strip() or user_info.get('username', 'Неизвестный')
    telegram_id = user_info.get('telegram_id', 'N/A')
    
    message = f"🛍 *Новый заказ!*\n\n"
    message += f"👤 *Клиент:* {user_name}\n"
    message += f"🆔 *Telegram ID:* {telegram_id}\n"
    message += f"📅 *Дата:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    message += f"📦 *Товары:*\n"
    
    for item in cart_items:
        message += f"• {item['name']} — {item['quantity']} шт. — {item['price']:,} сум\n"
    
    message += f"\n💰 *Итого:* {total:,} сум"
    
    # Send message via Telegram Bot API
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")
        return False

# Order endpoint
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        user_id = data.get('user_id')
        cart_items = data.get('items', [])
        total = data.get('total', 0)
        
        # Get user info
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user_info = cur.fetchone()
        
        # Send Telegram notification
        if user_info:
            send_telegram_notification(user_info, cart_items, total)
        
        # Clear the cart after order
        cur.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Order created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve React App - this must be the last route
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # If path is a file and exists in static folder, serve it
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Otherwise, serve index.html for SPA routing
    return send_from_directory(app.static_folder, 'index.html')

# Initialize database tables on startup
try:
    init_db()
    print("Database tables initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize database tables: {e}")

# Production: Gunicorn will use the 'app' object directly
# For local development, you can still run: python app.py
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
