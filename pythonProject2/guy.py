import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, END, Scrollbar
import database
import file_processing
import subprocess
import os

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem de Management al Criptării")
        self.geometry("600x400")
        self.database = database
        self.file_processing = file_processing
        self.create_widgets()
        self.populate_keys_dropdown()

    def create_widgets(self):
        # Selectare fișier
        self.label_file = tk.Label(self, text="Niciun fișier selectat")
        self.label_file.pack(pady=10)

        self.button_open = tk.Button(self, text="Deschide Fișier", command=self.open_file)
        self.button_open.pack()

        # Selectare cheie
        self.key_var = tk.StringVar(self)
        self.dropdown_keys = tk.OptionMenu(self, self.key_var, "")
        self.dropdown_keys.pack(pady=10)

        # Buton criptare
        self.button_encrypt = tk.Button(self, text="Criptează", command=self.encrypt_file)
        self.button_encrypt.pack(pady=5)

        # Buton decriptare
        self.button_decrypt = tk.Button(self, text="Decriptează", command=self.decrypt_file)
        self.button_decrypt.pack(pady=5)

        # Câmp de text pentru loguri (folosind Listbox)
        self.log = Listbox(self, height=10, width=50)
        self.scrollbar = Scrollbar(self, orient='vertical', command=self.log.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.log.config(yscrollcommand=self.scrollbar.set)
        self.log.pack(pady=10, fill='both', expand=True)

    def log_message(self, message):
        self.log.insert(END, message)
        self.log.see(END)  # Scroll to the bottom

    def open_file(self):
        self.filename = filedialog.askopenfilename(initialdir=os.path.expanduser('~'), title="Selectează fișier")
        if self.filename:
            self.label_file.config(text=f"Fișier selectat: {self.filename}")

    def populate_keys_dropdown(self):
        # Preia cheile din baza de date
        self.database.conn.row_factory = lambda cursor, row: row[0]
        cursor = self.database.conn.cursor()
        keys = cursor.execute('SELECT id_cheie FROM chei').fetchall()
        menu = self.dropdown_keys['menu']
        menu.delete(0, 'end')
        for key in keys:
            menu.add_command(label=key, command=lambda value=key: self.key_var.set(value))
        if keys:
            self.key_var.set(keys[0])  # Set the first key as default

    def encrypt_file(self):
        if not self.filename or not self.key_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier și o cheie!")
            return
        key_id = int(self.key_var.get())
        print("Începe criptarea...")
        self.file_processing.cripteaza_si_logheaza(None, self.filename, key_id)
        print("Fișierul a fost criptat.")
        self.file_processing.afiseaza_continut_fisier_hex(f"{self.filename}.enc")
        self.log_message(f"Fișierul {self.filename} a fost criptat.")

    def decrypt_file(self):
        if not self.filename or not self.key_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier și o cheie!")
            return
        key_id = int(self.key_var.get())
        print("Începe decriptarea...")
        self.file_processing.decripteaza_si_logheaza(None, self.filename + '.enc', key_id)
        print("Fișierul a fost decriptat.")
        self.log_message(f"Fișierul {self.filename} a fost decriptat.")
        self.file_processing.afiseaza_continut_fisier(self.filename)


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
