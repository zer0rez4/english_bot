import asyncio
import sys
import logging
import os
import random

from dotenv import load_dotenv
from translate import Translator

from db_classes import DB

from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

learn_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Новое слово', callback_data='learn')], [InlineKeyboardButton(text='Назад', callback_data='back')]])
back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='back')]])

answer_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Добавить', callback_data='adding_word')], [InlineKeyboardButton(text='Ввести свой перевод', callback_data='another_translate')]])



@dp.message(CommandStart())
async def start(message: Message):
    db = DB('main')
    db.create_new_user(message.from_user.id)
    await message.answer('Добро пожаловать в ELE - лучший бот для изучение английского',  reply_markup=main_kb)
@dp.callback_query(F.data == 'back')
async def main_menu(call: CallbackQuery):
    await call.message.edit_text('Учитесь с удовольствием', reply_markup=main_kb)



#учить (основной функционал)
@dp.callback_query(F.data == 'learn')
async def learn(call: CallbackQuery):
    db = DB('main')
    word, correct_translation, wrong_translations = db.get_random_word_and_translations()
    keyboard = InlineKeyboardBuilder()
    options = [correct_translation] + wrong_translations
    random.shuffle(options)
    for option in options:
        callback_data = f"answer:{option}:{correct_translation}"
        keyboard.button(text=option, callback_data=callback_data)

    await call.message.edit_text(f"Как переводится слово '{word}'?", reply_markup=keyboard.as_markup())

@dp.callback_query(F.data.startswith('answer:'))
async def check_answer(call: CallbackQuery):
    db = DB('main')
    _, user_answer, correct_answer = call.data.split(':')
    #добавить базы данных со стастикой
    if user_answer == correct_answer:
        response_text = "Правильно! Молодец!"
        db.correct_answer(call.from_user.id)
    else:
        response_text = f"Неправильно. Правильный ответ: {correct_answer}"
        db.incorrect_answer(call.from_user.id)
    
    await call.message.edit_text(response_text, reply_markup=learn_kb)



#добавление новых слов в общую базу данных
@dp.callback_query(F.data == 'add_word')
async def check_new_word(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Напишите слово для добавления', reply_markup=back_kb)
    await state.set_state(Form.russian_word)

@dp.message(Form.russian_word)
async def add_word_func(message: Message, state: FSMContext):
    await state.update_data(russian_word=message.text.lower())

    db = DB('main')
    result = db.check_word(word=message.text.lower())[0]
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

