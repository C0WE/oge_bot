
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


TOKEN = 'TOKEN'


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
