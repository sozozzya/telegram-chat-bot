import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.utils.serialization import deserialize_telegram_object_to_python

import dotenv

dotenv.load_dotenv()

dispatcher = Dispatcher()


@dispatcher.message(F.text)
async def message_text_echo_handler(message: Message) -> None:
    await message.answer(message.text)


@dispatcher.message(F.photo)
async def message_photo_echo_handler(message: Message) -> None:
    await message.answer_photo(message.photo[-1].file_id)


@dispatcher.update.outer_middleware()
async def logger_middleware(handler: callable, event: Update, data: dict):
    payload = deserialize_telegram_object_to_python(event)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return await handler(event, data)


async def main() -> None:
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
