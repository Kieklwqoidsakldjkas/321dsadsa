import asyncio
import logging
import uuid
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, LOG_CHAT_ID, SERVER_IP
from database import DatabaseManager
from proxy_manager import ProxyManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Инициализация менеджеров
db_manager = DatabaseManager()
proxy_manager = ProxyManager()

# Состояния для FSM
class AdminStates(StatesGroup):
    waiting_proxy_type = State()
    waiting_proxy_quantity = State()

class UserStates(StatesGroup):
    waiting_vless_request = State()

# Эмодзи для статусов
STATUS_EMOJIS = {
    'active': '🟢',
    'inactive': '🔴',
    'free': '⚪'
}

async def log_user_action(user_id: int, username: str, action: str):
    """Логировать действия пользователей"""
    try:
        message = f"👤 Пользователь: @{username} (ID: {user_id})\n"
        message += f"🔧 Действие: {action}\n"
        message += f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await bot.send_message(LOG_CHAT_ID, message)
    except Exception as e:
        logger.error(f"Ошибка отправки лога: {e}")

async def send_statistics():
    """Отправить статистику в лог-чат"""
    try:
        stats = await db_manager.get_proxy_stats()
        
        message = "📊 СТАТИСТИКА БОТА\n\n"
        message += f"👥 Всего пользователей: {stats['total_users']}\n"
        message += f"🔗 Всего прокси: {stats['total_proxies']}\n"
        message += f"🟢 Активные прокси: {stats['active_proxies']}\n"
        message += f"⚪ Свободные прокси: {stats['free_proxies']}\n"
        message += f"🔴 Не работающие: {stats['inactive_proxies']}\n"
        message += f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await bot.send_message(LOG_CHAT_ID, message)
    except Exception as e:
        logger.error(f"Ошибка отправки статистики: {e}")

async def send_database_backup():
    """Отправить бэкап базы данных"""
    try:
        backup_path = await db_manager.backup_database()
        
        with open(backup_path, 'rb') as backup_file:
            await bot.send_document(
                LOG_CHAT_ID,
                FSInputFile(backup_file, filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"),
                caption="🗄️ Автоматический бэкап базы данных"
            )
        
        # Удаляем временный файл
        import os
        os.remove(backup_path)
    except Exception as e:
        logger.error(f"Ошибка отправки бэкапа: {e}")

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Добавляем пользователя в базу
    await db_manager.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Логируем действие
    await log_user_action(user.id, user.username or "Unknown", "Нажал /start")
    
    if user.id == ADMIN_ID:
        # Админская панель
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить прокси", callback_data="add_proxy")],
            [InlineKeyboardButton(text="📋 Список прокси", callback_data="list_proxies")],
            [InlineKeyboardButton(text="🗑 Удалить прокси", callback_data="delete_proxy")],
            [InlineKeyboardButton(text="📊 Проверить статус всех прокси", callback_data="check_all_proxies")],
            [InlineKeyboardButton(text="💾 Бэкап БД", callback_data="backup_db")],
            [InlineKeyboardButton(text="📥 Восстановить БД", callback_data="restore_db")]
        ])
        
        await message.answer(
            "🔧 <b>Админская панель</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Обычный пользователь
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Получить VLESS ссылку", callback_data="get_vless")]
        ])
        
        await message.answer(
            "👋 <b>Добро пожаловать!</b>\n\n"
            "Этот бот поможет вам получить доступ к прокси-серверам.\n"
            "Нажмите кнопку ниже, чтобы получить VLESS ссылку:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@dp.message(Command("backup_db"))
async def cmd_backup_db(message: types.Message):
    """Ручная команда для бэкапа БД"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    await message.answer("💾 Создаю бэкап базы данных...")
    
    try:
        backup_path = await db_manager.backup_database()
        
        with open(backup_path, 'rb') as backup_file:
            await message.answer_document(
                FSInputFile(backup_file, filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"),
                caption="🗄️ Бэкап базы данных создан"
            )
        
        # Удаляем временный файл
        import os
        os.remove(backup_path)
        
        await log_user_action(message.from_user.id, message.from_user.username or "Admin", "Создал бэкап БД")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка создания бэкапа: {e}")

@dp.message(Command("restore_db"))
async def cmd_restore_db(message: types.Message):
    """Ручная команда для восстановления БД"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    await message.answer(
        "📥 <b>Восстановление базы данных</b>\n\n"
        "Отправьте файл базы данных (.db) для восстановления:",
        parse_mode="HTML"
    )
    
    await UserStates.waiting_vless_request.set()

