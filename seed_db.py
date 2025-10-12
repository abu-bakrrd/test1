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
    
    if result and result['count'] == 0:
        print("Добавление категорий...")
        categories = [
            ('Розы', '🌹'),
            ('Тюльпаны', '🌷'),
            ('Пионы', '🏵️'),
            ('Букеты', '💐'),
        ]
        
        category_ids = {}
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
        
        # Check if products exist
        cur.execute('SELECT COUNT(*) as count FROM products')
        result = cur.fetchone()
        
        if result and result['count'] == 0:
            print("Добавление товаров...")
            products = [
                {
                    'name': 'Букет красных роз',
                    'description': 'Изысканный букет из свежих красных роз премиум класса. Идеально подходит для выражения любви и признательности. В букете 15 крупных бутонов.',
                    'price': 150000,
                    'images': [
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1464618663641-bbdd760ae84a?w=400&h=400&fit=crop'
                    ],
                    'category': 'Розы'
                },
                {
                    'name': 'Розовые тюльпаны',
                    'description': 'Нежные розовые тюльпаны из Голландии. Символ весны и новых начинаний. Букет из 25 свежих цветов.',
                    'price': 90000,
                    'images': [
                        'https://images.unsplash.com/photo-1520763185298-1b434c919102?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1561181286-d3fee7d55364?w=400&h=400&fit=crop'
                    ],
                    'category': 'Тюльпаны'
                },
                {
                    'name': 'Белые пионы',
                    'description': 'Роскошные белые пионы с нежным ароматом. Идеальны для свадеб и торжественных мероприятий. Букет из 11 пионов.',
                    'price': 120000,
                    'images': [
                        'https://images.unsplash.com/photo-1591886960571-74d43a9d4166?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1588509095738-c342c5d917d2?w=400&h=400&fit=crop'
                    ],
                    'category': 'Пионы'
                },
                {
                    'name': 'Букет полевых цветов',
                    'description': 'Яркий букет из полевых цветов. Создает атмосферу лета и свободы. Микс из различных сезонных цветов.',
                    'price': 75000,
                    'images': [
                        'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1487070183336-b863922373d4?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                },
                {
                    'name': 'Фиолетовые лаванды',
                    'description': 'Ароматная лаванда с юга Франции. Успокаивающий аромат и нежная красота. Букет из 50 веточек.',
                    'price': 85000,
                    'images': [
                        'https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1611251180451-d0be0a74d3fc?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1595261740315-67e6bf46ecad?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                },
                {
                    'name': 'Желтые герберы',
                    'description': 'Солнечные герберы, поднимающие настроение. Яркие и жизнерадостные цветы. Букет из 15 крупных гербер.',
                    'price': 95000,
                    'images': [
                        'https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1597848212624-e30b9aeb6394?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                },
                {
                    'name': 'Розовые пионы',
                    'description': 'Очаровательные розовые пионы с пышными бутонами. Символ романтики и женственности. Букет из 9 пионов.',
                    'price': 130000,
                    'images': [
                        'https://images.unsplash.com/photo-1588509095738-c342c5d917d2?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1591886960571-74d43a9d4166?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?w=400&h=400&fit=crop'
                    ],
                    'category': 'Пионы'
                },
                {
                    'name': 'Подсолнухи',
                    'description': 'Яркие подсолнухи, символ счастья и оптимизма. Поднимают настроение в любую погоду. Букет из 7 больших подсолнухов.',
                    'price': 70000,
                    'images': [
                        'https://images.unsplash.com/photo-1597848212624-e30b9aeb6394?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                },
                {
                    'name': 'Белые розы',
                    'description': 'Элегантные белые розы, символ чистоты и невинности. Классический выбор для особых случаев. Букет из 21 розы.',
                    'price': 140000,
                    'images': [
                        'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1464618663641-bbdd760ae84a?w=400&h=400&fit=crop'
                    ],
                    'category': 'Розы'
                },
                {
                    'name': 'Сиреневые хризантемы',
                    'description': 'Изящные хризантемы сиреневого оттенка. Долго сохраняют свежесть. Букет из 15 веточек.',
                    'price': 100000,
                    'images': [
                        'https://images.unsplash.com/photo-1563535655-c6d52fdf3a89?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                },
                {
                    'name': 'Смешанный букет',
                    'description': 'Оригинальный микс из различных сезонных цветов. Каждый букет уникален. Яркое сочетание форм и оттенков.',
                    'price': 110000,
                    'images': [
                        'https://images.unsplash.com/photo-1487070183336-b863922373d4?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1563241527-3004b7be0ffd?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                },
                {
                    'name': 'Орхидеи',
                    'description': 'Экзотические орхидеи премиум класса. Символ роскоши и утонченности. Композиция из 5 веток орхидей.',
                    'price': 160000,
                    'images': [
                        'https://images.unsplash.com/photo-1584714268709-c3dd9c92b378?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1563535655-c6d52fdf3a89?w=400&h=400&fit=crop',
                        'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=400&fit=crop'
                    ],
                    'category': 'Букеты'
                }
            ]
            
            for product in products:
                category_id = category_ids.get(product['category'])
                cur.execute(
                    'INSERT INTO products (name, description, price, images, category_id) VALUES (%s, %s, %s, %s, %s)',
                    (product['name'], product.get('description'), product['price'], product['images'], category_id)
                )
            
            conn.commit()
            print(f"Добавлено {len(products)} товаров")
    else:
        print("База данных уже содержит данные")
    
    cur.close()
    conn.close()
    print("Готово!")

if __name__ == '__main__':
    seed_database()
