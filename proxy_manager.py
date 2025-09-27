import asyncio
import subprocess
import random
import string
import aiohttp
import psutil
from typing import Dict, Optional, List
from config import PROXY_TYPES, SERVER_IP

class ProxyManager:
    def __init__(self):
        self.active_processes = {}
    
    def generate_password(self, length: int = 12) -> str:
        """Генерировать случайный пароль"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def get_free_port(self, proxy_type: str) -> int:
        """Получить свободный порт"""
        port_range = PROXY_TYPES[proxy_type]['port_range']
        start_port, end_port = port_range
        
        # Проверяем занятые порты
        used_ports = set()
        for conn in psutil.net_connections():
            if conn.laddr.port:
                used_ports.add(conn.laddr.port)
        
        # Ищем свободный порт
        for port in range(start_port, end_port):
            if port not in used_ports:
                return port
        
        raise Exception("Не удалось найти свободный порт")
    
    async def create_socks5_proxy(self) -> Dict:
        """Создать SOCKS5 прокси через dante"""
        port = self.get_free_port('socks5')
        password = self.generate_password()
        
        # Создаем конфигурационный файл для dante
        config_content = f"""
logoutput: syslog
user.privileged: root
user.unprivileged: nobody

# The listening network interface or address.
internal: 0.0.0.0 port = {port}

# The listening network interface or address.
external.interface: 0.0.0.0

# socks-rules determine what is proxied through the socks server.
socksmethod: username

# client-rules determine who can connect to the socks server.
clientmethod: none

client pass {{
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}}

socks pass {{
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: bind connect udpassociate
    log: error
    socksmethod: username
}}

# Создаем пользователя для аутентификации
user.privileged: root
user.libwrap: nobody

# Добавляем пользователя
user.privileged: root
user.libwrap: nobody

# Настройка аутентификации
socksmethod: username
clientmethod: none

# Правила для клиентов
client pass {{
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}}

# Правила для SOCKS
socks pass {{
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: bind connect udpassociate
    log: error
    socksmethod: username
}}
"""
        
        # Сохраняем конфигурацию
        config_path = f"/tmp/dante_{port}.conf"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Запускаем dante
        cmd = f"dante -f {config_path} -D -p {port}"
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.active_processes[port] = process
        
        return {
            'type': 'socks5',
            'port': port,
            'password': password,
            'process_id': process.pid,
            'config_path': config_path
        }
    
    async def create_shadowsocks_proxy(self) -> Dict:
        """Создать Shadowsocks прокси"""
        port = self.get_free_port('shadowsocks')
        password = self.generate_password()
        
        # Запускаем shadowsocks
        cmd = f"ss-server -s 0.0.0.0 -p {port} -k {password} -m aes-256-gcm"
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.active_processes[port] = process
        
        return {
            'type': 'shadowsocks',
            'port': port,
            'password': password,
            'process_id': process.pid
        }
    
    async def create_proxy(self, proxy_type: str) -> Dict:
        """Создать прокси указанного типа"""
        if proxy_type == 'socks5':
            return await self.create_socks5_proxy()
        elif proxy_type == 'shadowsocks':
            return await self.create_shadowsocks_proxy()
        else:
            raise ValueError(f"Неподдерживаемый тип прокси: {proxy_type}")
    
    async def check_proxy_status(self, proxy_type: str, port: int, password: str = None) -> str:
        """Проверить статус прокси"""
        try:
            if proxy_type == 'socks5':
                return await self.check_socks5_status(port, password)
            elif proxy_type == 'shadowsocks':
                return await self.check_shadowsocks_status(port, password)
            else:
                return 'unknown'
        except Exception as e:
            print(f"Ошибка проверки прокси: {e}")
            return 'inactive'
    
    async def check_socks5_status(self, port: int, password: str) -> str:
        """Проверить статус SOCKS5 прокси"""
        try:
            proxy_url = f"socks5://user:{password}@127.0.0.1:{port}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://httpbin.org/ip',
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return 'active'
                    else:
                        return 'inactive'
        except Exception:
            return 'inactive'
    
    async def check_shadowsocks_status(self, port: int, password: str) -> str:
        """Проверить статус Shadowsocks прокси"""
        try:
            # Для Shadowsocks проверяем, что процесс запущен
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'ss-server' in ' '.join(proc.info['cmdline'] or []):
                        if str(port) in ' '.join(proc.info['cmdline'] or []):
                            return 'active'
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return 'inactive'
        except Exception:
            return 'inactive'
    
    async def stop_proxy(self, port: int):
        """Остановить прокси"""
        if port in self.active_processes:
            process = self.active_processes[port]
            process.terminate()
            await process.wait()
            del self.active_processes[port]
    
    async def stop_all_proxies(self):
        """Остановить все прокси"""
        for port, process in self.active_processes.items():
            process.terminate()
            await process.wait()
        self.active_processes.clear()
    
    def create_vless_url(self, proxy_type: str, port: int, password: str, user_uuid: str) -> str:
        """Создать VLESS ссылку через прокси"""
        if proxy_type == 'socks5':
            # Для SOCKS5 создаем VLESS с прокси
            vless_url = f"vless://{user_uuid}@{SERVER_IP}:{port}?security=none&type=tcp&socksPort={port}&socksUser=user&socksPass={password}#SOCKS5-Proxy"
        elif proxy_type == 'shadowsocks':
            # Для Shadowsocks создаем VLESS с прокси
            vless_url = f"vless://{user_uuid}@{SERVER_IP}:{port}?security=none&type=tcp&ssPort={port}&ssPassword={password}#Shadowsocks-Proxy"
        else:
            # Обычная VLESS ссылка
            vless_url = f"vless://{user_uuid}@{SERVER_IP}:{port}?security=none&type=tcp#{proxy_type}-Proxy"
        
        return vless_url
