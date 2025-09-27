#!/usr/bin/env python3
"""
Примеры использования Telegram Proxy Manager Bot
"""

import asyncio
from database import DatabaseManager
from proxy_manager import ProxyManager

async def example_create_proxy():
    """Пример создания прокси"""
    print("🔧 Пример создания прокси")
    
    proxy_manager = ProxyManager()
    
    # Создаем SOCKS5 прокси
    print("Создаю SOCKS5 прокси...")
    socks5_proxy = await proxy_manager.create_proxy('socks5')
    print(f"SOCKS5 прокси создан:")
    print(f"  Порт: {socks5_proxy['port']}")
    print(f"  Пароль: {socks5_proxy['password']}")
    print(f"  PID: {socks5_proxy['process_id']}")
    
    # Создаем Shadowsocks прокси
    print("\nСоздаю Shadowsocks прокси...")
    ss_proxy = await proxy_manager.create_proxy('shadowsocks')
    print(f"Shadowsocks прокси создан:")
    print(f"  Порт: {ss_proxy['port']}")
    print(f"  Пароль: {ss_proxy['password']}")
    print(f"  PID: {ss_proxy['process_id']}")
    
    # Останавливаем прокси
    await proxy_manager.stop_proxy(socks5_proxy['port'])
    await proxy_manager.stop_proxy(ss_proxy['port'])
    print("\n✅ Прокси остановлены")

async def example_database_operations():
    """Пример работы с базой данных"""
    print("🗄️ Пример работы с базой данных")
    
    db_manager = DatabaseManager()
    await db_manager.init_db()
    
    # Добавляем пользователя
    print("Добавляю пользователя...")
    await db_manager.add_user(
        user_id=12345,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    print("✅ Пользователь добавлен")
    
    # Добавляем прокси
    print("Добавляю прокси...")
    await db_manager.add_proxy(
        proxy_type="socks5",
        port=1080,
        password="test_password",
        process_id=1234
    )
    print("✅ Прокси добавлен")
    
    # Получаем статистику
    print("Получаю статистику...")
    stats = await db_manager.get_proxy_stats()
    print(f"Статистика: {stats}")
    
    # Получаем свободный прокси
    print("Ищу свободный прокси...")
    free_proxy = await db_manager.get_free_proxy()
    if free_proxy:
        print(f"Найден свободный прокси: {free_proxy}")
    else:
        print("Свободных прокси не найдено")

async def example_vless_creation():
    """Пример создания VLESS ссылки"""
    print("🔗 Пример создания VLESS ссылки")
    
    proxy_manager = ProxyManager()
    
    # Создаем прокси
    proxy_data = await proxy_manager.create_proxy('socks5')
    
    # Создаем VLESS ссылку
    user_uuid = "12345678-1234-1234-1234-123456789abc"
    vless_url = proxy_manager.create_vless_url(
        proxy_data['type'],
        proxy_data['port'],
        proxy_data['password'],
        user_uuid
    )
    
    print(f"VLESS ссылка создана:")
    print(f"  URL: {vless_url}")
    print(f"  Тип прокси: {proxy_data['type']}")
    print(f"  Порт: {proxy_data['port']}")
    print(f"  Пароль: {proxy_data['password']}")
    
    # Останавливаем прокси
    await proxy_manager.stop_proxy(proxy_data['port'])
    print("\n✅ Прокси остановлен")

async def example_proxy_monitoring():
    """Пример мониторинга прокси"""
    print("📊 Пример мониторинга прокси")
    
    proxy_manager = ProxyManager()
    
    # Создаем прокси
    proxy_data = await proxy_manager.create_proxy('socks5')
    
    # Проверяем статус
    print("Проверяю статус прокси...")
    status = await proxy_manager.check_proxy_status(
        proxy_data['type'],
        proxy_data['port'],
        proxy_data['password']
    )
    print(f"Статус прокси: {status}")
    
    # Останавливаем прокси
    await proxy_manager.stop_proxy(proxy_data['port'])
    print("✅ Прокси остановлен")

async def main():
    """Главная функция с примерами"""
    print("📚 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 50)
    
    try:
        await example_create_proxy()
        print("\n" + "="*50)
        
        await example_database_operations()
        print("\n" + "="*50)
        
        await example_vless_creation()
        print("\n" + "="*50)
        
        await example_proxy_monitoring()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n✅ Все примеры выполнены")

if __name__ == "__main__":
    asyncio.run(main())
