import random
import time

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from filters.filters import IsValidCostFilter
from fsm_settings import DefectsCalculation
from handlers.other_handlers import delete_warning
from lexicon.lexicon import CITIES_RU, LEXICON_RU
from loader import db
from utils import convert_to_float, create_inline_kb

router = Router()


async def check_users_input(state: FSMContext):
    user_data = await state.get_data()
    city = user_data.get("city")
    object_name = user_data.get("object_name")
    object_square = user_data.get("object_square")
    return bool(city and object_name and object_square)


async def confirm_changes(message: Message, state: FSMContext):
    keyboard = create_inline_kb(
        2,
        "yes_button",
        "no_button",
    )
    user_data = await state.get_data()
    city = user_data.get("city")
    object_name = user_data.get("object_name")
    object_square = user_data.get("object_square")
    await message.answer(
        text=LEXICON_RU["defects_confirm_details"].format(
            city, object_name, object_square
        ),
        reply_markup=keyboard,
    )
    await state.set_state(DefectsCalculation.confirm_details)


@router.callback_query(
    StateFilter(DefectsCalculation.start), F.data.in_(CITIES_RU)
)
async def process_cities_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "other":
        await callback.message.edit_text(text=LEXICON_RU["input_city"])
        await state.set_state(DefectsCalculation.input_city)
        return
    await state.update_data(city=LEXICON_RU[callback.data])
    if await check_users_input(state):
        await confirm_changes(callback.message, state)
        await callback.message.delete()
        return
    await callback.message.edit_text(text=LEXICON_RU["object_name"])
    await state.set_state(DefectsCalculation.object_name)


@router.message(
    StateFilter(DefectsCalculation.start),
)
async def process_cities_choice_warning(
    message: types.Message, state: FSMContext
):
    await delete_warning(message, LEXICON_RU["penalty_date_choice_warning"])


@router.message(
    StateFilter(DefectsCalculation.input_city),
    F.text.func(lambda message: len(message) <= 25),
)
async def process_city_input(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    if await check_users_input(state):
        await confirm_changes(message, state)
        return
    await message.answer(text=LEXICON_RU["object_name"])
    await state.set_state(DefectsCalculation.object_name)


@router.message(
    StateFilter(DefectsCalculation.input_city),
)
async def process_city_input_warning(
    message: types.Message, state: FSMContext
):
    await delete_warning(message, LEXICON_RU["input_city_warning"])


@router.message(
    StateFilter(DefectsCalculation.object_name),
    F.text.func(lambda message: len(message) <= 50),
)
async def process_object_name_input(message: types.Message, state: FSMContext):
    await state.update_data(object_name=message.text)
    if await check_users_input(state):
        await confirm_changes(message, state)
        return
    await message.answer(text=LEXICON_RU["object_square"])
    await state.set_state(DefectsCalculation.object_square)


@router.message(
    StateFilter(DefectsCalculation.object_name),
)
async def process_object_name_input_warning(
    message: types.Message, state: FSMContext
):
    await delete_warning(message, LEXICON_RU["object_name_warning"])


@router.message(
    StateFilter(DefectsCalculation.object_square), IsValidCostFilter()
)
async def process_object_square_input(
    message: types.Message, state: FSMContext
):
    object_square = convert_to_float(message.text)
    await state.update_data(object_square=object_square)
    await confirm_changes(message, state)


@router.message(
    StateFilter(DefectsCalculation.object_square),
)
async def process_object_square_input_warning(
    message: types.Message, state: FSMContext
):
    await delete_warning(message, LEXICON_RU["object_square_warning"])


@router.callback_query(
    StateFilter(DefectsCalculation.confirm_details), F.data.in_(["yes_button"])
)
async def process_confirm_details(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    city = user_data.get("city")
    object_name = user_data.get("object_name")
    object_square = user_data.get("object_square")
    x1, x2 = 20, 150
    y1, y2 = 240000, 948000
    compensation = y1 + (object_square - x1) * (y2 - y1) / (x2 - x1)
    random_factor = 1 + random.uniform(-0.05, 0.05)
    compensation *= random_factor
    compensation = round(compensation, 2)
    await callback.message.edit_text(
        text=LEXICON_RU["yes_button_callback_defects"].format(compensation)
    )
    await db.add_defects(
        user_id=callback.from_user.id,
        city=city,
        object_name=object_name,
        object_square=round(object_square, 2),
        compensation=compensation,
    )
    keyboard = create_inline_kb(
        1,
        "penalty_button",
        "defects_button",
        "ask_button",
    )
    await callback.message.answer(
        text=LEXICON_RU["penalty_added"], reply_markup=keyboard
    )
    await state.clear()


@router.callback_query(
    StateFilter(DefectsCalculation.confirm_details), F.data.in_(["no_button"])
)
async def process_change_details(callback: CallbackQuery, state: FSMContext):
    keyboard = create_inline_kb(
        1,
        "city_button",
        "object_name_button",
        "object_square_button",
    )
    await callback.message.edit_text(
        text=LEXICON_RU["no_button_callback"], reply_markup=keyboard
    )
    await state.set_state(DefectsCalculation.change_details)


@router.callback_query(
    StateFilter(DefectsCalculation.change_details),
    F.data.in_(["city_button", "object_name_button", "object_square_button"]),
)
async def process_change_details(callback: CallbackQuery, state: FSMContext):
    if callback.data == "city_button":
        keyboard = create_inline_kb(
            2,
            *CITIES_RU,
        )
        await callback.message.edit_text(
            text=LEXICON_RU["input_city"], reply_markup=keyboard
        )
        await state.set_state(DefectsCalculation.start)
    elif callback.data == "object_name_button":
        await callback.message.edit_text(text=LEXICON_RU["object_name"])
        await state.set_state(DefectsCalculation.object_name)
    elif callback.data == "object_square_button":
        await callback.message.edit_text(text=LEXICON_RU["object_square"])
        await state.set_state(DefectsCalculation.object_square)


@router.message(
    StateFilter(
        DefectsCalculation.confirm_details, DefectsCalculation.change_details
    )
)
async def warning_show_details(message: Message):
    await delete_warning(message, LEXICON_RU["penalty_choice_warning"])
