import sqlite3

# Conectare la baza de date
conn = sqlite3.connect('baza_de_date.db')
cursor = conn.cursor()

# Funcție pentru a verifica dacă o tabelă există deja
def table_exists(table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def creere_tabele():
    # Creare tabel pentru algoritmi
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
                hash TEXT,
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
    # Definirea listei de valori pentru a fi inserate
    valori_fisiere = [
        ('fisier1.txt', '/cale/fisier1.txt', 'criptare', '2024-03-25 10:00:00', 1),
        ('fisier2.txt', '/cale/fisier2.txt', 'decriptare', '2024-03-25 11:00:00', 2),
        ('fisier3.txt', '/cale/fisier3.txt', 'criptare', '2024-03-25 12:00:00', 3),
        # Mai multe fișiere pot fi adăugate aici
    ]

    # Inserarea valorilor în tabelul fisiere
    cursor.executemany('''
        INSERT INTO fisiere (nume_fisier, cale_fisier, tip_operatie, timestamp, id_cheie) 
        VALUES (?, ?, ?, ?, ?)
    ''', valori_fisiere)

def populare_performanta():
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

def main():
    # creere_tabele()
    # populare_tabele()
    # Interogare SQL pentru a selecta algoritmul cu cel mai mic timp de executie și cea mai puțină memorie utilizată
    cursor.execute('''
        SELECT a.nume, p.timp_executie, p.memorie_utilizata
        FROM algoritmi a
        INNER JOIN chei c ON a.id_algoritm = c.id_algoritm
        INNER JOIN fisiere f ON c.id_cheie = f.id_cheie
        INNER JOIN performanta p ON f.id_fisier = p.id_fisier
        ORDER BY p.timp_executie ASC, p.memorie_utilizata ASC
        LIMIT 1
    ''')

    # Extrage rezultatul interogării
    rezultat = cursor.fetchone()

    # Afisare rezultat
    if rezultat:
        nume_algoritm, timp_executie, memorie_utilizata = rezultat
        print(f"Algoritmul cu cel mai mic timp de executie și cea mai puțină memorie utilizată este: {nume_algoritm}")
        print(f"Timp de execuție: {timp_executie} secunde")
        print(f"Memorie utilizată: {memorie_utilizata} MB")
    else:
        print("Nu există date disponibile în baza de date.")

main()
# Salvare (commit) modificări și închidere conexiune
conn.commit()
conn.close()