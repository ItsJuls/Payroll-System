import json, datetime, csv, customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("500x300")
app.title("Payroll System v1.0")

greeting_label = ctk.CTkLabel(
    master=app,
    text="Hello World! Welcome to the Payroll System.",
    font=("Arial", 18, "bold")
)

greeting_label.pack(pady=40)

test_button = ctk.CTkButton(
    master=app,
    text="Click Me",
    command=lambda: print("Button was clicked!")
)
test_button.pack(pady=10)

app.mainloop()

