#!/usr/bin/env python3
"""
Скрипт запуска Telegram Proxy Manager Bot для Windows
Проверяет зависимости и запускает бота
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    print(f"✅ Python версия: {sys.version}")
    return True

def check_dependencies():
    """Проверка Python зависимостей"""
    try:
        import aiogram
        import aiohttp
        import aiofiles
        import psutil
        import requests
        print("✅ Все Python зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: install-missing.bat")
        return False

def check_env_file():
    """Проверка файла .env"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Файл .env не найден")
        print("Создайте файл .env с содержимым:")
        print("BOT_TOKEN=your_bot_token_here")
        return False
    
    print("✅ Файл .env найден")
    return True

def show_detected_ip():
    """Показать определенный IP сервера"""
    try:
        from config import get_server_ip
        ip = get_server_ip()
        print(f"🌐 Определен IP сервера: {ip}")
        return True
    except Exception as e:
        print(f"❌ Ошибка определения IP: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 Запуск Telegram Proxy Manager Bot (Windows)")
    print("=" * 50)
    
    # Проверки
    checks = [
        ("Версия Python", check_python_version),
        ("Python зависимости", check_dependencies),
        ("Файл конфигурации", check_env_file),
        ("IP сервера", show_detected_ip)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 Проверка {name}...")
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Не все проверки пройдены. Исправьте ошибки и попробуйте снова.")
        print("\n💡 Решения:")
        print("1. Установите недостающие пакеты: install-missing.bat")
        print("2. Создайте файл .env с токеном бота")
        print("3. Запустите от имени администратора")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
    
    print("\n✅ Все проверки пройдены!")
    print("🤖 Запуск бота...")
    
    # Запуск бота
    try:
        from bot import main as bot_main
        import asyncio
        asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска бота: {e}")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()
