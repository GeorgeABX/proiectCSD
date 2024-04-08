import sqlite3
import subprocess
import time
import os
import psutil

# Conectare la baza de date
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
    home_path = os.path.expanduser('~')  # Acesta va returna calea către directorul home al utilizatorului curent
    valori_fisiere = [
        ('test.txt', f'{home_path}/test.txt', 'criptare', '2024-03-25 10:00:00', 1),
        # Poți adăuga mai multe fișiere aici dacă este necesar
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


def executa_comanda_openssl(comanda):
    start_time = time.time()
    subprocess.run(comanda, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    end_time = time.time()
    timp_executie = end_time - start_time

    # Omite partea cu măsurarea memoriei pentru moment
    memorie_utilizata = 0  # Aici ar putea fi o valoare estimată sau lăsată la 0 dacă nu este relevantă

    return timp_executie, memorie_utilizata


def cripteaza_fisier(nume_fisier, cheie, algoritm):
    comanda = f'openssl enc -aes-256-cbc -salt -in {nume_fisier} -out {nume_fisier}.enc -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    return timp_executie, memorie_utilizata


def decripteaza_fisier(nume_fisier_enc, cheie, algoritm):
    comanda = f'openssl enc -d -{algoritm} -in {nume_fisier_enc} -out {nume_fisier_enc.replace(".enc", "")} -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    return timp_executie, memorie_utilizata

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

def cripteaza_si_logheaza(id_fisier, cale_fisier, id_cheie):
    valoare_cheie, nume_algoritm = preia_informatii_cheie(id_cheie)
    algoritm = nume_algoritm.lower()
    timp_executie, memorie_utilizata = cripteaza_fisier(cale_fisier, valoare_cheie, algoritm)
    logare_performanta(id_fisier, timp_executie, memorie_utilizata)
    actualizeaza_status_fisier(id_fisier, 'criptat')

def decripteaza_si_logheaza(id_fisier, cale_fisier, id_cheie):
    valoare_cheie, nume_algoritm = preia_informatii_cheie(id_cheie)
    algoritm = nume_algoritm.lower()
    timp_executie, memorie_utilizata = decripteaza_fisier(cale_fisier, valoare_cheie, algoritm)
    logare_performanta(id_fisier, timp_executie, memorie_utilizata)
    actualizeaza_status_fisier(id_fisier, 'decriptat')

def proceseaza_fisiere():
    cursor.execute("SELECT id_fisier, cale_fisier, id_cheie, tip_operatie FROM fisiere WHERE status = 'necriptat'")
    for id_fisier, cale_fisier, id_cheie, _ in cursor.fetchall():  # Ignoră tip_operatie cu _
        cripteaza_si_logheaza(id_fisier, cale_fisier, id_cheie)

    cursor.execute("SELECT id_fisier, cale_fisier, id_cheie, tip_operatie FROM fisiere WHERE status = 'criptat'")
    for id_fisier, cale_fisier, id_cheie, tip_operatie in cursor.fetchall():
        if tip_operatie == 'decriptare':  # Verifică dacă operația este de decriptare
            decripteaza_si_logheaza(id_fisier, cale_fisier, id_cheie)

def main():
    creare_tabele()
    populare_tabele()
    proceseaza_fisiere()
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
