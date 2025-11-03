from database import Database
from datetime import datetime


class StatusManager:
    def __init__(self, db: Database):
        self.db = db

    def resolve_problem(self, problem_id: int) -> bool:
        """Пометить проблему как решенную"""
        try:
            self.db.update_status(problem_id, 'решено')
            return True
        except Exception as e:
            print(f"Ошибка при решении проблемы #{problem_id}: {e}")
            return False

    def activate_problem(self, problem_id: int) -> bool:
        """Пометить проблему как актуальную"""
        try:
            self.db.update_status(problem_id, 'актуально')
            return True
        except Exception as e:
            print(f"Ошибка при активации проблемы #{problem_id}: {e}")
            return False

    def get_problem_status(self, problem_id: int) -> str:
        """Получить статус проблемы"""
        problems = self.db.get_problems()
        problem = next((p for p in problems if p[0] == problem_id), None)
        return problem[7] if problem else None

    def get_problem_by_id(self, problem_id: int) -> tuple:
        """Получить проблему по ID"""
        problems = self.db.get_problems()
        return next((p for p in problems if p[0] == problem_id), None)

    def get_problems_by_status(self, status: str) -> list:
        """Получить проблемы по статусу"""
        return self.db.get_problems(status=status)

    def get_all_problems(self) -> list:
        """Получить все проблемы"""
        return self.db.get_problems()

    def format_problem_message(self, problem: tuple) -> str:
        """Форматировать сообщение о проблеме"""
        problem_id, driver_id, driver_name, car_brand, car_number, problem_type, description, status, created_at, resolved_at = problem

        status_icon = "🔴" if status == 'актуально' else "✅"
        status_text = "АКТУАЛЬНА" if status == 'актуально' else "РЕШЕНА"

        message = f"""
{status_icon} **ЗАЯВКА #{problem_id}**

👤 **Водитель:** {driver_name} (ID: {driver_id})
🚗 **Автомобиль:** {car_brand} {car_number}
📋 **Тип проблемы:** {problem_type}
📝 **Описание:** {description}

📅 **Создана:** {created_at}
🔄 **Статус:** {status_text}
"""

        if resolved_at:
            message += f"✅ **Решена:** {resolved_at}"

        return message

    def get_stats_message(self) -> str:
        """Получить статистику в виде сообщения"""
        stats = self.db.get_stats()
        return f"""
📊 Статистика проблем:

• Всего заявок: {stats[0]}
• Актуальные проблемы: {stats[1]}
• Решенные проблемы: {stats[2]}
• Процент решенных: {(stats[2] / stats[0] * 100) if stats[0] > 0 else 0:.1f}%
"""