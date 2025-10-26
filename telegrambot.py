"""
Telegram бот для управления товарами в магазине
Использует pyTelegramBotAPI и ООП структуру
"""

import os
import json
import telebot
from telebot import types
from db_operations import (
    add_product, 
    delete_product, 
    get_all_products,
    get_product_by_id,
    get_categories_from_config,
    find_products_by_name
)


class ProductBot:
    """Класс для управления Telegram ботом товаров"""
    
    def __init__(self, token):
        """
        Инициализация бота
        
        Args:
            token (str): Telegram Bot API токен
        """
        self.bot = telebot.TeleBot(token)
        self.authorized_users = self._load_authorized_users()
        self.user_states = {}  # Хранение состояний пользователей
        self.temp_data = {}    # Временные данные для создания товаров
        
        # Регистрация обработчиков
        self._register_handlers()
    
    def _load_authorized_users(self):
        """Загружает список авторизованных пользователей из settingsbot.json"""
        try:
            with open('settingsbot.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('authorized_users', []))
        except FileNotFoundError:
            print("⚠️ Файл settingsbot.json не найден. Создайте его с списком авторизованных пользователей.")
            return set()
        except Exception as e:
            print(f"❌ Ошибка загрузки авторизованных пользователей: {e}")
            return set()
    
    def _is_authorized(self, user_id):
        """
        Проверяет, авторизован ли пользователь
        
        Args:
            user_id (int): Telegram ID пользователя
            
        Returns:
            bool: True если авторизован
        """
        return user_id in self.authorized_users
    
    def _create_main_menu(self):
        """Создает главное меню с кнопками"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_add = types.KeyboardButton("➕ Добавить товар")
        btn_delete = types.KeyboardButton("🗑 Удалить товар")
        btn_list = types.KeyboardButton("📋 Список товаров")
        btn_categories = types.KeyboardButton("📁 Категории")
        markup.add(btn_add, btn_delete)
        markup.add(btn_list, btn_categories)
        return markup
    
    def _register_handlers(self):
        """Регистрирует все обработчики команд и сообщений"""
        
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            user_id = message.from_user.id
            
            if not self._is_authorized(user_id):
                self.bot.send_message(
                    message.chat.id,
                    "❌ У вас нет доступа к этому боту.\n"
                    f"Ваш ID: {user_id}\n\n"
                    "Попросите администратора добавить ваш ID в список авторизованных пользователей."
                )
                return
            
            username = message.from_user.username or message.from_user.first_name
            self.bot.send_message(
                message.chat.id,
                f"👋 Привет, {username}!\n\n"
                "🛍 Добро пожаловать в бот управления товарами.\n\n"
                "Выберите действие из меню:",
                reply_markup=self._create_main_menu()
            )
        
        @self.bot.message_handler(func=lambda message: message.text == "➕ Добавить товар")
        def handle_add_product(message):
            if not self._is_authorized(message.from_user.id):
                self.bot.send_message(message.chat.id, "❌ Доступ запрещен")
                return
            
            self.user_states[message.from_user.id] = "awaiting_product_name"
            self.temp_data[message.from_user.id] = {}
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("❌ Отмена"))
            
            self.bot.send_message(
                message.chat.id,
                "📝 Введите название товара:",
                reply_markup=markup
            )
        
        @self.bot.message_handler(func=lambda message: message.text == "🗑 Удалить товар")
        def handle_delete_product_menu(message):
            if not self._is_authorized(message.from_user.id):
                self.bot.send_message(message.chat.id, "❌ Доступ запрещен")
                return
            
            # Получаем все товары
            products = get_all_products()
            
            if not products:
                self.bot.send_message(
                    message.chat.id,
                    "📭 Товаров пока нет в базе данных.",
                    reply_markup=self._create_main_menu()
                )
                return
            
            # Создаем inline кнопки для каждого товара
            markup = types.InlineKeyboardMarkup(row_width=1)
            for product in products[:20]:  # Показываем первые 20
                btn_text = f"🗑 {product['name']} - {product['price']:,} сум"
                callback_data = f"delete_{product['id']}"
                markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
            
            self.bot.send_message(
                message.chat.id,
                "🗑 <b>Выберите товар для удаления:</b>\n\n"
                f"Всего товаров: {len(products)}",
                parse_mode='HTML',
                reply_markup=markup
            )
        
        @self.bot.message_handler(func=lambda message: message.text == "📋 Список товаров")
        def handle_list_products(message):
            if not self._is_authorized(message.from_user.id):
                self.bot.send_message(message.chat.id, "❌ Доступ запрещен")
                return
            
            products = get_all_products()
            
            if not products:
                self.bot.send_message(
                    message.chat.id,
                    "📭 Товаров пока нет в базе данных."
                )
                return
            
            response = f"📋 <b>Список товаров ({len(products)}):</b>\n\n"
            
            for idx, product in enumerate(products[:30], 1):  # Показываем первые 30
                response += f"{idx}. <b>{product['name']}</b>\n"
                response += f"   💰 Цена: {product['price']:,} сум\n"
                response += f"   🆔 ID: <code>{product['id']}</code>\n\n"
            
            if len(products) > 30:
                response += f"\n... и еще {len(products) - 30} товаров"
            
            self.bot.send_message(
                message.chat.id,
                response,
                parse_mode='HTML'
            )
        
        @self.bot.message_handler(func=lambda message: message.text == "📁 Категории")
        def handle_categories(message):
            if not self._is_authorized(message.from_user.id):
                self.bot.send_message(message.chat.id, "❌ Доступ запрещен")
                return
            
            categories = get_categories_from_config()
            
            if not categories:
                self.bot.send_message(
                    message.chat.id,
                    "📭 Категории не настроены в конфигурации."
                )
                return
            
            response = "📁 <b>Категории товаров:</b>\n\n"
            
            for cat in categories:
                response += f"{cat['icon']} <b>{cat['name']}</b>\n"
                response += f"   🆔 ID: <code>{cat['id']}</code>\n\n"
            
            self.bot.send_message(
                message.chat.id,
                response,
                parse_mode='HTML'
            )
        
        @self.bot.message_handler(func=lambda message: message.text == "❌ Отмена")
        def handle_cancel(message):
            user_id = message.from_user.id
            
            if user_id in self.user_states:
                del self.user_states[user_id]
            if user_id in self.temp_data:
                del self.temp_data[user_id]
            
            self.bot.send_message(
                message.chat.id,
                "❌ Операция отменена.",
                reply_markup=self._create_main_menu()
            )
        
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
        def handle_delete_callback(call):
            """Обработка удаления товара"""
            if not self._is_authorized(call.from_user.id):
                self.bot.answer_callback_query(call.id, "❌ Доступ запрещен")
                return
            
            product_id = call.data.replace('delete_', '')
            
            # Получаем информацию о товаре перед удалением
            product = get_product_by_id(product_id)
            
            if not product:
                self.bot.answer_callback_query(call.id, "❌ Товар не найден")
                return
            
            # Удаляем товар
            if delete_product(product_id):
                self.bot.answer_callback_query(call.id, "✅ Товар удален")
                self.bot.edit_message_text(
                    f"✅ <b>Товар успешно удален:</b>\n\n"
                    f"📦 {product['name']}\n"
                    f"💰 {product['price']:,} сум\n"
                    f"🆔 {product_id}",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='HTML'
                )
            else:
                self.bot.answer_callback_query(call.id, "❌ Ошибка удаления")
        
        # Обработчик состояний для добавления товара
        @self.bot.message_handler(func=lambda message: message.from_user.id in self.user_states)
        def handle_states(message):
            user_id = message.from_user.id
            state = self.user_states.get(user_id)
            
            if not state:
                return
            
            if state == "awaiting_product_name":
                # Сохраняем название
                self.temp_data[user_id]['name'] = message.text
                self.user_states[user_id] = "awaiting_description"
                
                self.bot.send_message(
                    message.chat.id,
                    "📝 Введите описание товара:"
                )
            
            elif state == "awaiting_description":
                # Сохраняем описание
                self.temp_data[user_id]['description'] = message.text
                self.user_states[user_id] = "awaiting_price"
                
                self.bot.send_message(
                    message.chat.id,
                    "💰 Введите цену товара (в сумах, только число):"
                )
            
            elif state == "awaiting_price":
                # Проверяем и сохраняем цену
                try:
                    price = int(message.text)
                    self.temp_data[user_id]['price'] = price
                    self.user_states[user_id] = "awaiting_category"
                    
                    # Показываем категории
                    categories = get_categories_from_config()
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    
                    for cat in categories:
                        markup.add(types.KeyboardButton(f"{cat['icon']} {cat['name']}"))
                    markup.add(types.KeyboardButton("❌ Отмена"))
                    
                    self.bot.send_message(
                        message.chat.id,
                        "📁 Выберите категорию:",
                        reply_markup=markup
                    )
                except ValueError:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ Ошибка! Введите цену числом (например: 50000)"
                    )
            
            elif state == "awaiting_category":
                # Находим выбранную категорию
                categories = get_categories_from_config()
                selected_category = None
                
                for cat in categories:
                    if f"{cat['icon']} {cat['name']}" == message.text:
                        selected_category = cat
                        break
                
                if not selected_category:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ Неверная категория. Выберите из предложенных кнопок."
                    )
                    return
                
                self.temp_data[user_id]['category_id'] = selected_category['id']
                self.user_states[user_id] = "awaiting_images"
                
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton("⏭ Пропустить (без фото)"))
                markup.add(types.KeyboardButton("❌ Отмена"))
                
                self.bot.send_message(
                    message.chat.id,
                    "📸 Отправьте ссылки на изображения товара.\n\n"
                    "Формат: одна ссылка на строку\n"
                    "Например:\n"
                    "https://example.com/image1.jpg\n"
                    "https://example.com/image2.jpg\n\n"
                    "Или нажмите '⏭ Пропустить' чтобы добавить товар без изображений.",
                    reply_markup=markup
                )
            
            elif state == "awaiting_images":
                if message.text == "⏭ Пропустить (без фото)":
                    images = ["https://via.placeholder.com/400x400?text=No+Image"]
                else:
                    # Парсим ссылки
                    images = [line.strip() for line in message.text.split('\n') if line.strip()]
                
                # Сохраняем товар в БД
                product = add_product(
                    name=self.temp_data[user_id]['name'],
                    description=self.temp_data[user_id]['description'],
                    price=self.temp_data[user_id]['price'],
                    images=images,
                    category_id=self.temp_data[user_id]['category_id']
                )
                
                if product:
                    self.bot.send_message(
                        message.chat.id,
                        f"✅ <b>Товар успешно добавлен!</b>\n\n"
                        f"📦 Название: {product['name']}\n"
                        f"📝 Описание: {product['description']}\n"
                        f"💰 Цена: {product['price']:,} сум\n"
                        f"📁 Категория: {self.temp_data[user_id]['category_id']}\n"
                        f"🆔 ID: <code>{product['id']}</code>",
                        parse_mode='HTML',
                        reply_markup=self._create_main_menu()
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        "❌ Ошибка при добавлении товара в базу данных.",
                        reply_markup=self._create_main_menu()
                    )
                
                # Очищаем состояние
                del self.user_states[user_id]
                del self.temp_data[user_id]
    
    def run(self):
        """Запускает бота в режиме polling"""
        print("🤖 Бот запущен и готов к работе...")
        print(f"👥 Авторизованных пользователей: {len(self.authorized_users)}")
        if self.authorized_users:
            print(f"   IDs: {list(self.authorized_users)}")
        else:
            print("   ⚠️ ВНИМАНИЕ: Список авторизованных пользователей пуст!")
            print("   Добавьте Telegram ID в файл settingsbot.json")
        
        self.bot.infinity_polling()


def main():
    """Главная функция запуска бота"""
    # Получаем токен из переменных окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ ОШИБКА: TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        print("Установите переменную окружения TELEGRAM_BOT_TOKEN с токеном вашего бота.")
        return
    
    # Создаем и запускаем бота
    try:
        bot = ProductBot(bot_token)
        bot.run()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
