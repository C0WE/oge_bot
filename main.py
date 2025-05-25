# import random
# import aiosqlite
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from aiogram.client.default import DefaultBotProperties
#
# TOKEN = 'TOKEN'
#
#
# class Form(StatesGroup):
#     main_menu = State()
#     video_selection = State()
#     task_selection = State()
#     answer_input = State()
#
#
# async def create_db_connection():
#     return await aiosqlite.connect('bot_oge.db')
#
#
# async def start_bot(bot: Bot):
#     # await bot.send_message(chat_id=ADMIN_ID, text="Бот запущен!")  # Замените ADMIN_ID на ваш ID
#     pass
#
# async def shutdown_bot(bot: Bot):
#     # await bot.send_message(chat_id=ADMIN_ID, text="Бот остановлен!")
#     pass
#
# async def start_handler(message: types.Message, state: FSMContext):
#     builder = InlineKeyboardBuilder()
#     builder.add(
#         types.InlineKeyboardButton(text="🎥 Видео", callback_data="video"),
#         types.InlineKeyboardButton(text="🏋️Задание", callback_data="task")
#     )
#     await message.answer(
#         f"Приветствую, {message.from_user.first_name}!\n"
#         "Я бот-помощник для подготовки к ОГЭ по математике!\n"
#         "Выберите действие:",
#         reply_markup=builder.as_markup()
#     )
#     await state.set_state(Form.main_menu)
#
#
# async def main_menu_callback(callback: types.CallbackQuery, state: FSMContext):
#     if callback.data == "video":
#         await callback.message.edit_text(
#             "Напишите числом номер задания, видео-разбор которого вы хотите посмотреть",
#             reply_markup=None
#         )
#         await state.set_state(Form.video_selection)
#     elif callback.data == "task":
#         await callback.message.edit_text(
#             "Напишите *числом* номер задания",
#             parse_mode="Markdown"
#         )
#         await state.set_state(Form.task_selection)
#     await callback.answer()
#
#
# async def video_handler(message: types.Message, state: FSMContext):
#     number_lesson = message.text.strip().replace('№', '')
#
#     if not number_lesson.isdigit() or not 1 <= int(number_lesson) <= 25:
#         await message.answer('❌ Некорректный номер задания, нужно ввести число от 1 до 25')
#         return await show_main_keyboard(message, state)
#
#     async with await create_db_connection() as db:
#         async with db.execute(
#                 'SELECT * FROM lessons WHERE id = ?',
#                 (number_lesson,)
#         ) as cursor:
#             result = await cursor.fetchall()
#
#     if not result:
#         await message.answer('⚠️ Задание с таким номером не найдено')
#         return await show_main_keyboard(message, state)
#
#     result = random.choice(result)
#     comments = [
#         'Отличный выбор! 👍',
#         'Для лучшего усвоения материала рекомендую конспектировать ✍️',
#         'Думаю, вам это пригодится! ✍️',
#         'Рекомендую повторять за видео! ✍️✍️✍️'
#     ]
#
#     await message.answer(
#         f'*{number_lesson}. {result[1]}*.\n{random.choice(comments)}',
#         parse_mode='Markdown'
#     )
#     await message.answer(result[2])
#
#     await show_main_keyboard(message, state)
#
#
# async def task_handler(message: types.Message, state: FSMContext):
#     number_example = message.text.strip().replace('№', '')
#
#     if not number_example.isdigit() or not 1 <= int(number_example) <= 25:
#         await message.answer('❌ Некорректный номер задания, нужно ввести число от 1 до 25')
#         return await show_main_keyboard(message, state)
#
#     async with await create_db_connection() as db:
#         async with db.execute(
#                 'SELECT * FROM examples WHERE id_example = ?',
#                 (number_example,)
#         ) as cursor:
#             result = await cursor.fetchall()
#
#     if not result:
#         await message.answer('⚠️ Задание с таким номером не найдено')
#         return await show_main_keyboard(message, state)
#
#     result = random.choice(result)
#     await state.update_data(
#         answer=' '.join(result[4].split()),
#         current_task=number_example
#     )
#
#     text = result[2].replace('\n\n', '\n')
#     await message.answer(
#         f"*Задание № {number_example}*\n{text}",
#         parse_mode='Markdown'
#     )
#
#     if result[3] != 'нет':
#         await message.answer_photo(result[3])
#
#     await message.answer(
#         "✍️ Напишите *ответ* на задание. Если ответов несколько, укажите их через *пробел*",
#         parse_mode='Markdown'
#     )
#     await state.set_state(Form.answer_input)
#
#
# async def answer_handler(message: types.Message, state: FSMContext):
#     user_data = await state.get_data()
#     user_answer = ' '.join(message.text.strip().split())
#     correct_answer = user_data.get('answer', '')
#
#     if user_answer == correct_answer:
#         await message.answer(f'✅ Правильно, ответ: {correct_answer}')
#     else:
#         await message.answer(f'🚫 Неправильно, ответ: {correct_answer}')
#
#     await show_main_keyboard(message, state)
#
#
# async def show_main_keyboard(message: types.Message, state: FSMContext):
#     builder = InlineKeyboardBuilder()
#     builder.row(
#         types.InlineKeyboardButton(text="🎥 Видео", callback_data="video"),
#         types.InlineKeyboardButton(text="🏋️Задание", callback_data="task")
#     )
#     builder.row(types.InlineKeyboardButton(text="🛑 Хватит", callback_data="stop"))
#
#     await message.answer(
#         "👇 Выбирайте снова 👇",
#         reply_markup=builder.as_markup()
#     )
#     await state.set_state(Form.main_menu)
#
#
# async def stop_handler(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         f'👋 Всего доброго, {callback.from_user.first_name}!\n'
#         'Если снова захочешь позаниматься нажми /start'
#     )
#     await state.clear()
#     await callback.answer()
#
#
# async def setup_handlers(dp: Dispatcher):
#     dp.startup.register(start_bot)
#     dp.shutdown.register(shutdown_bot)
#
#     dp.message.register(start_handler, Command(commands=['start']))
#
#     dp.callback_query.register(main_menu_callback, Form.main_menu)
#     dp.callback_query.register(stop_handler, F.data == "stop")
#
#     dp.message.register(video_handler, Form.video_selection)
#     dp.message.register(task_handler, Form.task_selection)
#     dp.message.register(answer_handler, Form.answer_input)
#
#
# async def main():
#     # Исправленная инициализация бота
#     bot = Bot(
#         token=TOKEN,
#         default=DefaultBotProperties(parse_mode="Markdown")  # Новый формат
#     )
#     dp = Dispatcher()
#
#     await setup_handlers(dp)
#     await dp.start_polling(bot)
#
# if __name__ == '__main__':
#     import asyncio
#
#     asyncio.run(main())

