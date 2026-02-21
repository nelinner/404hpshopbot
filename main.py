import telebot
from telebot import types
import time

# Замени 'YOUR_BOT_TOKEN' на токен твоего бота, полученный от @BotFather
TOKEN = '8406682629:AAEfA-7QYFqqp8d7UrQ5cEqrzOWLphzNl2U'
bot = telebot.TeleBot(TOKEN)

# --- Словарь с товарами (цена может быть любой, например, в условных единицах) ---
products = {
    'premium_month': {'name': 'Премиум статус (1 месяц)', 'price': 250},
    'premium_year': {'name': 'Премиум статус (1 год)', 'price': 905},
    'unban': {'name': 'Разбан', 'price': 75},
    'unmute': {'name': 'Размут', 'price': 50}
}

# --- Функция для удаления предыдущего сообщения ---
def delete_previous_message(message):
    try:
        bot.delete_message(message.chat.id, message.message_id - 1)
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}") # Игнорируем, если сообщение уже удалено или слишком старое

# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Удаляем предыдущее сообщение с командой /start, чтобы не засорять чат
    delete_previous_message(message)

    # Создаем клавиатуру главного меню
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_rules = types.InlineKeyboardButton("📜 Регламент магазина", callback_data='rules')
    btn_products = types.InlineKeyboardButton("🛍️ Товары", callback_data='products_main')
    btn_support = types.InlineKeyboardButton("🆘 Тех. поддержка", callback_data='support')
    markup.add(btn_rules, btn_products, btn_support)

    # Текст приветствия
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n"
        f"Добро пожаловать в наш магазин.\n"
        f"Используй кнопки ниже для навигации."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- Обработчик нажатий на инлайн-кнопки (все меню) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Удаляем сообщение с кнопками, на которые нажали (для чистоты чата)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"Не удалось удалить сообщение с инлайн-кнопками: {e}")

    # --- 1. РЕГЛАМЕНТ МАГАЗИНА ---
    if call.data == 'rules':
        markup_back = types.InlineKeyboardMarkup()
        btn_rules2 = types.InlineKeyboardButton("📃 Регламент", callback_data='rules2', url="https://telegra.ph/Reglament-magazina-404hp-shop-02-21")
        btn_back = types.InlineKeyboardButton("🔙 В главное меню", callback_data='back_to_main')
        markup_back.add(btn_rules2, btn_back)

        rules_text = (
            "📜 *Регламент магазина:*\n\n"
            "🤝 Чтобы посмотреть  на регламент магазина нажми на кнопку регламента"
        )
        bot.send_message(call.message.chat.id, rules_text, parse_mode='Markdown', reply_markup=markup_back)

    # --- 2. ГЛАВНОЕ МЕНЮ ТОВАРОВ (Список категорий) ---
    elif call.data == 'products_main':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_month = types.InlineKeyboardButton("🥇 Премиум (1 месяц)", callback_data='buy_premium_month')
        btn_year = types.InlineKeyboardButton("🏆 Премиум (1 год)", callback_data='buy_premium_year')
        btn_unban = types.InlineKeyboardButton("🔨 Разбан", callback_data='buy_unban')
        btn_unmute = types.InlineKeyboardButton("🤐 Размут", callback_data='buy_unmute')
        btn_back = types.InlineKeyboardButton("🔙 В главное меню", callback_data='back_to_main')
        markup.add(btn_month, btn_year, btn_unban, btn_unmute, btn_back)

        bot.send_message(call.message.chat.id, "🛍️ *Выберите товар для покупки:*", parse_mode='Markdown', reply_markup=markup)

    # --- 3. ОБРАБОТКА ПОКУПКИ КАЖДОГО ТОВАРА ---
    elif call.data.startswith('buy_'):
        product_key = call.data.replace('buy_', '')
        product = products.get(product_key)

        if product:
            markup_pay = types.InlineKeyboardMarkup()
            # Кнопка "Оплатить" (имитация оплаты)
            btn_confirm = types.InlineKeyboardButton(f"✅ Оплатить {product['price']} руб.", callback_data=f'pay_{product_key}')
            btn_back = types.InlineKeyboardButton("🔙 Назад к товарам", callback_data='products_main')
            markup_pay.add(btn_confirm, btn_back)

            buy_text = (
                f"🛒 *Товар:* {product['name']}\n"
                f"💰 *Цена:* {product['price']} руб.\n\n"
                f"Нажмите 'Оплатить' для совершения покупки."
            )
            bot.send_message(call.message.chat.id, buy_text, parse_mode='Markdown', reply_markup=markup_pay)
        else:
            bot.send_message(call.message.chat.id, "Товар не найден.")
