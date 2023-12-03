import requests
from filters import IsUser
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.types.chat import ChatActions
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types import CallbackQuery
import logging
from aiogram.types import InputFile
from loader import dp, bot
from .menu import cart
from keyboards.inline.products_from_catalog import product_markup
from keyboards.inline.products_from_catalog import product_cb
from states import CheckoutState
from keyboards.default.markups import *
from .menu import *


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):
    cart_data = requests.get('http://localhost:8000/bot/cart/?user_id=' + str(message.chat.id)).json()
    if len(cart_data) == 0:

        await message.answer('Ваша корзина пуста.')

    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data['products'] = {}

        order_cost = 0

        for cart in cart_data:

            product = requests.get('http://localhost:8000/bot/product/' + str(cart['product'])).json()
            if product == None:

                res = requests.delete('http://localhost:8000/bot/cart/' + str(cart['id']) + '/')

            else:
                title = product['title']
                description = product['description']
                image = product['image']
                price = product['price']
                photo = "/Users/nurmuhammad/Downloads/vkusdoma/media/" + image

                order_cost += price

                async with state.proxy() as data:
                    data['products'][cart['id']] = [title, price, cart['quantity']]
                    markup = product_markup(cart['id'], round(cart['quantity'] * price, 2))
                    text = f'<b>{title}</b>\n\n{description}'
                await message.answer_photo(photo=InputFile(photo),
                                           caption=text,
                                           reply_markup=markup)

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('📦 Оформить заказ')

            await message.answer('Перейти к оформлению?',
                                 reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='delete'), state='*')
async def product_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    res = requests.delete('http://localhost:8000/bot/cart/' + str(callback_data['id']) + '/')
    res2 = requests.get('http://localhost:8000/bot/cart/?user_id=' + str(query.message.chat.id)).json()

    await query.answer('Удалено.')
    await query.message.delete()
    if len(res2) == 0:
        markup = ReplyKeyboardMarkup(selective=True)
        markup.add(catalog)
        markup.add(cart)
        markup.add(delivery_status)
        await query.message.answer('Ваша корзина пуста.', reply_markup=markup)
        await state.finish()


@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    answer = ''
    total_price = 0

    async with state.proxy() as data:
        for title, price, count_in_cart in data['products'].values():
            tp = count_in_cart * price
            answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}€\n'
            total_price += tp

    await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}€.',
                         reply_markup=check_markup())


@dp.message_handler(IsUser(),
                    lambda message: message.text not in [all_right_message,
                                                         back_message],
                    state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message,
                    state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message,
                    state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer('Укажите свое имя.',
                         reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):
    async with state.proxy() as data:

        data['name'] = message.text

        if 'address' in data.keys():

            await confirm(message)
            await CheckoutState.confirm.set()

        else:

            await CheckoutState.next()
            await message.answer('Укажите адрес для доставки.',
                                 reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer('Изменить имя с <b>' + data['name'] + '</b>?',
                             reply_markup=back_markup())

    await CheckoutState.name.set()


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text

    await confirm(message)
    await CheckoutState.next()


async def confirm(message):
    await message.answer(
        'Убедитесь, что все правильно оформлено и подтвердите заказ.',
        reply_markup=confirm_markup())


@dp.message_handler(IsUser(),
                    lambda message: message.text not in [confirm_message,
                                                         back_message],
                    state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    await message.reply('Такого варианта не было.')


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    await CheckoutState.address.set()

    async with state.proxy() as data:
        await message.answer('Изменить адрес с <b>' + data['address'] + '</b>?',
                             reply_markup=back_markup())


from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging


@dp.message_handler(IsUser(), text=confirm_message,
                    state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(continue_message, stop_message)

    logging.info('Deal was made.')

    async with state.proxy() as data:
        cid = message.chat.id
        user_id = message.from_user.id
        name = data['name']
        address = data['address']

        order = {
            'user_id': user_id,
            'name': name,
            'adress': address,

        }
        res = requests.post('http://localhost:8000/bot/order/', data=order)
        await message.answer(
            f'Ок! Ваш заказ №{res.text} принят, будет сделан и доставлен, после согласования с вами 📱\nИмя: <b>' + data[
                'name'] + '</b>\nАдрес: <b>' + data['address'] + '</b>',
            reply_markup=markup)

    await state.finish()
