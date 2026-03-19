import customtkinter as ctk
import sqlite3 as sql
import pandas as pd
import shutil
import os
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox as cmb
from ctkdateentry import CTkDateEntry as DateEntry, CTkStringVar
from datetime import datetime
from fpdf import FPDF


class ImportExportFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db_name = "payroll_system.db"
        self.settings_file = "settings.yml"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(self, text="Data Management", font=("Arial", 28, "bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")
        self.container.grid_columnconfigure((0, 1), weight=1)

        self.export_frame = ctk.CTkFrame(self.container, corner_radius=15, border_width=2, border_color="#1f538d")
        self.export_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.export_frame, text="Export Data", font=("Arial", 22, "bold")).pack(pady=(20, 10))

        self.date_frame = ctk.CTkFrame(self.export_frame, fg_color="transparent")
        self.date_frame.pack(pady=10)
        self.start_var = CTkStringVar(value=datetime.now().replace(day=1).strftime("%d/%m/%Y"))
        self.end_var = CTkStringVar(value=datetime.now().strftime("%d/%m/%Y"))

        self.start_entry = DateEntry(self.date_frame, width=110, variable=self.start_var)
        self.start_entry.grid(row=0, column=0, padx=5)
        self.end_entry = DateEntry(self.date_frame, width=110, variable=self.end_var)
        self.end_entry.grid(row=0, column=1, padx=5)

        ctk.CTkButton(self.export_frame, text="Export to Excel (.xlsx)",
                      command=lambda: self.export_data("excel")).pack(pady=5, padx=40, fill="x")
        ctk.CTkButton(self.export_frame, text="Export to PDF (.pdf)", fg_color="#E74C3C", hover_color="#C0392B",
                      command=self.export_to_pdf).pack(pady=5, padx=40, fill="x")
        ctk.CTkButton(self.export_frame, text="Export to CSV (.csv)", fg_color="#2b2b2b",
                      command=lambda: self.export_data("csv")).pack(pady=5, padx=40, fill="x")

        self.import_frame = ctk.CTkFrame(self.container, corner_radius=15, border_width=2, border_color="#1f538d")
        self.import_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.import_frame, text="Import Data", font=("Arial", 22, "bold")).pack(pady=(20, 10))
        ctk.CTkButton(self.import_frame, text="Download Template", fg_color="transparent", border_width=1,
                      command=self.download_template).pack(pady=5, padx=40, fill="x")
        ctk.CTkButton(self.import_frame, text="Upload CSV/Excel", height=45, fg_color="#1E8449",
                      command=self.import_data).pack(pady=20, padx=40, fill="x")

        self.maint_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", height=60, corner_radius=0)
        self.maint_frame.grid(row=2, column=0, sticky="ew")

        ctk.CTkLabel(self.maint_frame, text="MAINTENANCE:", text_color="gray", font=("Arial", 12, "bold")).pack(
            side="left", padx=(20, 10))

        ctk.CTkButton(self.maint_frame, text="Backup System", fg_color="#2b2b2b", width=120,
                      command=self.create_backup).pack(side="left", padx=5)
        ctk.CTkButton(self.maint_frame, text="Restore System", fg_color="#2b2b2b", width=120,
                      command=self.restore_backup).pack(side="left", padx=5)

        ctk.CTkButton(self.maint_frame, text="WIPE ALL DATA", fg_color="transparent", border_color="#E74C3C",
                      border_width=1, text_color="#E74C3C", hover_color="#331111", command=self.wipe_database).pack(
            side="right", padx=20)

    def export_data(self, file_type):
        raw_start = self.start_var.get()
        raw_end = self.end_var.get()
        try:
            db_start = datetime.strptime(raw_start, "%d/%m/%Y").strftime("%Y-%m-%d")
            db_end = datetime.strptime(raw_end, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return

        conn = sql.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM attendance WHERE date BETWEEN ? AND ?", conn, params=(db_start, db_end))
        conn.close()

        if df.empty:
            cmb(title="Empty", message="No records found for these dates.", icon="info")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=f".{file_type}")
        if file_path:
            if file_type == "excel":
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            cmb(title="Success", message="Export Complete!", icon="check")

    def download_template(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if file_path:
            cols = ["date", "employee_id", "employee_name", "role", "shift", "clock_in", "clock_out"]
            pd.DataFrame(columns=cols).to_excel(file_path, index=False)
            cmb(title="Success", message="Template saved!", icon="check")

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Data Files", "*.xlsx *.csv")])
        if not file_path: return
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            conn = sql.connect(self.db_name)
            cursor = conn.cursor()
            success, dupe = 0, 0
            for _, row in df.iterrows():
                cursor.execute("SELECT id FROM attendance WHERE date=? AND employee_id=? AND shift=?",
                               (row['date'], row['employee_id'], row['shift']))
                if cursor.fetchone():
                    dupe += 1
                else:
                    cursor.execute(
                        "INSERT INTO attendance (date, employee_id, employee_name, role, shift, clock_in, clock_out) VALUES (?,?,?,?,?,?,?)",
                        (row['date'], row['employee_id'], row['employee_name'], row['role'], row['shift'],
                         row['clock_in'], row['clock_out']))
                    success += 1
            conn.commit()
            conn.close()
            cmb(title="Import Result", message=f"Added: {success}\nSkipped: {dupe}", icon="check")
        except Exception as e:
            cmb(title="Error", message=str(e), icon="cancel")

    def export_to_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not file_path: return
        try:
            conn = sql.connect(self.db_name)
            df = pd.read_sql_query("SELECT date, employee_name, role, clock_in, clock_out FROM attendance LIMIT 100",
                                   conn)
            conn.close()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, "Attendance Report", ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", "B", 10)
            cols = ["Date", "Name", "Role", "In", "Out"]
            widths = [30, 60, 50, 25, 25]
            for i, col in enumerate(cols): pdf.cell(widths[i], 10, col, border=1)
            pdf.ln()
            pdf.set_font("Arial", "", 9)
            for _, row in df.iterrows():
                for i in range(len(cols)): pdf.cell(widths[i], 8, str(row[i]), border=1)
                pdf.ln()
            pdf.output(file_path)
            cmb(title="Success", message="PDF Saved!", icon="check")
        except Exception as e:
            cmb(title="Error", message=str(e), icon="cancel")

    def wipe_database(self):
        c1 = cmb(title="WIPE DATA", message="Delete ALL records?", icon="warning", option_1="No", option_2="Yes")
        if c1.get() == "Yes":
            c2 = cmb(title="FINAL WARNING", message="This cannot be undone. Proceed?", icon="warning", option_1="No",
                     option_2="Yes")
            if c2.get() == "Yes":
                conn = sql.connect(self.db_name);
                conn.cursor().execute("DELETE FROM attendance");
                conn.commit();
                conn.close()
                cmb(title="Success", message="Database is now empty.", icon="check")

    def create_backup(self):
        path = filedialog.askdirectory(title="Select Backup Location")
        if path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(self.db_name, os.path.join(path, f"LPS_DB_{ts}.db"))
            if os.path.exists(self.settings_file):
                shutil.copy2(self.settings_file, os.path.join(path, f"LPS_Settings_{ts}.yml"))
            cmb(title="Success", message="Backup files created successfully!", icon="check")

    def restore_backup(self):
        file = filedialog.askopenfilename(title="Select Database Backup (.db)", filetypes=[("Database", "*.db")])
        if file:
            c = cmb(title="Restore", message="This will overwrite current data. Proceed?", icon="warning",
                    option_1="No", option_2="Yes")
            if c.get() == "Yes":
                shutil.copy2(file, self.db_name)
                cmb(title="Success", message="Database restored! Please restart the app.", icon="check")