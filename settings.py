import customtkinter as ctk
import yaml
import os
from CTkMessagebox import CTkMessagebox as cmb


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.settings_file = "settings.yml"
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(self, text="SETTINGS", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw")

        # Scrollable container in case we add more settings later
        self.form_container = ctk.CTkScrollableFrame(self, border_width=2, border_color="#1f538d", corner_radius=10,
                                                     fg_color="transparent")
        self.form_container.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")
        self.form_container.grid_columnconfigure(0, weight=1)

        self.inner_form = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.inner_form.pack(pady=20, padx=20)

        # 1. Define ALL labels including new Shift labels
        labels = [
            "Regular Pay Rate (Php / 8 hours)",
            "Overtime Pay Rate (Php / hour)",
            "Night Differential (Decimal e.g., 0.10)",
            "Deduction Rate 1",
            "Deduction Rate 2",
            "Deduction Rate 3",
            "Shift 1: Start Time (HH:MM)", "Shift 1: End Time (HH:MM)",
            "Shift 2: Start Time (HH:MM)", "Shift 2: End Time (HH:MM)",
            "Shift 3: Start Time (HH:MM)", "Shift 3: End Time (HH:MM)"
        ]

        self.entries = {}

        for i, text in enumerate(labels):
            # Add a separator label before shifts for better UI

            lbl = ctk.CTkLabel(self.inner_form, text=text, font=("Arial", 16))
            lbl.grid(row=i + 10, column=0, padx=20, pady=10, sticky="w")  # row offset for safety

            ent = ctk.CTkEntry(self.inner_form, width=200, justify="center")
            ent.grid(row=i + 10, column=1, padx=20, pady=10, sticky="e")
            self.entries[text] = ent

        self.save_btn = ctk.CTkButton(self.form_container, text="Save Settings", font=("Arial", 16, "bold"),
                                      command=self.save_settings, width=200, height=40, fg_color="green",
                                      hover_color="#006400")
        self.save_btn.pack(pady=30)

        self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            return

        with open(self.settings_file, "r") as file:
            data = yaml.safe_load(file)

        rates = data.get("rates", {})
        deductions = data.get("deductions", {})
        shifts = data.get("shifts", {})

        # Fill Rates
        self.entries["Regular Pay Rate (Php / 8 hours)"].insert(0, str(rates.get("daily_salary", "0.00")))
        self.entries["Overtime Pay Rate (Php / hour)"].insert(0, str(rates.get("overtime_hourly_rate", "0.00")))
        self.entries["Night Differential (Decimal e.g., 0.10)"].insert(0,
                                                                       str(rates.get("night_diff_multiplier", "0.00")))

        # Fill Deductions
        self.entries["Deduction Rate 1"].insert(0, str(deductions.get("deduction_1", "0.00")))
        self.entries["Deduction Rate 2"].insert(0, str(deductions.get("deduction_2", "0.00")))
        self.entries["Deduction Rate 3"].insert(0, str(deductions.get("deduction_3", "0.00")))

        # Fill Shifts
        for i in range(1, 4):
            s_data = shifts.get(f"shift_{i}", {"in": "00:00", "out": "00:00"})
            self.entries[f"Shift {i}: Start Time (HH:MM)"].insert(0, s_data['in'])
            self.entries[f"Shift {i}: End Time (HH:MM)"].insert(0, s_data['out'])

    def save_settings(self):
        try:
            new_data = {
                "rates": {
                    "daily_salary": float(self.entries["Regular Pay Rate (Php / 8 hours)"].get()),
                    "overtime_hourly_rate": float(self.entries["Overtime Pay Rate (Php / hour)"].get()),
                    "night_diff_multiplier": float(self.entries["Night Differential (Decimal e.g., 0.10)"].get())
                },
                "shifts": {
                    "shift_1": {"in": self.entries["Shift 1: Start Time (HH:MM)"].get(),
                                "out": self.entries["Shift 1: End Time (HH:MM)"].get()},
                    "shift_2": {"in": self.entries["Shift 2: Start Time (HH:MM)"].get(),
                                "out": self.entries["Shift 2: End Time (HH:MM)"].get()},
                    "shift_3": {"in": self.entries["Shift 3: Start Time (HH:MM)"].get(),
                                "out": self.entries["Shift 3: End Time (HH:MM)"].get()}
                },
                "deductions": {
                    "deduction_1": float(self.entries["Deduction Rate 1"].get()),
                    "deduction_2": float(self.entries["Deduction Rate 2"].get()),
                    "deduction_3": float(self.entries["Deduction Rate 3"].get())
                }
            }

            with open(self.settings_file, "w") as file:
                yaml.dump(new_data, file, default_flow_style=False, sort_keys=False)

            cmb(title="Success", message="Settings and Shifts saved successfully!", icon="check")

        except ValueError:
            cmb(title="Input Error", message="Rates and Deductions must be numbers.", icon="warning")