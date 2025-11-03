import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name="taxi_bot.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Создаем таблицы если их нет"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблица проблем
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                driver_name TEXT NOT NULL,
                car_brand TEXT NOT NULL,
                car_number TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'актуально',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP NULL
            )
        ''')

        conn.commit()
        conn.close()

    def add_problem(self, driver_id, driver_name, car_brand, car_number, problem_type, description):
        """Добавляем новую проблему"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO problems 
            (driver_id, driver_name, car_brand, car_number, problem_type, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (driver_id, driver_name, car_brand, car_number, problem_type, description))

        conn.commit()
        problem_id = cursor.lastrowid
        conn.close()
        return problem_id

    def get_problems(self, status=None):
        """Получаем проблемы (все или по статусу)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if status:
            cursor.execute('''
                SELECT * FROM problems WHERE status = ? ORDER BY created_at DESC
            ''', (status,))
        else:
            cursor.execute('SELECT * FROM problems ORDER BY created_at DESC')

        problems = cursor.fetchall()
        conn.close()
        return problems

    def update_status(self, problem_id, status):
        """Обновляем статус проблемы"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        resolved_at = datetime.now() if status == 'решено' else None

        cursor.execute('''
            UPDATE problems 
            SET status = ?, resolved_at = ?
            WHERE id = ?
        ''', (status, resolved_at, problem_id))

        conn.commit()
        conn.close()

    def get_stats(self):
        """Статистика по проблемам"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'актуально' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'решено' THEN 1 ELSE 0 END) as resolved
            FROM problems
        ''')

        stats = cursor.fetchone()
        conn.close()
        return stats