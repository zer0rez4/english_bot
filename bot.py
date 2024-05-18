import asyncio
import sys
import logging
import os

from dotenv import load_dotenv
from translate import Translator

from db_classes import DB

from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

class Form(StatesGroup):
    russian_word = State()
    english_word = State()


#3 кнопки - добавить слово, учить, статистика (личная, общая (топ))
main_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Учить', callback_data='learn')], [InlineKeyboardButton(text='Добавить слово', callback_data='add_word')], [InlineKeyboardButton(text='Статистика', callback_data='stats')]])
stat_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Личная', callback_data='own_stat')], [InlineKeyboardButton(text='Топы', callback_data='users_top')]])
#top_kb = InlineKeyboardMarkup() #прописать топы (по добавленным словам (кто больше добавил), и по правильным ответам и процентом ответов)

back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='back')]])

answer_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Добавить', callback_data='adding_word')], [InlineKeyboardButton(text='Ввести свой перевод', callback_data='another_translate')]])



@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Добро пожаловать в ELE - лучший бот для изучение английского',  reply_markup=main_kb)
@dp.callback_query(F.data == 'back')
async def main_menu(call: CallbackQuery):
    await call.message.edit_text('Учитесь с удовольствием', reply_markup=main_kb)


#учить (основной функционал), прописать логику (выдавание слов)
@dp.callback_query(F.data == 'learn')
async def learn(call: CallbackQuery):
    await call.message.edit_text()




@dp.callback_query(F.data == 'add_word')
async def check_new_word(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Напишите слово для добавления', reply_markup=back_kb)
    await state.set_state(Form.russian_word)

@dp.message(Form.russian_word)
async def add_word_func(message: Message, state: FSMContext):
    await state.update_data(russian_word=message.text.lower())

    db = DB('main')
    result = db.check_word(word=message.text.lower())[0]
    print(result)
    if result:
        await message.answer('Данное слово уже существует в базе', reply_markup=back_kb)
    else:
        tr = Translator(to_lang='en', from_lang='ru')
        result = tr.translate(message.text)
        await message.answer(f'Добавить такой перевод?\n{message.text} - {result}', reply_markup=answer_kb)

@dp.callback_query(F.data == 'another_translate')
async def another_translate(call: CallbackQuery, state: FSMContext):
    await state.set_state(Form.english_word)
    await call.message.edit_text('Введите свой перевод')

@dp.message(Form.english_word)
async def adding_word_changed(message: Message, state: FSMContext):
    await state.update_data(english_word=message.text.lower())
    data = await state.get_data()
    await state.clear()

    db = DB('main')
    db.add_word(data['russian_word'], data['english_word'], message.from_user.id)
    await message.answer(f"Слово {data['english_word']} успешно добавлено", reply_markup=back_kb)

@dp.callback_query(F.data == 'adding_word')
async def adding_word_original(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    tr = Translator(to_lang='en', from_lang='ru')
    result = tr.translate(data['russian_word'])

    db = DB('main')
    db.add_word(data['russian_word'], result, call.from_user.id)
    await call.message.edit_text(f"Слово {result} успешно добавлено", reply_markup=back_kb)




async def main():
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

