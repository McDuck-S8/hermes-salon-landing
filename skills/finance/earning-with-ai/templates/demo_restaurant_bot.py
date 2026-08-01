#!/usr/bin/env python3
"""Template: Restaurant Bot. Adapt menu, prices, delivery fee per client."""

class RestaurantBot:
    def __init__(self, name="Ресторан"):
        self.name = name
        self.menu = {}  # category -> [{name, price, desc}]
        self.orders = []

    def add_category(self, category, items):
        self.menu[category] = items

    def show_menu(self):
        text = f"🍽 Меню {self.name}\n\n"
        for cat, items in self.menu.items():
            text += f"📌 {cat}:\n"
            for i in items:
                text += f"  • {i['name']} — {i['price']}₽ ({i['desc']})\n"
            text += "\n"
        return text

    def order(self, items, delivery=False, address=None, delivery_fee=200):
        found = []
        total = 0
        for name in items:
            for cat_items in self.menu.values():
                for item in cat_items:
                    if item["name"].lower() == name.lower():
                        found.append(item)
                        total += item["price"]
        if not found:
            return "❌ Блюда не найдены"
        if delivery:
            total += delivery_fee
        order = {"id": len(self.orders)+1, "items": found, "total": total, "delivery": delivery, "address": address}
        self.orders.append(order)
        text = f"✅ Заказ #{order['id']}\n"
        for i in found:
            text += f"• {i['name']} — {i['price']}₽\n"
        text += f"\n💰 Итого: {total}₽"
        if delivery:
            text += f"\n🚗 Доставка: {delivery_fee}₽\n📍 {address}"
        return text
