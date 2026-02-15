import telebot
from telebot import types
import logging

# Токен твоего бота (получи у @BotFather)
TOKEN = '8573515881:AAHAwcQu0nkaR3ZnT_zBndku0iZikFr7azs'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Контакты продавцов и админов (замени на свои)
SELLERS = {
    'seller1': '@nelinner',
    'seller2': '@seller2_username', 
}

ADMINS = {
    'admin1': '@nelinner',
    'admin2': '@admin2_username',
}

# Создание главного меню
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("📞 Контакты"),
        types.KeyboardButton("🛒 Каталог товаров"),
        types.KeyboardButton("🆘 Поддержка")
    ]
    keyboard.add(*buttons)
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 Привет,Ты находишься в магазине 404hp faceit {user_name}!\n\n"
        "Добро пожаловать в наш магазин премиум-услуг!\n"
        "Здесь ты можешь приобрести:\n"
        ""— ✨ Премиум статус\n"
        "— 🔓 Разбан аккаунта\n"
        "— 🔇 Снятие мута\n\n"
        "Выбери нужный раздел в меню ниже:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

# Обработчик кнопки "Контакты"
@bot.message_handler(func=lambda message: message.text == "📞 Контакты")
def contacts_command(message):
    contacts_text = (
        "📞 *Контакты продавцов:*\n\n"
        f"👤 linner: Продавец по отделам Разбан/размут/покупки  премиум"
        f"👤 Asquzyy: Продавец по отделам Разбан/размут/покупки премиум "       
        "💬 По всем вопросам обращайтесь к нашим продавцам!"
    )
    
    # Создаем инлайн кнопки
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопки для связи с продавцами
    btn1 = types.InlineKeyboardButton(
        text="📱 Связаться с linner", 
        url=f"https://t.me/nelinner"
    )
    btn2 = types.InlineKeyboardButton(
        text="📱 Связаться с Asquzyy ", 
        url=f"https://t.me/asquzyyy"
    )
    
    btn_back = types.InlineKeyboardButton(
        text="🔙 В главное меню", 
        callback_data="back_to_main"
    )
    
    keyboard.add(btn1, btn2, btn_back)
    
    bot.send_message(
        message.chat.id, 
        contacts_text, 
        parse_mode="Markdown", 
        reply_markup=keyboard
    )

# Обработчик кнопки "Каталог товаров"
@bot.message_handler(func=lambda message: message.text == "🛒 Каталог товаров")
def catalog_command(message):
    catalog_text = (
        "🛒 *Наш каталог товаров:*\n\n"
        "Выберите интересующую услугу:"
    )
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    btn_premium = types.InlineKeyboardButton(
        text="⭐️ Премиум статус", 
        callback_data="premium"
    )
    btn_unban = types.InlineKeyboardButton(
        text="🔓 Разбан", 
        callback_data="unban"
    )
    btn_unmute = types.InlineKeyboardButton(
        text="🔇 Размут", 
        callback_data="unmute"
    )
    btn_back = types.InlineKeyboardButton(
        text="🔙 В главное меню", 
        callback_data="back_to_main"
    )
    
    keyboard.add(btn_premium, btn_unban, btn_unmute, btn_back)
    
    bot.send_message(
        message.chat.id, 
        catalog_text, 
        parse_mode="Markdown", 
        reply_markup=keyboard
    )

