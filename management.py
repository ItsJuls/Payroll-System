import customtkinter as ctk
import sqlite3 as sql
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from datetime import datetime

class ManagementFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.db_name = "payroll_system.db"
        self.init_db()

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.date_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_controls_frame.grid(row=3, column=0, columnspan=3, padx=20, sticky="w")

        self.header = ctk.CTkLabel(self, text="Employee Management and Attendance Tracking", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw", columnspan=3)

        self.date_var = CTkStringVar(value="")

        self.date_entry = DateEntry(self.date_controls_frame, width=150, variable=self.date_var, state="readonly")
        self.date_entry.grid(row=3, column=1, pady=(1, 0), padx=(0, 10), sticky="w")

        self.chart_label = ctk.CTkLabel(self.date_controls_frame, text="Enter a Date:", font=("Arial", 14, "bold"))
        self.chart_label.grid(row=3, column=0, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")

        self.refresh_button = ctk.CTkButton(self.date_controls_frame, text="Refresh", command=self.load_attendance)
        self.refresh_button.grid(row=3, column=2, columnspan=1, pady=(1, 0), padx=(0, 10), sticky="nw")

        self.accent_frame = ctk.CTkFrame(self,
                                         fg_color="transparent",
                                         corner_radius=10,
                                         border_color="#1f538d",
                                         border_width=2,
                                         width=1000,
                                         height=400)
        self.accent_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="n")
        self.accent_frame.grid_propagate(False)
        self.accent_frame.pack_propagate(False)

        self.scrollable_input_frame = ctk.CTkScrollableFrame(self.accent_frame, fg_color="transparent")
        # pady=(10, 50) leaves 50 pixels of empty space at the bottom so it doesn't cover the Add button!
        self.scrollable_input_frame.pack(fill="both", expand=True, padx=10, pady=(10, 50))

        self.add_button = ctk.CTkButton(self.accent_frame, text="Add New Employee", command=self.show_input_fields)
        self.add_button.place(relx=0.05, rely=0.95, anchor="sw")

    def init_db(self):
        conn = sql.connect(self.db_name)

        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                employee_id INTEGER,
                employee_name TEXT,
                role TEXT,
                shift INTEGER,
                clock_in TEXT,
                clock_out TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def show_input_fields(self):
        target_date = self.date_var.get()

        if not target_date:
            cmb(title="Date Required", message="Please select a date before adding employees.", icon="warning",
                option_1="Got it")
            return

        # Notice we removed the "for widget in ... destroy()" loop!

        # Put the new row INSIDE the scrollable frame
        row_frame = ctk.CTkFrame(self.scrollable_input_frame, fg_color="transparent")
        row_frame.pack(pady=5, padx=5, fill="x")  # pack puts it right below the previous one

        # "X" Button (Destroys only this specific row_frame)
        cancel_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="#c84b31", hover_color="#a33a24",
                                   command=row_frame.destroy)
        cancel_btn.grid(row=0, column=0, padx=(0, 5))

        # We removed "self." so Python creates fresh variables for every row
        ent_id = ctk.CTkEntry(row_frame, placeholder_text="ID", width=60)
        ent_id.grid(row=0, column=1, padx=5)

        ent_name = ctk.CTkEntry(row_frame, placeholder_text="Full Name", width=150)
        ent_name.grid(row=0, column=2, padx=5)

        ent_role = ctk.CTkEntry(row_frame, placeholder_text="Role", width=120)
        ent_role.grid(row=0, column=3, padx=5)

        shift_var = ctk.StringVar(value="1")
        shift_menu = ctk.CTkOptionMenu(row_frame, values=["1", "2", "3"], variable=shift_var, width=80)
        shift_menu.grid(row=0, column=4, padx=5)

        ent_in = ctk.CTkEntry(row_frame, placeholder_text="In (00:00)", width=80)
        ent_in.grid(row=0, column=5, padx=5)

        ent_out = ctk.CTkEntry(row_frame, placeholder_text="Out (00:00)", width=80)
        ent_out.grid(row=0, column=6, padx=5)

        # --- THE MAGIC TRICK ---
        # We create a mini-function right here that captures the exact data for THIS row
        def save_this_row():
            self.db_save_employee(ent_id.get(), ent_name.get(), ent_role.get(),
                                  shift_var.get(), ent_in.get(), ent_out.get(), row_frame)

        final_save = ctk.CTkButton(row_frame, text="Confirm Save", fg_color="green", command=save_this_row)
        final_save.grid(row=0, column=7, padx=(10, 0))

        # Notice the new variables inside the parentheses
        def db_save_employee(self, emp_id, emp_name, role, shift, clock_in, clock_out, row_frame):
            raw_date = self.date_var.get()

            try:
                db_ready_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                cmb(title="Format Error", message="Date must be selected from the calendar.", icon="cancel")
                return

            # Use the passed-in variables!
            data = (db_ready_date, emp_id, emp_name, role, shift, clock_in, clock_out)

            conn = sql.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO attendance (date, employee_id, employee_name, role, shift, clock_in, clock_out) 
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
            conn.commit()
            conn.close()

            msg = cmb(title="Success", message="Employee Record Added Successfully!", icon="check", option_1="OK")

            if msg.get() == "OK":
                # Very satisfying UX: Once saved, the input row vanishes!
                row_frame.destroy()

            self.load_attendance()  # Refresh view

    def load_attendance(self):
        """Event: Query DB for selected date and show in console (for now)"""
        date = self.date_var.get()
        print(f"Loading data for: {date}")
        # Next step: Add a table here to show results!