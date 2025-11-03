import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, \
    CallbackQueryHandler

from config import Config
from database import Database
from keyboards import Keyboards
from status_manager import StatusManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CAR_BRAND, CAR_NUMBER, PROBLEM_TYPE, PROBLEM_DESCRIPTION = range(4)


class TaxiBot:
    def __init__(self):
        self.db = Database()
        self.status_manager = StatusManager(self.db)
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Настраиваем обработчики команд"""
        # Команды для водителей
        self.application.add_handler(CommandHandler("start", self.start))

        # Обработчик диалога сообщения о проблеме
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("📝 Сообщить о проблеме"), self.start_problem_report)],
            states={
                CAR_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_car_brand)],
                CAR_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_car_number)],
                PROBLEM_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_problem_type)],
                PROBLEM_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_problem_description)],
            },
            fallbacks=[MessageHandler(filters.Regex("❌ Отмена"), self.cancel)]
        )
        self.application.add_handler(conv_handler)

        # Команды для администратора
        self.application.add_handler(CommandHandler("admin", self.admin_panel))
        self.application.add_handler(MessageHandler(filters.Regex("📊 Статистика"), self.show_stats))
        self.application.add_handler(MessageHandler(filters.Regex("📋 Актуальные проблемы"), self.show_active_problems))
        self.application.add_handler(MessageHandler(filters.Regex("✅ Решенные проблемы"), self.show_resolved_problems))
        self.application.add_handler(MessageHandler(filters.Regex("📝 Все проблемы"), self.show_all_problems))
        self.application.add_handler(MessageHandler(filters.Regex("🔄 Управление заявками"), self.manage_problems))
        self.application.add_handler(MessageHandler(filters.Regex("◀️ Назад к списку"), self.admin_panel))

        # Обработка инлайн кнопок
        self.application.add_handler(CallbackQueryHandler(self.handle_inline_buttons,
                                                          pattern="^(resolve|active|details|delete|confirm_delete|cancel_delete)_"))

        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.message.from_user
        welcome_text = f"""
👋 Привет, {user.first_name}!

Я бот для оперативной связи с таксопарком.
Здесь вы можете быстро сообщить о проблемах с автомобилем.

