import yaml
import os
from datetime import datetime

class RatesManager:
    def __init__(self):
        self.filepath = "settings.yml"
        self.default_settings = {
            "rates": {
                "daily_salary": 600.00,
                "overtime_hourly_rate": 75.00,
                "night_diff_multiplier": 0.10
            }
        }
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            self.save_all_settings(self.default_settings)

    def get_all_settings(self):
        with open(self.filepath, 'r') as file:
            return yaml.safe_load(file)

    def save_all_settings(self, new_data):
        with open(self.filepath, 'w') as file:
            yaml.dump(new_data, file, default_flow_style=False)

    def get_today_date(self):
        return datetime.today().strftime("%d/%m/%Y")

    def get_daily_salary(self):
        return self.get_all_settings()["rates"].get("daily_salary", 600.00)

    def get_overtime_rate(self):
        return self.get_all_settings()["rates"].get("overtime_hourly_rate", 75.00)

    def calculate_night_diff(self):
        base = self.get_daily_salary()
        multiplier = self.get_all_settings()["rates"].get("night_diff_multiplier", 0.10)
        return base * multiplier

    def calculate_overtime_pay(self, clock_in_str, clock_out_str):
        try:
            t1 = datetime.strptime(clock_in_str, "%H:%M")
            t2 = datetime.strptime(clock_out_str, "%H:%M")
            duration = t2 - t1
            total_hours = duration.total_seconds() / 3600
            if total_hours < 0:
                total_hours += 24
            if total_hours > 8:
                ot_hours = total_hours - 8
                ot_rate = self.get_overtime_rate()
                return round(ot_hours * ot_rate, 2)
            return 0.0
        except:
            return 0.0