# --- 4. ПОДТВЕРЖДЕНИЕ ОПЛАТЫ (Функция покупки) ---
    elif call.data.startswith('pay_'):
        product_key = call.data.replace('pay_', '')
        product = products.get(product_key)

        if product:
            # Здесь должна быть логика проверки платежа, но мы просто имитируем успех
            success_text = (
                f"✅ *Покупка в процессе !*\n\n"
                f"Вы хотите приобрести '{product['name']}'.\n"
                f"Напишите нашим продавцам для оплаты товара @hp404prodv!"
            )
            # Добавляем кнопку возврата в меню
            markup_back = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 В главное меню", callback_data='back_to_main')
            markup_back.add(btn_back)
            bot.send_message(call.message.chat.id, success_text, parse_mode='Markdown', reply_markup=markup_back)
        else:
            bot.send_message(call.message.chat.id, "Ошибка при обработке платежа.")

    # --- 5. ТЕХНИЧЕСКАЯ ПОДДЕРЖКА (Контакты админов и описание) ---
    elif call.data == 'support':
        markup = types.InlineKeyboardMarkup(row_width=1)
        # Кнопки связи с продавцами (перенаправляем в раздел "Контакты продавцов")
        btn_contact_seller = types.InlineKeyboardButton("👤 Связаться с продавцом", callback_data='seller_contacts')
        btn_back = types.InlineKeyboardButton("🔙 В главное меню", callback_data='back_to_main')
        markup.add(btn_contact_seller, btn_back)

        support_text = (
            "🆘 *Техническая поддержка*\n\n"
            "📋 *Описание:*\n"
            "Если у вас возникли проблемы с оплатой, получением товара или работой бота, вы можете обратиться к администраторам.\n\n"
            "👮 *Контакты администрации:*\n"
            "• linner: @nelinner\n"
            "• Asquzyy : @asquzyyy\n"
        )
        bot.send_message(call.message.chat.id, support_text, parse_mode='Markdown', reply_markup=markup)

    # --- 6. КОНТАКТЫ ПРОДАВЦОВ ---
    elif call.data == 'seller_contacts':
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Кнопки для связи с продавцами
        btn_seller1 = types.InlineKeyboardButton("linner", url="https://t.me/nelinner")
        btn_seller2 = types.InlineKeyboardButton("Asquzyy ", url="https://t.me/@asquzyyy")
        btn_back = types.InlineKeyboardButton("🔙 Назад", callback_data='support')
        markup.add(btn_seller1, btn_seller2, btn_back)

        contact_text = (
            "👤 *Контакты продавцов*\n\n"
            "Здесь вы можете напрямую связаться с продавцами для уточнения деталей товара, скорости выдачи или особых условий.\n\n"
            "Нажмите на кнопку ниже, чтобы написать продавцу в личные сообщения:"
        )
        bot.send_message(call.message.chat.id, contact_text, parse_mode='Markdown', reply_markup=markup)

    # --- 7. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ ---
    elif call.data == 'back_to_main':
        # Переиспользуем функцию приветствия, чтобы показать главное меню
        # Но нам нужно создать объект message-like для send_welcome
        class Message:
            def __init__(self, chat, from_user, message_id):
                self.chat = chat
                self.from_user = from_user
                self.message_id = message_id

        msg = Message(call.message.chat, call.from_user, call.message.message_id)
        send_welcome(msg)

# --- Запуск бота ---
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
