TEXTS = {
    "choose_lang": {"uz": "Tilni tanlang:", "ru": "Выберите язык:", "en": "Choose a language:"},
    "ask_name": {"uz": "Ismingizni kiriting:", "ru": "Введите ваше имя:", "en": "Enter your name:"},
    "ask_phone": {
        "uz": "📱 Telefon raqamingizni yuboring (tugma orqali):",
        "ru": "📱 Отправьте номер телефона (через кнопку):",
        "en": "📱 Share your phone number (via button):",
    },
    "ask_region": {
        "uz": "Hududingizni kiriting (yoki ⏭ tashlab keting):",
        "ru": "Введите регион (или ⏭ пропустите):",
        "en": "Enter your region (or ⏭ skip):",
    },
    "registered": {
        "uz": "✅ Ro'yxatdan o'tdingiz! Xush kelibsiz, {name}.",
        "ru": "✅ Регистрация завершена! Добро пожаловать, {name}.",
        "en": "✅ Registered! Welcome, {name}.",
    },
    "main_menu": {
        "uz": "🏠 Bosh menyu. Kerakli bo'limni tanlang:",
        "ru": "🏠 Главное меню. Выберите раздел:",
        "en": "🏠 Main menu. Choose a section:",
    },
    "share_phone_btn": {"uz": "📱 Raqamni yuborish", "ru": "📱 Отправить номер", "en": "📱 Share number"},
    "skip_btn": {"uz": "⏭ Tashlab ketish", "ru": "⏭ Пропустить", "en": "⏭ Skip"},
    "m_catalog": {"uz": "🎭 Senariylar", "ru": "🎭 Сценарии", "en": "🎭 Scenarios"},
    "m_search": {"uz": "🔍 Qidiruv", "ru": "🔍 Поиск", "en": "🔍 Search"},
    "m_cart": {"uz": "🛒 Savatcha", "ru": "🛒 Корзина", "en": "🛒 Cart"},
    "m_purchases": {"uz": "📚 Xaridlarim", "ru": "📚 Покупки", "en": "📚 Purchases"},
    "m_premium": {"uz": "⭐ Premium", "ru": "⭐ Premium", "en": "⭐ Premium"},
    "m_help": {"uz": "📞 Yordam", "ru": "📞 Помощь", "en": "📞 Help"},
    "m_profile": {"uz": "👤 Profil", "ru": "👤 Профиль", "en": "👤 Profile"},
    "categories_title": {
        "uz": "🎭 Kategoriyani tanlang:",
        "ru": "🎭 Выберите категорию:",
        "en": "🎭 Choose a category:",
    },
    "no_scenarios": {
        "uz": "Bu bo'limda hozircha senariy yo'q.",
        "ru": "В этом разделе пока нет сценариев.",
        "en": "No scenarios here yet.",
    },
    "search_prompt": {
        "uz": "🔍 Qidiruv so'zini yuboring (nom yoki bayram nomi):",
        "ru": "🔍 Введите поисковый запрос (название или праздник):",
        "en": "🔍 Send a search query (title or event):",
    },
    "search_empty": {
        "uz": "Hech narsa topilmadi. Boshqa so'z bilan urinib ko'ring.",
        "ru": "Ничего не найдено. Попробуйте другой запрос.",
        "en": "Nothing found. Try another query.",
    },
    "buy_btn": {"uz": "💳 Sotib olish", "ru": "💳 Купить", "en": "💳 Buy"},
    "back_btn": {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"},
    "pages_label": {"uz": "Sahifa", "ru": "Стр.", "en": "Page"},
    "card_pages": {"uz": "📄 Sahifalar", "ru": "📄 Страниц", "en": "📄 Pages"},
    "card_price": {"uz": "💰 Narxi", "ru": "💰 Цена", "en": "💰 Price"},
    "card_rating": {"uz": "⭐ Reyting", "ru": "⭐ Рейтинг", "en": "⭐ Rating"},
    "already_owned": {
        "uz": "✅ Bu senariy sizda bor. 📚 Xaridlarim bo'limidan yuklab oling.",
        "ru": "✅ У вас уже есть этот сценарий. Скачайте в разделе 📚 Покупки.",
        "en": "✅ You already own this. Download it from 📚 Purchases.",
    },
    "invoice_title": {"uz": "Senariy: {title}", "ru": "Сценарий: {title}", "en": "Scenario: {title}"},
    "invoice_desc": {
        "uz": "{title} — to'lovdan so'ng fayl avtomatik yuboriladi.",
        "ru": "{title} — файл будет отправлен сразу после оплаты.",
        "en": "{title} — file is sent automatically after payment.",
    },
    "pay_success": {
        "uz": "✅ To'lov qabul qilindi! Faylingiz yuborilmoqda...",
        "ru": "✅ Оплата принята! Отправляем ваш файл...",
        "en": "✅ Payment received! Sending your file...",
    },
    "purchases_title": {
        "uz": "📚 Sizning xaridlaringiz:",
        "ru": "📚 Ваши покупки:",
        "en": "📚 Your purchases:",
    },
    "purchases_empty": {
        "uz": "Sizda hali xaridlar yo'q. 🎭 Senariylar bo'limiga o'ting.",
        "ru": "У вас пока нет покупок. Откройте 🎭 Сценарии.",
        "en": "No purchases yet. Open 🎭 Scenarios.",
    },
    "download_btn": {"uz": "⬇️ Yuklab olish", "ru": "⬇️ Скачать", "en": "⬇️ Download"},
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    entry = TEXTS.get(key, {})
    text = entry.get(lang) or entry.get("uz") or key
    return text.format(**kwargs) if kwargs else text
