import sqlite3
import subprocess

conn = sqlite3.connect('baza_de_date.db')
cursor = conn.cursor()

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

    if not table_exists('chei'):
        cursor.execute('''
            CREATE TABLE chei (
                id_cheie INTEGER PRIMARY KEY,
                valoare_cheie TEXT,
                id_algoritm INTEGER,
                FOREIGN KEY (id_algoritm) REFERENCES algoritmi(id_algoritm)
            )
        ''')

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

def populare_algoritmi():
    valori_algoritmi = [
        ('AES', 'simetric', 256),
        ('Blowfish', 'simetric', 128),
        ('Camellia', 'simetric', 256),
        ('DES', 'simetric', 56),
        ('RSA', 'asimetric', 2048),
    ]
    cursor.executemany('''
        INSERT INTO algoritmi (nume, tip, lungime_cheie) 
        VALUES (?, ?, ?)
    ''', valori_algoritmi)
    conn.commit()

def adauga_cheie_simetrica(valoare_cheie, id_algoritm):
    cursor.execute('''
        INSERT INTO chei (valoare_cheie, id_algoritm) 
        VALUES (?, ?)
    ''', (valoare_cheie, id_algoritm))
    conn.commit()

def adauga_cheie_rsa(dimensiune_cheie=2048):
    private_key_pem, public_key_pem = genereaza_chei_rsa(dimensiune_cheie)
    cursor.execute('''
        INSERT INTO chei (valoare_cheie, id_algoritm) 
        VALUES (?, ?)
    ''', (private_key_pem.decode(), 5))  # 5 este ID-ul pentru RSA în tabelul algoritmi
    conn.commit()
    return private_key_pem, public_key_pem

def genereaza_chei_rsa(dimensiune_cheie=2048):
    private_key = subprocess.check_output(f'openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:{dimensiune_cheie}', shell=True)
    public_key = subprocess.check_output('openssl rsa -pubout -in private_key.pem -out public_key.pem', shell=True)

    with open("private_key.pem", "rb") as priv_file:
        private_key_pem = priv_file.read()
    with open("public_key.pem", "rb") as pub_file:
        public_key_pem = pub_file.read()

    return private_key_pem, public_key_pem

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
        cursor.execute('''
            UPDATE performanta SET timp_executie = ?, memorie_utilizata = ? WHERE id_fisier = ?
        ''', (timp_executie, memorie_utilizata, id_fisier))
    else:
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
    conn.commit()

def populare_tabele():
    populare_algoritmi()

    # Adăugare chei simetrice
    aes_keys = ['thisisaverysecurekey1234567890', 'anothersecurekey1234567890']
    blowfish_keys = ['simplekey123', 'anotherblowfishkey123']
    camellia_keys = ['securecamelliakey256bitkey1234', 'anothercamelliakey123456']
    des_keys = ['shortkey', 'anotherdeskey']

    cursor.execute("SELECT id_algoritm FROM algoritmi WHERE nume = 'AES'")
    aes_id = cursor.fetchone()[0]
    for key in aes_keys:
        adauga_cheie_simetrica(key, aes_id)

    cursor.execute("SELECT id_algoritm FROM algoritmi WHERE nume = 'Blowfish'")
    blowfish_id = cursor.fetchone()[0]
    for key in blowfish_keys:
        adauga_cheie_simetrica(key, blowfish_id)

    cursor.execute("SELECT id_algoritm FROM algoritmi WHERE nume = 'Camellia'")
    camellia_id = cursor.fetchone()[0]
    for key in camellia_keys:
        adauga_cheie_simetrica(key, camellia_id)

    cursor.execute("SELECT id_algoritm FROM algoritmi WHERE nume = 'DES'")
    des_id = cursor.fetchone()[0]
    for key in des_keys:
        adauga_cheie_simetrica(key, des_id)

    # Adăugare chei RSA
    for _ in range(2):
        adauga_cheie_rsa()

# Populează baza de date
if __name__ == "__main__":
    creare_tabele()
    populare_tabele()
