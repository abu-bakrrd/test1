#!/bin/bash

# Скрипт автоматического развертывания на VPS Ubuntu 22.04
# Использование: ./deploy_vps.sh

set -e

echo "=================================================="
echo "🚀 Начало развертывания Telegram Shop на VPS"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка, что скрипт запущен с правами root
if [ "$EUID" -ne 0 ]; then 
    print_error "Пожалуйста, запустите скрипт с правами root (sudo)"
    exit 1
fi

# Запрос параметров
echo ""
echo "🔗 НАСТРОЙКА ИСТОЧНИКА КОДА"
echo ""
read -p "Введите URL вашего GitHub репозитория (или оставьте пустым для локальных файлов): " GITHUB_REPO
echo ""

if [ ! -z "$GITHUB_REPO" ]; then
    read -p "Введите ветку для клонирования [main]: " GIT_BRANCH
    GIT_BRANCH=${GIT_BRANCH:-main}
    echo ""
    print_step "Будет использован репозиторий: $GITHUB_REPO (ветка: $GIT_BRANCH)"
else
    print_step "Будут использованы локальные файлы"
fi

echo ""
echo "⚙️ НАСТРОЙКА ПРИЛОЖЕНИЯ"
echo ""

read -p "Введите имя пользователя для приложения [shopapp]: " APP_USER
APP_USER=${APP_USER:-shopapp}
# Валидация имени пользователя
if [[ ! "$APP_USER" =~ ^[a-z_][a-z0-9_-]*$ ]]; then
    print_error "Некорректное имя пользователя. Используется значение по умолчанию: shopapp"
    APP_USER="shopapp"
fi

read -p "Введите имя базы данных [shop_db]: " DB_NAME
DB_NAME=${DB_NAME:-shop_db}

read -p "Введите имя пользователя БД [shop_user]: " DB_USER
DB_USER=${DB_USER:-shop_user}

read -sp "Введите пароль для БД: " DB_PASSWORD
echo
# Проверка пароля
if [ -z "$DB_PASSWORD" ]; then
    print_error "Пароль не может быть пустым!"
    read -sp "Введите пароль для БД ещё раз: " DB_PASSWORD
    echo
fi

read -p "Введите порт для приложения [5000]: " APP_PORT
APP_PORT=${APP_PORT:-5000}

echo ""
echo "🤖 НАСТРОЙКА TELEGRAM БОТА"
echo ""
echo "Следующие параметры нужны для работы Telegram бота управления товарами:"
echo ""

read -p "Введите токен Telegram бота (от @BotFather): " TELEGRAM_BOT_TOKEN
while [ -z "$TELEGRAM_BOT_TOKEN" ]; do
    print_error "Токен бота не может быть пустым!"
    read -p "Введите токен Telegram бота (от @BotFather): " TELEGRAM_BOT_TOKEN
done

read -p "Введите ваш Telegram ID (для доступа к боту): " TELEGRAM_ADMIN_ID
while [ -z "$TELEGRAM_ADMIN_ID" ]; do
    print_error "Telegram ID не может быть пустым!"
    read -p "Введите ваш Telegram ID: " TELEGRAM_ADMIN_ID
done

read -p "Введите Cloudinary Cloud Name: " CLOUDINARY_CLOUD_NAME
while [ -z "$CLOUDINARY_CLOUD_NAME" ]; do
    print_error "Cloudinary Cloud Name не может быть пустым!"
    read -p "Введите Cloudinary Cloud Name: " CLOUDINARY_CLOUD_NAME
done

read -p "Введите Cloudinary API Key: " CLOUDINARY_API_KEY
while [ -z "$CLOUDINARY_API_KEY" ]; do
    print_error "Cloudinary API Key не может быть пустым!"
    read -p "Введите Cloudinary API Key: " CLOUDINARY_API_KEY
done

read -sp "Введите Cloudinary API Secret: " CLOUDINARY_API_SECRET
echo
while [ -z "$CLOUDINARY_API_SECRET" ]; do
    print_error "Cloudinary API Secret не может быть пустым!"
    read -sp "Введите Cloudinary API Secret: " CLOUDINARY_API_SECRET
    echo
done

print_step "Данные Telegram бота сохранены"

# Установка пакетов
print_step "Обновление системы и установка пакетов..."
apt update && apt upgrade -y

print_step "Установка необходимых пакетов..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl

# Node.js уже должен быть установлен (версия 20 от NodeSource)
# Если нет - установим
if ! command -v node &> /dev/null; then
    print_step "Установка Node.js LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    print_step "Node.js уже установлен: $(node --version)"
fi

# Создание пользователя приложения
print_step "Создание пользователя приложения: $APP_USER"
if id "$APP_USER" &>/dev/null; then
    print_warning "Пользователь $APP_USER уже существует"
