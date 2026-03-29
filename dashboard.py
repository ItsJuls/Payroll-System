import customtkinter as ctk
import matplotlib.pyplot as plt
import sqlite3 as sql
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from rates import RatesManager
from datetime import datetime, timedelta


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.rm = RatesManager()

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=8)

        self.header = ctk.CTkLabel(self, text="Dashboard Overview", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw", columnspan=3)

        self.sub_label = ctk.CTkLabel(self, text="Real-time Payroll Summary", font=("Arial", 16))
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nw", columnspan=3)

        self.date_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_controls_frame.grid(row=3, column=0, columnspan=3, padx=20, sticky="w")

        self.date_var = CTkStringVar(value=self.rm.get_today_date())

        self.date_entry = DateEntry(self.date_controls_frame, width=150, variable=self.date_var, state="readonly")
        self.date_entry.grid(row=3, column=1, pady=(1, 0), padx=(0, 10), sticky="w")

        self.chart_label = ctk.CTkLabel(self.date_controls_frame, text="Enter a Date:", font=("Arial", 14, "bold"))
        self.chart_label.grid(row=3, column=0, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")

        self.refresh_button = ctk.CTkButton(self.date_controls_frame, text="Refresh", command=self.refresh_dashboard)
        self.refresh_button.grid(row=3, column=2, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")

        self.accent_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=10, border_color="#1f538d",
                                         border_width=2, width=1200, height=300)
        self.accent_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="n")
        self.accent_frame.grid_propagate(False)
        self.accent_frame.pack_propagate(False)

        s1 = self.rm.get_shift_defaults(1)
        s2 = self.rm.get_shift_defaults(2)
        s3 = self.rm.get_shift_defaults(3)

        self.add_label(f"{s1['in']} - {s1['out']}", relx=0.075, rely=0.2, anchor="n")
        self.add_label(f"{s2['in']} - {s2['out']}", relx=0.075, rely=0.4, anchor="n")
        self.add_label(f"{s3['in']} - {s3['out']}", relx=0.075, rely=0.6, anchor="n")

        self.add_label("Employees\nPresent", relx=0.20, rely=0.05, anchor="n")
        self.add_label("Total\nRegular Pay", relx=0.35, rely=0.05, anchor="n")
        self.add_label("Total\nOvertime Pay", relx=0.50, rely=0.05, anchor="n")
        self.add_label("Total Night\nDifferential", relx=0.65, rely=0.05, anchor="n")
        self.add_label("Total Daily Payroll", relx=0.20, rely=0.9, anchor="s")
        self.add_label("Weekly Payroll Expense", relx=0.65, rely=0.9, anchor="s")
        self.add_label("Cost Per Shift", relx=0.80, rely=0.05, anchor="n")

        self.stats = {
            "s1": {"present": ctk.StringVar(value="0"), "reg": ctk.StringVar(value="0"), "ot": ctk.StringVar(value="0"),
                   "nd": ctk.StringVar(value="0"), "cost": ctk.StringVar(value="0")},
            "s2": {"present": ctk.StringVar(value="0"), "reg": ctk.StringVar(value="0"), "ot": ctk.StringVar(value="0"),
                   "nd": ctk.StringVar(value="0"), "cost": ctk.StringVar(value="0")},
            "s3": {"present": ctk.StringVar(value="0"), "reg": ctk.StringVar(value="0"), "ot": ctk.StringVar(value="0"),
                   "nd": ctk.StringVar(value="0"), "cost": ctk.StringVar(value="0")},
            "total_daily": ctk.StringVar(value="PhP 0.00"), "total_weekly": ctk.StringVar(value="PhP 0.00")
        }

        for i, key in enumerate(["s1", "s2", "s3"]):
            rely = 0.2 + (i * 0.2)
            self.add_label(variable=self.stats[key]["present"], relx=0.20, rely=rely, anchor="n")
            self.add_label(variable=self.stats[key]["reg"], relx=0.35, rely=rely, anchor="n")
            self.add_label(variable=self.stats[key]["ot"], relx=0.50, rely=rely, anchor="n")
            self.add_label(variable=self.stats[key]["nd"], relx=0.65, rely=rely, anchor="n")
            self.add_label(variable=self.stats[key]["cost"], relx=0.80, rely=rely, anchor="n")

        self.add_label(variable=self.stats["total_daily"], relx=0.35, rely=0.9, anchor="s")
        self.add_label(variable=self.stats["total_weekly"], relx=0.8, rely=0.9, anchor="s")

        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.grid(row=5, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="nsew")

        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 8), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.refresh_dashboard()

    def add_label(self, text=None, variable=None, relx=0, rely=0, anchor="n"):
        label = ctk.CTkLabel(self.accent_frame, text=text, textvariable=variable, font=("Arial", 16))
        label.place(relx=relx, rely=rely, anchor=anchor)

    def refresh_dashboard(self):
        raw_date = self.date_var.get()
        try:
            selected_date = datetime.strptime(raw_date, "%d/%m/%Y")
            db_date_str = selected_date.strftime("%Y-%m-%d")
        except:
            return

        conn = sql.connect("payroll_system.db")
        cursor = conn.cursor()

        total_selected_day = 0
        for s_num in [1, 2, 3]:
            key = f"s{s_num}"
            cursor.execute("SELECT clock_in, clock_out FROM attendance WHERE date = ? AND shift = ?",
                           (db_date_str, s_num))
            rows = cursor.fetchall()

            count = len(rows)
            shift_reg, shift_ot, shift_nd = 0, 0, 0

            for cin, cout in rows:
                pay = self.rm.calculate_full_pay(s_num, cin, cout)
                shift_reg += pay['regular']
                shift_ot += pay['overtime']
                shift_nd += pay['night_diff']

            shift_total = shift_reg + shift_ot + shift_nd
            total_selected_day += shift_total

            self.stats[key]["present"].set(str(count))
            self.stats[key]["reg"].set(f"{shift_reg:,.2f}")
            self.stats[key]["ot"].set(f"{shift_ot:,.2f}")
            self.stats[key]["nd"].set(f"{shift_nd:,.2f}")
            self.stats[key]["cost"].set(f"{shift_total:,.2f}")

        self.stats["total_daily"].set(f"PhP {total_selected_day:,.2f}")

        start_of_week = selected_date - timedelta(days=selected_date.weekday())
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_costs = []

        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            day_str = current_day.strftime("%Y-%m-%d")
            cursor.execute("SELECT shift, clock_in, clock_out FROM attendance WHERE date = ?", (day_str,))
            day_rows = cursor.fetchall()

            day_total = 0
            for s_num, cin, cout in day_rows:
                pay = self.rm.calculate_full_pay(s_num, cin, cout)
                day_total += pay['gross_total']
            weekly_costs.append(day_total)

        conn.close()

        total_week_sum = sum(weekly_costs)
        self.stats["total_weekly"].set(f"PhP {total_week_sum:,.2f}")

        self.ax.clear()
        bars = self.ax.bar(days_of_week, weekly_costs, color='#1f538d')
        selected_day_idx = selected_date.weekday()
        bars[selected_day_idx].set_color('#f39c12')

        self.ax.set_title(f"Weekly Payroll Trend (Week of {start_of_week.strftime('%d %b')})", pad=10, fontsize=20)
        self.ax.set_ylabel("Total PhP", fontsize=20)

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                self.ax.text(bar.get_x() + bar.get_width() / 2., height, f'P{height:,.0f}', ha='center', va='bottom',
                             fontsize=14)

        self.canvas.draw()