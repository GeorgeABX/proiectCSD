import subprocess
import time
from database import preia_informatii_cheie, logare_performanta, actualizeaza_status_fisier, cursor
import database

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
    comanda = f'openssl enc -d -aes-256-cbc -in "{nume_fisier_enc}" -out "{nume_fisier_enc.replace(".enc", "")}" -pass pass:{cheie}'

    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    return timp_executie, memorie_utilizata



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




def afiseaza_continut_fisier(nume_fisier):
    print(f"Conținutul fișierului {nume_fisier}:")
    try:
        with open(nume_fisier, 'rb') as fisier:  # Deschide ca binar
            continut = fisier.read()
            print(continut.decode('utf-8', errors='replace'))  # Încearcă să decodezi ca UTF-8, înlocuiește erorile
    except Exception as e:
        print(f"Eroare la citirea fișierului {nume_fisier}: {e}")

def afiseaza_continut_fisier_hex(nume_fisier):
    print(f"Conținutul fișierului {nume_fisier} (hex):")
    try:
        with open(nume_fisier, 'rb') as fisier:
            continut = fisier.read()
            print(continut.hex())
    except Exception as e:
        print(f"Eroare la citirea fișierului {nume_fisier}: {e}")

