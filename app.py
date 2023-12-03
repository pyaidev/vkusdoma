from aiogram import types
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram import executor
from logging import basicConfig, INFO
from aiogram.types import BotCommand
from data.config import ADMINS,DEFAULT_ADMINS
from handlers.user.catalog import process_catalog
from loader import db, bot
import handlers, requests
from handlers import dp
from handlers.user.menu import catalog, cart, delivery_status


user_message = 'Пользователь'
admin_message = 'Админ'
menu = 'Начать покупки'




@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    print(message.chat.id)
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id in DEFAULT_ADMINS:

        markup.row(user_message, admin_message)
    else:
        markup.row(menu)

    await message.answer('''Привет! 👋

🤖 Я бот-магазин по подаже товаров любой категории.

🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся 
товары возпользуйтесь командой /menu.

❓ Возникли вопросы? Не проблема! Команда /sos поможет 
связаться с админами, которые постараются как можно быстрее откликнуться.
    ''', reply_markup=markup)



@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):
    status = True
    res = requests.post('http://localhost:8000/bot/admins/', data={'user_id': message.from_user.id, 'status': status})
    await message.answer('Включен админский режим.',
                         reply_markup=ReplyKeyboardRemove())

@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    status = False
    res = requests.post('http://localhost:8000/bot/admins/', data={'user_id': message.from_user.id, 'status': status})
    await message.answer('Включен пользовательский режим.',
                         reply_markup=ReplyKeyboardRemove())

@dp.message_handler(text=menu)
async def menu_handler(message: types.Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(cart)
    markup.add(delivery_status)
    await process_catalog(message)
    await message.answer('Меню каталог', reply_markup=markup)


    # await bot.set_chat_menu_buttons(message.chat.id)


async def set_bot_commands():
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/sos", description="Get sos"),
        BotCommand(command="/menu", description="Open the menu"),
        # Add more commands as needed
    ]

    await bot.set_my_commands(commands)


async def on_startup(dp):
    basicConfig(level=INFO)
    await set_bot_commands()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)