###################################

# import random
# import aiosqlite
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from aiogram.client.default import DefaultBotProperties
#
# TOKEN = '7999210390:AAHu1TU-NRWrcFXHq305GmchA8Bc4BK8t2E'
# # ADMIN_ID = 123456789  # Замените на ваш ID или удалите
#
#
# class Form(StatesGroup):
#     MAIN_MENU = State()
#     VIDEO_SELECTION = State()
#     TASK_SELECTION = State()
#     ANSWER_INPUT = State()
#
#
# # Инициализация бота
# bot = Bot(
#     token=TOKEN,
#     default=DefaultBotProperties(parse_mode="Markdown")
# )
# dp = Dispatcher()
#
#
# # ========================
# # Клавиатуры
# # ========================
# def main_menu_keyboard():
#     builder = InlineKeyboardBuilder()
#     builder.add(
#         types.InlineKeyboardButton(text="🎥 Видео", callback_data="video"),
#         types.InlineKeyboardButton(text="🏋️ Задание", callback_data="task"),
#         types.InlineKeyboardButton(text="🛑 Хватит", callback_data="stop")
#     )
#     builder.adjust(2)
#     return builder.as_markup()
#
#
# # ========================
# # Обработчики команд
# # ========================
# @dp.message(Command(commands=['start']))
# async def start_handler(message: types.Message, state: FSMContext):
#     await message.answer(
#         f"Приветствую, {message.from_user.first_name}!\n"
#         "Я бот-помощник для подготовки к ОГЭ по математике!\n"
#         "Выберите действие:",
#         reply_markup=main_menu_keyboard()
#     )
#     await state.set_state(Form.MAIN_MENU)
#
#
# # ========================
# # Обработчики колбэков
# # ========================
# @dp.callback_query(F.data == "video", Form.MAIN_MENU)
# async def video_callback(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         "Напишите числом номер задания для просмотра видео-разбора:",
#         reply_markup=None
#     )
#     await state.set_state(Form.VIDEO_SELECTION)
#     await callback.answer()
#
#
# @dp.callback_query(F.data == "task", Form.MAIN_MENU)
# async def task_callback(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         "Напишите *числом* номер задания для тренировки:",
#         parse_mode="Markdown"
#     )
#     await state.set_state(Form.TASK_SELECTION)
#     await callback.answer()
#
#
# @dp.callback_query(F.data == "stop", Form.MAIN_MENU)
# async def stop_callback(callback: types.CallbackQuery, state: FSMContext):
#     await callback.message.edit_text(
#         f"👋 Всего доброго, {callback.from_user.first_name}!\n"
#         "Если захотите продолжить - нажмите /start"
#     )
#     await state.clear()
#     await callback.answer()
#
#
# # ========================
# # Обработчики состояний
# # ========================
# @dp.message(Form.VIDEO_SELECTION)
# async def video_handler(message: types.Message, state: FSMContext):
#     number = message.text.strip()
#
#     if not number.isdigit() or not 1 <= int(number) <= 25:
#         await message.answer("❌ Некорректный номер! Введите число от 1 до 25")
#         return await return_to_menu(message, state)
#
#     try:
#         async with aiosqlite.connect('bot_oge.db') as db:
#             async with db.execute(
#                     "SELECT title, video_url FROM lessons WHERE id = ?",
#                     (int(number),)
#             ) as cursor:
#                 result = await cursor.fetchall()
#
#         if not result:
#             return await message.answer("⚠️ Видео для этого задания не найдено")
#
#         lesson = random.choice(result)
#         await message.answer(f"📹 *Задание {number}: {lesson[0]}*\n{lesson[1]}")
#
#     except Exception as e:
#         await message.answer(f"⚠️ Ошибка: {str(e)}")
#
#     await return_to_menu(message, state)
#
#
# @dp.message(Form.TASK_SELECTION)
# async def task_handler(message: types.Message, state: FSMContext):
#     number = message.text.strip()
#
#     if not number.isdigit() or not 1 <= int(number) <= 25:
#         await message.answer("❌ Некорректный номер! Введите число от 1 до 25")
#         return await return_to_menu(message, state)
#
#     try:
#         async with aiosqlite.connect('bot_oge.db') as db:
#             async with db.execute(
#                     """SELECT description, image_url, answers
#                     FROM examples WHERE id_example = ?""",
#                     (int(number),)
#             ) as cursor:
#                 result = await cursor.fetchall()
#
#         if not result:
#             return await message.answer("⚠️ Задание не найдено")
#
#         task = random.choice(result)
#         await state.update_data(correct_answer=task[2])
#
#         await message.answer(f"📝 *Задание {number}*\n{task[0]}")
#         if task[1] and task[1] != 'нет':
#             await message.answer_photo(task[1])
#
#         await message.answer("✍️ Введите ответ(ы) через пробел:")
#         await state.set_state(Form.ANSWER_INPUT)
#
#     except Exception as e:
#         await message.answer(f"⚠️ Ошибка: {str(e)}")
#         await return_to_menu(message, state)
#
#
# @dp.message(Form.ANSWER_INPUT)
# async def answer_handler(message: types.Message, state: FSMContext):
#     user_answer = ' '.join(message.text.strip().split())
#     data = await state.get_data()
#     correct_answer = data.get('correct_answer', '')
#
#     if user_answer == correct_answer:
#         await message.answer(f"✅ Правильно! Ответ: {correct_answer}")
#     else:
#         await message.answer(f"❌ Неверно. Правильный ответ: {correct_answer}")
#
#     await return_to_menu(message, state)
#
#
# # ========================
# # Вспомогательные функции
# # ========================
# async def return_to_menu(message: types.Message, state: FSMContext):
#     await message.answer(
#         "👇 Выберите следующее действие:",
#         reply_markup=main_menu_keyboard()
#     )
#     await state.set_state(Form.MAIN_MENU)
#
#
# # ========================
# # Запуск бота
# # ========================
# async def main():
#     await dp.start_polling(bot)
#
#
# if __name__ == '__main__':
#     import asyncio
#
#     asyncio.run(main())


