@echo off
REM Скрипт запуска Telegram Proxy Manager Bot для Windows

echo 🚀 Запуск Telegram Proxy Manager Bot
echo ====================================

REM Активация виртуального окружения
if exist venv\Scripts\activate.bat (
    echo 📦 Активация виртуального окружения...
    call venv\Scripts\activate.bat
)

REM Запуск бота
echo 🤖 Запуск бота...
python run-windows.py

pause
