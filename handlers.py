from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from lexicon import ru
from keyboards import reply_keyboard


language = 'ru'
if language == 'ru':
    lex = ru


router = Router()


# /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text=lex['command']['start'],
                         reply_markup=reply_keyboard)


# /help
@router.message(Command(commands=['help']))
async def cmd_help(message: Message):
    await message.answer(text=lex['command']['help'])


# any_text
@router.message(F.text)
async def any_text(message: Message):
    await message.answer(text=lex['text']['any_text'])