# Обработчик кнопки "Поддержка"
@bot.message_handler(func=lambda message: message.text == "🆘 Поддержка")
def support_command(message):
    support_text = (
        "🆘 *Служба поддержки*\n\n"
        "По вопросам покупок и техническим проблемам обращайтесь:\n\n"
        f"👨‍💻 Linner: Руководитель  проекта  404hp, также является  продавцом по отделам разбана/размута/покупки премиум"

"👨‍💻 Аsquzyy: Главный администратор  на фей\n"
        "⏰ Время работы: круглосуточно.Если мы не отвечаем то заняты ожидайте  пожалуйста  ответа \n"
        "📝 Опишите вашу проблему - мы поможем!"
    )
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    btn_admin1 = types.InlineKeyboardButton(
        text="💬 Написать админу linner", 
        url=f"https://t.me/nelinner"
    )
    btn_admin2 = types.InlineKeyboardButton(
        text="💬 Написать админу Asquzyy", 
        url=f"https://t.me/asquzyyy"
    )
    btn_back = types.InlineKeyboardButton(
        text="🔙 В главное меню", 
        callback_data="back_to_main"
    )
    
    keyboard.add(btn_admin1, btn_admin2, btn_back)
    
    bot.send_message(
        message.chat.id, 
        support_text, 
        parse_mode="Markdown", 
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "premium":
        text = (
            "⭐️ *Премиум статус на месяц/год*\n\n"
            "🌟 *Преимущества премиум статуса:*\n"
            "• Уникальный значок в профиле\n"
            "• Доступ к эксклюзивным функциям\n"
            "• Приоритетная поддержка\n"
            "• Специальные предложения\n\n"
            "💰 *Цена:* 250 рублей на месяц / 905 на год\n\n"
            "Для покупки свяжитесь с продавцом: "
        )
        
        keyboard = types.InlineKeyboardMarkup()
        btn_buy = types.InlineKeyboardButton(
            text="💳 Купить", 
            url=f"https://t.me/hp404prodv"
        )
        btn_back = types.InlineKeyboardButton(
            text="🔙 Назад к каталогу", 
            callback_data="back_to_catalog"
        )
        keyboard.add(btn_buy, btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    elif call.data == "unban":
        text = (
            "🔓 *Разбан аккаунта*\n\n"
            "📋 *Услуга разблокировки аккаунта:*\n"
            "• Снятие блокировки\n"
            "• Восстановление доступа\n"
            "• Сохранение всех данных\n\n"
            "💰 *Цена:* 75 рублей\n\n"
            "Для заказа напишите продавцу: "
        )
        
        keyboard = types.InlineKeyboardMarkup()
        btn_buy = types.InlineKeyboardButton(
            text="🔓 Заказать разбан", 
            url=f"https://t.me/hp404prodv"
        )
        btn_back = types.InlineKeyboardButton(
            text="🔙 Назад к каталогу", 
            callback_data="back_to_catalog"
        )
        keyboard.add(btn_buy, btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    elif call.data == "unmute":
        text = (
            "🔇 *Снятие мута*\n\n"
            "📋 *Услуга снятия ограничений:*\n"
            "• Снятие мута в чатах\n"
            "• Возврат возможности писать\n"
            "• Быстрое решение проблемы\n\n"
            "💰 *Цена:* 50 рублей\n\n"
            "Для заказа напишите продавцу: "
        )
        
        keyboard = types.InlineKeyboardMarkup()
        btn_buy = types.InlineKeyboardButton(
            text="🔇 Снять мут", 
            url=f"https://t.me/hp404prodv"
        )
        btn_back = types.InlineKeyboardButton(
            text="🔙 Назад к каталогу", 
            callback_data="back_to_catalog"
        )
        keyboard.add(btn_buy, btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,

text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    elif call.data == "back_to_catalog":
        catalog_text = (
            "🛒 *Наш каталог товаров:*\n\n"
            "Выберите интересующую услугу:"
        )
        
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        btn_premium = types.InlineKeyboardButton(text="⭐️ Премиум статус", callback_data="premium")
        btn_unban = types.InlineKeyboardButton(text="🔓 Разбан", callback_data="unban")
        btn_unmute = types.InlineKeyboardButton(text="🔇 Размут", callback_data="unmute")
        btn_back = types.InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")
        keyboard.add(btn_premium, btn_unban, btn_unmute, btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=catalog_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    elif call.data == "back_to_main":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start_command(call.message)

# Обработчик для любых других сообщений
@bot.message_handler(func=lambda message: True)
def other_messages(message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста, используй кнопки меню для навигации.",
        reply_markup=main_keyboard()
    )

# Запуск бота
if name == 'main':
    print("Бот запущен!")
    bot.infinity_polling()
