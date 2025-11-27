from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import logging

from config import FAQ_DATA, FAQ_KEYS, ITEMS_PER_PAGE

logger = logging.getLogger(__name__)
router = Router()

def create_menu_markup(page: int = 0) -> InlineKeyboardMarkup:
    """Создаёт меню с пагинацией"""
    buttons = []
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    # Кнопки для этой страницы
    for i in range(start_idx, min(end_idx, len(FAQ_KEYS))):
        buttons.append([InlineKeyboardButton(
            text=FAQ_KEYS[i],
            callback_data=f"faq_{i}"
        )])
    
    # Навигация по страницам
    nav_buttons = []
    total_pages = (len(FAQ_KEYS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"page_{page - 1}"
        ))
    
    nav_buttons.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}",
        callback_data="noop"
    ))
    
    if end_idx < len(FAQ_KEYS):
        nav_buttons.append(InlineKeyboardButton(
            text="Вперед ▶️",
            callback_data=f"page_{page + 1}"
        ))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Кнопки действий
    buttons.append([InlineKeyboardButton(
        text="📅 Забронировать",
        callback_data="start_booking"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """Обработка /start"""
    await state.clear()
    
    markup = create_menu_markup(page=0)
    
    await message.answer(
        f"👋 <b>Добро пожаловать в ЦСО «Пеликан»!</b>\n\n"
        f"Здравствуйте, {message.from_user.first_name}! 🌊\n\n"
        "🏖️ База отдыха на озере Алаколь\n"
        "🌳 5000+ деревьев на территории\n"
        "🏡 Деревянные домики из натурального сруба\n"
        "👨‍👩‍👧 Идеально для семейного отдыха\n\n"
        "📋 Выберите интересующий раздел ⬇️",
        reply_markup=markup
    )

@router.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext) -> None:
    """Команда меню"""
    await state.clear()
    await cmd_start(message, state)

@router.callback_query(F.data.startswith("faq_"))
async def callback_show_faq(query: types.CallbackQuery) -> None:
    """Показывает выбранный раздел FAQ"""
    try:
        item_idx = int(query.data.split("_")[1])
        
        if 0 <= item_idx < len(FAQ_KEYS):
            question_key = FAQ_KEYS[item_idx]
            answer_text = FAQ_DATA[question_key]["text"]
            
            # Кнопка для возврата в меню
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="◀️ Назад в меню",
                    callback_data="back_menu"
                )
            ]])
            
            await query.message.edit_text(
                text=answer_text,
                reply_markup=markup
            )
        
        await query.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback_show_faq: {e}")
        await query.answer("Ошибка!", show_alert=True)

@router.callback_query(F.data.startswith("page_"))
async def callback_change_page(query: types.CallbackQuery) -> None:
    """Переключение страниц"""
    try:
        page_num = int(query.data.split("_")[1])
        total_pages = (len(FAQ_KEYS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = create_menu_markup(page=page_num)
        
        await query.message.edit_text(
            text=f"📋 <b>Выберите интересующий раздел (Страница {page_num + 1}/{total_pages}):</b>",
            reply_markup=markup
        )
        
        await query.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback_change_page: {e}")
        await query.answer("Ошибка!", show_alert=True)

@router.callback_query(F.data == "back_menu")
async def callback_back_menu(query: types.CallbackQuery) -> None:
    """Возврат в меню"""
    try:
        markup = create_menu_markup(page=0)
        
        await query.message.edit_text(
            text="📋 <b>Выберите интересующий раздел:</b>",
            reply_markup=markup
        )
        
        await query.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback_back_menu: {e}")
        await query.answer("Ошибка!", show_alert=True)

@router.callback_query(F.data == "noop")
async def callback_noop(query: types.CallbackQuery) -> None:
    """Пустой callback для кнопки пагинации"""
    await query.answer()

@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Справка"""
    await message.answer(
        "📖 <b>Справка</b>\n\n"
        "/start - главное меню\n"
        "/menu - показать FAQ\n"
        "/book - забронировать номер\n"
        "/location - показать на карте\n"
        "/contacts - контакты\n"
        "/help - этот текст\n\n"
        "📞 <b>Контакты для бронирования:</b>\n"
        "WhatsApp: +7 776 756 00 89\n"
        "Телефон: +7 (727) 275-00-89\n\n"
        "🌐 Сайт: https://pelican-alacol.ru"
    )

@router.message()
async def handle_unknown_message(message: types.Message) -> None:
    """Обработка неизвестных сообщений"""
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📋 Показать меню",
            callback_data="back_menu"
        )
    ]])
    
    await message.answer(
        "🤔 Не понимаю вашего вопроса.\n\n"
        "Пожалуйста, выберите интересующий раздел из меню.",
        reply_markup=markup
    )
