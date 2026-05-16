# handlers.py (основные обработчики)
import os
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from sqlalchemy import select, desc, func, update
from database import async_session, User, Lobby, LobbyPlayer, Complaint
from keyboards import main_menu_keyboard, back_button
from config import CHANNEL_ID, ADMIN_IDS

router = Router()

# Временное хранилище ID кастомных эмодзи (замените на реальные)
PREMIUM_EMOJI = {
    "fire": '<tg-emoji emoji-id="5368324170671202286">🔥</tg-emoji>',
    "crown": '<tg-emoji emoji-id="5373144111844569540">👑</tg-emoji>',
    "star": '<tg-emoji emoji-id="5377527538887172654">⭐</tg-emoji>',
    "cool": '<tg-emoji emoji-id="5377711422880940208">🆒</tg-emoji>',
}

# FSM
class Registration(StatesGroup):
    waiting_for_nickname = State()

class ComplaintFSM(StatesGroup):
    waiting_for_id = State()
    waiting_for_reason = State()

class PublishPost(StatesGroup):
    waiting_for_content = State()

class CreateLobby(StatesGroup):
    waiting_for_name = State()
    waiting_for_max_players = State()

class RegisterMatch(StatesGroup):
    waiting_for_photo = State()
    waiting_for_caption = State()

# Вспомогательные функции
async def get_user(telegram_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

async def check_subscription(user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in ("member", "administrator", "creator")
    except:
        return False

async def update_elo_rank(user: User):
    """Вычислить место в топе на основе ELO"""
    async with async_session() as session:
        subq = select(func.count()).where(User.elo > user.elo).scalar_subquery()
        result = await session.execute(select(subq))
        higher = result.scalar()
        return higher + 1

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    # Проверка подписки
    if not await check_subscription(message.from_user.id):
        await message.answer(
            f"{PREMIUM_EMOJI['fire']} Для доступа к боту подпишитесь на канал {CHANNEL_ID}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔔 Подписаться", url=f"https://t.me/{CHANNEL_ID[1:]}")],
                [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
            ])
        )
        return
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("👋 Добро пожаловать! Введите ваш никнейм:")
        await state.set_state(Registration.waiting_for_nickname)
        return
    # Пользователь зарегистрирован
    role = user.role
    # Определим, админ ли он по ID (на случай, если роль не установлена)
    if message.from_user.id in ADMIN_IDS and role != "admin":
        async with async_session() as session:
            await session.execute(update(User).where(User.telegram_id == message.from_user.id).values(role="admin"))
            await session.commit()
        role = "admin"
    await message.answer(
        f"{PREMIUM_EMOJI['crown']} Главное меню:",
        reply_markup=main_menu_keyboard(role)
    )

# Обработчик проверки подписки
@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: types.CallbackQuery, state: FSMContext):
    if await check_subscription(callback.from_user.id):
        user = await get_user(callback.from_user.id)
        if not user:
            await callback.message.edit_text("Введите ваш никнейм:")
            await state.set_state(Registration.waiting_for_nickname)
        else:
            role = user.role
            if callback.from_user.id in ADMIN_IDS and role != "admin":
                async with async_session() as session:
                    await session.execute(update(User).where(User.telegram_id == callback.from_user.id).values(role="admin"))
                    await session.commit()
                role = "admin"
            await callback.message.edit_text(
                f"{PREMIUM_EMOJI['crown']} Главное меню:",
                reply_markup=main_menu_keyboard(role)
            )
    else:
        await callback.answer("Вы ещё не подписаны!", show_alert=True)

# Регистрация ника
@router.message(Registration.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    nickname = message.text.strip()
    if not nickname:
        await message.answer("Никнейм не может быть пустым. Попробуйте снова:")
        return
    async with async_session() as session:
        user = User(telegram_id=message.from_user.id, nickname=nickname,
                    role="admin" if message.from_user.id in ADMIN_IDS else "player")
        session.add(user)
        await session.commit()
    await state.clear()
    role = "admin" if message.from_user.id in ADMIN_IDS else "player"
    await message.answer(
        f"{PREMIUM_EMOJI['star']} Регистрация успешна!",
        reply_markup=main_menu_keyboard(role)
    )

# Главное меню (обработка кнопки "Назад" и возврат в меню)
@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    role = user.role if user else "player"
    await callback.message.edit_text(
        f"{PREMIUM_EMOJI['crown']} Главное меню:",
        reply_markup=main_menu_keyboard(role)
    )

# Профиль
@router.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Сначала зарегистрируйтесь /start")
        return
    kd = user.kills / user.deaths if user.deaths > 0 else user.kills
    rank = await update_elo_rank(user)
    text = (
        f"{PREMIUM_EMOJI['star']} Профиль игрока:\n"
        f"ID: {user.telegram_id}\n"
        f"Nickname: {user.nickname}\n"
        f"K/D: {kd:.2f}\n"
        f"Победы: {user.wins}\n"
        f"Поражения: {user.losses}\n"
        f"Роль: {'👑 Администратор' if user.role=='admin' else '🎮 Игрок'}\n"
        f"Место в топе: #{rank}\n"
        f"ELO: {user.elo:.0f}"
    )
    await callback.message.edit_text(text, reply_markup=back_button())

# Топ-лист
@router.callback_query(F.data == "top")
async def show_top(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(User).order_by(desc(User.elo)).limit(50)
        )
        users = result.scalars().all()
    if not users:
        text = "Топ-лист пуст."
    else:
        lines = [f"{PREMIUM_EMOJI['crown']} Топ-50 игроков:"]
        for i, u in enumerate(users, 1):
            lines.append(f"{i}. {u.nickname} — ELO: {u.elo:.0f}")
        text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=back_button())

