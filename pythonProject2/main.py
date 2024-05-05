import os
import database
import file_processing

def main():
    database.creare_tabele()
    database.populare_tabele()

    id_cheie = 1
    cale_fisier = os.path.expanduser('fisiere/test1.txt')

    # Criptare
    print("Începe criptarea...")
    file_processing.cripteaza_si_logheaza(id_cheie, cale_fisier, id_cheie)
    print("Fișierul a fost criptat.")

    # Afișează conținutul fișierului criptat
    file_processing.afiseaza_continut_fisier_hex(f"{cale_fisier}.enc")

    # Decriptare
    print("Începe decriptarea...")
    file_processing.decripteaza_si_logheaza(id_cheie, f"{cale_fisier}.enc", id_cheie)
    print("Fișierul a fost decriptat.")

    # Afișează conținutul fișierului decriptat
    file_processing.afiseaza_continut_fisier(cale_fisier)

    database.conn.commit()
    database.conn.close()

if __name__ == "__main__":
    main()
