from aiogram import Router, F, types, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
import asyncio
import app.keyboards as kb
from app.currency_rate import usd_rate

router = Router()
class Enter(StatesGroup):
    up_bolder = State()
    down_bolder = State()

# Глобальная переменная для хранения границ и chat_id
current_borders = {"up_bolder": None, "down_bolder": None, "chat_id": None}

last_n = {"rate": None, "status": None}

# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!', reply_markup=kb.main)

@router.message(F.text == 'Текуший курс $')
async def cmd_rate(message: Message):
    await message.answer(f"Текущий курс доллара: {usd_rate}")

# Команда /help
@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.reply('Что надо?')

# Обработка кнопки "Ввод границ"
@router.message(F.text == 'Ввод границ')
async def up_enter(message: Message, state: FSMContext):
    await state.set_state(Enter.up_bolder)
    await message.answer('Введите значение верхней границы оповещения')

# Обработка ввода верхней границы
@router.message(Enter.up_bolder)
async def bolder_enter_up(message: Message, state: FSMContext):
    await state.update_data(up_bolder=message.text)
    await state.set_state(Enter.down_bolder)
    await message.answer('Введите значение нижней границы оповещения')

# Обработка ввода нижней границы
@router.message(Enter.down_bolder)
async def bolder_enter_down(message: Message, state: FSMContext):
    await state.update_data(down_bolder=message.text)
    data = await state.get_data()
    global current_borders
    current_borders["up_bolder"] = data["up_bolder"]
    current_borders["down_bolder"] = data["down_bolder"]
    current_borders["chat_id"] = message.chat.id
    await message.answer(f'Установленая верхняя граница: {data["up_bolder"]}\nУстановленая нижняя граница: {data["down_bolder"]}')
    await state.clear()

# Обработка кнопки "Текущие границы"
@router.message(F.text == 'Текущие границы')
async def show_current_borders(message: Message):
    if current_borders["up_bolder"] is None or current_borders["down_bolder"] is None:
        await message.answer("Границы не установлены.")
    else:
        await message.answer(f'Текущие границы:\nВерхняя граница: {current_borders["up_bolder"]}\nНижняя граница: {current_borders["down_bolder"]}')

# Функция для проверки курса доллара
async def check_rate_with_bounds(bot: Bot):
    global last_n
    while True:
        if current_borders["up_bolder"] is not None and current_borders["down_bolder"] is not None:
            rate = usd_rate
            # Проверяем, изменился ли курс и вышел ли он за границы
            if rate < current_borders["down_bolder"]:
                if last_n["status"] != "below" or last_n["rate"] != rate:
                    await bot.send_message(
                        chat_id=current_borders["chat_id"],
                        text=f"Курс доллара ниже нижней границы: {rate} RUB"
                    )
                    last_n["rate"] = rate
                    last_n["status"] = "below"
            elif rate > current_borders["up_bolder"]:
                if last_n["status"] != "above" or last_n["rate"] != rate:
                    await bot.send_message(
                        chat_id=current_borders["chat_id"],
                        text=f"Курс доллара выше верхней границы: {rate} RUB"
                    )
                    last_n["rate"] = rate
                    last_n["status"] = "above"
            else:
                last_n["rate"] = None
                last_n["status"] = None
        await asyncio.sleep(30)  # Проверка каждые 30 секунд

# Запуск фоновой задачи при старте бота
async def on_startup(bot: Bot):
    asyncio.create_task(check_rate_with_bounds(bot))

# Регистрация обработчика запуска
router.startup.register(on_startup)