#########################

import logging
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommand
)




logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


TOKEN = '7590336081:AAFrPhRrFpUYqF6_oA3Z0LoyQEibXg0ueOc'


class Form(StatesGroup):
    MAIN_MENU = State()
    VIDEO_SELECTION = State()
    TASK_SELECTION = State()
    ANSWER_INPUT = State()


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

async def set_main_menu():
    main_menu_commands = [
        BotCommand(command='/start', description='Запустить бота'),
        BotCommand(command='/stop', description='Остановить бота'),
    ]
    await bot.set_my_commands(main_menu_commands)







# ========================
# Клавиатуры
# ========================
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="🎥 Видео", callback_data="video"),
        types.InlineKeyboardButton(text="🏋️ Задание", callback_data="task"),
        types.InlineKeyboardButton(text="🛑 Хватит", callback_data="stop")
    )
    builder.adjust(2)
    return builder.as_markup()


# ========================
# Обработчики команд
# ========================
@dp.message(Command(commands=['start']))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        f"Приветствую, {message.from_user.first_name}!\n"
        "Я бот-помощник для подготовки к ОГЭ по математике!\n"
        "Выберите действие:",
        reply_markup=main_menu_keyboard()
    )
    await state.set_state(Form.MAIN_MENU)


@dp.message(Command(commands=['stop']))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        f"👋 Всего доброго, {message.from_user.first_name}!",
    )
    await state.clear()



