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
        self.populate_files_dropdown()  # Populează dropdown-ul cu fișiere

    def create_widgets(self):
        self.file_var = tk.StringVar(self)
        self.dropdown_files = tk.OptionMenu(self, self.file_var, "")
        self.dropdown_files.pack(pady=10)

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

    def populate_files_dropdown(self):
        # Preia fișierele din baza de date
        self.database.conn.row_factory = lambda cursor, row: row[0]
        cursor = self.database.conn.cursor()
        files = cursor.execute('SELECT nume_fisier FROM fisiere').fetchall()
        menu = self.dropdown_files['menu']
        menu.delete(0, 'end')
        for file in files:
            menu.add_command(label=file, command=lambda value=file: self.file_var.set(value))
        if files:
            self.file_var.set(files[0])  # Setează primul fișier ca implicit

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
        if not self.file_var.get() or not self.key_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier și o cheie!")
            return

        file_name = self.file_var.get()
        key_id = int(self.key_var.get())
        # Obține id_fisier și cale_fisier direct din baza de date bazat pe numele fișierului selectat din dropdown
        id_fisier, cale_fisier = self.database.cursor.execute(
            'SELECT id_fisier, cale_fisier FROM fisiere WHERE nume_fisier = ?', (file_name,)).fetchone()

        try:
            # Criptează fișierul și loghează performanța
            timp_executie, memorie_utilizata, content_hex = self.file_processing.cripteaza_si_logheaza(id_fisier,
                                                                                                       cale_fisier,
                                                                                                       key_id,
                                                                                                       self.log_message)
            # Actualizează statusul în baza de date la 'criptat'
            self.database.cursor.execute('UPDATE fisiere SET status = ? WHERE id_fisier = ?', ('criptat', id_fisier))
            self.database.conn.commit()
            # Logare mesaj de succes
            self.log_message(f"Fișierul a fost criptat. Timp executie: {timp_executie} secunde")
            self.log_message(f"Conținut criptat (hex): {content_hex[:60]}...")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")

    def decrypt_file(self):
        if not self.file_var.get() or not self.key_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier și o cheie!")
            return

        file_name = self.file_var.get()  # Numele fișierului original din dropdown
        key_id = int(self.key_var.get())

        try:
            # Obține calea originală a fișierului pentru a construi calea fișierului criptat
            cale_fisier_original, id_fisier = self.database.cursor.execute(
                'SELECT cale_fisier, id_fisier FROM fisiere WHERE nume_fisier = ?', (file_name,)).fetchone()
            cale_fisier_enc = cale_fisier_original + '.enc'  # Presupunem că fișierul criptat se află în aceeași locație

            # Decriptează fișierul și loghează performanța
            timp_executie, memorie_utilizata, content_decriptat = self.file_processing.decripteaza_si_logheaza(
                id_fisier, cale_fisier_enc, key_id, self.log_message)

            # Actualizează statusul în baza de date la 'decriptat'
            self.database.cursor.execute('UPDATE fisiere SET status = ? WHERE id_fisier = ?', ('decriptat', id_fisier))
            self.database.conn.commit()

            # Logare mesaj de succes
            if content_decriptat:
                try:
                    decoded_content = content_decriptat.decode('utf-8')
                    self.log_message(
                        f"Fișierul a fost decriptat. Timp executie: {timp_executie} secunde. Conținut decriptat: {decoded_content}")
                except UnicodeDecodeError:
                    self.log_message(
                        f"Fișierul a fost decriptat. Timp executie: {timp_executie} secunde. Conținut decriptat (hex): {content_decriptat.hex()}")
            else:
                self.log_message("Fișierul nu a putut fi decriptat.")
        except Exception as e:
            self.log_message(f"Eroare la decriptare: {str(e)}")


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
