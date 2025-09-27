import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 1048782601
LOG_CHAT_ID = -4809940849

# Database Configuration
DATABASE_PATH = 'proxy_manager.db'

# Proxy Configuration
PROXY_TYPES = {
    'socks5': {
        'port_range': (1080, 65535),
        'command_template': 'dante -f /etc/dante.conf -D -p {port}'
    },
    'shadowsocks': {
        'port_range': (8388, 65535),
        'command_template': 'ss-server -s 0.0.0.0 -p {port} -k {password} -m aes-256-gcm'
    }
}

# Server Configuration
def get_server_ip():
    """Автоматическое определение IP сервера"""
    try:
        import requests
        # Пробуем получить внешний IP через несколько сервисов
        services = [
            'https://api.ipify.org',
            'https://ipinfo.io/ip',
            'https://ifconfig.me/ip',
            'https://icanhazip.com'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if ip and len(ip.split('.')) == 4:  # Проверяем что это валидный IPv4
                        return ip
            except:
                continue
        
        # Если не удалось получить внешний IP, используем локальный
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            return local_ip
        except:
            return '127.0.0.1'
        finally:
            s.close()
    except:
        return '127.0.0.1'

SERVER_IP = os.getenv('SERVER_IP', get_server_ip())
