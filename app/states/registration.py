from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    lang = State()
    name = State()
    phone = State()
    region = State()
