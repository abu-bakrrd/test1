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
        print("Adding categories...")
        categories = [
            ('Category 1', '📦'),
            ('Category 2', '🏷️'),
            ('Category 3', '✨'),
            ('Category 4', '🎁'),
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
        print(f"Added {len(categories)} categories")
    else:
        print("Categories already exist, loading them...")
        # Load existing category IDs
        cur.execute('SELECT id, name FROM categories')
        categories = cur.fetchall()
        for cat in categories:
            category_ids[cat['name']] = cat['id']
        print(f"Loaded {len(category_ids)} categories")
    
    # Check if products exist
    cur.execute('SELECT COUNT(*) as count FROM products')
    product_count = cur.fetchone()
    
    if product_count and product_count['count'] == 0:
        print("Adding products...")
        products = [
            # Category 1
            {
                'name': 'Product Name 1',
                'description': 'Product description with details about the item',
                'price': 9999,
                'images': ['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800'],
                'category': 'Category 1'
            },
            {
                'name': 'Product Name 2',
                'description': 'Another product with a detailed description',
                'price': 14999,
                'images': ['https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800'],
                'category': 'Category 1'
            },
            {
                'name': 'Product Name 3',
                'description': 'Premium product with extended features',
                'price': 29999,
                'images': ['https://images.unsplash.com/photo-1560343090-f0409e92791a?w=800'],
                'category': 'Category 1'
            },
            # Category 2
            {
                'name': 'Product Name 4',
                'description': 'Quality product for everyday use',
                'price': 7999,
                'images': ['https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=800'],
                'category': 'Category 2'
            },
            {
                'name': 'Product Name 5',
                'description': 'Popular item with great reviews',
                'price': 12999,
                'images': ['https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800'],
                'category': 'Category 2'
            },
            # Category 3
            {
                'name': 'Product Name 6',
                'description': 'Exclusive limited edition product',
                'price': 39999,
                'images': ['https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800'],
                'category': 'Category 3'
            },
            {
                'name': 'Product Name 7',
                'description': 'Stylish design with modern features',
                'price': 19999,
                'images': ['https://images.unsplash.com/photo-1525328437458-0c4d4db7cab4?w=800'],
                'category': 'Category 3'
            },
            # Category 4
            {
                'name': 'Product Name 8',
                'description': 'Best value product in this category',
                'price': 8999,
                'images': ['https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800'],
                'category': 'Category 4'
            },
            {
                'name': 'Product Name 9',
                'description': 'Deluxe product with premium quality',
                'price': 24999,
                'images': ['https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800'],
                'category': 'Category 4'
            },
            {
                'name': 'Product Name 10',
                'description': 'Ultimate choice for demanding customers',
                'price': 49999,
                'images': ['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'],
                'category': 'Category 4'
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
        print(f"Added {len(products)} products")
    else:
        print(f"Products already exist ({product_count['count']} items)")
    
    cur.close()
    conn.close()
    print("Done!")

if __name__ == '__main__':
    seed_database()
