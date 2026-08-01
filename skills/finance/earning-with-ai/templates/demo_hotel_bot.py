#!/usr/bin/env python3
"""
Template: Hotel Booking Bot for Crimea tourism.
Adapt hotel_name, rooms, prices for each client.
Present as demo when applying to hotel automation orders on FL.ru.
"""

class HotelBot:
    def __init__(self, hotel_name="Отель"):
        self.hotel_name = hotel_name
        self.rooms = {
            "standard": {"name": "Стандарт", "price": 3500, "available": 5},
            "comfort": {"name": "Комфорт", "price": 5000, "available": 3},
            "lux": {"name": "Люкс", "price": 8000, "available": 2},
        }
        self.bookings = []

    def show_welcome(self):
        return f"🏨 Добро пожаловать в {self.hotel_name}!\nВыберите: 1) Номера 2) Бронировать 3) Проверить"

    def show_rooms(self):
        text = ""
        for key, r in self.rooms.items():
            status = "✅" if r["available"] > 0 else "❌"
            text += f"• {r['name']} — {r['price']}₽/ночь ({status})\n"
        return text

    def book_room(self, room_type, check_in, check_out, guests, name, phone):
        if room_type not in self.rooms:
            return "❌ Неверный тип"
        room = self.rooms[room_type]
        if room["available"] <= 0:
            return f"❌ {room['name']} занят"
        from datetime import datetime
        d1, d2 = datetime.strptime(check_in, "%d.%m.%Y"), datetime.strptime(check_out, "%d.%m.%Y")
        nights = (d2 - d1).days
        total = room["price"] * nights
        booking = {"id": len(self.bookings)+1, "room": room["name"], "nights": nights, "total": total, "name": name}
        self.bookings.append(booking)
        room["available"] -= 1
        return f"✅ Заказ #{booking['id']}: {booking['room']}, {nights} ночей, {total}₽"

# Usage: bot = HotelBot("Ялта Интурист")
# print(bot.show_welcome())
# print(bot.book_room("comfort", "15.07.2025", "22.07.2025", 2, "Иванов", "+7 978 123 45 67"))
