import yaml
import os
from datetime import datetime


class RatesManager:
    def __init__(self):
        self.filepath = "settings.yml"
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            default_data = {
                "rates": {
                    "daily_salary": 600.0,
                    "overtime_hourly_rate": 75.0,
                    "night_diff_multiplier": 0.1
                },
                "shifts": {
                    "shift_1": {"in": "06:00", "out": "14:00"},
                    "shift_2": {"in": "14:00", "out": "22:00"},
                    "shift_3": {"in": "22:00", "out": "06:00"}
                },
                "deductions": {
                    "sss_rate": 0.045, "phil_health_rate": 0.04, "pag_ibig_rate": 0.02
                }
            }
            self.save_all_settings(default_data)

    def get_all_settings(self):
        try:
            with open(self.filepath, 'r') as file:
                return yaml.safe_load(file)
        except:
            return {}

    def save_all_settings(self, new_data):
        with open(self.filepath, 'w') as file:
            yaml.dump(new_data, file, default_flow_style=False, sort_keys=False)

    def get_today_date(self):
        return datetime.today().strftime("%d/%m/%Y")

    def get_shift_defaults(self, shift_num):
        settings = self.get_all_settings()
        shift_key = f"shift_{shift_num}"
        return settings.get("shifts", {}).get(shift_key, {"in": "00:00", "out": "00:00"})

    def calculate_full_pay(self, shift_num, clock_in, clock_out):
        """ The master math function for the Dashboard and Payroll reports """
        settings = self.get_all_settings()
        rates = settings.get("rates", {})

        daily_base = rates.get("daily_salary", 600.0)
        ot_rate = rates.get("overtime_hourly_rate", 75.0)
        nd_multiplier = rates.get("night_diff_multiplier", 0.1)

        try:
            # 1. Calculate Duration
            fmt = "%H:%M"
            t1 = datetime.strptime(clock_in, fmt)
            t2 = datetime.strptime(clock_out, fmt)

            diff = t2 - t1
            hours_worked = diff.total_seconds() / 3600
            if hours_worked < 0: hours_worked += 24  # Handle midnight cross

            # 2. Overtime Math (Anything over 8 hours)
            ot_pay = 0.0
            ot_hours_worked = 0.0
            if hours_worked > 8:
                ot_hours_worked = hours_worked - 8
                ot_pay = ot_hours_worked * ot_rate

            # 3. Night Differential (Only for Shift 3)
            nd_pay = (daily_base * nd_multiplier) if int(shift_num) == 3 else 0.0

            # 4. Total Calculation
            total = daily_base + ot_pay + nd_pay

            return {
                "regular": round(daily_base, 2),
                "overtime": round(ot_pay, 2),
                "night_diff": round(nd_pay, 2),
                "gross_total": round(total, 2),
                "reg_hours": round(hours_worked, 2),
                "ot_hours": round(ot_hours_worked, 2)
            }
        except Exception as e:
            print(f"Math Error: {e}")
            return {"regular": 0, "overtime": 0, "night_diff": 0, "gross_total": 0, "reg_hours": 0, "ot_hours": 0}