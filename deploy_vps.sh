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
read -p "Введите имя пользователя для приложения [shopapp]: " APP_USER
APP_USER=${APP_USER:-shopapp}

read -p "Введите имя базы данных [shop_db]: " DB_NAME
DB_NAME=${DB_NAME:-shop_db}

read -p "Введите имя пользователя БД [shop_user]: " DB_USER
DB_USER=${DB_USER:-shop_user}

read -sp "Введите пароль для БД: " DB_PASSWORD
echo

read -p "Введите порт для приложения [5000]: " APP_PORT
APP_PORT=${APP_PORT:-5000}

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
print_step "Создание пользователя приложения..."
if id "$APP_USER" &>/dev/null; then
    print_warning "Пользователь $APP_USER уже существует"
else
    adduser --disabled-password --gecos "" $APP_USER
    print_step "Пользователь $APP_USER создан"
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

# Создание директории приложения
APP_DIR="/home/$APP_USER/app"
print_step "Создание директории приложения: $APP_DIR"
mkdir -p $APP_DIR

# Копирование файлов приложения
print_step "Копирование файлов приложения..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r $SCRIPT_DIR/* $APP_DIR/ 2>/dev/null || true
chown -R $APP_USER:$APP_USER $APP_DIR

# Создание .env файла
print_step "Создание файла .env..."
cat > $APP_DIR/.env <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
PORT=$APP_PORT
FLASK_ENV=production
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

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
