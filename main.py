import json, datetime, csv, customtkinter as ctk

class PayrollSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self._set_appearance_mode("dark")
        self._set_appearance_mode("blue")
        self.title("LPS")
        self.geometry("1000x500")

if __name__ == "__main__":
    app = PayrollSystem()
    app.mainloop()