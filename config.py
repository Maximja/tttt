import os


class Config:
    BOT_TOKEN = "8314366185:AAHoYA4_8M7OGHbBnf7AsydoAoUR4LRkAf4"
    ADMIN_ID = 646826842  # Ваш ID в Telegram

    # Типы проблем
    PROBLEM_TYPES = [
        "Двигатель",
        "Тормоза",
        "Электроника",
        "Коробка передач",
        "Кузов/салон",
        "Шины/колеса",
        "Другое"
    ]

    # Марки машин (замените на ваши)
    CAR_BRANDS = ["Geely", "VESTA", "Granta"]