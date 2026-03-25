import customtkinter as ctk
import sqlite3 as sql
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from datetime import datetime


class PayrollFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        #self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)
        #self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.header = ctk.CTkLabel(self, text="Payroll Processing", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw")

        """ CONTROL FRAME """
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, sticky="nsew")
        #self.controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.main_controls_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.main_controls_frame.grid(row=0, column=0, padx=0, sticky="nsew")

        # Date Entry
        self.date_entry_label = ctk.CTkLabel(self.main_controls_frame, text="Enter the Pay Period\nStart Date:", font=("Arial", 14, "bold"))
        self.date_entry_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

        self.date_var = CTkStringVar(value="")
        self.date_entry = DateEntry(self.main_controls_frame, width=150, variable=self.date_var, state="readonly")
        self.date_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="ew")

        # Employee Selection
        self.employee_menu_label = ctk.CTkLabel(self.main_controls_frame, text="Select an employee:", font=("Arial", 14, "bold"))
        self.employee_menu_label.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")

        self.employee_var = ctk.StringVar(value="")
        self.employee_menu = ctk.CTkOptionMenu(self.main_controls_frame, values=["1", "2", "3"], variable=self.employee_var)
        self.employee_menu.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")

        # Data View Radiobuttons
        self.dataview_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.dataview_frame.grid(row=0, column=1, padx=(50, 0), sticky="nsew")

        self.dataview_var = ctk.StringVar(value="cost_view")
        self.cost_view_radiobutton = ctk.CTkRadioButton(self.dataview_frame, text="Cost View", font=("Arial", 14, "bold"),
                                                        value="cost_view", variable=self.dataview_var)
        self.cost_view_radiobutton.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.hour_view_radiobutton = ctk.CTkRadioButton(self.dataview_frame, text="Hour View", font=("Arial", 14, "bold"),
                                                        value="hour_view", variable=self.dataview_var)
        self.hour_view_radiobutton.grid(row=1, column=0, padx=10, pady=(15, 0), sticky="w")

        # Refresh Button
        self.refresh_button = ctk.CTkButton(self.dataview_frame, text="Refresh", command='self.load_attendance')
        self.refresh_button.grid(row=0, column=1, rowspan=2, padx=(50, 0), pady=(10, 0), sticky="ns")

        # Employee Details
        self.e_details_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.e_details_frame.grid(row=0, column=3, padx=(250, 0), sticky="e")

        self.e_id_label = ctk.CTkLabel(self.e_details_frame, text="Employee ID: [?]", font=("Arial", 14, "bold"))
        self.e_id_label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="e")

        self.e_role_label = ctk.CTkLabel(self.e_details_frame, text="Role: [?]", font=("Arial", 14, "bold"))
        self.e_role_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")


        """ WEEKLY PAYROLL DATA """
        self.weekly_frame1 = WeeklyPayrollFrame(self)
        self.weekly_frame1.grid(row=2, column=0, pady=(15, 0), sticky="ns")

        self.weekly_frame2 = WeeklyPayrollFrame(self)
        self.weekly_frame2.grid(row=3, column=0, pady=(15, 0), sticky="ns")


        """ BIWEEKLY TOTALS """
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(row=4, column=0, pady=20, sticky="ns")

        self.summary_header = ctk.CTkLabel(self.summary_frame, text="BIWEEKLY  SUMMARY", font=("Arial", 20, "bold"))
        self.summary_header.grid(row=0, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="n")

        # GROSS PAY
        self.gross_pay_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.gross_pay_frame.grid(row=1, column=0, padx=40, sticky="ns")
        vertical_labels = ["Regular Pay", "Overtime Pay", "Night Differential", "GROSS PAY"]

        for row, text in enumerate(vertical_labels, 0):
            label = ctk.CTkLabel(self.gross_pay_frame, text=text, font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="nw")

        for row, text in enumerate(vertical_labels, 0):
            if row != 3:
                label = ctk.CTkLabel(self.gross_pay_frame, text=str(row), font=("Arial", 14))
            else:
                label = ctk.CTkLabel(self.gross_pay_frame, text=str(row), font=("Arial", 16, "bold"))

            label.grid(row=row, column=1, padx=(40, 0), pady=(0, 10), sticky="nw")

        # DEDUCTIONS
        self.deduction_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.deduction_frame.grid(row=1, column=1, padx=40, sticky="ns")
        vertical_labels = ["Deduction 1", "Deduction 2", "Deduction 3", "NET PAY"]

        for row, text in enumerate(vertical_labels, 0):
            label = ctk.CTkLabel(self.deduction_frame, text=text, font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="nw")

        for row, text in enumerate(vertical_labels, 0):
            if row != 3:
                label = ctk.CTkLabel(self.deduction_frame, text=str(row), font=("Arial", 14))
            else:
                label = ctk.CTkLabel(self.deduction_frame, text=str(row), font=("Arial", 16, "bold"))

            label.grid(row=row, column=1, padx=(40, 0), pady=(0, 10), sticky="nw")

        # EXPORT PAY SLIP
        self.export_button = ctk.CTkButton(self.summary_frame, text="Export Pay Slip (.pdf)", fg_color="#1E8449",
                                           hover_color="#196B3C", command='self.load_attendance')
        self.export_button.grid(row=1, column=2, padx=80, pady=(0, 10), sticky="nsew")


class WeeklyPayrollFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        #self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        '''self.weekly_frame = ctk.CTkFrame(self,
                                         fg_color="transparent",
                                         corner_radius=10,
                                         border_color="#1f538d",
                                         border_width=2,
                                         width=1000,
                                         height=180)'''
        self.weekly_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#1f538d")
        self.weekly_frame.grid(row=0, column=0, sticky="ns")
        self.weekly_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        #self.weekly_frame.grid_propagate(False)
        #self.weekly_frame.pack_propagate(False)

        self.add_header_labels()
        self.load_cost_data()


    def add_header_labels(self):
        vertical_labels = ["Regular Pay", "Overtime Pay", "Night Differential"]
        horizontal_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "TOTAL"] # TEMP VALUES

        for row, text in enumerate(vertical_labels, 1):
            label = ctk.CTkLabel(self.weekly_frame, text=text, font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=(20, 0), pady=(0, 10), sticky="nw")

        for column, text in enumerate(horizontal_labels, 1):
            label = ctk.CTkLabel(self.weekly_frame, text=text, font=("Arial", 16, "bold"))
            label.grid(row=0, column=column, padx=25, pady=10, sticky="n")

        weekly_total_label = ctk.CTkLabel(self.weekly_frame, text="WEEKLY TOTAL", font=("Arial", 16, "bold"))
        weekly_total_label.grid(row=4, column=6, columnspan=2, padx=25, pady=(0, 10), sticky="n")


    def load_cost_data(self):
        for row in range(1, 4):
            for column in range(1, 9):
                label = ctk.CTkLabel(self.weekly_frame, text=str(column), font=("Arial", 14))
                label.grid(row=row, column=column, padx=25, pady=(0, 10), sticky="n")

        label = ctk.CTkLabel(self.weekly_frame, text="1000", font=("Arial", 16, "bold"))
        label.grid(row=4, column=8, padx=25, pady=(0, 10), sticky="n")

    #def load_hour_data(self):


