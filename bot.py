import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# =============================================
# НАСТРОЙКИ — ВСТАВЬ СЮДА СВОЙ ТОКЕН
# =============================================
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Твой Telegram ID — чтобы получать предложения от пользователей
# Узнай свой ID написав боту @userinfobot в Telegram
ADMIN_ID = 8462022587  # ← замени на свой ID

# =============================================
# ДАННЫЕ ЛИЦЕЯ (редактируй под себя)
# =============================================

SCHEDULE = {
    # Пн-Чт: начало 08:30, уроки 45 мин, перемены 10 мин (между 2 и 3 — 15 мин)
    # 1: 08:30-09:15 | 2: 09:25-10:10 | перемена 15 мин | 3: 10:25-11:10
    # 4: 11:20-12:05 | 5: 12:15-13:00 | 6: 13:10-13:55 | 7: 14:05-14:50 | 8: 15:00-15:45
    "Понедельник": [
        "1. Кыргызский язык    (08:30 - 09:15)",
        "2. Алгебра            (09:25 - 10:10)",
        "3. Физика             (10:25 - 11:10)",
        "4. Английский язык    (11:20 - 12:05)",
        "5. Д.О.Т              (12:15 - 13:00)",
        "6. Ч.и.О              (14:00 - 14:45)",
        "7. Турецкий язык      (14:55 - 15:40)",
        "8. История            (15:50 - 16:35)",
    ],
    "Вторник": [
        "1. История            (08:30 - 09:15)",
        "2. Химия              (09:25 - 10:10)",
        "3. География          (10:25 - 11:10)",
        "4. Турецкий язык      (11:20 - 12:05)",
        "5. Английский язык    (12:15 - 13:00)",
        "6. Геометрия          (14:00 - 14:45)",
        "7. Литература         (14:55 - 15:40)",
        "8. Кыргыз адабият     (15:50 - 16:35)",
    ],
    "Среда": [
        "1. Физика             (08:30 - 09:15)",
        "2. Литература         (09:25 - 10:10)",
        "3. Информатика        (10:25 - 11:10)",
        "4. Алгебра            (11:20 - 12:05)",
        "5. Английский язык    (12:15 - 13:00)",
        "6. Английский язык    (14:00 - 14:45)",
        "7. Физкульура         (14:55 - 15:40)",
        "8. Турейкий язык      (15:50 - 16:35)",
    ],
    "Четверг": [
        "1. Русский язык       (08:30 - 09:15)",
        "2. География          (09:25 - 10:10)",
        "3. Алгебра            (10:25 - 11:10)",
        "4. Английский язык    (11:20 - 12:05)",
        "5. Кыргызский язык    (12:15 - 13:00)",
        "6. Химия              (14:00 - 14:45)",
        "7. Биология           (14:55 - 15:40)",
        "8. Технология         (15:50 - 16:35)",
    ],
    # Пятница: начало 08:00, уроки 40 мин, перемены 10 мин (между 2 и 3 — 15 мин)
    # 1: 08:00-08:40 | 2: 08:50-09:30 | перемена 15 мин | 3: 09:45-10:25
    # 4: 10:35-11:15 | 5: 11:25-12:05 | 6: 12:15-12:55
    "Пятница": [
        "1. Личностное развитие(08:00 - 08:40)",
        "2. Русский язык       (08:50 - 09:30)",
        "3. Алгебра            (09:40 - 10:20)",
        "4. Английский язык    (10:30 - 11:10)",
        "5. Биология           (11:20 - 12:00)",
        "6. Физкультура        (12:10 - 12:50)",
    ],
}

MENU = {
    "Понедельник": {
        "Завтрак": "Каша овсяная, чай, хлеб с маслом",
        "Обед": "Суп куриный, плов, салат, компот",
        "Ужин": "Картофельное пюре, котлета, чай",
    },
    "Вторник": {
        "Завтрак": "Яичница, чай, хлеб",
        "Обед": "Борщ, макароны с мясом, сок",
        "Ужин": "Рис с овощами, компот",
    },
    "Среда": {
        "Завтрак": "Блины со сметаной, чай",
        "Обед": "Лагман, салат из свежих овощей, компот",
        "Ужин": "Гречка с мясом, чай",
    },
    "Четверг": {
        "Завтрак": "Каша пшённая, какао, хлеб",
        "Обед": "Манты, салат, чай",
        "Ужин": "Картофель жареный, рыба, компот",
    },
    "Пятница": {
        "Завтрак": "Омлет, чай, хлеб с джемом",
        "Обед": "Шурпа, плов, сок",
        "Ужин": "Вермишель с сыром, компот",
    },
    "Суббота": {
        "Завтрак": "Сырники, чай",
        "Обед": "Суп с фрикадельками, рис, салат, компот",
        "Ужин": "—",
    },
    "Воскресенье": {
        "Завтрак": "Каша рисовая, чай",
        "Обед": "Куурдак, салат, компот",
        "Ужин": "Макароны с сыром, чай",
    },
}