# Обработчики callback-запросов
@dp.callback_query(F.data == "add_proxy")
async def callback_add_proxy(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик добавления прокси"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет прав для выполнения этого действия.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="SOCKS5", callback_data="proxy_type_socks5")],
        [InlineKeyboardButton(text="Shadowsocks", callback_data="proxy_type_shadowsocks")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
    ])
    
    await callback.message.edit_text(
        "➕ <b>Добавление прокси</b>\n\n"
        "Выберите тип прокси:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("proxy_type_"))
async def callback_proxy_type_selected(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора типа прокси"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет прав для выполнения этого действия.")
        return
    
    proxy_type = callback.data.split("_")[2]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data=f"quantity_1_{proxy_type}")],
        [InlineKeyboardButton(text="5", callback_data=f"quantity_5_{proxy_type}")],
        [InlineKeyboardButton(text="10", callback_data=f"quantity_10_{proxy_type}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="add_proxy")]
    ])
    
    await callback.message.edit_text(
        f"➕ <b>Добавление {proxy_type.upper()} прокси</b>\n\n"
        "Выберите количество:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("quantity_"))
async def callback_quantity_selected(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора количества прокси"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет прав для выполнения этого действия.")
        return
    
    parts = callback.data.split("_")
    quantity = int(parts[1])
    proxy_type = parts[2]
    
    await callback.message.edit_text(f"⏳ Создаю {quantity} {proxy_type.upper()} прокси...")
    
    created_count = 0
    for i in range(quantity):
        try:
            proxy_data = await proxy_manager.create_proxy(proxy_type)
            
            await db_manager.add_proxy(
                proxy_type=proxy_data['type'],
                port=proxy_data['port'],
                password=proxy_data['password'],
                process_id=proxy_data['process_id']
            )
            
            created_count += 1
            
        except Exception as e:
            logger.error(f"Ошибка создания прокси {i+1}: {e}")
    
    await callback.message.edit_text(
        f"✅ <b>Прокси созданы</b>\n\n"
        f"Создано: {created_count} из {quantity}\n"
        f"Тип: {proxy_type.upper()}",
        parse_mode="HTML"
    )
    
    await log_user_action(
        callback.from_user.id, 
        callback.from_user.username or "Admin", 
        f"Создал {created_count} {proxy_type.upper()} прокси"
    )

@dp.callback_query(F.data == "list_proxies")
async def callback_list_proxies(callback: types.CallbackQuery):
    """Обработчик списка прокси"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет прав для выполнения этого действия.")
        return
    
    proxies = await db_manager.get_all_proxies()
    
    if not proxies:
        await callback.message.edit_text("📋 <b>Список прокси</b>\n\nПрокси не найдены.")
        return
    
    message = "📋 <b>Список прокси</b>\n\n"
    
    for proxy in proxies[:10]:  # Показываем только первые 10
        status_emoji = STATUS_EMOJIS.get(proxy['status'], '❓')
        message += f"{status_emoji} <b>{proxy['proxy_type'].upper()}</b>\n"
        message += f"   Порт: {proxy['port']}\n"
        message += f"   Статус: {proxy['status']}\n"
        message += f"   Создан: {proxy['created_at']}\n\n"
    
    if len(proxies) > 10:
        message += f"... и еще {len(proxies) - 10} прокси"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
    ])
    
    await callback.message.edit_text(
        message,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "check_all_proxies")
async def callback_check_all_proxies(callback: types.CallbackQuery):
    """Обработчик проверки всех прокси"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет прав для выполнения этого действия.")
        return
    
    await callback.message.edit_text("⏳ Проверяю статус всех прокси...")
    
    proxies = await db_manager.get_all_proxies()
    checked_count = 0
    
    for proxy in proxies:
        try:
            status = await proxy_manager.check_proxy_status(
                proxy['proxy_type'],
                proxy['port'],
                proxy['password']
            )
            
            await db_manager.update_proxy_status(proxy['id'], status)
            checked_count += 1
            
        except Exception as e:
            logger.error(f"Ошибка проверки прокси {proxy['id']}: {e}")
    
    await callback.message.edit_text(
        f"✅ <b>Проверка завершена</b>\n\n"
        f"Проверено прокси: {checked_count} из {len(proxies)}",
        parse_mode="HTML"
    )
    
    await log_user_action(
        callback.from_user.id,
        callback.from_user.username or "Admin",
        f"Проверил статус {checked_count} прокси"
    )

