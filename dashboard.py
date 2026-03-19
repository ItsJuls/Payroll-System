import customtkinter as ctk
import matplotlib.pyplot as plt
import sqlite3 as sql
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from datetime import datetime


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Configure 3 columns to be equal width
        self.grid_columnconfigure((0, 1, 2), weight=1)
        # Configure the chart row to expand and take up the bottom space
        self.grid_rowconfigure(4, weight=1)

        # 1. Headers
        self.header = ctk.CTkLabel(self, text="Dashboard Overview", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw", columnspan=3)

        self.sub_label = ctk.CTkLabel(self, text="Real-time Payroll Summary", font=("Arial", 16))
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nw", columnspan=3)

        self.date_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_controls_frame.grid(row=3, column=0, columnspan=3, padx=20, sticky="w")

        self.date_var = CTkStringVar(value="")
        self.date_entry = DateEntry(self.date_controls_frame, width=150, variable=self.date_var, state="readonly")
        self.date_entry.grid(row=3, column=1, pady=(1, 0), padx=(0, 10), sticky="w")

        self.chart_label = ctk.CTkLabel(self.date_controls_frame, text="Enter a Date:", font=("Arial", 14, "bold"))
        self.chart_label.grid(row=3, column=0, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")

        self.refresh_button = ctk.CTkButton(self.date_controls_frame, text="Refresh")
        self.refresh_button.grid(row=3, column=2, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")


        self.accent_frame = ctk.CTkFrame(self,
                                         fg_color="transparent",
                                         corner_radius=10,
                                         border_color="#1f538d",
                                         border_width=2,
                                         width=1200,
                                         height=300)
        self.accent_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="n")
        self.accent_frame.grid_propagate(False)
        self.accent_frame.pack_propagate(False)

        self.employees_present = ctk.CTkLabel(self.accent_frame, text="Employees\nPresent", font=("Arial", 16))
        self.employees_present.place(relx=0.20, rely=0.05, anchor="n")

        self.total_reg_pay = ctk.CTkLabel(self.accent_frame, text="Total\nRegular Pay", font=("Arial", 16))
        self.total_reg_pay.place(relx=0.35, rely=0.05, anchor="n")

        self.total_ot_pay = ctk.CTkLabel(self.accent_frame, text="Total\nOvertime Pay", font=("Arial", 16))
        self.total_ot_pay.place(relx=0.50, rely=0.05, anchor="n")

        self.total_night_diff = ctk.CTkLabel(self.accent_frame, text="Total Night\nDifferential", font=("Arial", 16))
        self.total_night_diff.place(relx=0.65, rely=0.05, anchor="n")

        self.total_night_diff = ctk.CTkLabel(self.accent_frame, text="Total Daily Payroll", font=("Arial", 16))
        self.total_night_diff.place(relx=0.65, rely=0.9, anchor="s")


        self.cost_per_shift = ctk.CTkLabel(self.accent_frame, text="Cost Per Shift", font=("Arial", 16))
        self.cost_per_shift.place(relx=0.80, rely=0.05, anchor="n")



    def add_stat_card(self, title, value, row, col):
        card = ctk.CTkFrame(self, corner_radius=15, height=120)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.pack_propagate(False)

        title_lbl = ctk.CTkLabel(card, text=title, font=("Arial", 14))
        title_lbl.pack(pady=(20, 5))

        value_lbl = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color="#1f538d")
        value_lbl.pack(pady=(0, 20))