else
    # Создаём пользователя с автоматическими ответами
    adduser --disabled-password --gecos "" --quiet $APP_USER 2>/dev/null || \
    useradd -m -s /bin/bash $APP_USER
    
    if id "$APP_USER" &>/dev/null; then
        print_step "Пользователь $APP_USER создан"
    else
        print_error "Не удалось создать пользователя $APP_USER"
        exit 1
    fi
fi

# Добавление пользователя в группу www-data для работы с Nginx
usermod -a -G www-data $APP_USER
print_step "Пользователь $APP_USER добавлен в группу www-data"

# Настройка PostgreSQL
print_step "Настройка PostgreSQL..."
sudo -u postgres psql <<EOF
-- Создание базы данных и пользователя
SELECT 'CREATE DATABASE $DB_NAME' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
DO
\$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
   END IF;
END
\$\$;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

print_step "PostgreSQL настроен"

# Настройка pg_hba.conf для локальных подключений
PG_VERSION=$(ls /etc/postgresql/)
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

if ! grep -q "host.*all.*all.*127.0.0.1/32.*md5" "$PG_HBA"; then
    print_step "Настройка pg_hba.conf..."
    echo "host    all             all             127.0.0.1/32            md5" >> "$PG_HBA"
    systemctl restart postgresql
fi

# Создание директории приложения и получение кода
APP_DIR="/home/$APP_USER/app"

if [ ! -z "$GITHUB_REPO" ]; then
    # Клонирование из GitHub
    print_step "Клонирование репозитория из GitHub: $GITHUB_REPO"
    
    # Удаляем директорию если она существует
    if [ -d "$APP_DIR" ]; then
        print_warning "Директория $APP_DIR уже существует, удаляем..."
        rm -rf $APP_DIR
    fi
    
    # Клонируем репозиторий
    sudo -u $APP_USER git clone -b $GIT_BRANCH $GITHUB_REPO $APP_DIR
    
    if [ $? -ne 0 ]; then
        print_error "Ошибка клонирования репозитория"
        print_error "Проверьте URL репозитория и права доступа"
        exit 1
    fi
    
    print_step "Репозиторий успешно клонирован"
else
    # Копирование локальных файлов
    print_step "Создание директории приложения: $APP_DIR"
    mkdir -p $APP_DIR
    
    print_step "Копирование файлов приложения..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cp -r $SCRIPT_DIR/* $APP_DIR/ 2>/dev/null || true
    chown -R $APP_USER:$APP_USER $APP_DIR
    print_step "Локальные файлы скопированы"
fi

# Создание .env файла
print_step "Создание файла .env..."
cat > $APP_DIR/.env <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
PORT=$APP_PORT
FLASK_ENV=production
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

# Создание .env файла для Telegram бота
print_step "Создание файла .env для Telegram бота..."
cat > $APP_DIR/telegram_bot/.env <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET
EOF

chown $APP_USER:$APP_USER $APP_DIR/telegram_bot/.env
chmod 600 $APP_DIR/telegram_bot/.env
print_step "Файл .env для Telegram бота создан"

# Синхронизация категорий и настройка settingsbot.json
print_step "Синхронизация категорий и настройка Telegram бота..."
export APP_DIR
ADMIN_ID="$TELEGRAM_ADMIN_ID" python3 <<'PYTHON_SCRIPT'
import json
import os

# Пути к файлам
config_path = os.environ.get('APP_DIR') + "/config/settings.json"
settingsbot_path = os.environ.get('APP_DIR') + "/telegram_bot/settingsbot.json"
admin_id = os.environ.get('ADMIN_ID', '')

# Читаем категории из config/settings.json
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
    categories = config.get('categories', [])

# Читаем settingsbot.json
with open(settingsbot_path, 'r', encoding='utf-8') as f:
    settingsbot = json.load(f)

# Обновляем категории и admin ID
settingsbot['categories'] = categories

# Преобразуем admin_id в int, убираем @ если есть
admin_id_clean = admin_id.strip().lstrip('@')
try:
    admin_id_int = int(admin_id_clean)
    settingsbot['authorized_users'] = [admin_id_int]
except ValueError:
    print(f"⚠️ Внимание: {admin_id} не является числовым ID")
    print("Оставляем существующий список авторизованных пользователей")

# Сохраняем обновленный settingsbot.json
with open(settingsbot_path, 'w', encoding='utf-8') as f:
    json.dump(settingsbot, f, ensure_ascii=False, indent=2)

print("✅ Категории синхронизированы и Admin ID добавлен")
PYTHON_SCRIPT

chown $APP_USER:$APP_USER $APP_DIR/telegram_bot/settingsbot.json
print_step "Настройка Telegram бота завершена"

# Установка зависимостей и сборка
print_step "Установка зависимостей и сборка приложения..."
cd $APP_DIR

# Установка Node.js зависимостей и сборка фронтенда
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
npm install
npm run build
EOF