TURKISH_WORDS = [
    ("Merhaba", "Привет"),
    ("Teşekkür ederim", "Спасибо"),
    ("Evet", "Да"),
    ("Hayır", "Нет"),
    ("Okul", "Школа"),
    ("Öğretmen", "Учитель"),
    ("Kitap", "Книга"),
    ("Su", "Вода"),
    ("Ekmek", "Хлеб"),
    ("Günaydın", "Доброе утро"),
    ("İyi geceler", "Спокойной ночи"),
    ("Lütfen", "Пожалуйста"),
    ("Özür dilerim", "Извините"),
    ("Anlamıyorum", "Я не понимаю"),
    ("Yardım edin", "Помогите"),
    ("Arkadaş", "Друг"),
    ("Aile", "Семья"),
    ("Şehir", "Город"),
    ("Ülke", "Страна"),
    ("Kütüphane", "Библиотека"),
]

ANNOUNCEMENTS = [
    "📢 Олимпиада по математике — 10 июня в 14:00, актовый зал",
    "📢 Субботник — 7 июня, начало в 09:00",
    "📢 Родительское собрание — 12 июня в 18:00",
    "📢 Экзамены начинаются с 20 июня — готовьтесь!",
    "📢 Запись в кружки на новый учебный год открыта",
]

# =============================================
# СОСТОЯНИЯ ДЛЯ РАСПИСАНИЯ
# =============================================
CHOOSE_DAY = 1

