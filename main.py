import json, datetime, csv, customtkinter as ctk, os
from CTkMessagebox import CTkMessagebox as cmb
from PIL import Image
from dashboard import DashboardFrame
from management import ManagementFrame
from payroll import PayrollFrame
from settings import SettingsFrame
from importexport import ImportExportFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PayrollSystem(ctk.CTk):
    def __init__(self):
        super().__init__()


        self.title("LPS")

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()

        self.geometry(f"{width}x{height}")
        self.state('zoomed')


        self.sidebar_frame = ctk.CTkFrame(self, width=110, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=(20, 30))

        self.btn_dash = self.create_sidebar_button("Dashboard", self.show_dashboard, "dashboard.png")
        self.btn_employee = self.create_sidebar_button("Employees", self.show_employees, "employee.png")
        self.btn_payroll = self.create_sidebar_button("Process Pay", self.show_payroll, "payroll.png")
        self.btn_export = self.create_sidebar_button("Export", self.show_export, "export.png")
        self.btn_setting = self.create_sidebar_button("Settings", self.show_settings, "settings.png")
        self.btn_exit = self.create_sidebar_button("Exit", self.confirm_exit, "exit.png")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.show_dashboard()





    def create_sidebar_button(self, text, command, image):
            image_path = os.path.join(os.path.dirname(__file__), "Images", image)

            button_icon = ctk.CTkImage(light_image=Image.open(image_path),
                                        dark_image=Image.open(image_path),
                                        size=(30, 30))

            btn = ctk.CTkButton(self.sidebar_frame, text="", command=command, corner_radius=10, width=50, height=50, image=button_icon)
            btn.pack(pady=10, padx=10)
            return btn

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        self.dashboard = DashboardFrame(master=self.content_frame, fg_color="transparent")
        self.dashboard.pack(fill="both", expand=True)

    def show_employees(self):
        self.clear_content()
        self.management = ManagementFrame(master=self.content_frame, fg_color="transparent")
        self.management.pack(fill="both", expand=True)

    def show_payroll(self):
        self.clear_content()
        self.payroll = PayrollFrame(master=self.content_frame, fg_color="transparent")
        self.payroll.pack(fill="both", expand=True)

    def show_export(self):
        self.clear_content()
        self.export = ImportExportFrame(master=self.content_frame, fg_color="transparent")
        self.export.pack(fill="both", expand=True)

    def show_settings(self):
        self.clear_content()
        self.settings = SettingsFrame(master=self.content_frame, fg_color="transparent")
        self.settings.pack(fill="both", expand=True)

    def confirm_exit(self):
        msg = cmb(title="Exit Confirmation",
                  message="Are you sure you want to close the Payroll System?",
                  icon="question",
                  option_1="No",
                  option_2="Yes")

        if msg.get() == "Yes":
            self.quit()
            self.destroy()




if __name__ == "__main__":
    app = PayrollSystem()
    app.mainloop()