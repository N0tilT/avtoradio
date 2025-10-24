import logging
import time

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
from datetime import datetime
import random
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация точек квеста (теперь без последовательности)
QUEST_POINTS = {
    'МАСЛО': {
        'address': 'Эстер Авто, Сахановское шоссе, 19, Тверь',
        'hint': 'Подсказка: Это слово связано с автомобильным обслуживанием',
        'ad_message': '🌟 Спасибо нашему партнёру «Эстер Авто»!\nСкидка 10% на обслуживание авто для участников квеста. Поспешите, акция до конца ноября!\nТелефон: 61 01 61',
        'photo_path': "Logo_AvtoRadio/EsterAuto.jpg"  # Путь к фото, если есть
    },
    'КАРБОН': {
        'address': 'Карбон 69, бул. Цанова, 6, стр. 1 • этаж 2',
        'hint': 'Подсказка: Название материала, из которого делают спортивные детали',
        'ad_message': 'Спасибо нашему партнеру "Карбон69"\nПо промокоду "фартук в масле оливье" скидка 10% до конца ноября!',
        'photo_path': "Logo_AvtoRadio/Carbon69.jpg"
    },
    'СТРАХОВКА': {
        'address': 'Страховой Дом ВСК, ул. Дмитрия Донского, 37, стр. 1',
        'hint': 'Подсказка: Защита от непредвиденных ситуаций',
        'ad_message': 'Страховой Дом ВСК дарит подарки участникам автоквеста «Территория Авторадио»!\nСкидка 25% на КАСКО и другие популярные продукты добровольного страхования ВСК по промокоду «Автоквест».\nОформите полис со скидкой до 1 декабря 2025 г.: https://www.vsk.ru',
        'photo_path': "Logo_AvtoRadio/ВСК.jpg"
    },
    'ПОЛЕТ': {
        'address': 'Турагенство Взяли_Полетели, ул. Желябова, 28',
        'hint': 'Подсказка: Состояние, когда ты в воздухе',
        'ad_message': 'Туристические агентство Взяли_Полетели https://vk.com/poleteli_tver\nВсегда выгодные цены и профессиональный подбор тура под ваши пожелания!',
        'photo_path': "Logo_AvtoRadio/Турагенство.jpg"
    },
    'АККУМУЛЯТОР': {
        'address': 'Аккумуляторы ТуТ, ул. Маяковского, 31',
        'hint': 'Подсказка: Источник энергии для запуска автомобиля',
        'ad_message': 'Спасибо нашему партнеру "Аккумуляторы ТуТ" https://akbtver.ru\nПо промокоду "Авторадио" каждому покупателю стеклоомывающая жидкость в подарок до конца ноября!',
        'photo_path': "Logo_AvtoRadio/ТуТ.jpg"
    },
    'ЗАРЯДКА': {
        'address': 'Аккумуляторы ТуТ, г. Тверь, б-р Цанова, 12',
        'hint': 'Подсказка: Процесс восстановления энергии',
        'ad_message': 'Спасибо нашему партнеру "Аккумуляторы ТуТ" https://akbtver.ru\nПо промокоду "Авторадио" каждому покупателю стеклоомывающая жидкость в подарок до конца ноября!',
        'photo_path': "Logo_AvtoRadio/ТуТ.jpg"
    },
    'ФИНИШ': {
        'address': 'Кухня & Бар Yellow, бул. Радищева, 47',
        'hint': 'Подсказка: Конечная точка маршрута',
        'ad_message': 'Спасибо нашему партнеру "Кухня & Бар Yellow" https://yellowtver.ru\nПо промокоду «Yellow» каждому гостю скидка 10% на все меню до конца ноября!\n* Не действует на барную карту',
        'photo_path': "Logo_AvtoRadio/Yellow.jpg"
    },
    'СПОРТ': {
        'address': 'Фитнес клуб MAXFIT, проспект Калинина, 21Б',
        'hint': 'Подсказка: Физическая активность для здоровья',
        'ad_message': 'Фитнес клуб MAXFIT по промокоду "АВТОРАДИО" дарит неделю фитнеса для участников квеста!\nФитнес от 1650₽ в мес, Тренажерный зал и групповые, сауна и хаммам, скалодром, массаж, детская комната с воспитателем!\nЗвони: 301-911',
        'photo_path': "Logo_AvtoRadio/MAXFIT.jpg"
    },
    'ДЕТЕЙЛИНГ': {
        'address': 'Детейлинг студия PerfectCar, г. Тверь, ул. Бобкова, 7',
        'hint': 'Подсказка: Тщательный уход за автомобилем',
        'ad_message': 'Детейлинг студия PerfectCar https://pfcartver.ru\nВ Твери - все виды работ по восстановлению и защите лакокрасочного покрытия автомобиля, полировка кузова, бронирование фар, химчистка салона и другие услуги.',
        'photo_path': "Logo_AvtoRadio/ProjectCar.jpg"
    },
    'КУРС': {
        'address': '«Трафмастер», Лучи Твери, Трёхсвятская улица',
        'hint': 'Подсказка: Направление движения',
        'ad_message': 'Спасибо нашему партнёру «Трафмастер»!\nТрафмастер дарит всем участникам квеста бесплатный доступ к продуктам и услугам нашего города - пользуйтесь с удовольствием!\nhttps://vk.com/app5898182_-73763432#s=3381782',
        'photo_path': "Logo_AvtoRadio/ТРАФМАСТЕР.jpg"
    },
    'ЗАПРАВКА': {
        'address': 'Ресторан-бар "Местный", г.Тверь, ул. Дружинная 2, 2 этаж',
        'hint': 'Подсказка: То, что нужно автомобилю и человеку',
        'ad_message': '«Местный» https://vk.com/mestniy_restoran_tver — это рестобар Твери, в сердце спального района Южный, который создан для тех, кто ценит камерную атмосферу, вкусную кухню и душевные посиделки.\nКомплексный обед в «Местном» – всего за 550 ₽!',
        'photo_path': "Logo_AvtoRadio/Местный.jpg"
    },
    'ПЛОЩАДКА': {
        'address': 'Улица Коминтерна, 8 (слева от здания) ',
        'hint': 'Подсказка: Место тренировки в автошколе',
        'ad_message': '',
        'photo_path': ""
    }
}

