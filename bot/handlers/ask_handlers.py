import aiohttp
import openai
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from config_data.config import load_config
from fsm_settings import AskMode
from handlers.other_handlers import delete_warning
from lexicon.lexicon import LEXICON_RU
from loader import db, dp

router = Router()
config = load_config(path=None)

#
# async def ask_openai(question: str, message: Message):
#     headers = {
#         "Authorization": f"Bearer {config.openai.api_key}",
#         "Content-Type": "application/json",
#     }
#
#     payload = {
#         "prompt": question,
#         "max_tokens": 150
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(config.openai.url, headers=headers,
#                                 json=payload) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 return data['choices'][0]['text'].strip()
#             else:
#                 await message.answer(text="Ошибка OpenAI API")
#                 raise Exception(f"OpenAI API Error: {response.status} - {await response.text()}")

openai_prompt = (
    "Представь, что ты эксперт по долевому строительству в "
    "России. Ты владеешь всеми аспектами законодательства, "
    "касающегося долевого участия в строительстве, включая "
    "ФЗ-214, ГК РФ и иные регулятивные документы. Ты готов "
    "помочь во всех вопросах, связанных с долевым "
    "строительством, включая права и обязанности сторон, "
    "исполнение договорных условий, оспаривание действий "
    "застройщиков и взыскание неустойки. Твой ответ должен быть "
    "коротким и содержательным, не более 100 слов, "
    "в официально-деловом стиле. Если у тебя "
    "возникнут вопросы, я задам их дополнительно. Даже если в "
    "конце моего предложения не будет знака вопроса, не надо "
    "продолжать за меня, воспринимай это как вопрос. "
)


async def ask_openai_v2(question: str) -> str:
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": openai_prompt},
            {"role": "user", "content": question},
        ],
    )
    answer = chat_response.choices[0].message["content"]
    return answer


@router.message(StateFilter(AskMode.start), F.text, F.voice)
async def process_ask_mode(message: Message, state: FSMContext):
    question = message.text
    if message.content_type == "voice":
        await message.answer(text="Это голосовое сообщение")
        file_path = await dp.get_file_path(message.voice.file_id)
        file_url = (
            "https://api.telegram.org/file/bot{config.tg_bot.token}"
            f"/{file_path}"
        )
        transcription_response = openai.Whisper.transcribe(file_url)
        question = transcription_response.get("transcription", "")
    answer = await ask_openai_v2(question)
    await message.answer(text=answer)
    await db.add_question(
        user_id=message.from_user.id, question=question, answer=answer
    )


@router.message(
    StateFilter(AskMode.start),
)
async def process_ask_mode_warning(message: Message, state: FSMContext):
    await delete_warning(message, LEXICON_RU["ask_mode_warning"])
