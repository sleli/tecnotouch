import json
from datetime import datetime, timedelta
import sys

def add_days_to_json_dates(input_file, output_file, days_to_add=10):
    """
    Legge un file JSON e sposta tutte le date nei campi 'dateTime' avanti di un numero specificato di giorni

    Args:
        input_file: path del file JSON di input
        output_file: path del file JSON di output
        days_to_add: numero di giorni da aggiungere (default: 10)
    """

    print(f"📖 Leggendo il file: {input_file}")

    # Leggo il file JSON
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Errore: File {input_file} non trovato!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Errore nel parsing JSON: {e}")
        return None

    dates_modified = 0

    # Funzione per processare ricorsivamente la struttura dati
    def process_item(item):
        nonlocal dates_modified

        if isinstance(item, dict):
            # Se è un dizionario, controllo tutti i campi
            for key, value in item.items():
                if key == "dateTime" and isinstance(value, str):
                    # Parsing della data nel formato dd/MM/yy HH:mm:ss
                    try:
                        # Prima provo con anno a 2 cifre
                        date_obj = datetime.strptime(value, "%d/%m/%y %H:%M:%S")
                    except ValueError:
                        try:
                            # Se fallisce, provo con anno a 4 cifre
                            date_obj = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
                        except ValueError:
                            print(f"⚠️  Errore nel parsing della data: {value}")
                            continue

                    # Aggiungo i giorni
                    new_date = date_obj + timedelta(days=days_to_add)

                    # Riconverto nel formato originale (mantengo anno a 2 cifre)
                    old_date = item[key]
                    item[key] = new_date.strftime("%d/%m/%y %H:%M:%S")
                    dates_modified += 1

                    if dates_modified <= 5:  # Mostro solo i primi 5 esempi
                        print(f"   {old_date} → {item[key]}")

                elif isinstance(value, (dict, list)):
                    # Se il valore è un dict o una lista, processo ricorsivamente
                    process_item(value)

        elif isinstance(item, list):
            # Se è una lista, processo ogni elemento
            for element in item:
                process_item(element)

    # Processo i dati
    process_item(data)

    # Salvo il nuovo file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ File salvato: {output_file}")
        print(f"📊 Totale date modificate: {dates_modified}")
    except Exception as e:
        print(f"❌ Errore nel salvataggio: {e}")
        return None

    return data

if __name__ == "__main__":
    # Parametri di default
    input_file = "sample_data.json"  # Cambia questo con il nome del tuo file
    output_file = "sample_data_shifted.json"  # Nome del file di output
    days_to_add = 10

    # Se vengono passati parametri da riga di comando
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        days_to_add = int(sys.argv[3])

    print(f"🚀 Inizio elaborazione...")
    print(f"📂 File input: {input_file}")
    print(f"📂 File output: {output_file}")
    print(f"📅 Giorni da aggiungere: {days_to_add}")
    print("-" * 50)

    result = add_days_to_json_dates(input_file, output_file, days_to_add)

    if result is not None:
        print("-" * 50)
        print("🎉 Elaborazione completata con successo!")
    else:
        print("❌ Elaborazione fallita!")
