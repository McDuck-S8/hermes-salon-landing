#!/usr/bin/env python3
"""
Create lead magnet PDF for CPA bot.
"""
from fpdf import FPDF

class LeadMagnetPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(108, 92, 231)  # Accent color
        self.cell(0, 15, 'УМНЫЙ ДОМ ЗА ОДИН ВЕЧЕР', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100)
        self.cell(0, 8, 'Чек-лист: 7 схем подключения + список деталей за $50', align='C', new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Страница {self.page_no()}/{{nb}}  |  t.me/your_channel  |  Бесплатно. Без спама.', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(40, 40, 60)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(108, 92, 231)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def bullet(self, text, indent=15):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(5, 6, chr(8226))  # bullet
        self.multi_cell(0, 6, text)
        self.ln(1)

    def bold_bullet(self, bold_part, normal_part, indent=15):
        self.set_x(self.get_x() + indent)
        self.set_font('Helvetica', '', 10)
        self.cell(5, 6, chr(8226))
        self.set_font('Helvetica', 'B', 10)
        self.write(6, bold_part)
        self.set_font('Helvetica', '', 10)
        self.write(6, normal_part)
        self.ln(7)

pdf = LeadMagnetPDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=25)
pdf.add_page()

# Intro
pdf.set_font('Helvetica', '', 11)
pdf.set_text_color(40)
pdf.multi_cell(0, 7, 
    'Этот чек-лист — твой краткий путеводитель по сборке умного дома за один вечер. '
    'Никаких сложных плат, пайки или дорогих хабов. Только ESP8266/ESP32, MQTT и Home Assistant.')
pdf.ln(5)

# Section 1: Shopping List
pdf.section_title('🛒 ШОППИНГ-ЛИСТ (всего ~$50)')
pdf.bold_bullet('ESP8266 (NodeMCU/Wemos D1 Mini) ', '— $3-5 за штуку. Бери 3-5 шт.')
pdf.bold_bullet('ESP32 (DevKit V1) ', '— $6-8. Для сложных узлов (BLE, камера). 1-2 шт.')
pdf.bold_bullet('DHT22 (темп/влажность) ', '— $2. Альтернатива: AHT10 ($1.5, точнее).')
pdf.bold_bullet('BH1750 (освещенность) ', '— $1.5. Для авто-свет.')
pdf.bold_bullet('Реле 5V (1/2/4 канала) ', '— $1-2. Управление нагрузкой.')
pdf.bold_bullet('MQ-2 / MQ-135 (газ/воздух) ', '— $1.5. Безопасность.')
pdf.bold_bullet('Провода Dupont, пайка, термоклей ', '— $5. Расходники.')
pdf.bold_bullet('БП 5V 2A (или Mean Well 5V/12V) ', '— $3-5. Питание.')
pdf.ln(3)

# Section 2: Schemes
pdf.section_title('🔌 7 ГОТОВЫХ СХЕМ')
schemes = [
    ('1. Климат-мониторинг', 'ESP8266 + DHT22/AHT10 → MQTT → HA. Графики темп/влажности за сутки. Время: 20 мин.'),
    ('2. Авто-свет по движению', 'ESP8266 + PIR (HC-SR501) + реле → свет включается при движении. Таймер 30с. Время: 30 мин.'),
    ('3. Умная розетка (Sonoff клон)', 'ESP8266 + реле в коробке розетки. Управление нагрузкой до 10А. Мониторинг тока (HLW8012). Время: 40 мин.'),
    ('4. Увлажнитель/вентилятор по влажности', 'DHT22 + реле на вентиляторе/увлажнителе. Пороги в HA. Время: 25 мин.'),
    ('5. Детектор утечки воды', 'Датчик утечки (проводной) + ESP8266 → уведомление в Telegram. Время: 15 мин.'),
    ('6. CO2/качество воздуха', 'ESP32 + SCD40/SCD41 (CO2) + реле на вентиляции. Авто-проветривание при >1000 ppm. Время: 45 мин.'),
    ('7. Умные шторы/жалюзи', 'ESP32 + драйвер шагового (A4988) + концевики. Открытие по расписанию/свету. Время: 60 мин.'),
]
for title, desc in schemes:
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(40)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_x(20)
    pdf.multi_cell(0, 6, desc)
    pdf.ln(2)

pdf.ln(3)

# Section 3: Software
pdf.section_title('⚙️ СОФТ: MQTT + HOME ASSISTANT')
pdf.bullet('MQTT Broker: Mosquitto (аддон в HA) — порт 1883')
pdf.bullet('Прошивка: ESPHome (yaml) или Tasmota — без кода')
pdf.bullet('Пример ESPHome для DHT22:')
pdf.ln(2)

# Code block
pdf.set_font('Courier', '', 8)
pdf.set_fill_color(240, 240, 250)
pdf.set_text_color(30)
code = """esphome:
  name: climate-sensor
  platform: ESP8266
  board: d1_mini

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_pass

mqtt:
  broker: homeassistant.local
  username: !secret mqtt_user
  password: !secret mqtt_pass

sensor:
  - platform: dht
    model: DHT22
    pin: D4
    temperature:
      name: "Temp"
    humidity:
      name: "Humidity"
    update_interval: 30s"""
pdf.multi_cell(0, 4, code, fill=True)
pdf.ln(5)

# Section 4: Next Steps
pdf.section_title('🚀 ЧТО ДАЛЬШЕ?')
pdf.bullet('1. Закажи детали (AliExpress / ChipDip / Ozon) — 3-7 дней')
pdf.bullet('2. Прошей ESPHome через веб-интерфейс (esphome.io) — 5 мин')
pdf.bullet('3. Добавь в HA: Настройки → Устройства → ESPHome → "+"')
pdf.bullet('4. Создай автоматизации: "Если влажность > 70% → вентилятор ON"')
pdf.bullet('5. Настрой уведомления в Telegram (HA → Настройки → Уведомления)')
pdf.ln(3)

pdf.section_title('🔗 ПОЛЕЗНЫЕ ССЫЛКИ')
links = [
    ('ESPHome Docs', 'https://esphome.io/'),
    ('Home Assistant', 'https://www.home-assistant.io/'),
    ('MQTT Explorer (GUI)', 'https://mqtt-explorer.com/'),
    ('Схемы на GitHub', 'https://github.com/your-repo/smart-home-schemes'),
    ('Наш Telegram канал', 'https://t.me/your_channel'),
]
for name, url in links:
    pdf.set_font('Helvetica', 'U', 10)
    pdf.set_text_color(108, 92, 231)
    pdf.cell(0, 7, f'{name}: {url}', link=url, new_x="LMARGIN", new_y="NEXT")

pdf.ln(5)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(100)
pdf.multi_cell(0, 5, 
    'Этот материал бесплатен. Если сэкономил время — condivиди ссылку с другом. '
    'В канале @your_channel выкладываю новые схемы каждую неделю.')

# Save
output_path = "lead_magnet.pdf"
pdf.output(output_path)
print(f"✅ Created {output_path} ({os.path.getsize(output_path)} bytes)")