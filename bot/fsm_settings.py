from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()


class PenaltyCalculation(StatesGroup):
    start_date = State()
    end_date_choice = State()
    end_date = State()
    object_cost = State()
    confirm_details = State()
    change_details = State()


class DefectsCalculation(StatesGroup):
    start = State()


class AskMode(StatesGroup):
    start = State()