# Финальное сообщение
FINAL_MESSAGE = """🎉 Поздравляем! Вы собрали все кодовые слова и завершили автоквест «Территория Авторадио»!

🏆 Вы — настоящий герой города!

🤝 Благодарим за участие и всех наших партнеров."""

# Сообщение про IT FEST
IT_FEST_MESSAGE = """📱 Понравился чат-бот? 
Мы научим создавать такой же! 
Хочешь узнать больше? 
Приходи к нам 4 ноября в 12.00 на ТОП IT FEST🙌🏻
Вас ждут увлекательные мастер-классы, захватывающие IT-развлечения, много LEGO и море позитива 🤩 
Регистрируйся скорее🚀:  https://clc.li/GcnDF

Чтобы пройти квест заново, нажмите 'Начать сначала'"""

# Путь к фото для IT FEST
IT_FEST_PHOTO_PATH = "Logo_AvtoRadio/ITtop.jpg"  # Положи файл it_fest.jpg в ту же папку что и бот

# Хранение состояния пользователей
user_states = {}


def get_user_state(user_id):
    """Получить состояние пользователя"""
    if user_id not in user_states:
        user_states[user_id] = {
            'found_words': set(),  # Найденные слова
            'start_time': datetime.now(),
            'finished': False
        }
    return user_states[user_id]


def check_all_words_found(user_id):
    """Проверить, найдены ли все слова"""
    user_state = get_user_state(user_id)
    return len(user_state['found_words']) == len(QUEST_POINTS)


