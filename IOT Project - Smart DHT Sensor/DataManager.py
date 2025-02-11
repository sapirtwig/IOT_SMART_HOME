import sqlite3
from datetime import datetime

class DataManager:
    def __init__(self, db_name="sensor_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def save_data(self, temperature, humidity):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO sensor_data (timestamp, temperature, humidity)
            VALUES (?, ?, ?)
        ''', (timestamp, temperature, humidity))
        self.conn.commit()

    def check_alarms(self, temperature, humidity):
        if temperature < 18:
            return "Warning: Low Temperature!"
        if humidity > 85:
            return "Warning: High Humidity!"
        return "Info: Normal Conditions"

    def get_all_data(self):
        self.cursor.execute('SELECT * FROM sensor_data')
        rows = self.cursor.fetchall()
        return rows

    def get_data_by_date(self, start_date, end_date):
        self.cursor.execute('''
            SELECT * FROM sensor_data WHERE timestamp BETWEEN ? AND ?
        ''', (start_date, end_date))
        rows = self.cursor.fetchall()
        return rows

    def close(self):
        self.conn.close()
