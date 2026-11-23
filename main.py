
import sqlite3
from datetime import datetime

DB_NAME = "SpesePersonali.db"


# MENU PRINCIPALE
def mostra_menu():

    print("\n================================")
    print("   SISTEMA SPESE PERSONALI")
    print("================================")
    print("1. Gestione categorie")
    print("2. Inserisci spesa")
    print("3. Definisci Budget Mensile")
    print("4. Visualizza Report")
    print("5. Esci")
    print("================================")

    scelta = input("Inserisci la tua scelta: ")

    return scelta


# GESTIONE CATEGORIE
def gestione_categorie(conn):

    print("\n--- GESTIONE CATEGORIE ---")

    nome_categoria = input("Inserisci il nome della categoria: ")

    # Verifica che il nome non sia vuoto
    if nome_categoria == "":
        print("Errore: il nome della categoria non può essere vuoto.")
        return

    cursor = conn.cursor()

    # Verifica se la categoria esiste già
    cursor.execute("""
        SELECT id_categoria
        FROM CATEGORIE
        WHERE nome_categoria = ?
    """, (nome_categoria,))

    if cursor.fetchone() is not None:
        print("La categoria esiste già!")
        return

    # Inserimento della nuova categoria
    cursor.execute("""
        INSERT INTO CATEGORIE (nome_categoria)
        VALUES (?)
    """, (nome_categoria,))

    conn.commit()

    print("Categoria inserita correttamente!")


# INSERIMENTO SPESE
def inserisci_spesa(conn):

    print("\n--- INSERIMENTO NUOVA SPESA ---")

    # Acquisizione della data
    data_spesa = input("Inserisci la data (YYYY-MM-DD): ")

    # Validazione della data
    try:
        datetime.strptime(data_spesa, "%Y-%m-%d")
    except ValueError:
        print("Errore: data non valida. Utilizzare il formato YYYY-MM-DD.")
        return

    # Acquisizione degli altri dati
    importo = input("Inserisci l'importo: ")
    nome_categoria = input("Inserisci la categoria: ")
    descrizione = input("Inserisci una descrizione (facoltativa): ")

    # Validazione dell'importo
    try:
        importo = float(importo.replace(",", "."))
    except ValueError:
        print("Errore: importo non valido.")
        return

    if importo <= 0:
        print("Errore: l'importo deve essere maggiore di zero.")
        return

    cursor = conn.cursor()

    # Verifica dell'esistenza della categoria
    cursor.execute("""
        SELECT id_categoria
        FROM CATEGORIE
        WHERE nome_categoria = ?
    """, (nome_categoria,))

    categoria = cursor.fetchone()

    if categoria is None:
        print("Errore: la categoria non esiste.")
        return

    id_categoria = categoria[0]

    # Inserimento della spesa
    cursor.execute("""
        INSERT INTO SPESE
        (data_spesa, importo, id_categoria, descrizione)
        VALUES (?, ?, ?, ?)
    """, (data_spesa, importo, id_categoria, descrizione))

    conn.commit()

    print("Spesa inserita correttamente!")


# DEFINIZIONE BUDGET MENSILE
def definisci_budget(conn):

    print("\n--- DEFINIZIONE BUDGET MENSILE ---")

    # Acquisizione del mese
    anno_mese = input("Inserisci il mese (YYYY-MM): ")

    # Validazione del mese
    try:
        datetime.strptime(anno_mese, "%Y-%m")
    except ValueError:
        print("Errore: mese non valido. Utilizzare il formato YYYY-MM.")
        return

    # Acquisizione degli altri dati
    nome_categoria = input("Inserisci la categoria: ")
    importo_budget = input("Inserisci l'importo del budget: ")

    # Validazione dell'importo
    try:
        importo_budget = float(importo_budget.replace(",", "."))
    except ValueError:
        print("Errore: importo budget non valido.")
        return

    if importo_budget <= 0:
        print("Errore: l'importo budget deve essere maggiore di zero.")
        return

    cursor = conn.cursor()

    # Verifica dell'esistenza della categoria
    cursor.execute("""
        SELECT id_categoria
        FROM CATEGORIE
        WHERE nome_categoria = ?
    """, (nome_categoria,))

    categoria = cursor.fetchone()

    if categoria is None:
        print("Errore: la categoria non esiste.")
        return

    id_categoria = categoria[0]

    # Verifica dell'esistenza di un budget per il mese e la categoria
    cursor.execute("""
        SELECT id_budget
        FROM BUDGET_MENSILE
        WHERE anno_mese = ?
        AND id_categoria = ?
    """, (anno_mese, id_categoria))

    budget = cursor.fetchone()

    if budget is None:

        # Il budget non esiste: inserimento
        cursor.execute("""
            INSERT INTO BUDGET_MENSILE
            (anno_mese, id_categoria, importo_budget)
            VALUES (?, ?, ?)
        """, (anno_mese, id_categoria, importo_budget))

        print("Budget inserito correttamente!")

    else:

        # Il budget esiste: aggiornamento
        cursor.execute("""
            UPDATE BUDGET_MENSILE
            SET importo_budget = ?
            WHERE id_budget = ?
        """, (importo_budget, budget[0]))

        print("Budget aggiornato correttamente!")

    conn.commit()