# Поиск игры (список лобби)
@router.callback_query(F.data == "search_game")
async def search_game(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(Lobby).where(Lobby.status == "open")
        )
        lobbies = result.scalars().all()
    if not lobbies:
        await callback.message.edit_text(
            "🔍 Нет доступных лобби. Попросите администратора создать игру.",
            reply_markup=back_button()
        )
        return
    kb = InlineKeyboardBuilder()
    for lobby in lobbies:
        kb.add(InlineKeyboardButton(text=f"{lobby.name} (ID:{lobby.id})", callback_data=f"join_lobby_{lobby.id}"))
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    await callback.message.edit_text("Доступные лобби:", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("join_lobby_"))
async def join_lobby(callback: types.CallbackQuery):
    lobby_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    async with async_session() as session:
        # Проверка, не зарегистрирован ли уже
        exists = await session.execute(
            select(LobbyPlayer).where(LobbyPlayer.lobby_id == lobby_id, LobbyPlayer.user_id == user_id)
        )
        if exists.scalar_one_or_none():
            await callback.answer("Вы уже в этом лобби.", show_alert=True)
            return
        # Проверка заполненности
        lobby = await session.get(Lobby, lobby_id)
        count_result = await session.execute(
            select(func.count()).where(LobbyPlayer.lobby_id == lobby_id)
        )
        count = count_result.scalar()
        if count >= lobby.max_players:
            await callback.answer("Лобби заполнено.", show_alert=True)
            return
        session.add(LobbyPlayer(lobby_id=lobby_id, user_id=user_id))
        await session.commit()
    await callback.answer("Вы присоединились к лобби!", show_alert=False)
    await callback.message.edit_reply_markup(reply_markup=back_button())

