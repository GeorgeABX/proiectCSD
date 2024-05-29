import subprocess
import time
import psutil
from database import preia_informatii_cheie, logare_performanta, actualizeaza_status_fisier, cursor


def executa_comanda_openssl(comanda):
    start_time = time.time()
    process = subprocess.Popen(comanda, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ps_process = psutil.Process(process.pid)

    max_memory = 0
    while process.poll() is None:  # În timp ce procesul rulează
        try:
            memory_info = ps_process.memory_info()
            max_memory = max(max_memory, memory_info.rss / 1024)  # Actualizează memoria maximă în KB
        except psutil.NoSuchProcess:
            break  # Procesul s-a terminat

    process.communicate()  # Așteaptă terminarea procesului
    end_time = time.time()

    timp_executie = end_time - start_time
    return timp_executie, max_memory


def cripteaza_fisier_aes(nume_fisier, cheie):
    comanda = f'openssl enc -aes-256-cbc -salt -in "{nume_fisier}" -out "{nume_fisier}.enc" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(f"{nume_fisier}.enc", 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content.hex()


def decripteaza_fisier_aes(nume_fisier_enc, cheie):
    output_file = nume_fisier_enc.replace(".enc", "")
    comanda = f'openssl enc -d -aes-256-cbc -in "{nume_fisier_enc}" -out "{output_file}" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(output_file, 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content


def cripteaza_fisier_blowfish(nume_fisier, cheie):
    comanda = f'openssl enc -bf -salt -in "{nume_fisier}" -out "{nume_fisier}.enc" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(f"{nume_fisier}.enc", 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content.hex()


def decripteaza_fisier_blowfish(nume_fisier_enc, cheie):
    output_file = nume_fisier_enc.replace(".enc", "")
    comanda = f'openssl enc -d -bf -in "{nume_fisier_enc}" -out "{output_file}" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(output_file, 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content


def cripteaza_fisier_camellia(nume_fisier, cheie):
    comanda = f'openssl enc -camellia-256-cbc -salt -in "{nume_fisier}" -out "{nume_fisier}.enc" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(f"{nume_fisier}.enc", 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content.hex()


def decripteaza_fisier_camellia(nume_fisier_enc, cheie):
    output_file = nume_fisier_enc.replace(".enc", "")
    comanda = f'openssl enc -d -camellia-256-cbc -in "{nume_fisier_enc}" -out "{output_file}" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(output_file, 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content


def cripteaza_fisier_des(nume_fisier, cheie):
    comanda = f'openssl enc -des-cbc -salt -in "{nume_fisier}" -out "{nume_fisier}.enc" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(f"{nume_fisier}.enc", 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content.hex()


def decripteaza_fisier_des(nume_fisier_enc, cheie):
    output_file = nume_fisier_enc.replace(".enc", "")
    comanda = f'openssl enc -d -des-cbc -in "{nume_fisier_enc}" -out "{output_file}" -pass pass:{cheie}'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(output_file, 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content


def cripteaza_fisier_rsa(nume_fisier, cheie_publica):
    with open("public_key.pem", "wb") as file:
        file.write(cheie_publica.encode())
    comanda = f'openssl rsautl -encrypt -inkey public_key.pem -pubin -in "{nume_fisier}" -out "{nume_fisier}.enc"'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(f"{nume_fisier}.enc", 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content.hex()


def decripteaza_fisier_rsa(nume_fisier_enc, cheie_privata):
    with open("private_key.pem", "wb") as file:
        file.write(cheie_privata.encode())
    output_file = nume_fisier_enc.replace(".enc", "")
    comanda = f'openssl rsautl -decrypt -inkey private_key.pem -in "{nume_fisier_enc}" -out "{output_file}"'
    timp_executie, memorie_utilizata = executa_comanda_openssl(comanda)
    with open(output_file, 'rb') as file:
        content = file.read()
    return timp_executie, memorie_utilizata, content


def cripteaza_si_logheaza(id_fisier, cale_fisier, id_cheie, logger):
    try:
        valoare_cheie, nume_algoritm = preia_informatii_cheie(id_cheie)
        algoritm = nume_algoritm.lower()
        logger(f"Începe criptarea fișierului {cale_fisier}")

        if algoritm == "aes":
            timp_executie, memorie_utilizata, content_hex = cripteaza_fisier_aes(cale_fisier, valoare_cheie)
        elif algoritm == "blowfish":
            timp_executie, memorie_utilizata, content_hex = cripteaza_fisier_blowfish(cale_fisier, valoare_cheie)
        elif algoritm == "camellia":
            timp_executie, memorie_utilizata, content_hex = cripteaza_fisier_camellia(cale_fisier, valoare_cheie)
        elif algoritm == "des":
            timp_executie, memorie_utilizata, content_hex = cripteaza_fisier_des(cale_fisier, valoare_cheie)
        elif algoritm == "rsa":
            timp_executie, memorie_utilizata, content_hex = cripteaza_fisier_rsa(cale_fisier, valoare_cheie)
        else:
            raise ValueError("Algoritm necunoscut")

        logare_performanta(id_fisier, timp_executie, memorie_utilizata)
        actualizeaza_status_fisier(id_fisier, 'criptat')
        return timp_executie, memorie_utilizata, content_hex
    except Exception as e:
        logger(f"Error: {str(e)}")
        return 0, 0, ""


def decripteaza_si_logheaza(id_fisier, cale_fisier, id_cheie, logger):
    valoare_cheie, nume_algoritm = preia_informatii_cheie(id_cheie)
    algoritm = nume_algoritm.lower()
    logger(f"Începe decriptarea fișierului {cale_fisier}")
    try:
        if algoritm == "aes":
            timp_executie, memorie_utilizata, content_decriptat = decripteaza_fisier_aes(cale_fisier, valoare_cheie)
        elif algoritm == "blowfish":
            timp_executie, memorie_utilizata, content_decriptat = decripteaza_fisier_blowfish(cale_fisier,
                                                                                              valoare_cheie)
        elif algoritm == "camellia":
            timp_executie, memorie_utilizata, content_decriptat = decripteaza_fisier_camellia(cale_fisier,
                                                                                              valoare_cheie)
        elif algoritm == "des":
            timp_executie, memorie_utilizata, content_decriptat = decripteaza_fisier_des(cale_fisier, valoare_cheie)
        elif algoritm == "rsa":
            timp_executie, memorie_utilizata, content_decriptat = decripteaza_fisier_rsa(cale_fisier, valoare_cheie)
        else:
            raise ValueError("Algoritm necunoscut")

        logare_performanta(id_fisier, timp_executie, memorie_utilizata)
        actualizeaza_status_fisier(id_fisier, 'decriptat')
        return timp_executie, memorie_utilizata, content_decriptat
    except Exception as e:
        logger(f"Error: {str(e)}")
        return 0, 0, b""
