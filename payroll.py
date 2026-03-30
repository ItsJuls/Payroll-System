import customtkinter as ctk
import sqlite3 as sql
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from rates import RatesManager
from datetime import datetime, timedelta
from tkinter import filedialog
from fpdf import FPDF


class PayrollFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rm = RatesManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

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
        for name, misc in raw_e_names: e_names.append(name)

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

        """ SCROLLABLE FRAME """
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew")
        self.scrollable_frame.columnconfigure(0, weight=1)

        """ WEEKLY PAYROLL DATA """
        self.weekly_frame1 = WeeklyPayrollFrame(self.scrollable_frame, self.date_var, self.dataview_var, self.employee_var)
        self.weekly_frame1.grid(row=0, column=0, pady=(15, 0), sticky="ns")

        self.next_week_date = CTkStringVar(value=(datetime.strptime(self.date_var.get(), "%d/%m/%Y") + timedelta(days=7)).strftime("%d/%m/%Y"))

        self.weekly_frame2 = WeeklyPayrollFrame(self.scrollable_frame, self.next_week_date, self.dataview_var, self.employee_var)
        self.weekly_frame2.grid(row=1, column=0, pady=(15, 0), sticky="ns")


        """ BIWEEKLY SUMMARY """
        self.summary_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.summary_frame.grid(row=2, column=0, pady=20, sticky="ns")

        self.summary_header = ctk.CTkLabel(self.summary_frame, text="BIWEEKLY  SUMMARY", font=("Arial", 20, "bold"))
        self.summary_header.grid(row=0, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="n")

        # DEFAULT / PLACEHOLDER VALUES
        self.summary_labels = {
            "reg": ctk.StringVar(value="Regular"), "ot": ctk.StringVar(value="Overtime"),
            "nd": ctk.StringVar(value="Night Differential"), "gross_total": ctk.StringVar(value="GROSS PAY"),
            "d1": "SSS", "d2": "PhilHeath", "d3": "Pag-IBIG", "net_total": "NET PAY"
        }

        self.summary_data = {
            "reg": ctk.StringVar(value="0.00"), "ot": ctk.StringVar(value="0.00"), "nd": ctk.StringVar(value="0.00"),
            "gross_total": ctk.StringVar(value="0.00"),
            "d1": ctk.StringVar(value="0.00"), "d2": ctk.StringVar(value="0.00"), "d3": ctk.StringVar(value="0.00"),
            "net_total": ctk.StringVar(value="0.00"),
        }

        summary_keys = []
        for misc, key in enumerate(self.summary_data.keys()):
            summary_keys.append(key)
        #print(summary_keys)

        # GROSS PAY
        self.gross_pay_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.gross_pay_frame.grid(row=1, column=0, padx=40, sticky="ns")

        for i, row in enumerate(range(4), 0):
            label = ctk.CTkLabel(self.gross_pay_frame, textvariable=self.summary_labels[summary_keys[i]], font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="nw")

        for i, row in enumerate(range(4), 0):
            if row != 3:
                label = ctk.CTkLabel(self.gross_pay_frame, textvariable=self.summary_data[summary_keys[i]], font=("Arial", 14))
            else:
                label = ctk.CTkLabel(self.gross_pay_frame, textvariable=self.summary_data[summary_keys[i]], font=("Arial", 16, "bold"))

            label.grid(row=row, column=1, padx=(40, 0), pady=(0, 10), sticky="nw")

        # DEDUCTIONS
        self.deduction_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        self.deduction_frame.grid(row=1, column=1, padx=40, sticky="ns")

        for i, row in enumerate(range(4), 4):
            label = ctk.CTkLabel(self.deduction_frame, text=self.summary_labels[summary_keys[i]], font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=20, pady=(0, 10), sticky="nw")

        for i, row in enumerate(range(4), 4):
            if row != 3:
                label = ctk.CTkLabel(self.deduction_frame, textvariable=self.summary_data[summary_keys[i]], font=("Arial", 14))
            else:
                label = ctk.CTkLabel(self.deduction_frame, textvariable=self.summary_data[summary_keys[i]], font=("Arial", 16, "bold"))

            label.grid(row=row, column=1, padx=(40, 0), pady=(0, 10), sticky="nw")

        # EXPORT PAY SLIP
        self.export_button = ctk.CTkButton(self.summary_frame, text="Export Pay Slip (.pdf)", fg_color="#1E8449",
                                           hover_color="#196B3C", command=self.export_payslip)
        self.export_button.grid(row=1, column=2, padx=80, pady=(0, 10), sticky="nsew")


        """ REFRESH THE SCREEN """
        self.refresh_payroll()


    def refresh_payroll(self):
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

        # update the date control for the 2nd week's data
        self.next_week_date.set((datetime.strptime(self.date_var.get(), "%d/%m/%Y") + timedelta(days=7)).strftime("%d/%m/%Y"))

        # update weekly header labels and data
        self.weekly_frame1.update_all()
        self.weekly_frame2.update_all()

        # update biweekly summary labels
        if self.dataview_var.get() == "cost_view":
            self.summary_labels['reg'].set("Regular Pay")
            self.summary_labels['ot'].set("Overtime Pay")
            self.summary_labels['gross_total'].set("GROSS PAY")

            total_reg = self.weekly_frame1.total_reg_pay + self.weekly_frame2.total_reg_pay
            total_ot = self.weekly_frame1.total_ot_pay + self.weekly_frame2.total_ot_pay
            total_nd = self.weekly_frame1.total_nd_pay + self.weekly_frame2.total_nd_pay
        else:
            self.summary_labels['reg'].set("Regular Hours")
            self.summary_labels['ot'].set("Overtime Hours")
            self.summary_labels['gross_total'].set("GRAND TOTAL HOURS")

            total_reg = self.weekly_frame1.total_reg_hours + self.weekly_frame2.total_reg_hours
            total_ot = self.weekly_frame1.total_ot_hours + self.weekly_frame2.total_ot_hours
            total_nd = "-"

        grand_total = self.weekly_frame1.grand_total + self.weekly_frame2.grand_total

        # update biweekly summary data
        # gross pay
        if self.dataview_var.get() == "cost_view":
            self.summary_data['reg'].set(f"₱ {total_reg:,.2f}")
            self.summary_data['ot'].set(f"₱ {total_ot:,.2f}")
            self.summary_data['nd'].set(f"₱ {total_nd:,.2f}")
            self.summary_data['gross_total'].set(f"₱ {grand_total:,.2f}")
        else:
            self.summary_data['reg'].set(f"{total_reg:,.2f}")
            self.summary_data['ot'].set(f"{total_ot:,.2f}")
            self.summary_data['nd'].set("-")
            self.summary_data['gross_total'].set(f"{grand_total:,.2f}")

        # deductions and net pay
        deduct_list = self.rm.get_all_settings().get("deductions", {})
        net_total = grand_total

        for i, key in enumerate(deduct_list, 1):
            deduct = grand_total * deduct_list[key]
            net_total -= deduct

            if self.dataview_var.get() == "cost_view":
                self.summary_data[f"d{i}"].set(f"-₱ {deduct:,.2f}")
            else:
                self.summary_data[f"d{i}"].set("-")

        if self.dataview_var.get() == "cost_view":
            self.summary_data['net_total'].set(f"₱ {net_total:,.2f}")
        else:
            self.summary_data['net_total'].set("-")


    def export_payslip(self):
        # prevents the export if no employee was selected
        if self.employee_var.get() == "":
            cmb(title="Error", message="Please select an employee and refresh first.", icon="cancel")
            return

        # forces the data view to be the cost view, if it isn't already
        if self.dataview_var.get() == "hour_view":
            self.dataview_var.set("cost_view")
            self.refresh_payroll()

        start_date = self.weekly_frame1.start_of_week
        end_date = datetime.strptime(self.date_var.get(), "%d/%m/%Y") + timedelta(days=7)

        # sets the file name
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Payslip_{self.employee_var.get()}_{start_date.strftime('%Y-%m-%d')}"
                        f"_to_{end_date.strftime('%Y-%m-%d')}.pdf"
        )

        if not file_path: return
        try:
            pdf = FPDF()
            pdf.add_page(orientation="L", format="A5")

            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, "Payslip", align="C")
            pdf.ln()

            pdf.set_font("Arial", "B", 10)
            pdf.cell(190, 5, f"Pay Period: {start_date.strftime("%b. %d, %Y")} to {end_date.strftime("%b. %d, %Y")}", align="C")
            pdf.ln()
            pdf.ln()

            # Employee Details
            e_detail_width = 35
            pdf.cell(e_detail_width, 8, "Employee Name:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(e_detail_width, 8, self.employee_var.get())
            pdf.ln()

            pdf.set_font("Arial", "B", 10)
            pdf.cell(e_detail_width, 5, "Role:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(e_detail_width, 5, self.e_role_var.get())
            pdf.ln()
            pdf.ln()

            # Headers
            widths = [48, 47, 48, 47]
            headers = ["Earnings", "Amount", "Deductions", "Amount"]
            details_l = ["Regular Pay", "Overtime Pay", "Night Differential", "Gross Salary"]
            keys = ["reg", "ot", "nd", "gross_total", "net_total"]

            pdf.set_font("Arial", "B", 10)
            for i, header in enumerate(headers): pdf.cell(widths[i], 8, header, align="C", border=1)
            pdf.ln()

            # Detail Rows
            pdf.set_font("Arial", "", 10)
            total_deduct = 0.0

            for i, label in enumerate(details_l):
                if i != len(details_l) - 1:
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(widths[0], 8, f"  {label}", border=1)
                    pdf.cell(widths[1], 8, f"{self.summary_data[keys[i]].get()[2:]}", align="C", border=1)

                    pdf.cell(widths[2], 8, f"  {self.summary_labels[f"d{i + 1}"]}", border=1)
                    pdf.cell(widths[3], 8, f"{self.summary_data[f"d{i+1}"].get()[3:]}", align="C", border=1)

                    total_deduct += float(self.summary_data[f"d{i + 1}"].get()[3:])
                else:
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(widths[0], 8, f"  {label}", border=1)
                    pdf.cell(widths[1], 8, f"{self.summary_data[keys[i]].get()[2:]}", align="C", border=1)

                    pdf.cell(widths[2], 8, "  Total Deductions", border=1)
                    pdf.cell(widths[3], 8, f"{total_deduct:,.2f}", align="C", border=1)

                pdf.ln()

            # Net Pay
            pdf.set_font("Arial", "B", 12)
            pdf.cell(sum(widths[0:3]), 8, "NET PAY  ", align="R", border=1)
            pdf.cell(widths[3], 8, self.summary_data['net_total'].get()[2:], align="C", border=1)
            pdf.ln()
            pdf.ln()

            # Signature
            pdf.set_font("Arial", "", 10)
            pdf.cell(40, 8, "Employee's Signature and Date")
            pdf.ln()
            pdf.cell(55, 8, "", border="B")
            pdf.ln()

            pdf.set_font("Arial", "", 6)
            pdf.cell(190, 8, "This is a system generated payslip.", align="R")

            pdf.output(file_path)       # saves the PDF file

        except Exception as e:
            cmb(title="Error", message=str(e), icon="cancel")



class WeeklyPayrollFrame(ctk.CTkFrame):
    def __init__(self, master, raw_date, dataview_mode, e_name, **kwargs):
        super().__init__(master, **kwargs)

        self.rm = RatesManager()
        self.raw_date = raw_date
        self.dataview_mode = dataview_mode
        self.e_name = e_name

        self.weekly_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#1f538d")
        self.weekly_frame.grid(row=0, column=0, sticky="ns")
        self.weekly_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)
        #self.weekly_frame.grid_propagate(False)
        #self.weekly_frame.pack_propagate(False)

        # DEFAULT / PLACEHOLDER VALUES
        self.vertical_labels = {
            "reg": ctk.StringVar(value="Regular"), "ot": ctk.StringVar(value="Overtime"), "nd": ctk.StringVar(value="Night Differential")
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

        selected_date = datetime.strptime(self.raw_date.get(), "%d/%m/%Y")
        self.start_of_week = selected_date - timedelta(days=selected_date.weekday())

        self.total_reg_pay = 0.0
        self.total_ot_pay = 0.0
        self.total_nd_pay = 0.0
        self.total_reg_hours = 0.0
        self.total_ot_hours = 0.0
        self.grand_total = 0.0

        # adds the headers and placeholder data
        self.add_header_labels()
        self.add_placeholder_data()


    def add_header_labels(self):
        # Vertical
        for row, key in enumerate(self.vertical_labels, 1):
            label = ctk.CTkLabel(self.weekly_frame, textvariable=self.vertical_labels[key], font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=(20, 0), pady=(0, 10), sticky="nw")

        # Horizontal
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
        # reset these variables for a screen refresh
        selected_date = datetime.strptime(self.raw_date.get(), "%d/%m/%Y")
        self.start_of_week = selected_date - timedelta(days=selected_date.weekday())

        self.total_reg_pay = 0.0
        self.total_ot_pay = 0.0
        self.total_nd_pay = 0.0
        self.total_reg_hours = 0.0
        self.total_ot_hours = 0.0
        self.grand_total = 0.0

        # update the labels and data holders
        self.update_labels()
        self.update_data()


    def update_labels(self):
        # VERTICAL LABELS
        if self.dataview_mode.get() == "cost_view":
            self.vertical_labels["reg"].set("Regular Pay")
            self.vertical_labels["ot"].set("Overtime Pay")

        elif self.dataview_mode.get() == "hour_view":
            self.vertical_labels["reg"].set("Regular Hours")
            self.vertical_labels["ot"].set("Overtime Hours")

        # HORIZONTAL LABELS (DATES)
        for i, key in enumerate(self.horizontal_labels):
            if key == "total": break

            new_date = self.start_of_week + timedelta(days=i)
            self.horizontal_labels[key].set(new_date.strftime("%b. %d"))


    def update_data(self):
        conn = sql.connect("payroll_system.db")
        cursor = conn.cursor()

        # cycle through all days of the week for the employee
        shift_details = []
        for i in range(8):
            db_date_str = (self.start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")

            cursor.execute("SELECT shift, clock_in, clock_out FROM attendance WHERE date = ? AND employee_name = ?",
                           (db_date_str, self.e_name.get()))
            raw_detail = cursor.fetchone()

            if raw_detail is None: raw_detail = (0, 0, 0)
            shift_details.append(raw_detail)

        conn.close()
        #print(shift_details)

        day_keys = ["mon", "tue", "wed", "thu", "fri", "sat", "sun", "total"]
        i = 0

        # update each day's placeholder data
        for s_num, cin, cout in shift_details:
            if s_num == 0:
                self.weekly_data['reg'][day_keys[i]].set('-')
                self.weekly_data['ot'][day_keys[i]].set('-')
                self.weekly_data['nd'][day_keys[i]].set('-')
                i = i + 1
                continue

            pay = self.rm.calculate_full_pay(s_num, cin, cout)

            # compute running totals
            self.total_reg_pay += pay['regular']
            self.total_ot_pay += pay['overtime']
            self.total_nd_pay += pay['night_diff']
            self.total_reg_hours += pay['reg_hours']
            self.total_ot_hours += pay['ot_hours']

            if self.dataview_mode.get() == "cost_view":
                self.weekly_data['reg'][day_keys[i]].set(f"₱ {pay['regular']:,.2f}")
                self.weekly_data['ot'][day_keys[i]].set(f"₱ {pay['overtime']:,.2f}")
                self.weekly_data['nd'][day_keys[i]].set(f"₱ {pay['night_diff']:,.2f}")
            else:
                self.weekly_data['reg'][day_keys[i]].set(f"{pay['reg_hours']:,.2f}")
                self.weekly_data['ot'][day_keys[i]].set(f"{pay['ot_hours']:,.2f}")
                self.weekly_data['nd'][day_keys[i]].set('-')

            i = i + 1

        # update totals
        if self.dataview_mode.get() == "cost_view":
            self.weekly_data['reg']['total'].set(f"₱ {self.total_reg_pay:,.2f}")
            self.weekly_data['ot']['total'].set(f"₱ {self.total_ot_pay:,.2f}")
            self.weekly_data['nd']['total'].set(f"₱ {self.total_nd_pay:,.2f}")

            self.grand_total = self.total_reg_pay + self.total_ot_pay + self.total_nd_pay
            self.weekly_total.set(f"₱ {self.grand_total:,.2f}")
        else:
            self.weekly_data['reg']['total'].set(f"{self.total_reg_hours:,.2f}")
            self.weekly_data['ot']['total'].set(f"{self.total_ot_hours:,.2f}")
            self.weekly_data['nd']['total'].set("-")

            self.grand_total = self.total_reg_hours + self.total_ot_hours
            self.weekly_total.set(f"{self.grand_total:,.2f}")


