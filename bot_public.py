import g4f  # ТЕПЕРЬ ЭТО ПЕРВАЯ СТРОКА
import asyncio
import logging
from aiogram import Bot, Dispatcher, types

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- НАСТРОЙКИ ---
BOT_TOKEN = '8671221976:AAHSgGipqg0L4VZmeTBp9EnZcec15Xq345g'
MY_ID = 6934671653

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def analyze_message(text):
    try:
        # Не указываем провайдера вручную, пусть g4f выберет сам (автопилот)
        response = await asyncio.to_thread(
            g4f.ChatCompletion.create,
            model=g4f.models.default, # Используем модель по умолчанию
            messages=[{"role": "user", "content": f"Is this urgent or a question? Reply ONLY 'IMPORTANT' or 'NO': {text}"}],
        )
        
        if response and isinstance(response, str):
            print(f"🤖 Ответ ИИ: {response.strip()}") # Увидим, что ответил ИИ
            return "IMPORTANT" in response.upper()
        return False
        
    except Exception as e:
        print(f"⚠️ Ошибка ИИ: {e}")
        return False

@dp.message()
async def filter_messages(message: types.Message):
    # Игнорируем пустое, ботов и самого себя
    if not message.text or message.from_user.is_bot or message.from_user.id == MY_ID:
        return

    print(f"🔎 Проверка: {message.text[:30]}...")
    
    is_important = await analyze_message(message.text)
    
    if is_important:
        print(f"🔥 ВАЖНОЕ!")
        try:
            await bot.send_message(
                MY_ID, 
                f"🎯 **ВАЖНОЕ**\n👤 {message.from_user.first_name}\n💬 {message.text}"
            )
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
    else:
        print(f"☁️ Пропущено")

async def main():
    print("--- ЗАПУСК БОТА (G4F FINAL V2) ---")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nБот остановлен.")
