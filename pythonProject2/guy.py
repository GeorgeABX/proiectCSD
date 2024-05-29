import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import database
import file_processing
import os

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem de Management al Criptării")
        self.geometry("800x600")
        self.configure(bg="#ffffff")  # Fundal alb
        self.database = database
        self.file_processing = file_processing
        self.create_widgets()
        self.populate_algs_dropdown()
        self.populate_files_dropdown()

    def create_widgets(self):
        # Stiluri
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('TButton', font=('Helvetica', 10), padding=6)
        style.map('TButton', background=[('active', '#cccccc')], foreground=[('active', '#000000')])
        style.configure('TLabel', font=('Helvetica', 10), padding=6, background="#ffffff", foreground="#000000")
        style.configure('TEntry', font=('Helvetica', 10), padding=6)
        style.configure('TCombobox', font=('Helvetica', 10), padding=6)
        style.configure('TFrame', background="#ffffff")
        style.configure('TLabelframe', background="#f0f0f0", foreground="#000000")
        style.configure('TLabelframe.Label', background="#f0f0f0", foreground="#000000")
        style.configure('TScrollbar', background="#cccccc")

        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill='both', expand=True)

        file_frame = ttk.LabelFrame(main_frame, text="Gestionare Fișiere", padding="10 10 10 10")
        file_frame.pack(fill='x', pady=10)

        self.label_file = ttk.Label(file_frame, text="Selectează fișier")
        self.label_file.pack(pady=5)

        self.file_var = tk.StringVar(self)
        self.dropdown_files = ttk.Combobox(file_frame, textvariable=self.file_var, state="readonly")
        self.dropdown_files.pack(fill='x', pady=5)

        self.button_add_file = ttk.Button(file_frame, text="Adaugă fișier", command=self.add_file)
        self.button_add_file.pack(pady=5)

        key_frame = ttk.LabelFrame(main_frame, text="Selectează Cheie și Algoritm", padding="10 10 10 10")
        key_frame.pack(fill='x', pady=10)

        self.label_alg = ttk.Label(key_frame, text="Selectează algoritm")
        self.label_alg.pack(pady=5)

        self.alg_var = tk.StringVar(self)
        self.alg_var.trace('w', self.update_keys_dropdown)
        self.dropdown_algs = ttk.Combobox(key_frame, textvariable=self.alg_var, state="readonly")
        self.dropdown_algs.pack(fill='x', pady=5)

        self.label_key = ttk.Label(key_frame, text="Selectează cheie")
        self.label_key.pack(pady=5)

        self.key_var = tk.StringVar(self)
        self.dropdown_keys = ttk.Combobox(key_frame, textvariable=self.key_var, state="readonly")
        self.dropdown_keys.pack(fill='x', pady=5)

        action_frame = ttk.Frame(main_frame, padding="10 10 10 10")
        action_frame.pack(fill='x', pady=10)

        self.button_encrypt = ttk.Button(action_frame, text="Criptează", command=self.encrypt_file)
        self.button_encrypt.pack(side='left', padx=10, pady=5)

        self.button_decrypt = ttk.Button(action_frame, text="Decriptează", command=self.decrypt_file)
        self.button_decrypt.pack(side='left', padx=10, pady=5)

        log_frame = ttk.LabelFrame(main_frame, text="Loguri", padding="10 10 10 10")
        log_frame.pack(fill='both', expand=True, pady=10)

        self.log = tk.Text(log_frame, height=15, wrap='word', bg="#ffffff", fg="#000000", font=('Helvetica', 10))
        self.scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log.yview)
        self.log['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side='right', fill='y')
        self.log.pack(fill='both', expand=True, pady=5)

    def populate_algs_dropdown(self):
        self.database.conn.row_factory = None
        cursor = self.database.conn.cursor()
        algs = cursor.execute('SELECT id_algoritm, nume FROM algoritmi').fetchall()
        self.dropdown_algs['values'] = [alg[1] for alg in algs]
        if algs:
            self.alg_var.set(algs[0][1])

    def update_keys_dropdown(self, *args):
        selected_algorithm = self.alg_var.get()
        if selected_algorithm:
            self.database.conn.row_factory = None
            cursor = self.database.conn.cursor()
            alg_id = cursor.execute('SELECT id_algoritm FROM algoritmi WHERE nume = ?', (selected_algorithm,)).fetchone()[0]
            keys = cursor.execute('SELECT id_cheie FROM chei WHERE id_algoritm = ?', (alg_id,)).fetchall()
            self.dropdown_keys['values'] = [key[0] for key in keys]
            if keys:
                self.key_var.set(keys[0][0])

    def log_message(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def populate_files_dropdown(self):
        self.database.conn.row_factory = lambda cursor, row: row[0]
        cursor = self.database.conn.cursor()
        files = cursor.execute('SELECT nume_fisier FROM fisiere').fetchall()
        self.dropdown_files['values'] = files
        if files:
            self.file_var.set(files[0])

    def add_file(self):
        project_directory = os.path.dirname(os.path.realpath(__file__))
        file_paths = filedialog.askopenfilenames(initialdir=project_directory, title="Selectează fișiere")
        if file_paths:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                self.database.cursor.execute('''
                    INSERT INTO fisiere (nume_fisier, cale_fisier, tip_operatie, timestamp, id_cheie) 
                    VALUES (?, ?, ?, datetime('now'), NULL)
                ''', (file_name, file_path, 'criptare'))
                self.log_message(f"Fișier adăugat: {file_name}")
            self.database.conn.commit()
            self.populate_files_dropdown()

    def encrypt_file(self):
        if not self.file_var.get() or not self.key_var.get() or not self.alg_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier, o cheie și un algoritm!")
            return

        file_name = self.file_var.get()
        key_id = int(self.key_var.get())
        alg_name = self.alg_var.get().lower()

        id_fisier, cale_fisier = self.database.cursor.execute(
            'SELECT id_fisier, cale_fisier FROM fisiere WHERE nume_fisier = ?', (file_name,)).fetchone()

        try:
            timp_executie, memorie_utilizata, content_hex = self.file_processing.cripteaza_si_logheaza(id_fisier,
                                                                                                       cale_fisier,
                                                                                                       key_id,
                                                                                                       self.log_message)
            self.database.cursor.execute('UPDATE fisiere SET status = ? WHERE id_fisier = ?', ('criptat', id_fisier))
            self.database.conn.commit()
            self.log_message(f"Fișierul a fost criptat.\nTimp executie: {timp_executie:.2f} secunde\nMemorie utilizată: {memorie_utilizata:.2f} KB")
            self.log_message(f"Conținut criptat (hex): {content_hex[:60]}...")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")

    def decrypt_file(self):
        if not self.file_var.get() or not self.key_var.get() or not self.alg_var.get():
            messagebox.showerror("Eroare", "Selectează un fișier, o cheie și un algoritm!")
            return

        file_name = self.file_var.get()
        key_id = int(self.key_var.get())
        alg_name = self.alg_var.get().lower()

        try:
            cale_fisier_original, id_fisier = self.database.cursor.execute(
                'SELECT cale_fisier, id_fisier FROM fisiere WHERE nume_fisier = ?', (file_name,)).fetchone()
            cale_fisier_enc = cale_fisier_original + '.enc'

            timp_executie, memorie_utilizata, content_decriptat = self.file_processing.decripteaza_si_logheaza(
                id_fisier, cale_fisier_enc, key_id, self.log_message)

            self.database.cursor.execute('UPDATE fisiere SET status = ? WHERE id_fisier = ?', ('decriptat', id_fisier))
            self.database.conn.commit()

            if content_decriptat:
                try:
                    decoded_content = content_decriptat.decode('utf-8')
                    self.log_message(f"Fișierul a fost decriptat.\nTimp executie: {timp_executie:.2f} secunde\nMemorie utilizată: {memorie_utilizata:.2f} KB\nConținut decriptat: {decoded_content}")
                except UnicodeDecodeError:
                    self.log_message(f"Fișierul a fost decriptat.\nTimp executie: {timp_executie:.2f} secunde\nMemorie utilizată: {memorie_utilizata:.2f} KB\nConținut decriptat (hex): {content_decriptat.hex()}")
            else:
                self.log_message("Fișierul nu a putut fi decriptat.")
        except Exception as e:
            self.log_message(f"Eroare la decriptare: {str(e)}")

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
