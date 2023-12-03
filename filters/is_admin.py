from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from data.config import ADMINS
import requests


class IsAdmin(BoundFilter):
    print(22)
    async def check(self, message: Message):
        return message.from_user.id in  tuple(i['user_id'] for i in requests.get('http://localhost:8000/bot/admins/get_admin/').json())
