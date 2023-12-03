from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery
from hashlib import md5
from aiogram.dispatcher import FSMContext
from aiogram.types.chat import ChatActions
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import ContentType
from aiogram import types
import requests
from handlers.user.menu import settings
from states import CategoryState, ProductState
from loader import bot
from loader import dp, db
from filters import IsAdmin
from keyboards.default.markups import *
from aiogram.types import InputFile

basedir = "/home/oqdev/Desktop/vkusdoma"

category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

add_product = '➕ Добавить товар'
delete_category = '🗑️ Удалить категорию'

@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()
    cats = requests.get('http://localhost:8000/bot/category/').json()
    print(cats)
    for cat in cats:

        markup.add(InlineKeyboardButton(
            cat['title'], callback_data=category_cb.new(id=cat['id'], action='view')))

    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category'))

    await message.answer('Настройка категорий:', reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer('Название категории?')
    await CategoryState.title.set()


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):

    category = message.text
    requests.post("http://localhost:8000/bot/category/",{"title":category})

    await state.finish()
    await process_settings(message)
@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict,
                                    state: FSMContext):
    category_idx = callback_data['id']
    print(category_idx)


    products = requests.get(f'http://localhost:8000/bot/product/?cats={category_idx}').json()
    print(products)
    await query.message.delete()
    await query.answer('Все добавленные товары в эту категорию.')
    await state.update_data(category=category_idx)
    await show_products(query.message, products, category_idx)



async def show_products(m, products, category_idx):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for product in products:
        text = f'<b>{product["title"]}</b>\n\n{product["description"]}\n\nЦена: {product["price"]} евро.'

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            '🗑️ Удалить',
            callback_data=product_cb.new(id=product['id'], action='delete')))
        image = product['image']
        image = image.split("media")[-1]
        photo = "/home/oqdev/Desktop/vkusdoma/media/"+image
        await m.answer_photo(photo=InputFile(photo),
                                caption=text,
                                reply_markup=markup)

    markup = ReplyKeyboardMarkup()
    markup.add(add_product)
    markup.add(delete_category)

    await m.answer('Хотите что-нибудь добавить или удалить?',
                   reply_markup=markup)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        print(data)
        if 'category' in data.keys():
            idx = data['category']

            res = requests.delete(f'http://localhost:8000/bot/category/{idx}/')

            await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)

@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):
    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)

    await message.answer('Название?', reply_markup=markup)

@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)

@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    # state.finish()
    # await process_add_product(message)
    await process_cancel(message, state)

@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await ProductState.description.set()
    await message.answer('Описание?', reply_markup=back_markup())



@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.description)
async def process_description_back(message: Message, state: FSMContext):
    await ProductState.title.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить название с <b>{data['title']}</b>?",
                             reply_markup=back_markup())

@dp.message_handler(IsAdmin(), state=ProductState.description)
async def process_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    await ProductState.next()
    await message.answer('Фото?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO,
                    state=ProductState.image)
async def process_image_photo(message: Message, state: FSMContext):
    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = await bot.download_file(file_info.file_path)
    new_filename = f"/media/products/{message.chat.id}_{message.message_id}.jpg"
    with open(basedir + new_filename, 'wb') as new_file:
        new_file.write(downloaded_file.read())

    async with state.proxy() as data:
        data['image'] = new_filename
        data['photo'] = f"{message.chat.id}_{message.message_id}.jpg"

    await ProductState.next()
    await message.answer('Цена?', reply_markup=back_markup())

@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(),
                    state=ProductState.price)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

        title = data['title']
        description = data['description']
        price = data['price']

        await ProductState.next()
        text = f'<b>{title}</b>\n\n{description}\n\nЦена: {price} евро.'


        markup = check_markup()

        await message.answer_photo(photo=InputFile(basedir+data['image']),
                                   caption=text,
                                   reply_markup=markup)

@dp.message_handler(IsAdmin(), text=all_right_message,
                    state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        print(data)
        title = data['title']
        description = data['description']
        image_path = basedir + data['image']
        price = data['price']
        category = data['category']
        # Read the file contents into memory
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        # Create a dictionary with form data
        form_data = {
            'title': title,
            'description': description,
            'price': price,
            'category': category,
            "image": "http://localhost:8000"+data['image']
        }

        # Include the image data in the form data with the correct field name

        # Send the POST request with the correct content type
        res = requests.post("http://localhost:8000/bot/product/", data=form_data)
        

    await state.finish()
    await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)

@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery,
                                          callback_data: dict):
    product_idx = callback_data['id']

    res = requests.delete(f"http://localhost:8000/bot/product/{product_idx}/")
    print(res)
    await query.answer('Удалено!')
    await query.message.delete()

@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):
    await ProductState.price.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить цену с <b>{data['price']}</b>?",
                             reply_markup=back_markup())

@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT,
                    state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):
    if message.text == back_message:

        await ProductState.description.set()

        async with state.proxy() as data:

            await message.answer(f"Изменить описание с <b>{data['description']}</b>?",
                                 reply_markup=back_markup())
    else:

        await message.answer('Вам нужно прислать фото товара.')


@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: types.Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.image.set()
        async with state.proxy() as data:
            await message.answer("Другое изображение?", reply_markup=back_markup())
    else:
        try:
            price = round(float(message.text), 2)
            async with state.proxy() as data:
                data['price'] = price
            await process_price(message, state)
        except ValueError:
            await message.answer('Укажите цену в виде числа!')

@dp.message_handler(IsAdmin(),
                    lambda message: message.text not in [back_message,
                                                         all_right_message],
                    state=ProductState.confirm)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer('Такого варианта не было.')
