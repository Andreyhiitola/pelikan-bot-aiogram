from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import logging

from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()

class BookingForm(StatesGroup):
    """Состояния для заполнения формы бронирования"""
    waiting_checkin = State()
    waiting_checkout = State()
    waiting_room_type = State()
    waiting_guests_count = State()
    waiting_phone = State()
    waiting_name = State()
    waiting_confirmation = State()

ROOM_TYPES = {
    "econom": "🏠 Эконом (3-6 мест)",
    "bungalo": "🏡 Бунгало (3-6 мест)",
    "standard": "🏢 Стандарт (2-5 мест)",
    "lux": "⭐ Люкс (2-6 мест)"
}

@router.callback_query(F.data == "start_booking")
async def start_booking(query: types.CallbackQuery, state: FSMContext) -> None:
    """Начало процесса бронирования"""
    await state.set_state(BookingForm.waiting_checkin)
    
    # Генерируем даты (следующие 14 дней)
    buttons = []
    today = datetime.now()
    
    for i in range(1, 15):
        date = today + timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y")
        date_callback = date.strftime("%Y-%m-%d")
        
        buttons.append([InlineKeyboardButton(
            text=date_str,
            callback_data=f"checkin_{date_callback}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_booking"
    )])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(
        "📅 <b>Выберите дату заезда:</b>",
        reply_markup=markup
    )
    await query.answer()

@router.callback_query(F.data.startswith("checkin_"))
async def process_checkin_date(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора даты заезда"""
    checkin_date_str = query.data.split("_")[1]
    checkin_date = datetime.strptime(checkin_date_str, "%Y-%m-%d")
    
    await state.update_data(checkin=checkin_date_str)
    await state.set_state(BookingForm.waiting_checkout)
    
    # Генерируем даты выезда (от заезда + 1)
    buttons = []
    
    for i in range(1, 15):
        date = checkin_date + timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y")
        date_callback = date.strftime("%Y-%m-%d")
        
        buttons.append([InlineKeyboardButton(
            text=date_str,
            callback_data=f"checkout_{date_callback}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_booking"
    )])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(
        f"📅 Заезд: <b>{checkin_date.strftime('%d.%m.%Y')}</b>\n\n"
        f"📅 <b>Выберите дату выезда:</b>",
        reply_markup=markup
    )
    await query.answer()

@router.callback_query(F.data.startswith("checkout_"))
async def process_checkout_date(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора даты выезда"""
    checkout_date_str = query.data.split("_")[1]
    
    await state.update_data(checkout=checkout_date_str)
    await state.set_state(BookingForm.waiting_room_type)
    
    # Предлагаем выбрать тип номера
    buttons = []
    for room_key, room_name in ROOM_TYPES.items():
        buttons.append([InlineKeyboardButton(
            text=room_name,
            callback_data=f"room_{room_key}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_booking"
    )])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    data = await state.get_data()
    checkin = datetime.strptime(data['checkin'], "%Y-%m-%d")
    checkout = datetime.strptime(checkout_date_str, "%Y-%m-%d")
    nights = (checkout - checkin).days
    
    await query.message.edit_text(
        f"📅 Заезд: <b>{checkin.strftime('%d.%m.%Y')}</b>\n"
        f"📅 Выезд: <b>{checkout.strftime('%d.%m.%Y')}</b>\n"
        f"🌙 Ночей: <b>{nights}</b>\n\n"
        f"🛏️ <b>Выберите тип номера:</b>",
        reply_markup=markup
    )
    await query.answer()

@router.callback_query(F.data.startswith("room_"))
async def process_room_type(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора типа номера"""
    room_key = query.data.split("_")[1]
    room_name = ROOM_TYPES.get(room_key, "Не выбран")
    
    await state.update_data(room_type=room_name)
    await state.set_state(BookingForm.waiting_guests_count)
    
    # Предлагаем выбрать количество гостей
    buttons = []
    for i in range(1, 7):
        guests_text = f"{i} {'гость' if i == 1 else 'гостя' if i < 5 else 'гостей'}"
        buttons.append([InlineKeyboardButton(
            text=guests_text,
            callback_data=f"guests_{i}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_booking"
    )])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await query.message.edit_text(
        f"🛏️ Тип номера: <b>{room_name}</b>\n\n"
        f"👥 <b>Сколько гостей будет проживать?</b>",
        reply_markup=markup
    )
    await query.answer()

@router.callback_query(F.data.startswith("guests_"))
async def process_guests_count(query: types.CallbackQuery, state: FSMContext) -> None:
    """Обработка количества гостей"""
    guests_count = int(query.data.split("_")[1])
    
    await state.update_data(guests=guests_count)
    await state.set_state(BookingForm.waiting_phone)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel_booking"
        )
    ]])
    
    await query.message.edit_text(
        f"👥 Количество гостей: <b>{guests_count}</b>\n\n"
        f"📱 <b>Введите ваш номер телефона:</b>\n"
        f"Например: +7 776 123 45 67",
        reply_markup=markup
    )
    await query.answer()

@router.message(BookingForm.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext) -> None:
    """Обработка номера телефона"""
    phone = message.text.strip()
    
    if len(phone) < 10:
        await message.answer(
            "❌ Некорректный номер телефона. Попробуйте ещё раз:\n"
            "Например: +7 776 123 45 67"
        )
        return
    
    await state.update_data(phone=phone)
    await state.set_state(BookingForm.waiting_name)
    
    await message.answer(
        f"📱 Телефон: <b>{phone}</b>\n\n"
        f"👤 <b>Введите ваше имя и фамилию:</b>"
    )

@router.message(BookingForm.waiting_name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    """Обработка имени"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите ваше имя:")
        return
    
    await state.update_data(name=name)
    await state.set_state(BookingForm.waiting_confirmation)
    
    # Получаем все данные
    data = await state.get_data()
    
    checkin = datetime.strptime(data['checkin'], "%Y-%m-%d")
    checkout = datetime.strptime(data['checkout'], "%Y-%m-%d")
    nights = (checkout - checkin).days
    
    # Формируем сообщение для подтверждения
    confirmation_text = (
        "📋 <b>Проверьте данные бронирования:</b>\n\n"
        f"👤 Имя: <b>{name}</b>\n"
        f"📱 Телефон: <b>{data['phone']}</b>\n\n"
        f"📅 Заезд: <b>{checkin.strftime('%d.%m.%Y')}</b>\n"
        f"📅 Выезд: <b>{checkout.strftime('%d.%m.%Y')}</b>\n"
        f"🌙 Ночей: <b>{nights}</b>\n\n"
        f"🛏️ Тип номера: <b>{data['room_type']}</b>\n"
        f"👥 Гостей: <b>{data['guests']}</b>\n\n"
        f"Всё верно?"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, отправить", callback_data="confirm_booking"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_booking")
        ]
    ])
    
    await message.answer(confirmation_text, reply_markup=markup)

