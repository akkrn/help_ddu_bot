from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()


class PenaltyCalculation(StatesGroup):
    StartDate = State()
    CalculationDateChoice = State()
    CalculationDate = State()
    ObjectCost = State()
    ConfirmDetails = State()
