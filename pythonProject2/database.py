import sqlite3
import os

conn = sqlite3.connect('baza_de_date.db')
cursor = conn.cursor()

# Funcție pentru a verifica dacă o tabelă există deja
def table_exists(table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None


def creare_tabele():
    if not table_exists('algoritmi'):
        cursor.execute('''
            CREATE TABLE algoritmi (
                id_algoritm INTEGER PRIMARY KEY,
                nume TEXT,
                tip TEXT,
                lungime_cheie INTEGER
            )
        ''')

    # Creare tabel pentru chei
    if not table_exists('chei'):
        cursor.execute('''
            CREATE TABLE chei (
                id_cheie INTEGER PRIMARY KEY,
                valoare_cheie TEXT,
                id_algoritm INTEGER,
                FOREIGN KEY (id_algoritm) REFERENCES algoritmi(id_algoritm)
            )
        ''')

    # Creare tabel pentru fisiere
    if not table_exists('fisiere'):
        cursor.execute('''
            CREATE TABLE fisiere (
                id_fisier INTEGER PRIMARY KEY,
                nume_fisier TEXT,
                cale_fisier TEXT,
                tip_operatie TEXT,
                timestamp TEXT,
                id_cheie INTEGER,
                status TEXT DEFAULT 'necriptat',
                FOREIGN KEY (id_cheie) REFERENCES chei(id_cheie)
            )
        ''')

    # Creare tabel pentru performanta
    if not table_exists('performanta'):
        cursor.execute('''
            CREATE TABLE performanta (
                id_performanta INTEGER PRIMARY KEY,
                id_fisier INTEGER UNIQUE,
                timp_executie REAL,
                memorie_utilizata REAL,
                FOREIGN KEY (id_fisier) REFERENCES fisiere(id_fisier)
            )
        ''')
def populare_tabele():
    populare_algoritmi()
    populare_chei()
    populare_fisiere()
    populare_performanta()

def populare_algoritmi():
    # Definirea listei de valori pentru a fi inserate
    valori_algoritmi = [
        ('AES', 'simetric', 128), #192,256
        ('Blowfish', 'simetric', 32), #up to 448
        ('Camellia', 'simetric', 128), #192,256
        ('DES', 'simetric', 56),
        ('RC4', 'simetric', 40), #up to 2048
        ('RC5', 'simetric', 128), #up to 2048
        ('RSA', 'asimetric' ,2048),
    ]

    # Inserarea valorilor în tabelul algoritmi
    cursor.executemany('''
        INSERT INTO algoritmi (nume, tip, lungime_cheie) 
        VALUES (?, ?, ?)
    ''', valori_algoritmi)

def populare_chei():
    # Definirea listei de valori pentru a fi inserate
    valori_chei = [
        ('cheie1', 1),  # Exemplu de cheie pentru algoritmul cu id_algoritm 1
        ('cheie2', 1),  # Exemplu de cheie pentru algoritmul cu id_algoritm 1
        ('cheie3', 4),  # Exemplu de cheie pentru algoritmul cu id_algoritm 4
        # Mai multe chei pot fi adăugate aici
    ]

    # Inserarea valorilor în tabelul chei
    cursor.executemany('''
        INSERT INTO chei (valoare_cheie, id_algoritm) 
        VALUES (?, ?)
    ''', valori_chei)

def populare_fisiere():
    # Asumând că utilizatorul este pe Linux/macOS și că fișierul este în directorul home
    proiect_path = os.path.dirname(__file__)  # Calea către directorul în care se află scriptul curent
    fisiere_path = os.path.join(proiect_path, 'fisiere')  # Calea către subdirectorul "fisiere"

    valori_fisiere = [
        ('test.txt', os.path.join(fisiere_path, 'test.txt'), 'criptare', '2024-03-25 10:00:00', 1),
        ('test1.txt', os.path.join(fisiere_path, 'test1.txt'), 'criptare', '2024-03-25 10:00:00', 2),

        # Poți adăuga mai multe fișiere aici dacă este necesar
    ]

    # Inserarea valorilor în tabelul fisiere
    cursor.executemany('''
        INSERT INTO fisiere (nume_fisier, cale_fisier, tip_operatie, timestamp, id_cheie) 
        VALUES (?, ?, ?, ?, ?)
    ''', valori_fisiere)
def populare_performanta():
    cursor.execute('DELETE FROM performanta')  # Adaugă această linie pentru a goli tabelul
    valori_performanta = [
        (1, 0.5, 1024),  # Exemplu de performanță pentru fișierul cu id_fisier 1
        (2, 1.2, 2048),  # Exemplu de performanță pentru fișierul cu id_fisier 2
        (3, 0.8, 1536),  # Exemplu de performanță pentru fișierul cu id_fisier 3
        # Mai multe performanțe pot fi adăugate aici
    ]

    # Inserarea valorilor în tabelul performanta
    cursor.executemany('''
        INSERT INTO performanta (id_fisier, timp_executie, memorie_utilizata) 
        VALUES (?, ?, ?)
    ''', valori_performanta)

def preia_informatii_cheie(id_cheie):
    cursor.execute('''
        SELECT c.valoare_cheie, a.nume
        FROM chei c
        JOIN algoritmi a ON c.id_algoritm = a.id_algoritm
        WHERE c.id_cheie = ?
    ''', (id_cheie,))
    return cursor.fetchone()

def logare_performanta(id_fisier, timp_executie, memorie_utilizata):
    cursor.execute('SELECT id_fisier FROM performanta WHERE id_fisier = ?', (id_fisier,))
    if cursor.fetchone():
        # Actualizează înregistrarea existentă
        cursor.execute('''
            UPDATE performanta SET timp_executie = ?, memorie_utilizata = ? WHERE id_fisier = ?
        ''', (timp_executie, memorie_utilizata, id_fisier))
    else:
        # Inserează o nouă înregistrare
        cursor.execute('''
            INSERT INTO performanta (id_fisier, timp_executie, memorie_utilizata)
            VALUES (?, ?, ?)
        ''', (id_fisier, timp_executie, memorie_utilizata))

def actualizeaza_status_fisier(id_fisier, status_nou):
    cursor.execute('''
        UPDATE fisiere
        SET status = ?
        WHERE id_fisier = ?
    ''', (status_nou, id_fisier))