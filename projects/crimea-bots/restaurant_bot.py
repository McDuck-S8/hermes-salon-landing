#!/usr/bin/env python3
"""DEMO: Restaurant Bot for Crimea"""

class RestaurantBot:
    def __init__(self, name="Ресторан «Крымский дворик»"):
        self.name = name
        self.menu = {
            "Салаты": [
                {"name": "Греческий", "price": 450, "desc": "Свежие овощи, оливки, фета"},
                {"name": "Цезарь", "price": 550, "desc": "Романо, пармезан, соус"},
            ],
            "Горячее": [
                {"name": "Шашлык", "price": 850, "desc": "Баранина, 200г"},
                {"name": "Плов", "price": 650, "desc": "Рис, баранина, специи"},
                {"name": "Рыба дня", "price": 750, "desc": "Чёрное море"},
            ],
            "Десерты": [
                {"name": "Пахлава", "price": 350, "desc": "Домашняя, орехи"},
            ],
            "Напитки": [
                {"name": "Чай", "price": 150, "desc": "Крымский зелёный"},
                {"name": "Лимонад", "price": 250, "desc": "Мята, лимон, мёд"},
            ],
        }
        self.orders = []
    
    def show_menu(self):
        text = f"\U0001f37d Меню {self.name}\n\n"
        for cat, items in self.menu.items():
            text += f"\U0001f4cc {cat}:\n"
            for i in items:
                text += f"  \u2022 {i['name']} \u2014 {i['price']}\u20bd ({i['desc']})\n"
            text += "\n"
        return text
    
    def create_order(self, items, delivery=False, address=None):
        order_items = []
        total = 0
        for item_name in items:
            for cat_items in self.menu.values():
                for item in cat_items:
                    if item["name"].lower() == item_name.lower():
                        order_items.append(item)
                        total += item["price"]
        if not order_items:
            return "\u274c Блюда не найдены"
        if delivery:
            total += 200
        order = {"id": len(self.orders)+1, "items": order_items, "total": total, "delivery": delivery, "address": address, "status": "принят"}
        self.orders.append(order)
        text = f"\u2705 Заказ #{order['id']}\n\n"
        for i in order_items:
            text += f"\u2022 {i['name']} \u2014 {i['price']}\u20bd\n"
        text += f"\n\U0001f4b0 Итого: {total}\u20bd"
        if delivery:
            text += f"\n\U0001f697 Доставка: 200\u20bd\n\U0001f4cd Адрес: {address}"
        text += f"\n\nСтатус: {order['status']}"
        return text

bot = RestaurantBot()
print(bot.show_menu())
print("--- Заказ ---")
print(bot.create_order(["Шашлык", "Греческий", "Чай"], delivery=True, address="ул. Ленина, 15"))
print("\n✅ Демо завершено!")