def report_spese_categoria(conn):

    print("\n--- TOTALE SPESE PER CATEGORIA ---")
    print("\nCategoria.............Totale Speso\n")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            C.nome_categoria,
            COALESCE(SUM(S.importo), 0) AS totale_speso
        FROM CATEGORIE C
        LEFT JOIN SPESE S
            ON C.id_categoria = S.id_categoria
        GROUP BY C.id_categoria, C.nome_categoria
        ORDER BY totale_speso DESC
    """)

    risultati = cursor.fetchall()

    if risultati:
        for riga in risultati:
            print(riga[0], "............", round(riga[1], 2))
    else:
        print("Nessuna categoria presente.")


def report_budget_mensile(conn):

    print("\n--- REPORT SPESE MENSILI VS BUDGET ---")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            B.anno_mese,
            C.nome_categoria,
            B.importo_budget,
            COALESCE(SUM(S.importo), 0) AS totale_speso
        FROM BUDGET_MENSILE B
        JOIN CATEGORIE C
            ON B.id_categoria = C.id_categoria
        LEFT JOIN SPESE S
            ON B.id_categoria = S.id_categoria
            AND SUBSTR(S.data_spesa, 1, 7) = B.anno_mese
        GROUP BY
            B.anno_mese,
            C.nome_categoria,
            B.id_categoria,
            B.importo_budget
        ORDER BY
            B.anno_mese,
            C.nome_categoria
    """)

    risultati = cursor.fetchall()

    if risultati:
        for riga in risultati:

            mese = riga[0]
            categoria = riga[1]
            budget = riga[2]
            speso = riga[3]

            print("\nMese:", mese)
            print("Categoria:", categoria)
            print("Budget:", budget)
            print("Speso:", round(speso, 2))

            if speso > budget:
                print("Stato: SUPERAMENTO BUDGET")
            else:
                print("Stato: BUDGET RISPETTATO")

    else:
        print("Nessun budget presente.")


def report_elenco_spese(conn):

    print("\n--- ELENCO SPESE ---")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            S.data_spesa,
            C.nome_categoria,
            S.importo,
            S.descrizione
        FROM SPESE S
        JOIN CATEGORIE C
            ON S.id_categoria = C.id_categoria
        ORDER BY S.data_spesa DESC
    """)

    risultati = cursor.fetchall()

    print("Data........Categoria........Importo........Descrizione")
    print("-------------------------------------------------------")

    if risultati:
        for riga in risultati:
            print(riga[0], ".....", riga[1], ".....",
                  riga[2], ".....", riga[3])
    else:
        print("Nessuna spesa presente.")

################################################################
# Menù dei report
################################################################
def menu_report(conn):

    while True:

        print("\n================================")
        print("       MENU REPORT")
        print("================================")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs Budget")
        print("3. Elenco spese per data")
        print("4. Torna al menu principale")
        print("================================")

        scelta = input("Seleziona un report: ")

        if scelta == "1":
            report_spese_categoria(conn)

        elif scelta == "2":
            report_budget_mensile(conn)

        elif scelta == "3":
            report_elenco_spese(conn)

        elif scelta == "4":
            break

        else:
            print("Scelta non valida. Riprova.")


################################################################
# PROGRAMMA PRINCIPALE
################################################################
def main():

    conn = sqlite3.connect(DB_NAME)

    # Attivazione dei vincoli di integrità referenziale
    conn.execute("PRAGMA foreign_keys = ON")

    try:

        while True:

            scelta = mostra_menu()

            if scelta == "1":
                gestione_categorie(conn)

            elif scelta == "2":
                inserisci_spesa(conn)

            elif scelta == "3":
                definisci_budget(conn)

            elif scelta == "4":
                menu_report(conn)

            elif scelta == "5":
                print("Arrivederci!")
                break

            else:
                print("Scelta non valida. Riprova.")

    finally:
        conn.close()



if __name__ == "__main__":
    main()
