from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
import asyncio
import logging

# Logging
logging.basicConfig(level=logging.INFO)

# Функция для чтения значений из config.txt
def read_config():
    config = {}
    with open("config.txt", "r") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            config[key] = value
    return config["BOT_TOKEN"], config["MANAGER_CHAT_ID"]

# Чтение значений из config.txt
BOT_TOKEN, MANAGER_CHAT_ID = read_config()

# States
class ClientForm(StatesGroup):
    name = State()
    service = State()

# Initialize bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Start command handler
@dp.message(Command(commands=['start']))
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(ClientForm.name)
    await message.answer("Здравствуйте! Как вас зовут?", reply_markup=types.ReplyKeyboardRemove())

# Name handler
@dp.message(ClientForm.name)
async def name_handler(message: Message, state: FSMContext):
    user_name = message.text.strip()
    user_nickname = message.from_user.username or "(не указан)"
    await state.update_data(name=user_name, nickname=user_nickname)
    await state.set_state(ClientForm.service)
    await message.answer(f"Рад познакомиться, {user_name}! Какая услуга вас интересует и есть ли у вас клиентская база?")

# Service handler
@dp.message(ClientForm.service)
async def service_handler(message: Message, state: FSMContext):
    service_interest = message.text.strip()
    user_data = await state.get_data()

    # Form the client card
    client_card = (
        f"✅ Новая заявка:\n\n"
        f"Имя: {user_data['name']}\n"
        f"Никнейм: @{user_data['nickname']}\n"
        f"Услуга: {service_interest}"
    )

    # Send the client card to the manager
    await bot.send_message(MANAGER_CHAT_ID, client_card)

    # Confirm to the user
    await message.answer(
        "Отлично! Мы уже передали информацию персональный менеджер спешит вам помочь и активировать бонус. А пока вы можете получить доступы для тестирования зарегистрируйтесь на сайте prostor-sms.ru"
    )

    # Clear user state
    await state.clear()

# Main entry point
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