# Создание виртуального окружения и установка Python зависимостей
sudo -u $APP_USER bash <<EOF
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Настройка прав доступа для Nginx
print_step "Настройка прав доступа для Nginx..."
# Nginx должен иметь доступ к родительским директориям
chmod 755 /home/$APP_USER
chmod 755 $APP_DIR

# Права доступа к собранному фронтенду
if [ -d "$APP_DIR/dist" ]; then
    chown -R $APP_USER:www-data $APP_DIR/dist
    chmod -R 755 $APP_DIR/dist
    print_step "Права на dist/ настроены"
fi

# Права доступа к конфигурации (для /config endpoint)
if [ -d "$APP_DIR/config" ]; then
    chown -R $APP_USER:www-data $APP_DIR/config
    chmod -R 755 $APP_DIR/config
    print_step "Права на config/ настроены"
fi

# Создание systemd сервиса
print_step "Создание systemd сервиса..."
cat > /etc/systemd/system/shop-app.service <<EOF
[Unit]
Description=Telegram Shop Flask Application
After=network.target postgresql.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn app:app --bind 127.0.0.1:$APP_PORT --workers 4 --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
print_step "Запуск приложения..."
systemctl daemon-reload
systemctl enable shop-app
systemctl start shop-app

# Проверка статуса
sleep 3
if systemctl is-active --quiet shop-app; then
    print_step "Приложение успешно запущено!"
else
    print_error "Ошибка запуска приложения. Проверьте логи: journalctl -u shop-app -n 50"
    exit 1
fi

# Настройка Nginx
print_step "Настройка Nginx..."
cat > /etc/nginx/sites-available/shop <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    access_log /var/log/nginx/shop_access.log;
    error_log /var/log/nginx/shop_error.log;

    location /assets {
        alias $APP_DIR/dist/public/assets;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /config {
        alias $APP_DIR/config;
        expires 1h;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
EOF

# Активация конфигурации Nginx
ln -sf /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации Nginx
if nginx -t; then
    print_step "Nginx конфигурация корректна"
    systemctl restart nginx
else
    print_error "Ошибка в конфигурации Nginx"
    exit 1
fi

# Настройка Firewall
print_step "Настройка Firewall..."
if command -v ufw &> /dev/null; then
    ufw allow ssh
    ufw allow http
    ufw allow https
    echo "y" | ufw enable
else
    print_warning "UFW не установлен. Рекомендуется установить и настроить firewall"
fi

# Инициализация базы данных с тестовыми данными
print_step "Хотите загрузить тестовые данные? (y/n)"
read -p "Ответ: " LOAD_SEED
if [ "$LOAD_SEED" = "y" ] || [ "$LOAD_SEED" = "Y" ]; then
    sudo -u $APP_USER bash <<EOF
cd $APP_DIR
source venv/bin/activate
python3 seed_db.py
EOF
    print_step "Тестовые данные загружены"
fi

# Финальная информация
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Развертывание завершено успешно!${NC}"
echo "=================================================="
echo ""
echo "📋 Информация о развертывании:"
echo "  - Приложение: http://$(hostname -I | awk '{print $1}')"
echo "  - Пользователь: $APP_USER"
echo "  - Директория: $APP_DIR"
echo "  - База данных: $DB_NAME"
echo "  - Порт приложения: $APP_PORT"
echo ""
echo "🔧 Полезные команды:"
echo "  - Проверить статус: systemctl status shop-app"
echo "  - Просмотреть логи: journalctl -u shop-app -f"
echo "  - Перезапустить: systemctl restart shop-app"
echo ""
echo "📝 Для обновления приложения используйте: ./update_vps.sh"
echo ""

# Создание архива telegram_bot для скачивания
print_step "Создание архива Telegram бота для Windows..."
cd $APP_DIR
apt install -y zip > /dev/null 2>&1
ZIP_FILE="telegram_bot_$(date +%Y%m%d_%H%M%S).zip"
zip -r $ZIP_FILE telegram_bot/ -x "telegram_bot/__pycache__/*" > /dev/null 2>&1
chown $APP_USER:$APP_USER $ZIP_FILE

echo ""
echo "=================================================="
echo -e "${GREEN}🤖 TELEGRAM БОТ - ГОТОВ К СБОРКЕ${NC}"
echo "=================================================="
echo ""
echo "Архив Telegram бота создан: $ZIP_FILE"
echo ""
echo "📥 Команда для скачивания на ваш Windows компьютер:"
echo ""
echo -e "${YELLOW}scp root@$(hostname -I | awk '{print $1}'):$APP_DIR/$ZIP_FILE .${NC}"
echo ""
echo "После скачивания:"
echo "  1. Распакуйте архив"
echo "  2. Запустите build_exe.bat в папке telegram_bot"
echo "  3. Получите готовый .exe файл в папке dist/"
echo ""
echo "=================================================="
echo ""