@router.callback_query(F.data == "confirm_booking")
async def confirm_booking(query: types.CallbackQuery, state: FSMContext) -> None:
    """Подтверждение и отправка заявки"""
    data = await state.get_data()
    
    checkin = datetime.strptime(data['checkin'], "%Y-%m-%d")
    checkout = datetime.strptime(data['checkout'], "%Y-%m-%d")
    nights = (checkout - checkin).days
    
    # Формируем сообщение для администраторов
    admin_message = (
        "🔔 <b>НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ</b>\n\n"
        f"👤 Имя: <b>{data['name']}</b>\n"
        f"📱 Телефон: <b>{data['phone']}</b>\n"
        f"👤 Telegram: @{query.from_user.username or 'не указан'}\n"
        f"🆔 User ID: <code>{query.from_user.id}</code>\n\n"
        f"📅 Заезд: <b>{checkin.strftime('%d.%m.%Y')}</b>\n"
        f"📅 Выезд: <b>{checkout.strftime('%d.%m.%Y')}</b>\n"
        f"🌙 Ночей: <b>{nights}</b>\n\n"
        f"🛏️ Тип номера: <b>{data['room_type']}</b>\n"
        f"👥 Гостей: <b>{data['guests']}</b>"
    )
    
    # Отправляем администраторам
    for admin_id in ADMIN_IDS:
        try:
            await query.bot.send_message(admin_id, admin_message)
            logger.info(f"✅ Заявка отправлена администратору {admin_id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить заявку администратору {admin_id}: {e}")
    
    # Сообщение пользователю
    await query.message.edit_text(
        "✅ <b>Спасибо за заявку!</b>\n\n"
        "Ваша заявка на бронирование отправлена.\n"
        "Наш администратор свяжется с вами в ближайшее время.\n\n"
        "📞 <b>Вы также можете:</b>\n"
        "WhatsApp: +7 776 756 00 89\n"
        "Телефон: +7 (727) 275-00-89\n\n"
        "🏖️ Спасибо за выбор «Пеликана»!"
    )
    
    await state.clear()
    await query.answer("✅ Заявка отправлена!")

@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(query: types.CallbackQuery, state: FSMContext) -> None:
    """Отмена бронирования"""
    await state.clear()
    
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="📋 Главное меню",
            callback_data="back_menu"
        )
    ]])
    
    await query.message.edit_text(
        "❌ <b>Бронирование отменено</b>",
        reply_markup=markup
    )
    await query.answer()

@router.message(Command("book"))
async def cmd_book(message: types.Message, state: FSMContext) -> None:
    """Команда для начала бронирования"""
    await state.set_state(BookingForm.waiting_checkin)
    
    buttons = []
    today = datetime.now()
    
    for i in range(1, 15):
        date = today + timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y")
        date_callback = date.strftime("%Y-%m-%d")
        
        buttons.append([InlineKeyboardButton(
            text=date_str,
            callback_data=f"checkin_{date_callback}"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_booking"
    )])
    
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await message.answer(
        "📅 <b>Выберите дату заезда:</b>",
        reply_markup=markup
    )
