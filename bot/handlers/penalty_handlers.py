import time
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from filters.filters import IsValidCostFilter, IsValidDateFilter
from fsm_settings import PenaltyCalculation
from handlers.other_handlers import delete_warning
from lexicon.lexicon import LEXICON_RU
from loader import db
from utils import convert_to_float, create_inline_kb

router = Router()


async def check_users_input(state: FSMContext):
    user_data = await state.get_data()
    start_date = user_data.get("start_date")
    end_date = user_data.get("end_date")
    object_cost = user_data.get("object_cost")
    return bool(start_date and end_date and object_cost)


async def confirm_changes(message: Message, state: FSMContext):
    keyboard = create_inline_kb(
        2,
        "yes_button",
        "no_button",
    )
    user_data = await state.get_data()
    start_date = user_data.get("start_date")
    end_date = user_data.get("end_date")
    object_cost = user_data.get("object_cost")
    await message.answer(
        text=LEXICON_RU["penalty_confirm_details"].format(
            start_date.strftime("%d.%m.%Y"),
            end_date.strftime("%d.%m.%Y"),
            object_cost,
        ),
        reply_markup=keyboard,
    )
    await state.set_state(PenaltyCalculation.confirm_details)


@router.message(
    StateFilter(PenaltyCalculation.start_date),
    F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"),
    IsValidDateFilter(),
)
async def process_start_date_sent(message: Message, state: FSMContext):
    start_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    await state.update_data(start_date=start_date)
    if await check_users_input(state):
        await confirm_changes(message, state)
        return
    keyboard = create_inline_kb(
        2,
        "today_button",
        "not_today_button",
    )
    await message.answer(
        text=LEXICON_RU["penalty_end_date_choice"], reply_markup=keyboard
    )
    await state.set_state(PenaltyCalculation.end_date_choice)


@router.callback_query(
    StateFilter(PenaltyCalculation.end_date_choice),
    F.data.in_(["today_button", "not_today_button"]),
)
async def process_date_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "today_button":
        await callback.message.edit_text(
            text=LEXICON_RU["today_button_callback"]
        )
        await state.update_data(end_date=datetime.now().date())
        await state.set_state(PenaltyCalculation.object_cost)
        return
    await callback.message.edit_text(text=LEXICON_RU["penalty_end_date"])
    await state.set_state(PenaltyCalculation.end_date)


@router.message(
    StateFilter(PenaltyCalculation.end_date),
    F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"),
    IsValidDateFilter(),
)
async def process_end_date_sent(message: Message, state: FSMContext):
    end_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    user_data = await state.get_data()
    if user_data.get("start_date") > end_date:
        await delete_warning(message, LEXICON_RU["penalty_mix_warning"])
        return
    await state.update_data(end_date=end_date)
    if await check_users_input(state):
        await confirm_changes(message, state)
        return
    await message.answer(text=LEXICON_RU["penalty_object_cost"])
    await state.set_state(PenaltyCalculation.object_cost)


@router.message(
    (StateFilter(PenaltyCalculation.start_date, PenaltyCalculation.end_date)),
    F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"),
)
async def process_end_date_sent(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await delete_warning(message, LEXICON_RU["penalty_error_date_warning"])
    if date > datetime.now():
        await delete_warning(
            message, LEXICON_RU["penalty_future_date_warning"]
        )
    elif date < datetime(2006, 10, 23):
        await delete_warning(message, LEXICON_RU["penalty_early_date_warning"])


@router.message(
    StateFilter(PenaltyCalculation.start_date, PenaltyCalculation.end_date),
)
async def warning_not_date(message: Message, state: FSMContext):
    await delete_warning(message, LEXICON_RU["penalty_date_warning"])


@router.message(
    StateFilter(PenaltyCalculation.object_cost),
    IsValidCostFilter(),
)
async def process_object_cost(message: Message, state: FSMContext):
    object_cost = convert_to_float(message.text)
    await state.update_data(object_cost=object_cost)
    await confirm_changes(message, state)


@router.message(
    StateFilter(PenaltyCalculation.object_cost),
)
async def warning_not_object_cost(message: Message, state: FSMContext):
    await delete_warning(message, LEXICON_RU["penalty_object_cost_warning"])


@router.callback_query(
    StateFilter(PenaltyCalculation.confirm_details), F.data.in_(["yes_button"])
)
async def process_confirm_details(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    start_date = user_data.get("start_date")
    end_date = user_data.get("end_date")
    object_cost = user_data.get("object_cost")
    rate = await db.get_rate_for_date(end_date)
    num_days_overdue = (end_date - start_date).days + 1
    penalty = object_cost * int(num_days_overdue) * (1 / 150) * rate / 100
    await callback.message.edit_text(
        text=LEXICON_RU["yes_button_callback_penalties"].format(penalty)
    )
    await db.add_penalty(
        user_id=callback.from_user.id,
        start_date=start_date,
        end_date=end_date,
        object_cost=object_cost,
        penalty=round(penalty, 2),
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
    StateFilter(PenaltyCalculation.confirm_details), F.data.in_(["no_button"])
)
async def process_change_details(callback: CallbackQuery, state: FSMContext):
    keyboard = create_inline_kb(
        1,
        "start_date_button",
        "end_date_button",
        "object_cost_button",
    )
    await callback.message.edit_text(
        text=LEXICON_RU["no_button_callback"], reply_markup=keyboard
    )
    await state.set_state(PenaltyCalculation.change_details)


@router.callback_query(
    StateFilter(PenaltyCalculation.change_details),
    F.data.in_(["start_date_button", "end_date_button", "object_cost_button"]),
)
async def process_change_details(callback: CallbackQuery, state: FSMContext):
    if callback.data == "start_date_button":
        await callback.message.edit_text(
            text=LEXICON_RU["penalty_date_change"]
        )
        await state.set_state(PenaltyCalculation.start_date)
    elif callback.data == "end_date_button":
        await callback.message.edit_text(
            text=LEXICON_RU["penalty_date_change"]
        )
        await state.set_state(PenaltyCalculation.end_date)
    elif callback.data == "object_cost_button":
        await callback.message.edit_text(
            text=LEXICON_RU["penalty_object_cost"]
        )
        await state.set_state(PenaltyCalculation.object_cost)


@router.message(
    StateFilter(
        PenaltyCalculation.confirm_details,
        PenaltyCalculation.change_details,
        PenaltyCalculation.end_date_choice,
    )
)
async def warning_show_details(message: Message):
    await delete_warning(message, LEXICON_RU["penalty_choice_warning"])
