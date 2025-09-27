#!/bin/bash

# Скрипт установки Telegram Proxy Manager Bot

set -e

echo "🚀 Установка Telegram Proxy Manager Bot"
echo "======================================"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root: sudo ./install.sh"
    exit 1
fi

# Определение дистрибутива
if [ -f /etc/debian_version ]; then
    DISTRO="debian"
elif [ -f /etc/redhat-release ]; then
    DISTRO="redhat"
else
    echo "❌ Неподдерживаемый дистрибутив"
    exit 1
fi

echo "📦 Установка системных зависимостей..."

if [ "$DISTRO" = "debian" ]; then
    apt update
    apt install -y python3 python3-pip python3-venv dante-server shadowsocks-libev
elif [ "$DISTRO" = "redhat" ]; then
    yum install -y python3 python3-pip dante shadowsocks-libev
fi

echo "✅ Системные зависимости установлены"

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка Python зависимостей
echo "📚 Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python зависимости установлены"

# Создание директории для логов
echo "📁 Создание директорий..."
mkdir -p /var/log/proxy-bot
mkdir -p /etc/proxy-bot

# Копирование конфигурации dante
echo "⚙️ Настройка dante..."
cp dante_config_example.conf /etc/dante.conf

# Создание пользователя для dante
useradd -r -s /bin/false dante 2>/dev/null || true

# Настройка прав
chown dante:dante /etc/dante.conf
chmod 600 /etc/dante.conf

echo "✅ dante настроен"

# Создание systemd сервиса
echo "🔧 Настройка автозапуска..."
cp proxy-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable proxy-bot

echo "✅ Сервис настроен"

# Создание файла .env если его нет
if [ ! -f .env ]; then
    echo "📝 Создание файла конфигурации..."
    
    # Определяем IP сервера
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "127.0.0.1")
    
    cat > .env << EOF
BOT_TOKEN=your_bot_token_here
# SERVER_IP будет определен автоматически при запуске
# Текущий IP: $SERVER_IP
EOF
    echo "⚠️ Отредактируйте файл .env и укажите токен бота"
    echo "🌐 Определен IP сервера: $SERVER_IP"
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env: nano .env"
echo "2. Укажите токен бота в BOT_TOKEN"
echo "3. Запустите бота: systemctl start proxy-bot"
echo "4. Проверьте статус: systemctl status proxy-bot"
echo "5. Просмотрите логи: journalctl -u proxy-bot -f"
echo ""
echo "🔧 Административные утилиты:"
echo "python3 admin_utils.py"
echo ""
echo "📖 Документация: README.md"
