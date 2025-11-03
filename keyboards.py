from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config


class Keyboards:
    @staticmethod
    def main_menu():
        """Главное меню для водителей"""
        return ReplyKeyboardMarkup([
            ["📝 Сообщить о проблеме"],
            ["ℹ️ Мои последние заявки"]
        ], resize_keyboard=True)

    @staticmethod
    def car_brands():
        """Выбор марки машины"""
        buttons = [[brand] for brand in Config.CAR_BRANDS]
        buttons.append(["◀️ Назад", "🏠 Главное меню"])
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    @staticmethod
    def problem_types():
        """Выбор типа проблемы"""
        buttons = [Config.PROBLEM_TYPES[i:i + 2] for i in range(0, len(Config.PROBLEM_TYPES), 2)]
        buttons.append(["◀️ Назад", "🏠 Главное меню"])
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    @staticmethod
    def cancel():
        """Кнопка отмены"""
        return ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)

    @staticmethod
    def back_and_main():
        """Кнопки Назад и Главное меню"""
        return ReplyKeyboardMarkup([["◀️ Назад", "🏠 Главное меню"]], resize_keyboard=True)

    @staticmethod
    def admin_menu():
        """Меню администратора"""
        return ReplyKeyboardMarkup([
            ["📊 Статистика", "📋 Актуальные проблемы"],
            ["✅ Решенные проблемы", "📝 Все проблемы"],
            ["🔄 Управление заявками", "🏠 Главное меню"]
        ], resize_keyboard=True)

    @staticmethod
    def admin_problem_actions(problem_id):
        """Инлайн кнопки для управления конкретной заявкой"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Решено", callback_data=f"resolve_{problem_id}"),
                InlineKeyboardButton("🔴 Актуально", callback_data=f"active_{problem_id}")
            ],
            [
                InlineKeyboardButton("📋 Подробнее", callback_data=f"details_{problem_id}"),
                InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{problem_id}")
            ],
            [
                InlineKeyboardButton("◀️ Назад к списку", callback_data="back_to_list"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]
        ])

    @staticmethod
    def admin_back_to_list():
        """Кнопка возврата к списку заявок"""
        return ReplyKeyboardMarkup([["◀️ Назад к списку"]], resize_keyboard=True)

    @staticmethod
    def confirm_delete(problem_id):
        """Кнопки подтверждения удаления"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{problem_id}"),
                InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_delete_{problem_id}")
            ]
        ])

    @staticmethod
    def admin_navigation():
        """Инлайн кнопки навигации для админа"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 Актуальные", callback_data="show_active"),
                InlineKeyboardButton("✅ Решенные", callback_data="show_resolved")
            ],
            [
                InlineKeyboardButton("📝 Все заявки", callback_data="show_all"),
                InlineKeyboardButton("📊 Статистика", callback_data="show_stats")
            ],
            [
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]
        ])