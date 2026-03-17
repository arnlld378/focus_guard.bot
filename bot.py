import g4f
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# Настройка логирования (Render лучше читает logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# --- НАСТРОЙКИ ---
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
            logging.info(f"🤖 Ответ ИИ: {response.strip()}")
            return "IMPORTANT" in response.upper()
        return False
    except Exception as e:
        logging.error(f"⚠️ Ошибка ИИ: {e}")
        return False

@dp.message()
async def filter_messages(message: types.Message):
    if not message.text or message.from_user.is_bot or message.from_user.id == MY_ID:
        return

    logging.info(f"🔎 Проверка: {message.text[:30]}...")
    is_important = await analyze_message(message.text)
    
    if is_important:
        logging.info(f"🔥 ВАЖНОЕ!")
        try:
            await bot.send_message(
                MY_ID, 
                f"🎯 **ВАЖНОЕ**\n👤 {message.from_user.full_name}\n💬 {message.text}"
            )
        except Exception as e:
            logging.error(f"❌ Ошибка отправки: {e}")
    else:
        logging.info(f"☁️ Пропущено")

async def main():
    # Настройка веб-сервера
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start() # Запускаем сайт первым
    
    logging.info(f"--- ВЕБ-СЕРВЕР ЗАПУЩЕН НА ПОРТУ {port} ---")
    
    # Очищаем очередь обновлений и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("--- БОТ НАЧИНАЕТ ОПРОС (POLLING) ---")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
