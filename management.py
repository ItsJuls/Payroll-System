import customtkinter as ctk
import sqlite3 as sql
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from datetime import datetime
from rates import RatesManager

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

        self.date_var = CTkStringVar(value=RatesManager.get_today_date(self))

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
        self.accent_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="ns")
        self.accent_frame.grid_propagate(False)
        self.accent_frame.pack_propagate(False)

        self.scrollable_input_frame = ctk.CTkScrollableFrame(self.accent_frame, fg_color="transparent")
        self.scrollable_input_frame.pack(fill="both", expand=True, padx=10, pady=(10, 50))

        self.add_button = ctk.CTkButton(self.accent_frame, text="Add New Employee", command=self.show_input_fields)
        self.add_button.place(relx=0.05, rely=0.95, anchor="sw")

        self.active_rows = []

        self.save_all_button = ctk.CTkButton(self.accent_frame, text="Save All Entries", fg_color="green",
                                             hover_color="#006400", command=self.bulk_save_employees)
        self.save_all_button.place(relx=0.25, rely=0.95, anchor="sw")

        self.load_attendance()


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
            cmb(title="Date Required", message="Please select a date before adding employees.", icon="warning")
            return

        self.add_input_row()
    def bulk_save_employees(self):
        if not self.active_rows:
            cmb(title="Nothing to Save", message="Please add or edit at least one employee row.", icon="info")
            return


        raw_date = self.date_var.get()
        try:
            db_ready_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            cmb(title="Format Error", message="Date must be selected from the calendar.", icon="cancel")
            return

        insert_data = []  # For brand new people
        update_data = []  # For people already in the database

        # 3. Loop through tracked rows, Validate, and Sort!
        for index, row in enumerate(self.active_rows):
            e_id = row["id"].get().strip()
            e_name = row["name"].get().strip()
            e_role = row["role"].get().strip()
            e_shift = row["shift"].get()
            e_in = row["in"].get().strip()
            e_out = row["out"].get().strip()

            # CHECK 1: Are there blank boxes?
            if not all([e_id, e_name, e_role, e_in, e_out]):
                cmb(title="Missing Information",
                    message=f"Row {index + 1} has blank fields!\nPlease fill everything out.",
                    icon="warning")
                return

            # CHECK 2: Are the times real? (e.g., no 77:77)
            try:
                datetime.strptime(e_in, "%H:%M")
                datetime.strptime(e_out, "%H:%M")
            except ValueError:
                cmb(title="Invalid Time",
                    message=f"Row {index + 1} has an invalid time!\nPlease use 24-hour format like 08:30.",
                    icon="cancel")
                return

            db_id = row.get("db_id")

            if db_id:
                update_data.append((db_ready_date, e_id, e_name, e_role, e_shift, e_in, e_out, db_id))
            else:
                insert_data.append((db_ready_date, e_id, e_name, e_role, e_shift, e_in, e_out))

        try:
            conn = sql.connect(self.db_name)
            cursor = conn.cursor()

            if insert_data:
                cursor.executemany('''INSERT INTO attendance 
                                      (date, employee_id, employee_name, role, shift, clock_in, clock_out) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''', insert_data)

            if update_data:
                cursor.executemany('''UPDATE attendance 
                                      SET date=?, employee_id=?, employee_name=?, role=?, shift=?, clock_in=?, clock_out=?
                                      WHERE id=?''', update_data)

            conn.commit()
            conn.close()

        except Exception as e:
            cmb(title="Database Error", message=f"An error occurred: {e}", icon="cancel")
            return

        # 5. Success Message & UI Reset
        total_saved = len(insert_data) + len(update_data)
        cmb(title="Success", message=f"Successfully saved and updated {total_saved} records!", icon="check")

        # We call load_attendance() to instantly refresh the screen so it matches the database exactly
        self.load_attendance()

    def add_input_row(self, db_id=None, e_id="", e_name="", e_role="", e_shift="1", e_in="", e_out=""):
        row_frame = ctk.CTkFrame(self.scrollable_input_frame, fg_color="transparent")
        row_frame.pack(pady=5, padx=5, fill="x")
        # --- NEW: HOLD TO DELETE LOGIC ---
        btn_state = {"timer": None, "armed": False, "ignore_next_release": False}

        def arm_button():
            # 1 second has passed! Arm the button.
            btn_state["armed"] = True
            btn_state["ignore_next_release"] = True  # So letting go of the mouse doesn't instantly delete
            cancel_btn.configure(text="Sure?", fg_color="black", hover_color="#333333")

        def reset_hint():
            # Reverts the text if they just tapped it
            if not btn_state["armed"]:
                cancel_btn.configure(text="X")

        def on_press(event):
            # Mouse button pressed down
            if not btn_state["armed"]:
                # Start a 1-second (1000ms) timer
                btn_state["timer"] = cancel_btn.after(1000, arm_button)

        def on_release(event):
            # Mouse button let go
            if btn_state["timer"]:
                # They let go before 1 second was up! Cancel the timer.
                cancel_btn.after_cancel(btn_state["timer"])
                btn_state["timer"] = None

                # Show a quick hint to teach them how to use it
                if not btn_state["armed"]:
                    cancel_btn.configure(text="Hold")
                    cancel_btn.after(800, reset_hint)

            if btn_state["armed"]:
                if btn_state["ignore_next_release"]:
                    # They just finished holding it. Ignore this specific mouse release.
                    btn_state["ignore_next_release"] = False
                else:
                    # They TAPPED the armed button! DELETE TIME.
                    if db_id:
                        # It's an existing record. Delete it from SQLite permanently!
                        conn = sql.connect(self.db_name)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM attendance WHERE id=?", (db_id,))
                        conn.commit()
                        conn.close()

                    # Remove from UI memory and screen
                    if row_data in self.active_rows:
                        self.active_rows.remove(row_data)
                    row_frame.destroy()

        # Create the button WITHOUT a command=. We use bindings instead!
        cancel_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="#c84b31", hover_color="#a33a24")
        cancel_btn.grid(row=0, column=0, padx=(0, 5))

        # Bind the left-click mouse events to our custom functions
        cancel_btn.bind("<ButtonPress-1>", on_press)
        cancel_btn.bind("<ButtonRelease-1>", on_release)
        # ---------------------------------

        # ID
        ent_id = ctk.CTkEntry(row_frame, placeholder_text="ID", width=60)
        if e_id: ent_id.insert(0, str(e_id))
        ent_id.grid(row=0, column=1, padx=5)

        # Name
        ent_name = ctk.CTkEntry(row_frame, placeholder_text="Full Name", width=150)
        if e_name: ent_name.insert(0, str(e_name))
        ent_name.grid(row=0, column=2, padx=5)

        # Role
        ent_role = ctk.CTkEntry(row_frame, placeholder_text="Role", width=120)
        if e_role: ent_role.insert(0, str(e_role))
        ent_role.grid(row=0, column=3, padx=5)

        # Shift
        shift_var = ctk.StringVar(value=str(e_shift))
        shift_menu = ctk.CTkOptionMenu(row_frame, values=["1", "2", "3"], variable=shift_var, width=80)
        shift_menu.grid(row=0, column=4, padx=5)

        # Clock In
        ent_in = ctk.CTkEntry(row_frame, placeholder_text="In (00:00)", width=80)
        if e_in: ent_in.insert(0, str(e_in))
        ent_in.grid(row=0, column=5, padx=5)

        # Clock Out
        ent_out = ctk.CTkEntry(row_frame, placeholder_text="Out (00:00)", width=80)
        if e_out: ent_out.insert(0, str(e_out))
        ent_out.grid(row=0, column=6, padx=5)

        # Track the row. We added 'db_id' so the database knows if this is a new or existing record!
        row_data = {
            "db_id": db_id,
            "frame": row_frame,
            "id": ent_id,
            "name": ent_name,
            "role": ent_role,
            "shift": shift_var,
            "in": ent_in,
            "out": ent_out
        }
        self.active_rows.append(row_data)

    def load_attendance(self):
        raw_date = self.date_var.get()
        if not raw_date:
            return

        try:
            db_ready_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return

        # 1. Clear the screen first! (So we don't stack duplicates on screen)
        for row in self.active_rows:
            row["frame"].destroy()
        self.active_rows.clear()

        # 2. Ask the database for everyone who worked on this date
        conn = sql.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE date = ?", (db_ready_date,))
        records = cursor.fetchall()
        conn.close()

        # 3. Loop through the database results and draw a row for each one
        for rec in records:
            # rec[0] is the database ID. The rest are your data columns.
            self.add_input_row(db_id=rec[0], e_id=rec[2], e_name=rec[3], e_role=rec[4],
                               e_shift=rec[5], e_in=rec[6], e_out=rec[7])