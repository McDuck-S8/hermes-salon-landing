# Telethon + Aiogram — Knowledge Reference
## Для Telegram-ботов, каналов, парсинга и автоматизации

> Дата: 2026-07-21 | Для CPA/Traffic воронок

## 1. Telethon (MTProto — работаем как пользователь/админ)

### Установка
```bash
pip install telethon
```

### Базовая авторизация (пользователь)
```python
from telethon import TelegramClient, events
import asyncio

api_id = 12345       # my.telegram.org → API Development
api_hash = 'ваш_hash'
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()
    # теперь авторизован
    me = await client.get_me()
    print(f'Я: {me.username}')

asyncio.run(main())
```

### Авторизация бота (вместо пользователя)
```python
client = TelegramClient('bot_session', api_id, api_hash)
await client.start(bot_token='YOUR_BOT_TOKEN')
```

### Отправка сообщений
```python
# Отправить себе
await client.send_message('me', 'Привет!')

# Отправить в канал/чат
await client.send_message('@channel_username', 'Пост в канал')

# С фото/видео
await client.send_file('@channel_username', 'file.mp4', caption='Подпись')

# С кнопками (inline)
from telethon import Button
buttons = [[Button.inline('Купить', 'buy_1'), Button.url('Сайт', 'https://')]]
await client.send_message('@channel', 'Текст', buttons=buttons)
```

### Чтение сообщений из канала/группы
```python
# Получить последние 100 сообщений
async for msg in client.iter_messages('@channel_name', limit=100):
    print(msg.text, msg.id, msg.date)
    if msg.media:
        await msg.download_media()
```

### Получить список участников группы
```python
# Только для групп/супергрупп (не mega-групп >200)
participants = await client.get_participants('@group_name')
for user in participants:
    print(user.id, user.username, user.first_name)
```

### Обработка событий (с Telethon)
```python
@client.on(events.NewMessage(chats='@group'))
async def handler(event):
    print(f'Новое сообщение: {event.message.text}')

await client.run_until_disconnected()
```

### Прокси
```python
client = TelegramClient('session', api_id, api_hash,
    proxy=('socks5', '127.0.0.1', 9050))
```

### Полезные TL-функции
```python
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest

# Присоединиться по invite
await client(ImportChatInviteRequest('invite_hash'))
await client(JoinChannelRequest('@channel_name'))

# Ответить на сообщение
await msg.reply('Ответ')
```

---

## 2. Aiogram 3.x (Bot API — работаем как бот)

### Установка
```bash
pip install aiogram
```

### Минимальный бот
```python
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = '...'
dp = Dispatcher()

@dp.message(Command('start'))
async def start(msg: Message):
    await msg.answer('Привет! Я бот')

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

asyncio.run(main())
```

### Отправка в канал (админ канала)
```python
bot = Bot(token=BOT_TOKEN)
# Как бот-администратор канала — через chat_id
await bot.send_message(chat_id='@channel_username', text='Пост')
# С медиа + кнопки
await bot.send_photo(chat_id='@channel', photo=URL, caption='Текст',
    reply_markup=inline_keyboard)
```

### Inline клавиатура
```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Вариант 1: Builder
kb = InlineKeyboardBuilder()
kb.button(text='Купить USDT', callback_data='buy')
kb.button(text='Гайд', url='https://t.me/channel')
kb.adjust(1)  # по одному в ряд

# Вариант 2: прямо
kb2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Купить', callback_data='buy')],
    [InlineKeyboardButton(text='Сайт', url='https://')],
])

await msg.answer('Выбери:', reply_markup=kb.as_markup())
```

### Обработка нажатий (callback)
```python
from aiogram.filters import Command
from aiogram.types import CallbackQuery

@dp.callback_query(lambda c: c.data == 'buy')
async def buy_handler(call: CallbackQuery):
    await call.message.answer('Ссылка на оплату: ...')
    await call.answer()  # закрыть "часики" на кнопке
```

### FSM — многошаговый диалог
```python
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class OrderStates(StatesGroup):
    waiting_amount = State()
    waiting_wallet = State()

@dp.message(Command('order'))
async def order_start(msg: Message, state: FSMContext):
    await msg.answer('Сколько USDT?')
    await state.set_state(OrderStates.waiting_amount)

@dp.message(OrderStates.waiting_amount)
async def process_amount(msg: Message, state: FSMContext):
    await state.update_data(amount=msg.text)
    await msg.answer('Адрес кошелька?')
    await state.set_state(OrderStates.waiting_wallet)

@dp.message(OrderStates.waiting_wallet)
async def process_wallet(msg: Message, state: FSMContext):
    data = await state.get_data()
    await msg.answer(f'Ордер: {data["amount"]} USDT → {msg.text}')
    await state.clear()
```

### Media Group (альбом)
```python
from aiogram.types import InputMediaPhoto, InputMediaVideo

media = [
    InputMediaPhoto(media='URL1', caption='Пост 1'),
    InputMediaPhoto(media='URL2'),
    InputMediaVideo(media='URL3'),
]
await bot.send_media_group(chat_id='@channel', media=media)
```

### Middleware — логирование/защита
```python
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        print(f'Event: {type(event).__name__}')
        return await handler(event, data)

dp.message.middleware(LoggingMiddleware())
```

---

## 3. Когда что использовать

| Задача | Инструмент |
|---|---|
| Постить в канал от имени бота-админа | **Aiogram** (`bot.send_message`) |
| Постить в канал от имени пользователя | **Telethon** (`client.send_message`) |
| Собирать посты из чужих каналов | **Telethon** (`iter_messages`) |
| Собирать участников группы | **Telethon** (`get_participants`) |
| Отвечать пользователям (инлайн кнопки) | **Aiogram** (dispatcher, handlers) |
| Многошаговая форма (FSM) | **Aiogram** (states, FSMContext) |
| Автоматизация аккаунта (вступление, рассылка) | **Telethon** |
| Обработка callback кнопок | **Aiogram** (`callback_query`) |

---

## 4. Типовые паттерны для CPA/Traffic

### А. Приветствие + контент-лок (Aiogram)
```
User → /start
Bot → "Привет! Хочешь гайд по USDT?" [Кнопка: Получить гайд]
User нажимает → Bot: "Подпишись на канал @usdt_prosto"
User подписался → Bot проверяет через Telethon/API → разблокирует контент
```

### Б. Рассылка по подписчикам (Telethon)
```python
# Получить всех участников
participants = await client.get_participants('@my_channel')
for user in participants:
    if not user.bot and user.username:
        try:
            await client.send_message(user.id, 'Новый гайд по USDT!')
            await asyncio.sleep(1)  # анти-флуд
        except:
            pass
```

### В. Мониторинг канала (Telethon)
```python
@client.on(events.NewMessage(chats='@competitor_channel'))
async def handler(event):
    if 'usdt' in event.message.text.lower():
        await client.send_message('me', f'Найдено: {event.message.text}')
```

---

## 5. Полезные ссылки

- Aiogram docs: https://docs.aiogram.dev
- Aiogram GitHub: https://github.com/aiogram/aiogram
- Telethon docs: https://docs.telethon.dev
- Telethon GitHub: https://github.com/LonamiWebs/Telethon
- @BotFather — создать бота: https://t.me/BotFather
- API credentials: https://my.telegram.org/apps
