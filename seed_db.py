import psycopg2
from psycopg2.extras import RealDictCursor
import os

def seed_database():
    # Debug: print all environment variables starting with PG or DATABASE
    print(f"=== Environment Variables ===")
    for key in sorted(os.environ.keys()):
        if key.startswith('PG') or key.startswith('DATABASE') or key.startswith('REPL'):
            print(f"{key} = {os.environ[key][:50] if len(os.environ[key]) > 50 else os.environ[key]}")
    print(f"=== End Environment Variables ===")
    
    # Use DATABASE_URL if available, otherwise build from individual vars
    database_url = os.getenv('DATABASE_URL')
    
    print(f"Connecting to database...")
    print(f"DATABASE_URL exists: {'Yes' if database_url else 'No'}")
    
    if database_url:
        # Add sslmode=require for Neon database
        if 'sslmode=' not in database_url:
            database_url = database_url + ('&' if '?' in database_url else '?') + 'sslmode=require'
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
        # Build connection from individual PostgreSQL environment variables
        pghost = os.getenv('PGHOST')
        print(f"PGHOST: {pghost if pghost else 'Not set'}")
        
        conn = psycopg2.connect(
            host=pghost,
            port=os.getenv('PGPORT', '5432'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            database=os.getenv('PGDATABASE'),
            sslmode='require',
            cursor_factory=RealDictCursor
        )
    cur = conn.cursor()
    
    # Create tables if they don't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            icon TEXT NOT NULL
        )
    ''')
    
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
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            telegram_id BIGINT UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            password TEXT
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
            product_id VARCHAR REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(user_id, product_id)
        )
    ''')
    
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
    
    # Check if categories exist
    cur.execute('SELECT COUNT(*) as count FROM categories')
    result = cur.fetchone()
    
    category_ids = {}
    if result and result['count'] == 0:
        print("Добавление категорий...")
        categories = [
            ('Розы', '🌹'),
            ('Тюльпаны', '🌷'),
            ('Пионы', '🏵️'),
            ('Букеты', '💐'),
        ]
        
        for name, icon in categories:
            cur.execute(
                'INSERT INTO categories (name, icon) VALUES (%s, %s) RETURNING id',
                (name, icon)
            )
            result = cur.fetchone()
            if result:
                category_ids[name] = result['id']
        
        conn.commit()
        print(f"Добавлено {len(categories)} категорий")
    else:
        print("Категории уже существуют, загружаем их...")
        # Load existing category IDs
        cur.execute('SELECT id, name FROM categories')
        categories = cur.fetchall()
        for cat in categories:
            category_ids[cat['name']] = cat['id']
        print(f"Загружено {len(category_ids)} категорий")
    
    # Check if products exist
    cur.execute('SELECT COUNT(*) as count FROM products')
    product_count = cur.fetchone()
    
    if product_count and product_count['count'] == 0:
        print("Добавление товаров...")
        products = [
            # Розы
            {
                'name': 'Красные розы "Классика"',
                'description': 'Букет из 15 красных роз высшего качества',
                'price': 2500,
                'images': ['https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800', 'https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=800'],
                'category': 'Розы'
            },
            {
                'name': 'Белые розы "Нежность"',
                'description': 'Букет из 11 белых роз',
                'price': 2200,
                'images': ['https://images.unsplash.com/photo-1496062031456-07b8f162a322?w=800'],
                'category': 'Розы'
            },
            {
                'name': 'Розовые розы "Романтика"',
                'description': 'Букет из 21 розовой розы',
                'price': 3500,
                'images': ['https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=800'],
                'category': 'Розы'
            },
            # Тюльпаны
            {
                'name': 'Тюльпаны "Весна"',
                'description': 'Яркий букет из 25 разноцветных тюльпанов',
                'price': 1800,
                'images': ['https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=800'],
                'category': 'Тюльпаны'
            },
            {
                'name': 'Красные тюльпаны',
                'description': 'Букет из 15 красных тюльпанов',
                'price': 1500,
                'images': ['https://images.unsplash.com/photo-1520763185298-1b434c919102?w=800'],
                'category': 'Тюльпаны'
            },
            # Пионы
            {
                'name': 'Пионы "Роскошь"',
                'description': 'Букет из 7 крупных пионов',
                'price': 3200,
                'images': ['https://images.unsplash.com/photo-1591886960571-74d43a9d4166?w=800'],
                'category': 'Пионы'
            },
            {
                'name': 'Белые пионы',
                'description': 'Букет из 5 белых пионов',
                'price': 2800,
                'images': ['https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?w=800'],
                'category': 'Пионы'
            },
            # Букеты
            {
                'name': 'Букет "Летний день"',
                'description': 'Яркий микс полевых цветов',
                'price': 2000,
                'images': ['https://images.unsplash.com/photo-1487070183336-b863922373d4?w=800'],
                'category': 'Букеты'
            },
            {
                'name': 'Букет "Нежность"',
                'description': 'Романтичный букет в пастельных тонах',
                'price': 2700,
                'images': ['https://images.unsplash.com/photo-1535288262947-259331d73d4f?w=800'],
                'category': 'Букеты'
            },
            {
                'name': 'Букет "Премиум"',
                'description': 'Роскошная композиция из роз и пионов',
                'price': 4500,
                'images': ['https://images.unsplash.com/photo-1561181286-d3fee7d55364?w=800'],
                'category': 'Букеты'
            },
        ]
        
        for product in products:
            category_id = category_ids.get(product['category'])
            if category_id:
                cur.execute(
                    'INSERT INTO products (name, description, price, images, category_id) VALUES (%s, %s, %s, %s, %s)',
                    (product['name'], product['description'], product['price'], product['images'], category_id)
                )
        
        conn.commit()
        print(f"Добавлено {len(products)} товаров")
    else:
        print(f"Товары уже существуют ({product_count['count']} шт.)")
    
    cur.close()
    conn.close()
    print("Готово!")

if __name__ == '__main__':
    seed_database()
