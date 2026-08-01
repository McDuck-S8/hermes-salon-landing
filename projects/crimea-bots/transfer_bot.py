#!/usr/bin/env python3
"""DEMO: Transfer Bot for Crimea"""

class TransferBot:
    def __init__(self):
        self.routes = {
            "Симферополь \u2192 Ялта": {"price": 2500, "time": "2 часа"},
            "Симферополь \u2192 Алушта": {"price": 2000, "time": "1.5 часа"},
            "Симферополь \u2192 Судак": {"price": 3000, "time": "2.5 часа"},
            "Симферополь \u2192 Евпатория": {"price": 1800, "time": "1 час"},
            "Симферополь \u2192 Феодосия": {"price": 2800, "time": "2 часа"},
        }
        self.bookings = []
    
    def show_routes(self):
        text = "\U0001f697 Маршруты трансфера\n\n"
        for route, info in self.routes.items():
            text += f"\u2022 {route} \u2014 {info['price']}\u20bd ({info['time']})\n"
        return text
    
    def book_transfer(self, route, date, time, passengers, name, phone):
        if route not in self.routes:
            return "\u274c Маршрут не найден"
        info = self.routes[route]
        total = info["price"] * passengers
        booking = {
            "id": len(self.bookings)+1, "route": route, "date": date, "time": time,
            "passengers": passengers, "name": name, "phone": phone, "total": total, "status": "подтверждено"
        }
        self.bookings.append(booking)
        return f"""\u2705 Трансфер #{booking['id']}

\U0001f697 Маршрут: {route}
\U0001f4c5 Дата: {date}
\U0001f552 Время: {time}
\U0001f465 Пассажиров: {passengers}
\U0001f4b0 Сумма: {total}\u20bd

\U0001f464 {name}
\U0001f4f1 {phone}

Статус: {booking['status']}"""

bot = TransferBot()
print(bot.show_routes())
print("--- Бронирование ---")
print(bot.book_transfer("Симферополь \u2192 Ялта", "15.07.2025", "10:00", 3, "Иванов", "+7 978 123 45 67"))
print("\n✅ Демо завершено!")
