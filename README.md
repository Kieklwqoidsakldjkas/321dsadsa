# Telegram Proxy Manager Bot

Telegram-бот на Python (aiogram) для управления прокси-серверами с возможностью создания VLESS ссылок.

## Возможности

### Общие функции
- ✅ Логирование всех действий пользователей в отдельный чат
- ✅ Автоматическая отправка статистики каждые 60 минут
- ✅ Автоматический бэкап базы данных каждые 30 минут
- ✅ Ручные команды для бэкапа и восстановления БД

### Админские функции
- ✅ Панель управления с inline-кнопками
- ✅ Добавление прокси (SOCKS5, Shadowsocks)
- ✅ Просмотр списка всех прокси
- ✅ Удаление прокси
- ✅ Проверка статуса всех прокси
- ✅ Управление базой данных

### Управление прокси
- ✅ Автоматическое создание прокси на сервере
- ✅ Генерация случайных портов и паролей
- ✅ Мониторинг статуса прокси (🟢 Работает, 🔴 Не работает, ⚪ Свободен)
- ✅ Поддержка SOCKS5 (через dante) и Shadowsocks

### VLESS ссылки
- ✅ Создание VLESS ссылок через прокси
- ✅ Автоматическое назначение свободных прокси пользователям
- ✅ Отслеживание пользовательских сессий

## Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd vpn
```

### 2. Автоматическая установка

#### Для Linux/Unix:
```bash
sudo ./install.sh
```

#### Для Windows:
```cmd
install.bat
```

### 3. Ручная установка

#### Установка Python зависимостей:
```bash
pip install -r requirements.txt
```

#### Установка системных зависимостей

**Для Ubuntu/Debian:**
```bash
# Установка dante (SOCKS5)
sudo apt update
sudo apt install dante-server

# Установка shadowsocks
sudo apt install shadowsocks-libev
```

**Для CentOS/RHEL:**
```bash
# Установка dante
sudo yum install dante

# Установка shadowsocks
sudo yum install shadowsocks-libev
```

**Для Windows:**
- Установите Python 3.8+ с https://python.org
- Системные зависимости не требуются (прокси запускаются через Python)
- При проблемах с установкой: `fix-install.bat`

### 4. Настройка конфигурации

Создайте файл `.env` в корне проекта:
```env
BOT_TOKEN=your_bot_token_here
# SERVER_IP будет определен автоматически при запуске
```

**Автоматическое определение IP:**
- Бот автоматически определяет внешний IP сервера при запуске
- Использует несколько сервисов для надежности: api.ipify.org, ipinfo.io, ifconfig.me, icanhazip.com
- Если внешний IP недоступен, использует локальный IP сервера
- Можно принудительно задать IP в переменной `SERVER_IP` в файле `.env`

### 5. Настройка dante (для SOCKS5)

Создайте файл конфигурации `/etc/dante.conf`:
```
logoutput: syslog
user.privileged: root
user.unprivileged: nobody

# The listening network interface or address.
internal: 0.0.0.0 port = 1080

# The listening network interface or address.
external.interface: 0.0.0.0

# socks-rules determine what is proxied through the socks server.
socksmethod: username

# client-rules determine who can connect to the socks server.
clientmethod: none

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: bind connect udpassociate
    log: error
    socksmethod: username
}
```

## Запуск

### Быстрый запуск:

**Linux/Unix:**
```bash
python run.py
```

**Windows:**
```cmd
run.bat
```

### Прямой запуск:
```bash
python bot.py
```

### Тестирование определения IP:
```bash
python test_ip.py
```

## Использование

### Для администратора (ID: 1048782601)

1. Отправьте команду `/start` боту
2. Используйте админскую панель с кнопками:
   - **➕ Добавить прокси** - создание новых прокси
   - **📋 Список прокси** - просмотр всех прокси
   - **🗑 Удалить прокси** - удаление прокси
   - **📊 Проверить статус всех прокси** - проверка работоспособности
   - **💾 Бэкап БД** - создание резервной копии
   - **📥 Восстановить БД** - восстановление из бэкапа

### Для пользователей

1. Отправьте команду `/start` боту
2. Нажмите кнопку "🔗 Получить VLESS ссылку"
3. Скопируйте полученную ссылку и используйте в вашем клиенте

## Структура проекта

```
vpn/
├── bot.py                    # Основной файл бота
├── config.py                 # Конфигурация с автоопределением IP
├── database.py              # Управление базой данных
├── proxy_manager.py         # Управление прокси
├── admin_utils.py           # Административные утилиты
├── run.py                   # Скрипт запуска с проверками (Linux/Unix)
├── run.bat                  # Скрипт запуска для Windows
├── test_ip.py              # Тест определения IP
├── examples.py              # Примеры использования
├── install.sh               # Скрипт установки (Linux/Unix)
├── install.bat              # Скрипт установки для Windows
├── proxy-bot.service        # Systemd сервис
├── dante_config_example.conf # Пример конфигурации dante
├── requirements.txt         # Python зависимости
├── README.md               # Документация
└── .env                    # Переменные окружения (создать самостоятельно)
```

## База данных

Бот использует SQLite базу данных со следующими таблицами:

- **users** - информация о пользователях
- **proxies** - информация о прокси-серверах
- **user_sessions** - активные пользовательские сессии

## Мониторинг

- Все действия пользователей логируются в чат с ID: -4809940849
- Статистика отправляется каждые 60 минут
- Бэкап базы данных создается каждые 30 минут

## Безопасность

- Проверка прав администратора по ID
- Валидация всех входящих данных
- Безопасное управление процессами прокси

## Поддерживаемые типы прокси

- **SOCKS5** - через dante-server
- **Shadowsocks** - через shadowsocks-libev

## Формат VLESS ссылок

```
vless://uuid@ip:port?security=none&type=tcp#Название
```

## Требования

- Python 3.8+
- Ubuntu/Debian/CentOS/RHEL
- dante-server (для SOCKS5)
- shadowsocks-libev (для Shadowsocks)
- Telegram Bot Token

## 🆘 Решение проблем

### Проблемы с установкой зависимостей на Windows

**Ошибка с Rust/cryptography:**
```cmd
fix-install.bat
```

**Альтернативные решения:**
1. Установите Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Используйте conda вместо pip:
   ```cmd
   conda install aiogram aiohttp aiofiles python-dotenv psutil requests
   ```
3. Установите пакеты по одному:
   ```cmd
   pip install aiogram
   pip install aiohttp
   pip install aiofiles
   pip install python-dotenv
   pip install psutil
   pip install requests
   ```

**Проблемы с правами:**
- Запустите командную строку от имени администратора
- Или используйте `--user` флаг: `pip install --user -r requirements.txt`

**Проблемы с Python:**
- Убедитесь, что Python 3.8+ установлен
- Проверьте, что pip обновлен: `python -m pip install --upgrade pip`

## Лицензия

MIT License
