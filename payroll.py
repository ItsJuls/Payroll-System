import customtkinter as ctk
import sqlite3 as sql
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from rates import RatesManager
from datetime import datetime, timedelta


class PayrollFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rm = RatesManager()

        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(self, text="Payroll Processing", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw")

        """ CONTROL FRAME """
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, sticky="nsew")

        self.main_controls_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.main_controls_frame.grid(row=0, column=0, padx=0, sticky="nsew")

        # Date Entry
        self.date_entry_label = ctk.CTkLabel(self.main_controls_frame, text="Enter a Date:", font=("Arial", 14, "bold"))
        self.date_entry_label.grid(row=0, column=0, pady=(10, 0), sticky="w")

        self.date_var = CTkStringVar(value=self.rm.get_today_date())
        self.date_entry = DateEntry(self.main_controls_frame, width=150, variable=self.date_var, state="readonly")
        self.date_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="ew")

        # Employee Selection
        self.employee_menu_label = ctk.CTkLabel(self.main_controls_frame, text="Select an Employee:", font=("Arial", 14, "bold"))
        self.employee_menu_label.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="w")

        # retrieve the list of employee names
        conn = sql.connect("payroll_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT employee_name, employee_name FROM attendance GROUP BY employee_name ORDER BY employee_name ASC")
        raw_e_names = cursor.fetchall()
        conn.close()

        e_names = []
        for name, misc in raw_e_names:
            e_names.append(name)

        self.employee_var = ctk.StringVar(value="")
        self.employee_menu = ctk.CTkOptionMenu(self.main_controls_frame, values=e_names, variable=self.employee_var)
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
        self.refresh_button = ctk.CTkButton(self.dataview_frame, text="Refresh", command=self.refresh_payroll)
        self.refresh_button.grid(row=0, column=1, rowspan=2, padx=(50, 0), pady=(10, 0), sticky="ns")

        # Employee Details
        self.e_details_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.e_details_frame.grid(row=0, column=3, padx=(235, 0), sticky="e")

        self.e_id_label = ctk.CTkLabel(self.e_details_frame, text="Employee ID:", font=("Arial", 14, "bold"))
        self.e_id_label.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="w")

        self.e_id_var = ctk.StringVar(value="?")
        self.e_id_display = ctk.CTkLabel(self.e_details_frame, textvariable=self.e_id_var, font=("Arial", 14, "bold"))
        self.e_id_display.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w")

        self.e_role_label = ctk.CTkLabel(self.e_details_frame, text="Role:", font=("Arial", 14, "bold"))
        self.e_role_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        self.e_role_var = ctk.StringVar(value="?")
        self.e_role_display = ctk.CTkLabel(self.e_details_frame, textvariable=self.e_role_var, font=("Arial", 14, "bold"))
        self.e_role_display.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")


        """ WEEKLY PAYROLL DATA """
        self.weekly_frame1 = WeeklyPayrollFrame(self, self.date_var, self.dataview_var, self.employee_var)
        self.weekly_frame1.grid(row=2, column=0, pady=(15, 0), sticky="ns")

        next_week_date = CTkStringVar(value=(datetime.strptime(self.date_var.get(), "%d/%m/%Y") + timedelta(days=7)).strftime("%d/%m/%Y"))

        self.weekly_frame2 = WeeklyPayrollFrame(self, next_week_date, self.dataview_var, self.employee_var)
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
                                           hover_color="#196B3C", command='self.test')
        self.export_button.grid(row=1, column=2, padx=80, pady=(0, 10), sticky="nsew")


        """ REFRESH DATA SETUP """
        self.refresh_payroll()



    def refresh_payroll(self):
        '''

        conn = sql.connect("payroll_system.db")
        cursor = conn.cursor()

        for i in range(7):
            current_day = start_of_week + timedelta(days=7)
            day_str = current_day.strftime("%Y-%m-%d")
            cursor.execute("SELECT shift, clock_in, clock_out FROM attendance WHERE date = ?", (day_str,))
            day_rows = cursor.fetchall()'''

        # update employee details
        if self.employee_var.get() != "":
            conn = sql.connect("payroll_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT employee_id, role FROM attendance WHERE employee_name = ? GROUP BY employee_id, role",
                           (self.employee_var.get(),))
            e_details = cursor.fetchall()
            conn.close()
            #print(e_details)

            self.e_id_var.set(e_details[0][0])
            self.e_role_var.set(e_details[0][1])

        # update weekly header labels and data
        self.weekly_frame1.update_all()
        self.weekly_frame2.update_all()




