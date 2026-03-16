import g4f
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ (Берутся из настроек Render) ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_ID = int(os.getenv('MY_ID', '6934671653'))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ФЕЙКОВЫЙ ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Focus Guard is Alive!")

async def analyze_message(text):
    try:
        response = await asyncio.to_thread(
            g4f.ChatCompletion.create,
            model=g4f.models.default,
            messages=[{"role": "user", "content": f"Is this urgent or a question? Reply ONLY 'IMPORTANT' or 'NO': {text}"}],
        )
        
        if response and isinstance(response, str):
            print(f"🤖 Ответ ИИ: {response.strip()}")
            return "IMPORTANT" in response.upper()
        return False
        
    except Exception as e:
        print(f"⚠️ Ошибка ИИ: {e}")
        return False

@dp.message()
async def filter_messages(message: types.Message):
    if not message.text or message.from_user.is_bot or message.from_user.id == MY_ID:
        return

    print(f"🔎 Проверка: {message.text[:30]}...")
    is_important = await analyze_message(message.text)
    
    if is_important:
        print(f"🔥 ВАЖНОЕ!")
        try:
            await bot.send_message(
                MY_ID, 
                f"🎯 **ВАЖНОЕ**\n👤 {message.from_user.full_name}\n💬 {message.text}"
            )
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
    else:
        print(f"☁️ Пропущено")

async def main():
    # Настройка веб-сервера
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render дает порт в переменную окружения PORT
    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    print(f"--- ЗАПУСК БОТА НА ПОРТУ {port} ---")
    
    # Запускаем и сервер, и бота одновременно
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        site.start(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nБот остановлен.")
