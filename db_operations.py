import psycopg2
from psycopg2.extras import RealDictCursor
import os


def get_db_connection():
    """Создает подключение к базе данных"""
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


def add_product(name, description, price, images, category_id=None):
    """
    Добавляет новый товар в базу данных
    
    Параметры:
        name (str): Название товара
        description (str): Описание товара
        price (int): Цена товара в копейках
        images (list): Массив URL изображений
        category_id (str, optional): ID категории
    
    Возвращает:
        dict: Словарь с данными созданного товара или None в случае ошибки
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
        print(f"Ошибка при добавлении товара: {e}")
        return None


def delete_product(product_id):
    """
    Удаляет товар из базы данных
    
    Параметры:
        product_id (str): ID товара для удаления
    
    Возвращает:
        bool: True если товар удален, False в случае ошибки
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
        print(f"Ошибка при удалении товара: {e}")
        return False


def add_category(name, icon):
    """
    Добавляет новую категорию в базу данных
    
    Параметры:
        name (str): Название категории
        icon (str): Иконка категории (эмодзи или текст)
    
    Возвращает:
        dict: Словарь с данными созданной категории или None в случае ошибки
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO categories (name, icon) VALUES (%s, %s) RETURNING *',
            (name, icon)
        )
        category = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return category
    except Exception as e:
        print(f"Ошибка при добавлении категории: {e}")
        return None


def delete_category(category_id):
    """
    Удаляет категорию из базы данных
    
    Параметры:
        category_id (str): ID категории для удаления
    
    Возвращает:
        bool: True если категория удалена, False в случае ошибки
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM categories WHERE id = %s', (category_id,))
        deleted_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return deleted_count > 0
    except Exception as e:
        print(f"Ошибка при удалении категории: {e}")
        return False


def get_all_products(category_id=None):
    """
    Получает все товары из базы данных (с возможностью фильтрации по категории)
    
    Параметры:
        category_id (str, optional): ID категории для фильтрации
    
    Возвращает:
        list: Массив словарей с данными товаров или пустой массив в случае ошибки
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
        print(f"Ошибка при получении товаров: {e}")
        return []


def get_all_categories():
    """
    Получает все категории из базы данных
    
    Возвращает:
        list: Массив словарей с данными категорий или пустой массив в случае ошибки
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM categories')
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return categories
    except Exception as e:
        print(f"Ошибка при получении категорий: {e}")
        return []


def get_product_by_id(product_id):
    """
    Получает товар по ID
    
    Параметры:
        product_id (str): ID товара
    
    Возвращает:
        dict: Словарь с данными товара или None если не найден
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
        print(f"Ошибка при получении товара: {e}")
        return None


def get_category_by_id(category_id):
    """
    Получает категорию по ID
    
    Параметры:
        category_id (str): ID категории
    
    Возвращает:
        dict: Словарь с данными категории или None если не найдена
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM categories WHERE id = %s', (category_id,))
        category = cur.fetchone()
        cur.close()
        conn.close()
        return category
    except Exception as e:
        print(f"Ошибка при получении категории: {e}")
        return None


def find_products_by_name(name):
    """
    Ищет товары по названию (частичное совпадение)
    
    Параметры:
        name (str): Название или часть названия товара
    
    Возвращает:
        list: Массив словарей с данными товаров или пустой массив
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
        print(f"Ошибка при поиске товаров: {e}")
        return []


# Пример использования функций
if __name__ == "__main__":
    print("=== Пример работы с базой данных ===\n")
    
    # 1. Получаем все категории
    print("1. Все категории:")
    categories = get_all_categories()
    for cat in categories:
        print(f"   ID: {cat['id']}, Название: {cat['name']}, Иконка: {cat['icon']}")
    print()
    
    # 2. Получаем все товары
    print("2. Все товары:")
    products = get_all_products()
    for prod in products[:3]:  # Показываем первые 3
        print(f"   ID: {prod['id']}, Название: {prod['name']}, Цена: {prod['price']}")
    print(f"   ... всего {len(products)} товаров\n")
    
    # 3. Поиск товаров по названию
    print("3. Поиск товаров с 'роз' в названии:")
    found = find_products_by_name("роз")
    for prod in found:
        print(f"   ID: {prod['id']}, Название: {prod['name']}")
    print()
    
    # 4. Добавление новой категории
    print("4. Добавление новой категории:")
    new_category = add_category("Орхидеи", "🌸")
    if new_category:
        print(f"   ✓ Категория добавлена: {new_category['name']} (ID: {new_category['id']})\n")
        
        # 5. Добавление товара в эту категорию
        print("5. Добавление товара:")
        new_product = add_product(
            name="Белая орхидея",
            description="Элегантная белая орхидея в горшке",
            price=250000,
            images=["https://example.com/orchid1.jpg", "https://example.com/orchid2.jpg"],
            category_id=new_category['id']
        )
        if new_product:
            print(f"   ✓ Товар добавлен: {new_product['name']} (ID: {new_product['id']})\n")
            
            # 6. Получение товара по ID
            print("6. Получение товара по ID:")
            product = get_product_by_id(new_product['id'])
            if product:
                print(f"   Найден: {product['name']}, цена: {product['price']}\n")
            
            # 7. Удаление товара (теперь знаем ID!)
            print("7. Удаление товара:")
            if delete_product(new_product['id']):
                print(f"   ✓ Товар удален (ID: {new_product['id']})\n")
        
        # 8. Удаление категории (теперь знаем ID!)
        print("8. Удаление категории:")
        if delete_category(new_category['id']):
            print(f"   ✓ Категория удалена (ID: {new_category['id']})")
