#!/usr/bin/env python3
"""
Утилиты для администрирования Telegram Proxy Manager Bot
"""

import asyncio
import sqlite3
from datetime import datetime
from database import DatabaseManager
from proxy_manager import ProxyManager

class AdminUtils:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.proxy_manager = ProxyManager()
    
    async def show_stats(self):
        """Показать статистику"""
        stats = await self.db_manager.get_proxy_stats()
        
        print("📊 СТАТИСТИКА БОТА")
        print("=" * 30)
        print(f"👥 Всего пользователей: {stats['total_users']}")
        print(f"🔗 Всего прокси: {stats['total_proxies']}")
        print(f"🟢 Активные прокси: {stats['active_proxies']}")
        print(f"⚪ Свободные прокси: {stats['free_proxies']}")
        print(f"🔴 Не работающие: {stats['inactive_proxies']}")
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def list_proxies(self):
        """Показать список всех прокси"""
        proxies = await self.db_manager.get_all_proxies()
        
        if not proxies:
            print("❌ Прокси не найдены")
            return
        
        print("📋 СПИСОК ПРОКСИ")
        print("=" * 50)
        
        for proxy in proxies:
            status_emoji = {
                'active': '🟢',
                'inactive': '🔴',
                'free': '⚪'
            }.get(proxy['status'], '❓')
            
            print(f"{status_emoji} ID: {proxy['id']}")
            print(f"   Тип: {proxy['proxy_type'].upper()}")
            print(f"   Порт: {proxy['port']}")
            print(f"   Пароль: {proxy['password']}")
            print(f"   Статус: {proxy['status']}")
            print(f"   Создан: {proxy['created_at']}")
            print(f"   Последняя проверка: {proxy['last_check'] or 'Никогда'}")
            print("-" * 30)
    
    async def check_all_proxies(self):
        """Проверить все прокси"""
        proxies = await self.db_manager.get_all_proxies()
        
        if not proxies:
            print("❌ Прокси не найдены")
            return
        
        print("⏳ Проверяю статус всех прокси...")
        
        checked = 0
        active = 0
        inactive = 0
        
        for proxy in proxies:
            try:
                status = await self.proxy_manager.check_proxy_status(
                    proxy['proxy_type'],
                    proxy['port'],
                    proxy['password']
                )
                
                await self.db_manager.update_proxy_status(proxy['id'], status)
                
                if status == 'active':
                    active += 1
                else:
                    inactive += 1
                
                checked += 1
                print(f"✅ Прокси {proxy['id']} ({proxy['proxy_type']}:{proxy['port']}) - {status}")
                
            except Exception as e:
                print(f"❌ Ошибка проверки прокси {proxy['id']}: {e}")
        
        print(f"\n📊 Результат проверки:")
        print(f"   Проверено: {checked}")
        print(f"   Активных: {active}")
        print(f"   Неактивных: {inactive}")
    
    async def cleanup_inactive_proxies(self):
        """Очистка неактивных прокси"""
        proxies = await self.db_manager.get_all_proxies()
        inactive_proxies = [p for p in proxies if p['status'] == 'inactive']
        
        if not inactive_proxies:
            print("✅ Неактивных прокси не найдено")
            return
        
        print(f"🗑 Найдено {len(inactive_proxies)} неактивных прокси")
        
        for proxy in inactive_proxies:
            try:
                # Останавливаем процесс
                await self.proxy_manager.stop_proxy(proxy['port'])
                
                # Удаляем из базы
                await self.db_manager.delete_proxy(proxy['id'])
                
                print(f"✅ Удален прокси {proxy['id']} ({proxy['proxy_type']}:{proxy['port']})")
                
            except Exception as e:
                print(f"❌ Ошибка удаления прокси {proxy['id']}: {e}")
    
    async def create_backup(self):
        """Создать бэкап базы данных"""
        try:
            backup_path = await self.db_manager.backup_database()
            print(f"✅ Бэкап создан: {backup_path}")
        except Exception as e:
            print(f"❌ Ошибка создания бэкапа: {e}")
    
    async def show_users(self):
        """Показать список пользователей"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_name, created_at, is_active
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            print("❌ Пользователи не найдены")
            return
        
        print("👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 50)
        
        for user in users:
            status = "✅ Активен" if user[5] else "❌ Неактивен"
            username = f"@{user[1]}" if user[1] else "Без username"
            name = f"{user[2]} {user[3]}" if user[2] or user[3] else "Без имени"
            
            print(f"ID: {user[0]}")
            print(f"   Username: {username}")
            print(f"   Имя: {name}")
            print(f"   Статус: {status}")
            print(f"   Регистрация: {user[4]}")
            print("-" * 30)

async def main():
    """Главная функция утилиты"""
    utils = AdminUtils()
    
    while True:
        print("\n🔧 АДМИНИСТРАТИВНЫЕ УТИЛИТЫ")
        print("=" * 40)
        print("1. Показать статистику")
        print("2. Список прокси")
        print("3. Проверить все прокси")
        print("4. Очистить неактивные прокси")
        print("5. Создать бэкап")
        print("6. Список пользователей")
        print("0. Выход")
        
        choice = input("\nВыберите действие (0-6): ").strip()
        
        if choice == "0":
            print("👋 До свидания!")
            break
        elif choice == "1":
            await utils.show_stats()
        elif choice == "2":
            await utils.list_proxies()
        elif choice == "3":
            await utils.check_all_proxies()
        elif choice == "4":
            await utils.cleanup_inactive_proxies()
        elif choice == "5":
            await utils.create_backup()
        elif choice == "6":
            await utils.show_users()
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    asyncio.run(main())