class WeeklyPayrollFrame(ctk.CTkFrame):
    def __init__(self, master, raw_date, dataview_mode, e_name, **kwargs):
        super().__init__(master, **kwargs)

        self.raw_date = raw_date
        self.dataview_mode = dataview_mode
        self.e_name = e_name
        #self.vertical_labels = vertical_labels
        #self.horizontal_labels = date_labels

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

        # DEFAULT / PLACEHOLDER VALUES
        self.vertical_labels = {
            "reg": ctk.StringVar(value="Regular"), "ot": ctk.StringVar(value="Overtime"), "nd": ctk.StringVar(value="Night")
        }

        self.horizontal_labels = {
            "mon": ctk.StringVar(value="Monday"), "tue": ctk.StringVar(value="Tuesday"), "wed": ctk.StringVar(value="Wednesday"),
            "thu": ctk.StringVar(value="Thursday"), "fri": ctk.StringVar(value="Friday"), "sat": ctk.StringVar(value="Saturday"),
            "sun": ctk.StringVar(value="Sunday"), "total": ctk.StringVar(value="TOTAL")
        }

        self.weekly_data = {
            "reg": {"mon": ctk.StringVar(value="1"), "tue": ctk.StringVar(value="2"), "wed": ctk.StringVar(value="3"),
                    "thu": ctk.StringVar(value="4"), "fri": ctk.StringVar(value="5"), "sat": ctk.StringVar(value="6"),
                    "sun": ctk.StringVar(value="7"), "total": ctk.StringVar(value="8")},
            "ot": {"mon": ctk.StringVar(value="1"), "tue": ctk.StringVar(value="2"), "wed": ctk.StringVar(value="3"),
                    "thu": ctk.StringVar(value="4"), "fri": ctk.StringVar(value="5"), "sat": ctk.StringVar(value="6"),
                    "sun": ctk.StringVar(value="7"), "total": ctk.StringVar(value="8")},
            "nd": {"mon": ctk.StringVar(value="1"), "tue": ctk.StringVar(value="2"), "wed": ctk.StringVar(value="3"),
                    "thu": ctk.StringVar(value="4"), "fri": ctk.StringVar(value="5"), "sat": ctk.StringVar(value="6"),
                    "sun": ctk.StringVar(value="7"), "total": ctk.StringVar(value="8")},
        }

        self.weekly_total = ctk.StringVar(value="1000")

        # try:
        selected_date = datetime.strptime(self.raw_date.get(), "%d/%m/%Y")
        #self.db_date_str = selected_date.strftime("%Y-%m-%d")
        # except:
        #   return

        self.start_of_week = selected_date - timedelta(days=selected_date.weekday())
        self.db_date_str = self.start_of_week.strftime("%Y-%m-%d")

        self.add_header_labels()
        self.add_placeholder_data()


    def add_header_labels(self):

        for row, key in enumerate(self.vertical_labels, 1):
            label = ctk.CTkLabel(self.weekly_frame, textvariable=self.vertical_labels[key], font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=(20, 0), pady=(0, 10), sticky="nw")

        for column, key in enumerate(self.horizontal_labels, 1):
            label = ctk.CTkLabel(self.weekly_frame, textvariable=self.horizontal_labels[key], font=("Arial", 16, "bold"))
            label.grid(row=0, column=column, padx=25, pady=10, sticky="n")

        weekly_total_label = ctk.CTkLabel(self.weekly_frame, text="WEEKLY TOTAL", font=("Arial", 16, "bold"))
        weekly_total_label.grid(row=4, column=6, columnspan=2, padx=25, pady=(0, 10), sticky="n")


    def add_placeholder_data(self):
        for row, main_key in enumerate(["reg", "ot", "nd"], 1):
            for column, day_key in enumerate(self.weekly_data[main_key].keys(), 1):
                label = ctk.CTkLabel(self.weekly_frame, textvariable=self.weekly_data[main_key][day_key], font=("Arial", 14))
                label.grid(row=row, column=column, padx=25, pady=(0, 10), sticky="n")

        label = ctk.CTkLabel(self.weekly_frame, textvariable=self.weekly_total, font=("Arial", 16, "bold"))
        label.grid(row=4, column=8, padx=25, pady=(0, 10), sticky="n")


    def update_all(self):
        self.update_labels()
        self.update_data()


    def update_labels(self):
        # VERTICAL LABELS
        if self.dataview_mode.get() == "cost_view":
            self.vertical_labels["reg"].set("Regular Pay")
            self.vertical_labels["ot"].set("Overtime Pay")
            self.vertical_labels["nd"].set("Night Differential")

        elif self.dataview_mode.get() == "hour_view":
            self.vertical_labels["reg"].set("Regular Hours")
            self.vertical_labels["ot"].set("Overtime Hours")
            self.vertical_labels["nd"].set("Night Hours")

        # HORIZONTAL LABELS (DATES)
        for i, key in enumerate(self.horizontal_labels):
            if key == "total":
                break

            new_date = self.start_of_week + timedelta(days=i)
            self.horizontal_labels[key].set(new_date.strftime("%b. %d"))


    def update_data(self):
        # need to cycle through all dates
        conn = sql.connect("payroll_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT shift, clock_in, clock_out FROM attendance WHERE date = ? AND employee_name = ?",
                       (self.db_date_str, self.e_name.get()))
        e_details = cursor.fetchall()
        conn.close()
        print(e_details)
