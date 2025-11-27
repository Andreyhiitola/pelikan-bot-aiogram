import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import os
import sys

# Импортируем роутеры
from routers.menu import router as menu_router
from routers.booking import router as booking_router
from routers.info import router as info_router
from config import FAQ_DATA

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем токен
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    print("❌ BOT_TOKEN не установлен в .env файле!")
    sys.exit(1)

# Инициализация
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем роутеры
dp.include_router(menu_router)
dp.include_router(booking_router)
dp.include_router(info_router)

async def set_commands():
    """Устанавливает команды бота"""
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="menu", description="📋 FAQ меню"),
        BotCommand(command="book", description="📅 Забронировать номер"),
        BotCommand(command="contacts", description="📞 Контакты"),
        BotCommand(command="location", description="🗺️ Локация"),
        BotCommand(command="help", description="❓ Справка"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Команды установлены")

async def main():
    """Главная функция"""
    logger.info("🤖 Запуск бота Пеликан...")
    await set_commands()
    
    # Удаляем вебхук если есть
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при удалении вебхука: {e}")
    
    logger.info("✅ Бот готов к работе!")
    logger.info(f"📝 Загружено {len(FAQ_DATA)} разделов FAQ")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
