from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    language = State()


class Chat(StatesGroup):
    active = State()
