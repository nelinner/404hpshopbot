# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard(user_role: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    kb.add(InlineKeyboardButton(text="🏆 Топ-лист", callback_data="top"))
    kb.add(InlineKeyboardButton(text="🔍 Поиск игры", callback_data="search_game"))
    if user_role == "admin":
        kb.add(InlineKeyboardButton(text="🎮 Начать игру", callback_data="create_lobby"))
        kb.add(InlineKeyboardButton(text="📝 Зарегистрировать матч", callback_data="register_match"))
        kb.add(InlineKeyboardButton(text="⚠️ Проверка жалоб", callback_data="check_complaints"))
        kb.add(InlineKeyboardButton(text="📢 Опубликовать пост", callback_data="publish_post"))
    else:
        kb.add(InlineKeyboardButton(text="🚨 Подать жалобу", callback_data="complaint"))
    kb.add(InlineKeyboardButton(text="👥 Список администраторов", callback_data="admins"))
    kb.adjust(2, 2, 1)  # примерная раскладка
    return kb.as_markup()

def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder().add(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    ).as_markup()