# =============================================
# ЛОГИРОВАНИЕ
# =============================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =============================================
# ГЛАВНОЕ МЕНЮ
# =============================================
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📅 Расписание"), KeyboardButton("🍽️ Меню")],
        [KeyboardButton("📢 Объявления"), KeyboardButton("🇹🇷 Слово дня")],
        [KeyboardButton("ℹ️ О лицее"), KeyboardButton("📞 Контакты")],
        [KeyboardButton("💡 Предложения и пожелания")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def days_keyboard():
    keyboard = [
        [KeyboardButton("Понедельник"), KeyboardButton("Вторник")],
        [KeyboardButton("Среда"), KeyboardButton("Четверг")],
        [KeyboardButton("Пятница")],
        [KeyboardButton("🔙 Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def menu_days_keyboard():
    keyboard = [
        [KeyboardButton("Пн меню"), KeyboardButton("Вт меню"), KeyboardButton("Ср меню")],
        [KeyboardButton("Чт меню"), KeyboardButton("Пт меню"), KeyboardButton("Сб меню")],
        [KeyboardButton("Вс меню"), KeyboardButton("🔙 Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =============================================
# ОБРАБОТЧИКИ
# =============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {name}!\n\n"
        "🏫 Добро пожаловать в бот Турецкого лицея Кыргызстана!\n\n"
        "Здесь ты найдёшь:\n"
        "📅 Расписание уроков\n"
        "🍽️ Меню столовой\n"
        "📢 Объявления\n"
        "🇹🇷 Турецкие слова\n\n"
        "Выбери нужный раздел 👇",
        reply_markup=main_menu_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # --- РАСПИСАНИЕ ---
    if text == "📅 Расписание":
        await update.message.reply_text(
            "📅 Выбери день недели:",
            reply_markup=days_keyboard()
        )

    elif text in SCHEDULE:
        lessons = "\n".join(SCHEDULE[text])
        await update.message.reply_text(
            f"📅 *Расписание — {text}*\n\n{lessons}",
            parse_mode="Markdown",
            reply_markup=days_keyboard()
        )

    # --- МЕНЮ ---
    elif text == "🍽️ Меню":
        await update.message.reply_text(
            "🍽️ Выбери день для меню:",
            reply_markup=menu_days_keyboard()
        )

    elif text in ["Пн меню", "Вт меню", "Ср меню", "Чт меню", "Пт меню", "Сб меню", "Вс меню"]:
        day_map = {
            "Пн меню": "Понедельник",
            "Вт меню": "Вторник",
            "Ср меню": "Среда",
            "Чт меню": "Четверг",
            "Пт меню": "Пятница",
            "Сб меню": "Суббота",
            "Вс меню": "Воскресенье",
        }
        day = day_map[text]
        menu = MENU.get(day, {})
        msg = f"🍽️ *Меню — {day}*\n\n"
        for meal, dish in menu.items():
            msg += f"🕐 *{meal}:* {dish}\n"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=menu_days_keyboard())

    # --- ОБЪЯВЛЕНИЯ ---
    elif text == "📢 Объявления":
        msg = "📢 *Актуальные объявления:*\n\n"
        for ann in ANNOUNCEMENTS:
            msg += f"{ann}\n\n"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    # --- СЛОВО ДНЯ ---
    elif text == "🇹🇷 Слово дня":
        import random
        word, translation = random.choice(TURKISH_WORDS)
        await update.message.reply_text(
            f"🇹🇷 *Турецкое слово дня:*\n\n"
            f"🔤 *{word}*\n"
            f"📖 {translation}\n\n"
            f"_Запомни и используй сегодня!_ 💪",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # --- О ЛИЦЕЕ ---
    elif text == "ℹ️ О лицее":
        await update.message.reply_text(
            "🏫 *Кыргызко Турецкий лицей*\n\n"
            "Один из ведущих лицеев страны с углублённым изучением турецкого и английского языков.\n\n"
            "📌 *Адрес:* г. Каракол, ул. Тыныстанова 28\n"
            "🕐 *Рабочие часы:* 08:00 — 18:00\n"
            "🎯 *Наша цель:* воспитать образованных, многоязычных учеников!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # --- КОНТАКТЫ ---
    elif text == "📞 Контакты":
        await update.message.reply_text(
            "📞 *Контакты лицея:*\n\n"
            "☎️ Телефон: +996 508 356 785\n"
            "📧 Email: HussainKarassaev_highschool@gmail.com\n"
            "📍 Адрес: г. Каракол\n"
            "_По всем вопросам обращайтесь в секретариат._",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # --- ПРЕДЛОЖЕНИЯ ---
    elif text == "💡 Предложения и пожелания":
        context.user_data["waiting_suggestion"] = True
        await update.message.reply_text(
            "💡 *Напиши своё предложение или пожелание!*\n\n"
            "Что хочешь улучшить в боте? Какие функции добавить?\n"
            "Просто напиши текст и отправь 👇\n\n"
            "_(Для отмены нажми кнопку ниже)_",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("❌ Отмена")]],
                resize_keyboard=True
            )
        )

    elif text == "❌ Отмена":
        context.user_data["waiting_suggestion"] = False
        await update.message.reply_text(
            "Главное меню 👇",
            reply_markup=main_menu_keyboard()
        )

    # --- НАЗАД ---
    elif text == "🔙 Назад":
        await update.message.reply_text(
            "Главное меню 👇",
            reply_markup=main_menu_keyboard()
        )

    else:
        if context.user_data.get("waiting_suggestion"):
            context.user_data["waiting_suggestion"] = False
            user = update.effective_user

            # Сохраняем в файл
            with open("suggestions.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[{user.first_name} | @{user.username}]\n{text}\n" + "-"*40 + "\n")

            # Отправляем администратору
            try:
                msg = "Новое предложение!\n\n"
                msg += "От: " + str(user.first_name) + " " + str(user.last_name or "") + "\n"
                msg += "Username: @" + str(user.username or "нет") + "\n"
                msg += "Текст:\n" + text
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

            except Exception:
                pass

            await update.message.reply_text(
                "✅ *Спасибо за твоё предложение!*\n\n"
                "Мы обязательно рассмотрим его и постараемся улучшить бота 🙏",
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "Не понимаю 🤔 Используй кнопки меню.",
                reply_markup=main_menu_keyboard()
            )

# =============================================
# ЗАПУСК БОТА
# =============================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()
