import customtkinter as ctk
import sqlite3 as sql
from tkcalendar import DateEntry

class ManagementFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Configure 3 columns to be equal width
        self.grid_columnconfigure((0, 1, 2), weight=1)
        # Configure the chart row to expand and take up the bottom space
        self.grid_rowconfigure(4, weight=1)

        # 1. Headers
        self.header = ctk.CTkLabel(self, text="Employee Management and Attendance Tracking", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw", columnspan=3)

        self.date_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_controls_frame.grid(row=3, column=0, columnspan=3, padx=20, sticky="w")

        self.chart_label = ctk.CTkLabel(self.date_controls_frame, text="Enter a Date:", font=("Arial", 14, "bold"))
        self.chart_label.grid(row=3, column=0, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")

        self.date_entry = DateEntry(self.date_controls_frame, width=15, background="#1f538d",
                        foreground="white", borderwidth=2,
                        date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=3, column=1, columnspan=1, pady=(4, 0), padx=(0, 10), sticky="w")

        self.save_button = ctk.CTkButton(self.date_controls_frame, text="Save Date")
        self.save_button.grid(row=3, column=2, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")