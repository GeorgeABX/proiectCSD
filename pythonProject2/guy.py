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

        # Label pentru confirmarea încărcării fișierului
        self.label_confirmation = tk.Label(self, text="", fg="green")
        self.label_confirmation.pack(pady=10)

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
        # Setează directorul inițial la directorul curent al proiectului
        project_directory = os.path.dirname(os.path.realpath(__file__))
        self.filename = filedialog.askopenfilename(initialdir=project_directory, title="Selectează fișier")
        if self.filename:
            self.label_file.config(text=f"Fișier selectat: {os.path.basename(self.filename)}")
            self.label_confirmation.config(text="Fișier încărcat cu succes!")  # Afisează confirmarea

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
        # Apelul funcției de criptare și gestionarea răspunsului
        try:
            timp_executie, memorie_utilizata, content_hex = self.file_processing.cripteaza_si_logheaza(None,
                                                                                                       self.filename,
                                                                                                       key_id,
                                                                                                       self.log_message)
            self.log_message(f"Fișierul a fost criptat. Timp executie: {timp_executie} secunde")
            self.log_message(
                f"Conținut criptat (hex): {content_hex[:60]}...")  # Afișează primele 60 de caractere din conținutul hex

        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            return 0, 0, ""

    def decrypt_file(self):
        if not self.filename or not self.key_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier și o cheie!")
            return
        key_id = int(self.key_var.get())
        try:
            timp_executie, _, decrypted_content = self.file_processing.decripteaza_si_logheaza(None,
                                                                                               self.filename + '.enc',
                                                                                               key_id,
                                                                                               self.log_message)
            if decrypted_content:
                try:
                    decoded_content = decrypted_content.decode('utf-8')
                    self.log_message(
                        f"Fișierul a fost decriptat. Timp executie: {timp_executie} secunde. Conținut decriptat: {decoded_content}")
                except UnicodeDecodeError:
                    self.log_message(
                        f"Fișierul a fost decriptat. Timp executie: {timp_executie} secunde. Conținut decriptat (hex): {decrypted_content.hex()}")
            else:
                self.log_message("Fișierul nu a putut fi decriptat.")
        except Exception as e:
            self.log_message(f"Eroare la decriptare: {str(e)}")


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
