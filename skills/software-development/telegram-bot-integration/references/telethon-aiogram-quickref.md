# Telethon + Aiogram Quick Reference

## Telethon (MTProto — работаем как пользователь)
```python
from telethon import TelegramClient, events, Button

client = TelegramClient('session', api_id, api_hash)
await client.start(bot_token='TOKEN')  # или для пользователя
await client.send_message('@channel', 'текст', buttons=[
    [Button.inline('Купить', 'buy_1'), Button.url('Сайт', 'https://')]
])
await client.send_file('@channel', 'video.mp4', caption='подпись')
async for msg in client.iter_messages('@channel', limit=100): ...
await client.get_participants('@group')
```

## Aiogram 3.x (Bot API — бот)
```python
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

dp = Dispatcher()
bot = Bot(token='TOKEN')

@dp.message(Command('start'))
async def start(msg: Message): ...

# Inline keyboard
kb = InlineKeyboardBuilder()
kb.button(text='Купить', callback_data='buy')
kb.adjust(1)
await msg.answer('Выбери:', reply_markup=kb.as_markup())

# Callback
@dp.callback_query(lambda c: c.data == 'buy')
async def buy_cb(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Готово')

# FSM
class MyStates(StatesGroup):
    step1 = State()
    step2 = State()

@dp.message(MyStates.step1)
async def step1(msg: Message, state: FSMContext):
    await state.update_data(key=msg.text)
    await state.set_state(MyStates.step2)
```

## Когда что использовать
- **Постинг в канал от бота-админа** → Aiogram bot.send_message
- **Сбор постов из чужого канала** → Telethon iter_messages
- **Сбор участников** → Telethon get_participants
- **Инлайн кнопки + FSM** → Aiogram
- **Автоматизация аккаунта (рассылка)** → Telethon

## Полезные ссылки
- Aiogram docs: https://docs.aiogram.dev
- Telethon docs: https://docs.telethon.dev
- @BotFather: https://t.me/BotFather
- API credentials: https://my.telegram.org/apps