# Создание лобби (админ)
@router.callback_query(F.data == "create_lobby")
async def start_create_lobby(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    if not user or user.role != "admin":
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    await callback.message.edit_text("Введите название лобби:")
    await state.set_state(CreateLobby.waiting_for_name)

@router.message(CreateLobby.waiting_for_name)
async def lobby_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите максимальное количество игроков (число):")
    await state.set_state(CreateLobby.waiting_for_max_players)

@router.message(CreateLobby.waiting_for_max_players)
async def lobby_max_players(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число:")
        return
    max_p = int(message.text)
    data = await state.get_data()
    async with async_session() as session:
        lobby = Lobby(name=data["name"], creator_id=message.from_user.id, max_players=max_p)
        session.add(lobby)
        await session.commit()
    await state.clear()
    await message.answer(
        f"✅ Лобби \"{data['name']}\" создано! Игроки могут присоединиться через поиск игры.",
        reply_markup=back_button()
    )

# Подать жалобу
@router.callback_query(F.data == "complaint")
async def start_complaint(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите Telegram ID нарушителя:")
    await state.set_state(ComplaintFSM.waiting_for_id)

@router.message(ComplaintFSM.waiting_for_id)
async def complaint_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("ID должен быть числом. Попробуйте снова:")
        return
    against_id = int(message.text)
    async with async_session() as session:
        target = await session.get(User, against_id)
        if not target:
            await message.answer("Пользователь с таким ID не найден в боте.")
            return
    await state.update_data(against_id=against_id)
    await message.answer("Опишите причину жалобы:")
    await state.set_state(ComplaintFSM.waiting_for_reason)

@router.message(ComplaintFSM.waiting_for_reason)
async def complaint_reason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        complaint = Complaint(
            from_user_id=message.from_user.id,
            against_user_id=data["against_id"],
            reason=message.text
        )
        session.add(complaint)
        await session.commit()
    await state.clear()
    await message.answer("🚨 Жалоба отправлена. Администраторы рассмотрят её.", reply_markup=back_button())

# Проверка жалоб (админ)
@router.callback_query(F.data == "check_complaints")
async def check_complaints(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user or user.role != "admin":
        await callback.answer("Нет доступа.", show_alert=True)
        return
    async with async_session() as session:
        result = await session.execute(
            select(Complaint).where(Complaint.status == "pending")
        )
        complaints = result.scalars().all()
    if not complaints:
        await callback.message.edit_text("Нет нерассмотренных жалоб.", reply_markup=back_button())
        return
    # Показываем первую жалобу с кнопками
    complaint = complaints[0]
    from_user = await get_user(complaint.from_user_id)
    against_user = await get_user(complaint.against_user_id)
    text = (
        f"⚠️ Жалоба #{complaint.id}\n"
        f"От: {from_user.nickname if from_user else complaint.from_user_id}\n"
        f"На: {against_user.nickname if against_user else complaint.against_user_id}\n"
        f"Причина: {complaint.reason}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_complaint_{complaint.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_complaint_{complaint.id}")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data.startswith("accept_complaint_"))
async def accept_complaint(callback: types.CallbackQuery):
    complaint_id = int(callback.data.split("_")[-1])
    admin = await get_user(callback.from_user.id)
    async with async_session() as session:
        complaint = await session.get(Complaint, complaint_id)
        if not complaint or complaint.status != "pending":
            await callback.answer("Жалоба уже обработана.", show_alert=True)
            return
        complaint.status = "accepted"
        complaint.resolved_by = callback.from_user.id
        await session.commit()
    # Уведомление отправителю жалобы
    try:
        await bot.send_message(
            complaint.from_user_id,
            f"✅ Ваша жалоба #{complaint.id} была принята администратором {admin.nickname}."
        )
    except:
        pass
    await callback.message.edit_text(
        f"Жалоба #{complaint_id} принята.",
        reply_markup=back_button()
    )

@router.callback_query(F.data.startswith("reject_complaint_"))
async def reject_complaint(callback: types.CallbackQuery):
    complaint_id = int(callback.data.split("_")[-1])
    async with async_session() as session:
        complaint = await session.get(Complaint, complaint_id)
        if not complaint or complaint.status != "pending":
            await callback.answer("Жалоба уже обработана.", show_alert=True)
            return
        await session.delete(complaint)
        await session.commit()
    await callback.message.edit_text(
        f"Жалоба #{complaint_id} отклонена и удалена.",
        reply_markup=back_button()
    )

# Список администраторов
@router.callback_query(F.data == "admins")
async def list_admins(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.role == "admin"))
        admins = result.scalars().all()
    if not admins:
        text = "Список администраторов пуст."
    else:
        lines = [f"{PREMIUM_EMOJI['crown']} Администраторы:"]
        for a in admins:
            lines.append(f"• {a.nickname} (ID: {a.telegram_id})")
        text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=back_button())

# Публикация поста (админ)
@router.callback_query(F.data == "publish_post")
async def publish_post_start(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    if not user or user.role != "admin":
        await callback.answer("Недостаточно прав.", show_alert=True)
        return
    await callback.message.edit_text("📢 Отправьте пост (текст, фото, видео), который хотите опубликовать в канале.")
    await state.set_state(PublishPost.waiting_for_content)

@router.message(PublishPost.waiting_for_content, F.content_type.in_(['text', 'photo', 'video', 'document']))
async def publish_post_forward(message: types.Message, state: FSMContext):
    try:
        await message.copy_to(CHANNEL_ID)
    except Exception as e:
        await message.answer(f"Ошибка при публикации: {e}")
        return
    await state.clear()
    await message.answer(f"{PREMIUM_EMOJI['fire']} Пост опубликован в канале!", reply_markup=back_button())

# Регистрация матча (админ)
@router.callback_query(F.data == "register_match")
async def register_match_start(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    if not user or user.role != "admin":
        await callback.answer("Нет прав.", show_alert=True)
        return
    await callback.message.edit_text("📸 Отправьте фотографию для матча:")
    await state.set_state(RegisterMatch.waiting_for_photo)

@router.message(RegisterMatch.waiting_for_photo, F.photo)
async def match_photo(message: types.Message, state: FSMContext):
    # Сохраняем file_id фотографии
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("Введите подпись к матчу (текст):")
    await state.set_state(RegisterMatch.waiting_for_caption)

@router.message(RegisterMatch.waiting_for_caption)
async def match_caption(message: types.Message, state: FSMContext):
    data = await state.get_data()
    caption = message.text
    # Шаблон оформления
    final_caption = (
        f"{PREMIUM_EMOJI['fire']} МАТЧ ЗАВЕРШЁН {PREMIUM_EMOJI['fire']}\n"
        f"{PREMIUM_EMOJI['star']} Результаты:\n"
        f"{caption}\n\n"
        f"{PREMIUM_EMOJI['cool']} Опубликовано администратором"
    )
    try:
        await bot.send_photo(CHANNEL_ID, data["photo"], caption=final_caption)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        return
    await state.clear()
    await message.answer(f"{PREMIUM_EMOJI['crown']} Матч зарегистрирован и опубликован!", reply_markup=back_button())

# Обработчик неизвестных сообщений в состояниях
@router.message()
async def unknown_message(message: types.Message):
    await message.answer("Используйте команды или кнопки меню.")