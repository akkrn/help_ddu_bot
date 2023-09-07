import time

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from fsm_settings import AskMode, DefectsCalculation, PenaltyCalculation
from lexicon.lexicon import LEXICON_RU
from loader import db
from utils import create_inline_kb

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    keyboard = create_inline_kb(
        1,
        "penalty_button",
        "defects_button",
        "ask_button",
    )
    await message.answer(text=LEXICON_RU["/start"], reply_markup=keyboard)


@router.callback_query(
    F.data.in_(
        [
            "penalty_button",
            "defects_button",
            "ask_button",
        ]
    )
)
async def process_start_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data == "penalty_button":
        await callback.message.edit_text(
            text=LEXICON_RU["penalty_start_date1"]
        )
        time.sleep(1)
        await callback.message.answer(text=LEXICON_RU["penalty_start_date2"])
        time.sleep(2)
        await callback.message.answer(text=LEXICON_RU["penalty_start_date3"])
        await state.set_state(PenaltyCalculation.start_date)
    elif callback.data == "defects_button":
        await callback.message.edit_text(text=LEXICON_RU["defects_text"])
        await state.set_state(DefectsCalculation.start)
    elif callback.data == "ask_button":
        await callback.message.edit_text(text=LEXICON_RU["ask_text"])
        await state.set_state(AskMode.start)


@router.message(Command(commands="cancel"), StateFilter(default_state))
async def process_cancel_command(message: Message):
    keyboard = create_inline_kb(
        1,
        LEXICON_RU["penalty_button"],
        LEXICON_RU["defects_button"],
        LEXICON_RU["ask_button"],
    )
    bot_message = await message.answer(
        text=LEXICON_RU["/cancel_in_default_state"], reply_markup=keyboard
    )
    time.sleep(4)
    await message.delete()
    await bot_message.delete()


@router.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    keyboard = create_inline_kb(
        1,
        LEXICON_RU["penalty_button"],
        LEXICON_RU["defects_button"],
        LEXICON_RU["ask_button"],
    )
    bot_message = await message.answer(
        text=LEXICON_RU["/cancel"], reply_markup=keyboard
    )
    await state.clear()
    time.sleep(4)
    await message.delete()
    await bot_message.delete()


@router.message(Command(commands="help"), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.edit_text(text=LEXICON_RU["/help"])


@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    bot_message = await message.answer(
        text=f"{LEXICON_RU['message_warning']}\n"
        f"{LEXICON_RU['cancel_call']}"
    )
    time.sleep(4)
    await message.delete()
    await bot_message.delete()
