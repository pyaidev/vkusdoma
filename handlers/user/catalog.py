from filters import IsUser
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types.chat import ChatActions
from aiogram.types.input_file import InputFile
from keyboards.inline.categories import categories_markup
from .menu import catalog, continue_message, stop_message
from loader import dp, bot
from keyboards.inline.categories import category_cb
import requests


@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=categories_markup())


@dp.message_handler(IsUser(), text=continue_message)
async def process_countinue(message: Message):
    markup = ReplyKeyboardRemove()
    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=categories_markup())
    await message.answer('Выберите категорию', reply_markup=markup)


@dp.message_handler(IsUser(), text=stop_message)
async def process_countinue(message: Message):
    markup = ReplyKeyboardRemove()

    await message.answer('Спасибо за покупку. Ждем вас в следующий раз', reply_markup=markup)


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):
    products = requests.get(f'http://localhost:8000/bot/product/?cats={callback_data["id"]}').json(),

    await query.answer('Все доступные товары.')
    await show_products(query.message, products)


from loader import bot

from keyboards.inline.products_from_cart import product_markup, product_cb


async def show_products(m, products):
    if len(products) == 0:

        await m.answer('Здесь ничего нет 😢')

    else:

        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
        for product in products[0]:
            title = product['title']
            description = product['description']
            image = product['image']
            price = product['price']
            photo = "/Users/nurmuhammad/Downloads/vkusdoma/media/" + image.split('media/')[-1]
            markup = product_markup(product['id'], 1, product['price'])
            text = f"<b>{title}</b>\n\n{description}"

            await m.answer_photo(photo=InputFile(photo),
                                 caption=text,
                                 reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'), state='*')
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'), state='*')
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'), state='*')
@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'), state='*')
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    idx = callback_data['id']
    action = callback_data['action']
    count = int(callback_data['current_count'])
    price = float(callback_data['price'])

    if 'count' == action:
        count = 0
        keyboard = product_markup(idx, count, price)
        await query.message.edit_reply_markup(keyboard)

    elif action == 'add':
        res = requests.post('http://localhost:8000/bot/cart/',
                            {'product': idx, 'quantity': count, 'user_id': query.from_user.id})
        await query.message.edit_caption("Товар добавлен в корзину")
    elif action == 'increase':
        keyboard = product_markup(idx, count + 1, price)
        await query.message.edit_reply_markup(keyboard)
    else:
        keyboard = product_markup(idx, count - 1, price)
        await query.message.edit_reply_markup(keyboard)