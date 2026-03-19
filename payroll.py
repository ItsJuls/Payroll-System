import customtkinter as ctk
import sqlite3 as sql
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from datetime import datetime


class PayrollFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.header = ctk.CTkLabel(self, text="Payroll Processing", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw", columnspan=3)


        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, columnspan=4, padx=20, sticky="w")

        self.date_var = CTkStringVar(value="")
        self.date_entry = DateEntry(self.controls_frame, width=150, variable=self.date_var, state="readonly")
        self.date_entry.grid(row=0, column=1, pady=(1, 0), padx=(0, 10), sticky="w")

        self.date_entry_label = ctk.CTkLabel(self.controls_frame, text="Enter the Pay Period\nStart Date:", font=("Arial", 14, "bold"))
        self.date_entry_label.grid(row=0, column=0, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")


        self.employee_var = ctk.StringVar(value="")
        self.employee_menu = ctk.CTkOptionMenu(self.controls_frame, values=["1", "2", "3"], variable=self.employee_var)
        self.employee_menu.grid(row=1, column=1, padx=5)

        self.employee_menu_label = ctk.CTkLabel(self.controls_frame, text="Select an employee:", font=("Arial", 14, "bold"))
        self.employee_menu_label.grid(row=1, column=0, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")


        self.dataview_var = ctk.StringVar(value="")
        self.cost_view_radiobutton = ctk.CTkRadioButton(self.controls_frame, text="Cost View", value="cost_view", variable=self.dataview_var)
        self.cost_view_radiobutton.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="w")

        self.hour_view_radiobutton = ctk.CTkRadioButton(self.controls_frame, text="Hour View", value="hour_view", variable=self.dataview_var)
        self.hour_view_radiobutton.grid(row=1, column=2, padx=10, pady=(10, 0), sticky="w")


        self.refresh_button = ctk.CTkButton(self.controls_frame, text="Refresh", command='self.load_attendance')
        self.refresh_button.grid(row=1, column=3, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")


        self.e_id_label = ctk.CTkLabel(self.controls_frame, text="Employee ID: [?]", font=("Arial", 14, "bold"))
        self.e_id_label.grid(row=0, column=4, padx=10, pady=(0, 10), sticky="e")

        self.e_role_label = ctk.CTkLabel(self.controls_frame, text="Role: [?]", font=("Arial", 14, "bold"))
        self.e_role_label.grid(row=1, column=4, padx=10, pady=(0, 10), sticky="e")


        self.weekly_frame = WeeklyPayrollFrame(self)
        self.weekly_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="n")

class WeeklyPayrollFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.accent_frame = ctk.CTkFrame(self,
                                         fg_color="transparent",
                                         corner_radius=10,
                                         border_color="#1f538d",
                                         border_width=2,
                                         width=1000,
                                         height=180)
        self.accent_frame.grid(row=0, column=0, columnspan=3, sticky="n")
        self.accent_frame.grid_propagate(False)
        self.accent_frame.pack_propagate(False)

        self.add_header_labels()


    def add_header_labels(self):
        vertical_labels = ["Regular Pay", "Overtime Pay", "Night Differential"]
        horizontal_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] # TEMP VALUES

        for row, text in enumerate(vertical_labels, 1):
            label = ctk.CTkLabel(self.accent_frame, text=text, font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=(20, 0), pady=(10, 0), sticky="nw")

        for column, text in enumerate(horizontal_labels, 1):
            label = ctk.CTkLabel(self.accent_frame, text=text, font=("Arial", 16, "bold"))
            label.grid(row=0, column=column, padx=(25, 0), pady=(15, 0), sticky="nw")


