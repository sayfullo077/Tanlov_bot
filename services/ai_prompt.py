# import httpx
# from database.config import DEEPSEEK_TOKEN, ADMINS
# from loader import bot
# from database.orm_query import get_single_token, increment_token_count
# from database.engine import session_maker
#
#
# MAX_TOKENS_PER_REQUEST = 3800
#
#
# async def ask_ai_deepseek(user_text, AI_ANALYST_PROMPT):
#     async with session_maker() as session:
#         # Tokenni olish
#         token_obj = await get_single_token(session)
#         used_token = token_obj.token if token_obj else DEEPSEEK_TOKEN
#
#         try:
#             # Async client ishlatish
#             async with httpx.AsyncClient(timeout=30) as client:
#                 response = await client.post(
#                     "https://openrouter.ai/api/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {used_token}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "deepseek/deepseek-chat",
#                         "max_tokens": MAX_TOKENS_PER_REQUEST,
#                         "messages": [
#                             {"role": "system", "content": AI_ANALYST_PROMPT},
#                             {"role": "user", "content": user_text}
#                         ]
#                     }
#                 )
#
#             # Token noto‘g‘ri bo‘lsa
#             if response.status_code == 401:
#                 for admin in ADMINS:
#                     await bot.send_message(chat_id=admin, text="❌ Unauthorized: Token expired or invalid.")
#                 return "⚠️ Unexpected error! Please try again later."
#
#             # Boshqa API xatolik
#             if response.status_code != 200:
#                 for admin in ADMINS:
#                     await bot.send_message(
#                         chat_id=admin,
#                         text=f"❌ API Error: {response.status_code} - {response.text}"
#                     )
#                 return "⚠️ Unexpected error! Please try again later."
#
#             # Token count oshirish
#             if token_obj:
#                 await increment_token_count(session, token_obj.id)
#
#             # Muvaffaqiyatli natija
#             return response.json()["choices"][0]["message"]["content"]
#
#         except httpx.RequestError as e:
#             return f"❌ HTTP Request Error: {e}"
#         except Exception as e:
#             return f"❌ Unknown Error: {e}"
