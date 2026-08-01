#!/usr/bin/env python3
"""
DEMO: Telegram Bot for Hotel Booking in Crimea
For FL.ru order and Crimea tourism market
"""

import json
from datetime import datetime, timedelta

class HotelBot:
    """AI-powered hotel booking bot."""
    
    def __init__(self, hotel_name="Отель «Черноморский»"):
        self.hotel_name = hotel_name
        self.rooms = {
            "standard": {"name": "Стандарт", "price": 3500, "available": 5},
            "comfort": {"name": "Комфорт", "price": 5000, "available": 3},
            "lux": {"name": "Люкс", "price": 8000, "available": 2},
        }
        self.bookings = []
    
    def show_welcome(self):
        return f"""🏨 Добро пожаловать в {self.hotel_name}!

Я помогу вам забронировать номер в Крыму.

Выберите действие:
1️⃣ Посмотреть номера
2️⃣ Забронировать номер
3️⃣ Проверить бронирование
4️⃣ Связаться с администратором
"""
    
    def show_rooms(self):
        text = "🏠 Наши номера:\n\n"
        for key, room in self.rooms.items():
            status = "✅ Доступен" if room["available"] > 0 else "❌ Занят"
            text += f"• {room['name']} — {room['price']}₽/ночь ({status})\n"
        text += "\nВыберите номер (1-3) или нажмите «Назад»"
        return text
    
    def book_room(self, room_type, check_in, check_out, guests, name, phone):
        """Create a booking."""
        if room_type not in self.rooms:
            return "❌ Неверный тип номера"
        
        room = self.rooms[room_type]
        if room["available"] <= 0:
            return f"❌ Номер «{room['name']}» сейчас занят"
        
        # Calculate price
        try:
            d1 = datetime.strptime(check_in, "%d.%m.%Y")
            d2 = datetime.strptime(check_out, "%d.%m.%Y")
            nights = (d2 - d1).days
            if nights <= 0:
                return "❌ Дата выезда должна быть позже даты заезда"
        except ValueError:
            return "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ"
        
        total = room["price"] * nights
        
        booking = {
            "id": len(self.bookings) + 1,
            "room": room["name"],
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "guests": guests,
            "name": name,
            "phone": phone,
            "total": total,
            "status": "подтверждено"
        }
        
        self.bookings.append(booking)
        room["available"] -= 1
        
        return f"""✅ Бронирование #{booking['id']}

🏨 Номер: {booking['room']}
📅 Заезд: {booking['check_in']}
📅 Выезд: {booking['check_out']}
🌙 Ночей: {booking['nights']}
👥 Гостей: {booking['guests']}
💰 Сумма: {booking['total']}₽

👤 Имя: {booking['name']}
📱 Телефон: {booking['phone']}

Статус: {booking['status']}

Для подтверждения оплаты свяжитесь с администратором.
"""
    
    def check_booking(self, booking_id):
        """Check booking status."""
        for b in self.bookings:
            if b["id"] == booking_id:
                return f"📋 Бронирование #{b['id']}: {b['room']}, {b['check_in']}-{b['check_out']}, статус: {b['status']}"
        return "❌ Бронирование не найдено"


def demo():
    """Run demo of hotel bot."""
    print("=" * 60)
    print("DEMO: HOTEL BOOKING BOT")
    print("=" * 60)
    
    bot = HotelBot("Отель «Ялта Интурист»")
    
    # Show welcome
    print(bot.show_welcome())
    
    # Show rooms
    print(bot.show_rooms())
    
    # Simulate booking
    print("\n--- Симуляция бронирования ---")
    result = bot.book_room(
        room_type="comfort",
        check_in="15.07.2025",
        check_out="22.07.2025",
        guests=2,
        name="Иванов Иван",
        phone="+7 978 123 45 67"
    )
    print(result)
    
    # Check booking
    print(bot.check_booking(1))
    
    print("\n✅ Демо завершено!")
    print("\nВ продакшн версии:")
    print("- Реальный Telegram бот на aiogram")
    print("- База данных PostgreSQL")
    print("- Интеграция с платёжной системой")
    print("- Уведомления администратору")
    print("- Статистика и аналитика")


if __name__ == "__main__":
    demo()
