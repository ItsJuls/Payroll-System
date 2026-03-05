import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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

        # 2. Stat Cards (Row 2)
        self.add_stat_card("Total Employees", "24", 2, 0)
        self.add_stat_card("Active Shift", "Shift 1", 2, 1)
        self.add_stat_card("Daily Payroll", "₱14,400", 2, 2)

        # 3. Chart Label (Row 3)
        self.chart_label = ctk.CTkLabel(self, text="Weekly Payroll Expense (PhP)", font=("Arial", 16, "bold"))
        self.chart_label.grid(row=3, column=0, columnspan=3, pady=(30, 0))

        # 4. Data & Plotting
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        y_values = [14400, 15200, 14800, 16100, 15900, 12000, 0]

        fig, ax = plt.subplots(figsize=(6, 3), dpi=100, facecolor='#242424')
        fig.patch.set_facecolor('#242424')
        ax.set_facecolor('#242424')

        ax.plot(days, y_values, color='#1f538d', marker='o', linewidth=3, markersize=8)

        # Styling the axis
        ax.tick_params(colors='white', which='both')
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # 5. Embedding (Row 4)
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg='#242424', highlightthickness=0)
        canvas_widget.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")


    def add_stat_card(self, title, value, row, col):
        card = ctk.CTkFrame(self, corner_radius=15, height=120)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.pack_propagate(False)  # This is okay because it's INSIDE the card frame

        title_lbl = ctk.CTkLabel(card, text=title, font=("Arial", 14))
        title_lbl.pack(pady=(20, 5))

        value_lbl = ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color="#1f538d")
        value_lbl.pack(pady=(0, 20))