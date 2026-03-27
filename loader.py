# import aioredis
from aiogram import Bot,Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from database.config import BOT_TOKEN


bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode='HTML')
)
dp = Dispatcher(storage=MemoryStorage())
# redis = aioredis.from_url("redis://localhost", decode_responses=True)