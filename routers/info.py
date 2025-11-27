from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

from config import PELICAN_LAT, PELICAN_LON, PELICAN_ADDRESS, CONTACTS

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("location"))
async def cmd_location(message: types.Message) -> None:
    """Показать локацию на карте"""
    # Отправляем локацию
    await message.answer_location(
        latitude=PELICAN_LAT,
        longitude=PELICAN_LON
    )
    
    # Отправляем информацию с кнопками
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🗺️ Google Maps",
            url=f"https://www.google.com/maps?q={PELICAN_LAT},{PELICAN_LON}"
        )],
        [InlineKeyboardButton(
            text="🗺️ Yandex Maps",
            url=f"https://yandex.ru/maps/?pt={PELICAN_LON},{PELICAN_LAT}&z=15&l=map"
        )],
        [InlineKeyboardButton(
            text="📋 Главное меню",
            callback_data="back_menu"
        )]
    ])
    
    await message.answer(
        f"📍 <b>ЦСО «Пеликан»</b>\n\n"
        f"🗺️ <b>Координаты:</b>\n"
        f"Широта: {PELICAN_LAT}\n"
        f"Долгота: {PELICAN_LON}\n\n"
        f"📍 {PELICAN_ADDRESS}\n\n"
        f"🚗 <b>Как добраться:</b>\n"
        f"• Поездом «Тальго» до ст. Акши (БЕСПЛАТНАЯ встреча)\n"
        f"• Самолётом до аэропорта Урджар (75 км)\n"
        f"• На автомобиле от Алматы (~600 км)\n\n"
        f"📞 При приезде звоните: +7 776 756 00 89",
        reply_markup=markup
    )

@router.message(Command("contacts"))
async def cmd_contacts(message: types.Message) -> None:
    """Показать контакты"""
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📱 WhatsApp",
            url=f"https://wa.me/{CONTACTS['whatsapp'].replace('+', '').replace(' ', '')}"
        )],
        [InlineKeyboardButton(
            text="🌐 Сайт",
            url=CONTACTS['website']
        )],
        [InlineKeyboardButton(
            text="📷 Instagram",
            url=f"https://instagram.com/{CONTACTS['instagram'].replace('@', '')}"
        )],
        [InlineKeyboardButton(
            text="📋 Главное меню",
            callback_data="back_menu"
        )]
    ])
    
    await message.answer(
        f"📞 <b>Контакты ЦСО «Пеликан»</b>\n\n"
        f"📱 <b>WhatsApp:</b> {CONTACTS['whatsapp']}\n\n"
        f"☎️ <b>Телефоны:</b>\n"
        f"• {CONTACTS['phone_1']}\n"
        f"• {CONTACTS['phone_2']}\n\n"
        f"🌐 <b>Сайт:</b> {CONTACTS['website']}\n"
        f"📷 <b>Instagram:</b> {CONTACTS['instagram']}\n\n"
        f"⏰ <b>Время работы:</b> 24/7 (круглосуточно)\n\n"
        f"💬 <b>Забронировать номер:</b>\n"
        f"Используйте кнопку 'Забронировать' в меню\n"
        f"или напишите нам в WhatsApp",
        reply_markup=markup
    )
