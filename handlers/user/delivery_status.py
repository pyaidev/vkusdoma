from aiogram.types import Message
from loader import dp, db
from .menu import delivery_status
from filters import IsUser
import requests


@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):
    print(123456789,'salom')
    orders = requests.get(f'http://localhost:8000/bot/order/{message.from_user.id}/get_order/').json()

    if len(orders) == 0:
        await message.answer('У вас нет активных заказов.')
    else:
        await delivery_status_answer(message, orders)

async def delivery_status_answer(message, orders):
    res = ''

    for order in orders:
        res += f'Заказ <b>№{order["id"]}  {order["name"]}</b>'
        answer = [
            f' status {order["is_finished"]}.',
            ' доставка'
        ]

        res += answer[0]
        res += '\n\n'

    await message.answer(res)
