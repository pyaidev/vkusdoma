from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from keyboards.default.markups import all_right_message, cancel_message, \
    submit_markup
from aiogram.types import Message
from states import SosState
from filters import IsUser
from loader import dp, db
import requests


@dp.message_handler(commands='sos')
async def cmd_sos(message: Message):
    await SosState.question.set()
    await message.answer(
        'В чем суть проблемы? Опишите как можно детальнее'
        ' и администратор обязательно вам ответит.',
        reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=SosState.question)
async def process_question(message: Message, state: FSMContext):
    async with state.proxy()as data:
        data['question'] = message.text
        data['message_id'] = message.message_id
    if message.text == cancel_message:
        await message.answer('Отмена.', reply_markup=ReplyKeyboardRemove())
        await state.finish()

    await message.answer('Убедитесь, что все верно.',
                         reply_markup=submit_markup())
    await SosState.next()

@dp.message_handler(
    lambda message: message.text not in [cancel_message, all_right_message],
    state=SosState.submit)
async def process_price_invalid(message: Message):
    await message.answer('Такого варианта не было.')



@dp.message_handler(text=all_right_message, state=SosState.submit)
async def process_submit(message: Message, state: FSMContext):
    cid = message.chat.id
    
    async with state.proxy() as data:
            res = requests.post('http://localhost:8000/bot/question/',{'question':data['question'],'message_id':data['message_id'],"user_id":int(message.from_user.id)})

    await message.answer('Ваш ответ отправлен администратору!', reply_markup=ReplyKeyboardRemove())
    await state.finish()



@dp.message_handler(text=cancel_message, state=SosState.submit)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Изменить вопрос.', reply_markup=ReplyKeyboardRemove())
    await SosState.question.set()