async def send_with_photo(update: Update, photo_path: str, caption: str):
    """Отправить сообщение с фото"""
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=caption)
        else:
            await update.message.reply_text(caption)
    except Exception as e:
        logger.error(f"Error sending photo {photo_path}: {e}")
        await update.message.reply_text(caption)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        user_id = update.effective_user.id
        user_state = get_user_state(user_id)

        # Сброс прогресса
        user_state['found_words'] = set()
        user_state['finished'] = False
        user_state['start_time'] = datetime.now()

        # Создаем клавиатуру с кнопками
        keyboard = [
            [KeyboardButton("Подсказка"), KeyboardButton("Начать сначала")],
            [KeyboardButton("Партнеры"), KeyboardButton("Мой прогресс")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        start_message = """Приветствуем на «Территории Авторадио» — твоём ключе к интересным и драйвовым местам города! 

🎯 Ваша задача: собрать 12 кодовых слов, посещая партнеров Авторадио.

📍 Посещайте точки в любом порядке
🔍 Вводите кодовые слова, которые найдете на местах
🎁 Получайте подарки от партнеров

Введи первое кодовое слово:"""

        await update.message.reply_text(start_message, reply_markup=reply_markup)
        logger.info(f"User {user_id} started the quest")

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте еще раз.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    try:
        user_id = update.effective_user.id
        user_state = get_user_state(user_id)
        text = update.message.text.upper().strip()

        logger.info(f"User {user_id} sent: {text}")

        # Обработка кнопок
        if text == "ПОДСКАЗКА":
            await give_random_hint(update, context)
            return
        elif text == "НАЧАТЬ СНАЧАЛА":
            await start(update, context)
            return
        elif text == "ПАРТНЕРЫ":
            await show_partners(update, context)
            return
        elif text == "МОЙ ПРОГРЕСС":
            await show_progress(update, context)
            return

        # Проверяем, завершен ли квест
        if user_state['finished']:
            await update.message.reply_text(
                "🎉 Вы уже завершили квест! Чтобы пройти заново, нажмите 'Начать сначала'"
            )
            return

        # Нормализуем ввод пользователя для обработки буквы Ё
        normalized_text = text.replace('Ё', 'Е')

        # Проверяем, является ли введенное слово кодовым
        if normalized_text in QUEST_POINTS:
            if normalized_text in user_state['found_words']:
                await update.message.reply_text("✅ Это слово вы уже находили ранее!")
            else:
                # Новое слово найдено!
                user_state['found_words'].add(normalized_text)
                point = QUEST_POINTS[normalized_text]

                # Отправляем информацию о точке с фото
                caption = f"✅ Верно! Вы нашли слово: {normalized_text}\n📍 Адрес: {point['address']}"
                if(len(point['photo_path'])>0):
                    await send_with_photo(update, point['photo_path'], caption)
                else:
                    await update.message.reply_text(caption)

                # Отправляем рекламное сообщение
                if(len(point['ad_message'])>0):
                    await update.message.reply_text(point['ad_message'])

                # Проверяем, завершен ли квест
                if check_all_words_found(user_id):
                    time.sleep(3)
                    user_state['finished'] = True
                    finish_time = datetime.now()
                    duration = finish_time - user_state['start_time']

                    # Отправляем финальное сообщение
                    await update.message.reply_text(FINAL_MESSAGE)

                    # Отправляем IT FEST сообщение с фото
                    await send_with_photo(update, IT_FEST_PHOTO_PATH, IT_FEST_MESSAGE)

                    logger.info(f"User {user_id} finished the quest in {duration}")
                else:
                    remaining = len(QUEST_POINTS) - len(user_state['found_words'])
                    await update.message.reply_text(
                        f"🎯 Отлично! Осталось найти {remaining} слов.\n"
                        f"Продолжайте в том же духе!"
                    )
        else:
            # Неизвестное слово
            await update.message.reply_text(
                "❌ Это слово не из нашего квеста. Попробуйте другое слово или воспользуйтесь подсказкой."
            )

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("Произошла ошибка при обработке сообщения.")


async def give_random_hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдать случайную подсказку для ненайденных слов"""
    try:
        user_id = update.effective_user.id
        user_state = get_user_state(user_id)

        if user_state['finished']:
            await update.message.reply_text("Квест уже завершен!")
            return

        # Находим слова, которые еще не найдены
        found_words = user_state['found_words']
        available_words = [word for word in QUEST_POINTS.keys() if word not in found_words]

        if not available_words:
            await update.message.reply_text("Вы уже нашли все слова!")
            return

        # Выбираем случайное слово для подсказки
        random_word = random.choice(available_words)
        hint = QUEST_POINTS[random_word]['hint']

        await update.message.reply_text(f"💡 {hint}")

    except Exception as e:
        logger.error(f"Error in give_random_hint: {e}")
        await update.message.reply_text("Произошла ошибка при получении подсказки.")


async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать прогресс пользователя"""
    try:
        user_id = update.effective_user.id
        user_state = get_user_state(user_id)

        found_count = len(user_state['found_words'])
        total_count = len(QUEST_POINTS)

        progress_text = f"📊 Ваш прогресс:\n\n"
        progress_text += f"✅ Найдено слов: {found_count}/{total_count}\n"
        progress_text += f"📈 Завершено: {int(found_count / total_count * 100)}%\n\n"

        if found_count > 0:
            progress_text += "🔍 Найденные слова:\n"
            for word in sorted(user_state['found_words']):
                progress_text += f"• {word}\n"

        if found_count < total_count:
            remaining = total_count - found_count
            progress_text += f"\n🎯 Осталось найти: {remaining} слов"

        await update.message.reply_text(progress_text)

    except Exception as e:
        logger.error(f"Error in show_progress: {e}")
        await update.message.reply_text("Произошла ошибка при получении прогресса.")


async def show_partners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать всех партнеров"""
    try:
        partners_text = "🤝 Наши партнеры:\n\n"

        for i, (word, point) in enumerate(QUEST_POINTS.items(), 1):
            lines = point['ad_message'].split('\n')
            partner_name = lines[0] if lines else f"Партнер {i}"
            partners_text += f"• {partner_name}\n"

        partners_text += "\n🔍 Посетите точки партнеров, чтобы найти кодовые слова!"

        await update.message.reply_text(partners_text)
    except Exception as e:
        logger.error(f"Error in show_partners: {e}")
        await update.message.reply_text("Произошла ошибка при получении списка партнеров.")


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс прогресса"""
    await start(update, context)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")

    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте еще раз или начните заново с /start"
            )
    except Exception as e:
        logger.error(f"Error in error_handler: {e}")


def main():
    """Основная функция"""
    try:
        TOKEN = "8062301119:AAEBoNK_RheW97W3weVbp2ARmIl3QKg4BYc"

        application = Application.builder().token(TOKEN).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("restart", restart))
        application.add_handler(CommandHandler("hint", give_random_hint))
        application.add_handler(CommandHandler("partners", show_partners))
        application.add_handler(CommandHandler("progress", show_progress))

        # Обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Обработчик ошибок
        application.add_error_handler(error_handler)

        # Запускаем бота
        print("Бот запущен...")
        application.run_polling()

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Ошибка при запуске бота: {e}")


if __name__ == '__main__':
    main()