@echo off
REM Скрипт установки Telegram Proxy Manager Bot для Windows

echo 🚀 Установка Telegram Proxy Manager Bot для Windows
echo ================================================

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo ✅ Python найден

REM Создание виртуального окружения
echo 🐍 Создание виртуального окружения...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Ошибка создания виртуального окружения
    pause
    exit /b 1
)

REM Активация виртуального окружения
echo 📦 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Обновление pip
echo 📚 Обновление pip...
python -m pip install --upgrade pip

REM Установка зависимостей
echo 📚 Установка Python зависимостей...

REM Сначала пробуем установить основные пакеты
echo 🔧 Установка основных пакетов...
pip install aiogram==3.2.0 aiohttp==3.9.1 aiofiles==23.2.1 python-dotenv==1.0.0 psutil==5.9.6 requests==2.31.0

REM Если есть проблемы с cryptography, устанавливаем предкомпилированную версию
echo 🔧 Установка cryptography...
pip install --only-binary=all cryptography==41.0.7
if %errorlevel% neq 0 (
    echo ⚠️ Проблемы с cryptography, пробуем альтернативную установку...
    pip install cryptography==41.0.7 --no-build-isolation
)

REM Проверяем установку
echo 🔍 Проверка установленных пакетов...
python -c "import aiogram, aiohttp, aiofiles, psutil, requests; print('✅ Основные пакеты установлены')"
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки зависимостей
    echo 💡 Попробуйте запустить: pip install --upgrade pip setuptools wheel
    pause
    exit /b 1
)

echo ✅ Python зависимости установлены

REM Создание файла .env если его нет
if not exist .env (
    echo 📝 Создание файла конфигурации...
    
    REM Определяем IP сервера
    for /f %%i in ('powershell -Command "(Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing).Content"') do set SERVER_IP=%%i
    
    echo BOT_TOKEN=your_bot_token_here > .env
    echo # SERVER_IP будет определен автоматически при запуске >> .env
    echo # Текущий IP: %SERVER_IP% >> .env
    
    echo ⚠️ Отредактируйте файл .env и укажите токен бота
    echo 🌐 Определен IP сервера: %SERVER_IP%
)

echo.
echo 🎉 Установка завершена!
echo.
echo 📋 Следующие шаги:
echo 1. Отредактируйте файл .env: notepad .env
echo 2. Укажите токен бота в BOT_TOKEN
echo 3. Запустите бота: run.bat
echo 4. Или напрямую: python run.py
echo.
echo 🔧 Административные утилиты:
echo python admin_utils.py
echo.
echo 📖 Документация: README.md
echo.
pause
