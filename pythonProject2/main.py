import os
import database
import file_processing

def main():
    database.creare_tabele()
    database.populare_tabele()



    database.conn.commit()
    database.conn.close()

if __name__ == "__main__":
    main()
