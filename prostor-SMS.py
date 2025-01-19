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

def read_config():
    with open('config.txt', 'r') as file:
        config_data = file.readlines()
        bot_token = config_data[0].split('=')[1].strip()
        manager_chat_id = config_data[1].split('=')[1].strip()
    return bot_token, manager_chat_id

# Чтение конфигурации
BOT_TOKEN, MANAGER_CHAT_ID = read_config()


# States
class ClientForm(StatesGroup):
    name = State()
    service = State()
    phone = State()

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
    await state.update_data(name=user_name)
    await state.set_state(ClientForm.service)
    await message.answer(f"Рад познакомиться, {user_name}! Какая услуга вас интересует?")

# Service handler
@dp.message(ClientForm.service)
async def service_handler(message: Message, state: FSMContext):
    service_interest = message.text.strip()
    await state.update_data(service=service_interest)
    await state.set_state(ClientForm.phone)
    await message.answer("Спасибо! Пожалуйста, напишите ваш номер телефона, чтобы наш менеджер мог с вами связаться.")

# Phone handler
@dp.message(ClientForm.phone)
async def phone_handler(message: Message, state: FSMContext):
    phone_number = message.text.strip()
    user_data = await state.get_data()

    # Save phone number and form the client card
    user_data["phone"] = phone_number
    client_card = (
        f"✅ Новая заявка:\n\n"
        f"Имя: {user_data['name']}\n"
        f"Услуга: {user_data['service']}\n"
        f"Телефон: {user_data['phone']}"
    )

    # Send the client card to the manager
    await bot.send_message(MANAGER_CHAT_ID, client_card)

    # Confirm to the user
    await message.answer(
        "Спасибо за информацию! Наш менеджер свяжется с вами в ближайшее время. Хорошего дня!"
    )

    # Clear user state
    await state.clear()

# Main entry point
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
