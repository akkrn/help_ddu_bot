from aiogram import Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import database
from bot.lexicon.lexicon import LEXICON_RU

router = Router()


@router.message_handler(commands=["start"])
async def on_start(message: types.Message):
    user = await database.get_user(message.from_user.id)
    if not user:
        await database.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    await show_main_menu(message)


async def show_main_menu(message: types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            LEXICON_RU["penalty_button"], callback_data="penalty_button"
        )
    )
    markup.add(
        InlineKeyboardButton(
            LEXICON_RU["defects_button"], callback_data="defects_button"
        )
    )
    markup.add(
        InlineKeyboardButton(
            LEXICON_RU["ask_button"], callback_data="ask_button"
        )
    )
    await message.answer("Выберите действие:", reply_markup=markup)


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    user = await database.get_user(message.from_user.id)
    if not user:
        await database.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    await show_main_menu(message)

    await message.answer(text=LEXICON_RU["/start"])


@router.message(Command(commands="cancel"), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text=LEXICON_RU["/cancel_in_default_state"])


@router.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU["/cancel"])
    await state.clear()


@router.message(Command(commands="menu"), StateFilter(default_state))
async def process_menu_command(message: Message):
    await show
    await message.answer(text=LEXICON_RU["/menu"])


@router.message(Command(commands="help"), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU["/help"])