# ========================
# Обработчики колбэков
# ========================
@dp.callback_query(F.data == "video", Form.MAIN_MENU)
async def video_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите номер задания для просмотра видео:")
    await state.set_state(Form.VIDEO_SELECTION)
    await callback.answer()


@dp.callback_query(F.data == "task", Form.MAIN_MENU)
async def task_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите номер задания для тренировки:")
    await state.set_state(Form.TASK_SELECTION)
    await callback.answer()


@dp.callback_query(F.data == "stop", Form.MAIN_MENU)
async def stop_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f"👋 Всего доброго, {callback.from_user.first_name}!")
    await state.clear()
    await callback.answer()


# ========================
# Обработчики состояний (адаптированы под ваши таблицы)
# ========================
@dp.message(Form.VIDEO_SELECTION)
async def video_handler(message: types.Message, state: FSMContext):
    try:
        number = int(message.text.strip())
        async with aiosqlite.connect('bot_oge.db') as db:
            async with db.execute(
                    "SELECT name, url_video FROM lessons WHERE id = ?",
                    (number,)
            ) as cursor:
                result = await cursor.fetchone()

        if not result:
            return await message.answer("❌ Видео для этого задания не найдено")

        title, video_url = result
        await message.answer(f"📹 *{title}*\n{video_url}")

    except ValueError:
        await message.answer("🔢 Введите число от 1 до 25")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")

    await return_to_menu(message, state)


@dp.message(Form.TASK_SELECTION)
async def task_handler(message: types.Message, state: FSMContext):

    try:
        number = int(message.text.strip())

        async with aiosqlite.connect('bot_oge.db') as db:
            # Выбираем случайный вариант задания из всех доступных для указанного номера
            async with db.execute(
                    """SELECT example, url_image, answer 
                    FROM examples 
                    WHERE id_example = ? 
                    ORDER BY RANDOM() 
                    LIMIT 1""",
                    (number,)
            ) as cursor:
                result = await cursor.fetchone()




        if not result:
            return await message.answer("❌ Задание не найдено")

        description, image_url, answer = result
        await state.update_data(correct_answer=answer)

        response_text = f"📝 *Задание {number}*\n{description}"
        if image_url and image_url.lower() != "нет":
            await message.answer_photo(image_url, caption=response_text)
        else:
            await message.answer(response_text)

        await message.answer("✍️ Введите ответ(ы) через пробел:")
        await state.set_state(Form.ANSWER_INPUT)

    except ValueError:
        await message.answer("🔢 Введите число от 1 до 25")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
        await return_to_menu(message, state)


@dp.message(Form.ANSWER_INPUT)
async def answer_handler(message: types.Message, state: FSMContext):
    user_answer = ' '.join(message.text.strip().split())
    data = await state.get_data()
    correct_answer = data.get('correct_answer', '')

    if user_answer == correct_answer:
        await message.answer(f"✅ Правильно! Ответ: {correct_answer}")
    else:
        await message.answer(f"❌ Неверно. Правильный ответ: {correct_answer}")

    await return_to_menu(message, state)


# ========================
# Вспомогательные функции
# ========================
async def return_to_menu(message: types.Message, state: FSMContext):
    await message.answer("👇 Выберите действие:", reply_markup=main_menu_keyboard())
    await state.set_state(Form.MAIN_MENU)


# ========================
# Запуск бота
# ========================
async def main():
    await set_main_menu()
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
