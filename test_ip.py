#!/usr/bin/env python3
"""
Тест автоматического определения IP сервера
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ip_detection():
    """Тестирование определения IP"""
    print("🌐 Тестирование автоматического определения IP сервера")
    print("=" * 60)
    
    try:
        from config import get_server_ip, SERVER_IP
        
        print("🔍 Определение IP сервера...")
        detected_ip = get_server_ip()
        
        print(f"✅ Определен IP: {detected_ip}")
        print(f"✅ Используется IP: {SERVER_IP}")
        
        if detected_ip == SERVER_IP:
            print("✅ IP определен корректно!")
        else:
            print("⚠️ Возможно, есть проблема с определением IP")
        
        # Дополнительная информация
        print(f"\n📋 Дополнительная информация:")
        print(f"   IP из переменной окружения: {os.getenv('SERVER_IP', 'Не задан')}")
        print(f"   Финальный IP: {SERVER_IP}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка определения IP: {e}")
        return False

def test_services():
    """Тестирование сервисов определения IP"""
    print("\n🔍 Тестирование сервисов определения IP")
    print("=" * 50)
    
    import requests
    
    services = [
        ('api.ipify.org', 'https://api.ipify.org'),
        ('ipinfo.io', 'https://ipinfo.io/ip'),
        ('ifconfig.me', 'https://ifconfig.me/ip'),
        ('icanhazip.com', 'https://icanhazip.com')
    ]
    
    working_services = []
    
    for name, url in services:
        try:
            print(f"🔍 Тестирую {name}...")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                if ip and len(ip.split('.')) == 4:
                    print(f"   ✅ {name}: {ip}")
                    working_services.append((name, ip))
                else:
                    print(f"   ❌ {name}: Неверный формат IP")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    print(f"\n📊 Результат: {len(working_services)} из {len(services)} сервисов работают")
    
    if working_services:
        print("✅ Рабочие сервисы:")
        for name, ip in working_services:
            print(f"   - {name}: {ip}")
    else:
        print("❌ Ни один сервис не работает")
    
    return len(working_services) > 0

def main():
    """Главная функция"""
    print("🚀 ТЕСТ АВТОМАТИЧЕСКОГО ОПРЕДЕЛЕНИЯ IP")
    print("=" * 60)
    
    # Тест сервисов
    services_ok = test_services()
    
    # Тест определения IP
    ip_ok = test_ip_detection()
    
    print(f"\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Сервисы IP: {'✅' if services_ok else '❌'}")
    print(f"   Определение IP: {'✅' if ip_ok else '❌'}")
    
    if services_ok and ip_ok:
        print("\n🎉 Все тесты пройдены! IP определяется корректно.")
    else:
        print("\n⚠️ Есть проблемы с определением IP.")
        print("   Проверьте интернет-соединение и настройки файрвола.")

if __name__ == "__main__":
    main()
