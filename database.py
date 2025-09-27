import sqlite3
import asyncio
import aiofiles
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        
    async def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Таблица прокси
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy_type TEXT NOT NULL,
                port INTEGER NOT NULL,
                password TEXT NOT NULL,
                status TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check TIMESTAMP,
                process_id INTEGER,
                UNIQUE(port)
            )
        ''')
        
        # Таблица пользовательских сессий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                proxy_id INTEGER,
                vless_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (proxy_id) REFERENCES proxies (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавить пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    async def add_proxy(self, proxy_type: str, port: int, password: str, process_id: int = None):
        """Добавить прокси"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO proxies (proxy_type, port, password, process_id)
            VALUES (?, ?, ?, ?)
        ''', (proxy_type, port, password, process_id))
        
        conn.commit()
        conn.close()
    
    async def get_free_proxy(self) -> Optional[Dict]:
        """Получить свободный прокси"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM proxies 
            WHERE status = 'free' AND last_check IS NOT NULL
            ORDER BY created_at ASC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'proxy_type': result[1],
                'port': result[2],
                'password': result[3],
                'status': result[4],
                'created_at': result[5],
                'last_check': result[6],
                'process_id': result[7]
            }
        return None
    
    async def update_proxy_status(self, proxy_id: int, status: str):
        """Обновить статус прокси"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE proxies 
            SET status = ?, last_check = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, proxy_id))
        
        conn.commit()
        conn.close()
    
    async def get_proxy_stats(self) -> Dict:
        """Получить статистику прокси"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество прокси
        cursor.execute('SELECT COUNT(*) FROM proxies')
        total_proxies = cursor.fetchone()[0]
        
        # Активные прокси
        cursor.execute('SELECT COUNT(*) FROM proxies WHERE status = "active"')
        active_proxies = cursor.fetchone()[0]
        
        # Свободные прокси
        cursor.execute('SELECT COUNT(*) FROM proxies WHERE status = "free"')
        free_proxies = cursor.fetchone()[0]
        
        # Не работающие прокси
        cursor.execute('SELECT COUNT(*) FROM proxies WHERE status = "inactive"')
        inactive_proxies = cursor.fetchone()[0]
        
        # Количество пользователей
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        total_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_proxies': total_proxies,
            'active_proxies': active_proxies,
            'free_proxies': free_proxies,
            'inactive_proxies': inactive_proxies,
            'total_users': total_users
        }
    
    async def get_all_proxies(self) -> List[Dict]:
        """Получить все прокси"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proxies ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        proxies = []
        for result in results:
            proxies.append({
                'id': result[0],
                'proxy_type': result[1],
                'port': result[2],
                'password': result[3],
                'status': result[4],
                'created_at': result[5],
                'last_check': result[6],
                'process_id': result[7]
            })
        
        return proxies
    
    async def delete_proxy(self, proxy_id: int):
        """Удалить прокси"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM proxies WHERE id = ?', (proxy_id,))
        
        conn.commit()
        conn.close()
    
    async def create_user_session(self, user_id: int, proxy_id: int, vless_url: str):
        """Создать пользовательскую сессию"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_sessions (user_id, proxy_id, vless_url)
            VALUES (?, ?, ?)
        ''', (user_id, proxy_id, vless_url))
        
        conn.commit()
        conn.close()
    
    async def get_user_session(self, user_id: int) -> Optional[Dict]:
        """Получить активную сессию пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT us.*, p.proxy_type, p.port, p.password
            FROM user_sessions us
            JOIN proxies p ON us.proxy_id = p.id
            WHERE us.user_id = ? AND us.is_active = 1
            ORDER BY us.created_at DESC
            LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'proxy_id': result[2],
                'vless_url': result[3],
                'created_at': result[4],
                'is_active': result[5],
                'proxy_type': result[6],
                'port': result[7],
                'password': result[8]
            }
        return None
    
    async def backup_database(self) -> str:
        """Создать бэкап базы данных"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_{timestamp}.db"
        
        # Копируем базу данных
        async with aiofiles.open(self.db_path, 'rb') as source:
            content = await source.read()
            async with aiofiles.open(backup_path, 'wb') as backup:
                await backup.write(content)
        
        return backup_path