Выберите действие:
        """
        await update.message.reply_text(welcome_text, reply_markup=Keyboards.main_menu())

    # === ДИАЛОГ СООБЩЕНИЯ О ПРОБЛЕМЕ ===

    async def start_problem_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало диалога сообщения о проблеме"""
        await update.message.reply_text(
            "Выберите марку автомобиля:",
            reply_markup=Keyboards.car_brands()
        )
        return CAR_BRAND

    async def get_car_brand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получаем марку автомобиля"""
        text = update.message.text

        # Обработка кнопок навигации
        if text == "◀️ Назад":
            await update.message.reply_text(
                "❌ Нечего возвращать назад. Начните заново:",
                reply_markup=Keyboards.main_menu()
            )
            return ConversationHandler.END
        elif text == "🏠 Главное меню":
            await update.message.reply_text(
                "Возвращаемся в главное меню:",
                reply_markup=Keyboards.main_menu()
            )
            return ConversationHandler.END

        car_brand = text
        if car_brand not in Config.CAR_BRANDS:
            await update.message.reply_text(
                "Пожалуйста, выберите марку из предложенных вариантов:",
                reply_markup=Keyboards.car_brands()
            )
            return CAR_BRAND

        context.user_data['car_brand'] = car_brand
        await update.message.reply_text(
            "📝 Введите госномер автомобиля:",
            reply_markup=Keyboards.back_and_main()
        )
        return CAR_NUMBER

    async def get_car_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получаем госномер автомобиля"""
        text = update.message.text

        # Обработка кнопок навигации
        if text == "◀️ Назад":
            await update.message.reply_text(
                "Выберите марку автомобиля:",
                reply_markup=Keyboards.car_brands()
            )
            return CAR_BRAND
        elif text == "🏠 Главное меню":
            await update.message.reply_text(
                "Возвращаемся в главное меню:",
                reply_markup=Keyboards.main_menu()
            )
            context.user_data.clear()
            return ConversationHandler.END

        car_number = text.upper()
        context.user_data['car_number'] = car_number

        await update.message.reply_text(
            "Выберите тип проблемы:",
            reply_markup=Keyboards.problem_types()
        )
        return PROBLEM_TYPE

    async def get_problem_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получаем тип проблемы"""
        text = update.message.text

        # Обработка кнопок навигации
        if text == "◀️ Назад":
            await update.message.reply_text(
                "📝 Введите госномер автомобиля:",
                reply_markup=Keyboards.back_and_main()
            )
            return CAR_NUMBER
        elif text == "🏠 Главное меню":
            await update.message.reply_text(
                "Возвращаемся в главное меню:",
                reply_markup=Keyboards.main_menu()
            )
            context.user_data.clear()
            return ConversationHandler.END

        problem_type = text
        if problem_type not in Config.PROBLEM_TYPES:
            await update.message.reply_text(
                "Пожалуйста, выберите тип из предложенных вариантов:",
                reply_markup=Keyboards.problem_types()
            )
            return PROBLEM_TYPE

        context.user_data['problem_type'] = problem_type

        if problem_type == "Другое":
            await update.message.reply_text(
                "📝 Опишите проблему подробно:",
                reply_markup=Keyboards.back_and_main()
            )
        else:
            await update.message.reply_text(
                f"💬 Уточните проблему с {problem_type.lower()}:",
                reply_markup=Keyboards.back_and_main()
            )
        return PROBLEM_DESCRIPTION

    async def get_problem_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получаем описание проблемы и сохраняем заявку"""
        text = update.message.text

        # Обработка кнопок навигации
        if text == "◀️ Назад":
            await update.message.reply_text(
                "Выберите тип проблемы:",
                reply_markup=Keyboards.problem_types()
            )
            return PROBLEM_TYPE
        elif text == "🏠 Главное меню":
            await update.message.reply_text(
                "Возвращаемся в главное меню:",
                reply_markup=Keyboards.main_menu()
            )
            context.user_data.clear()
            return ConversationHandler.END

        description = text
        user = update.message.from_user

        # Сохраняем проблему в базу
        problem_id = self.db.add_problem(
            driver_id=user.id,
            driver_name=f"{user.first_name} {user.last_name or ''}",
            car_brand=context.user_data['car_brand'],
            car_number=context.user_data['car_number'],
            problem_type=context.user_data['problem_type'],
            description=description
        )

        # Уведомляем администратора
        await self.notify_admin(update, context, problem_id, description)

        await update.message.reply_text(
            "✅ Спасибо! Ваша заявка принята. Мы уже работаем над проблемой!",
            reply_markup=Keyboards.main_menu()
        )

        # Очищаем данные пользователя
        context.user_data.clear()
        return ConversationHandler.END

    async def notify_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, problem_id: int, description: str):
        """Уведомляем администратора о новой проблеме"""
        user = update.message.from_user
        problem_info = f"""
🚨 НОВАЯ ЗАЯВКА #{problem_id}

👤 Водитель: {user.first_name} {user.last_name or ''} (ID: {user.id})
🚗 Автомобиль: {context.user_data['car_brand']} {context.user_data['car_number']}
📋 Тип проблемы: {context.user_data['problem_type']}
📝 Описание: {description}

Для изменения статуса используйте команду /admin
        """

        try:
            await context.bot.send_message(
                chat_id=Config.ADMIN_ID,
                text=problem_info
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить администратора: {e}")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена диалога"""
        await update.message.reply_text(
            "❌ Диалог отменен",
            reply_markup=Keyboards.main_menu()
        )
        context.user_data.clear()
        return ConversationHandler.END

    # === АДМИН ПАНЕЛЬ ===

    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Панель администратора"""
        user_id = update.message.from_user.id

        if user_id != Config.ADMIN_ID:
            await update.message.reply_text("⛔ У вас нет доступа к этой команде")
            return

        stats = self.db.get_stats()
        welcome_text = f"""
⚙️ Панель администратора

📊 Статистика:
• Всего заявок: {stats[0]}
• Актуальные: {stats[1]}
• Решено: {stats[2]}

Выберите действие:
        """
        await update.message.reply_text(welcome_text, reply_markup=Keyboards.admin_menu())

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику"""
        if update.message.from_user.id != Config.ADMIN_ID:
            return

        stats_text = self.status_manager.get_stats_message()
        await update.message.reply_text(stats_text)

    async def show_active_problems(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать актуальные проблемы"""
        if update.message.from_user.id != Config.ADMIN_ID:
            return

        problems = self.status_manager.get_problems_by_status('актуально')
        await self.send_problems_list(update, problems, "🔴 АКТУАЛЬНЫЕ ПРОБЛЕМЫ")

    async def show_resolved_problems(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать решенные проблемы"""
        if update.message.from_user.id != Config.ADMIN_ID:
            return

        problems = self.status_manager.get_problems_by_status('решено')
        await self.send_problems_list(update, problems, "✅ РЕШЕННЫЕ ПРОБЛЕМЫ")

    async def show_all_problems(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать все проблемы"""
        if update.message.from_user.id != Config.ADMIN_ID:
            return

        problems = self.status_manager.get_all_problems()
        await self.send_problems_list(update, problems, "📋 ВСЕ ПРОБЛЕМЫ")

    async def send_problems_list(self, update: Update, problems: list, title: str):
        """Отправляет список проблем с кнопками управления"""
        if not problems:
            await update.message.reply_text(f"📭 {title}\n\nНет заявок")
            return

        # Отправляем первую заявку с кнопками управления
        first_problem = problems[0]
        await self.send_problem_detail(update, first_problem, title, 0, len(problems))

        # Если есть еще заявки, сообщим об этом
        if len(problems) > 1:
            await update.message.reply_text(
                f"📋 Показана заявка 1 из {len(problems)}\n"
                f"Используйте кнопки ниже для управления или введите номер заявки вручную",
                reply_markup=Keyboards.admin_back_to_list()
            )

    async def send_problem_detail(self, update: Update, problem: tuple, title: str, current_index: int, total: int):
        """Отправляет детальную информацию о заявке с кнопками управления"""
        message = self.status_manager.format_problem_message(problem)
        problem_id = problem[0]

        if isinstance(update, Update) and update.message:
            await update.message.reply_text(
                message,
                reply_markup=Keyboards.admin_problem_actions(problem_id)
            )
        else:
            # Если это обновление сообщения (для callback)
            query = update.callback_query
            await query.edit_message_text(
                message,
                reply_markup=Keyboards.admin_problem_actions(problem_id)
            )

    async def manage_problems(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление заявками - поиск по номеру"""
        if update.message.from_user.id != Config.ADMIN_ID:
            return

        await update.message.reply_text(
            "🔍 **Управление заявками**\n\n"
            "Введите номер заявки для управления (например: 1)\n"
            "Или выберите действие из меню:",
            reply_markup=Keyboards.admin_back_to_list()
        )

    async def handle_inline_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на инлайн кнопки"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        if user_id != Config.ADMIN_ID:
            await query.message.reply_text("⛔ У вас нет доступа")
            return

        data = query.data
        problem_id = int(data.split('_')[1])

        if data.startswith('resolve_'):
            # Пометить как решено
            if self.status_manager.resolve_problem(problem_id):
                await query.message.reply_text(f"✅ Заявка #{problem_id} отмечена как РЕШЕННАЯ")

                # Обновляем сообщение с заявкой
                problem = self.status_manager.get_problem_by_id(problem_id)
                if problem:
                    await self.send_problem_detail(update, problem, "ОБНОВЛЕННАЯ ЗАЯВКА", 0, 1)
            else:
                await query.message.reply_text(f"❌ Ошибка при обновлении заявки #{problem_id}")

        elif data.startswith('active_'):
            # Пометить как актуально
            if self.status_manager.activate_problem(problem_id):
                await query.message.reply_text(f"🔴 Заявка #{problem_id} отмечена как АКТУАЛЬНАЯ")

                # Обновляем сообщение с заявкой
                problem = self.status_manager.get_problem_by_id(problem_id)
                if problem:
                    await self.send_problem_detail(update, problem, "ОБНОВЛЕННАЯ ЗАЯВКА", 0, 1)
            else:
                await query.message.reply_text(f"❌ Ошибка при обновлении заявки #{problem_id}")

        elif data.startswith('details_'):
            # Показать подробности (уже показаны)
            await query.answer("ℹ️ Вы уже просматриваете эту заявку")

        elif data.startswith('delete_'):
            # Подтверждение удаления
            await query.message.reply_text(
                f"⚠️ Вы уверены что хотите удалить заявку #{problem_id}?",
                reply_markup=Keyboards.confirm_delete(problem_id)
            )

        elif data.startswith('confirm_delete_'):
            # TODO: Реализовать удаление из базы данных
            await query.message.reply_text(f"🗑️ Заявка #{problem_id} удалена")
            await query.message.delete()

        elif data.startswith('cancel_delete_'):
            # Отмена удаления
            await query.answer("❌ Удаление отменено")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений"""
        text = update.message.text

        # Обработка кнопки "Главное меню" из любого места
        if text == "🏠 Главное меню":
            await update.message.reply_text(
                "Возвращаемся в главное меню:",
                reply_markup=Keyboards.main_menu()
            )
            return

        # Обработка кнопки "Назад" вне диалога
        if text == "◀️ Назад":
            await update.message.reply_text(
                "Вы уже в главном меню",
                reply_markup=Keyboards.main_menu()
            )
            return

        # Обработка админских команд - ручной ввод номеров заявок
        if update.message.from_user.id == Config.ADMIN_ID:
            # Попытка распознать номер заявки
            if text.isdigit():
                problem_id = int(text)
                problem = self.status_manager.get_problem_by_id(problem_id)

                if problem:
                    await self.send_problem_detail(update, problem, "НАЙДЕННАЯ ЗАЯВКА", 0, 1)
                else:
                    await update.message.reply_text(f"❌ Заявка #{problem_id} не найдена")
                return

            text_lower = text.lower()
            if text_lower.startswith('решить ') or text_lower.startswith('закрыть '):
                try:
                    problem_id = int(text_lower.split()[1])
                    if self.status_manager.resolve_problem(problem_id):
                        await update.message.reply_text(f"✅ Заявка #{problem_id} отмечена как решенная")
                    else:
                        await update.message.reply_text(f"❌ Ошибка при обновлении заявки #{problem_id}")
                except (ValueError, IndexError):
                    await update.message.reply_text("❌ Используйте: 'решить НОМЕР' или 'закрыть НОМЕР'")
            elif text_lower.startswith('открыть '):
                try:
                    problem_id = int(text_lower.split()[1])
                    if self.status_manager.activate_problem(problem_id):
                        await update.message.reply_text(f"🔴 Заявка #{problem_id} отмечена как актуальная")
                    else:
                        await update.message.reply_text(f"❌ Ошибка при обновлении заявки #{problem_id}")
                except (ValueError, IndexError):
                    await update.message.reply_text("❌ Используйте: 'открыть НОМЕР'")

    def run(self):
        """Запуск бота"""
        print("🤖 Бот запущен...")
        self.application.run_polling()


# Запуск бота
if __name__ == "__main__":
    bot = TaxiBot()
    bot.run()