@dp.callback_query(F.data == "get_vless")
async def callback_get_vless(callback: types.CallbackQuery):
    """Обработчик получения VLESS ссылки"""
    user_id = callback.from_user.id
    
    # Проверяем, есть ли у пользователя активная сессия
    session = await db_manager.get_user_session(user_id)
    
    if session:
        await callback.message.edit_text(
            f"🔗 <b>Ваша VLESS ссылка</b>\n\n"
            f"<code>{session['vless_url']}</code>\n\n"
            f"Тип прокси: {session['proxy_type'].upper()}\n"
            f"Порт: {session['port']}\n"
            f"Создана: {session['created_at']}",
            parse_mode="HTML"
        )
        return
    
    # Ищем свободный прокси
    free_proxy = await db_manager.get_free_proxy()
    
    if not free_proxy:
        await callback.message.edit_text(
            "❌ <b>Нет доступных прокси</b>\n\n"
            "В данный момент все прокси заняты. Попробуйте позже.",
            parse_mode="HTML"
        )
        return
    
    # Создаем VLESS ссылку
    user_uuid = str(uuid.uuid4())
    vless_url = proxy_manager.create_vless_url(
        free_proxy['proxy_type'],
        free_proxy['port'],
        free_proxy['password'],
        user_uuid
    )
    
    # Создаем пользовательскую сессию
    await db_manager.create_user_session(user_id, free_proxy['id'], vless_url)
    
    # Обновляем статус прокси на "активный"
    await db_manager.update_proxy_status(free_proxy['id'], 'active')
    
    await callback.message.edit_text(
        f"🔗 <b>Ваша VLESS ссылка</b>\n\n"
        f"<code>{vless_url}</code>\n\n"
        f"Тип прокси: {free_proxy['proxy_type'].upper()}\n"
        f"Порт: {free_proxy['port']}\n"
        f"Создана: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode="HTML"
    )
    
    await log_user_action(
        user_id,
        callback.from_user.username or "Unknown",
        f"Получил VLESS ссылку (прокси {free_proxy['id']})"
    )

@dp.callback_query(F.data == "back_to_admin")
async def callback_back_to_admin(callback: types.CallbackQuery):
    """Возврат в админскую панель"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет прав для выполнения этого действия.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить прокси", callback_data="add_proxy")],
        [InlineKeyboardButton(text="📋 Список прокси", callback_data="list_proxies")],
        [InlineKeyboardButton(text="🗑 Удалить прокси", callback_data="delete_proxy")],
        [InlineKeyboardButton(text="📊 Проверить статус всех прокси", callback_data="check_all_proxies")],
        [InlineKeyboardButton(text="💾 Бэкап БД", callback_data="backup_db")],
        [InlineKeyboardButton(text="📥 Восстановить БД", callback_data="restore_db")]
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Админская панель</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Периодические задачи
async def periodic_tasks():
    """Периодические задачи"""
    while True:
        try:
            # Отправляем статистику каждые 60 минут
            await asyncio.sleep(3600)  # 60 минут
            await send_statistics()
            
            # Отправляем бэкап каждые 30 минут
            await asyncio.sleep(1800)  # 30 минут
            await send_database_backup()
            
        except Exception as e:
            logger.error(f"Ошибка в периодических задачах: {e}")

async def main():
    """Главная функция"""
    # Показываем определенный IP сервера
    logger.info(f"🌐 IP сервера: {SERVER_IP}")
    
    # Инициализируем базу данных
    await db_manager.init_db()
    
    # Запускаем периодические задачи
    asyncio.create_task(periodic_tasks())
    
    # Запускаем бота
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
