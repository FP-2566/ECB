import requests
from bs4 import BeautifulSoup
import re
import time

T0 = time.time()

def BTM0(url):
    # Make the request to the URL
    response = requests.get(url)
    # Parse the content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the parent div containing the box class
    parent_div = soup.find('div', class_='px-0 lg:px-8 py-0 lg:py-12 mx-auto max-w-7xl xl:px-0 issuers')
    if parent_div:
        # Now find the 'box' div within the parent
        box_div = parent_div.find('div', class_='box')
        if box_div:
            # Extract the x-data attribute
            x_data = box_div.get('x-data')
            if x_data:
                # Use regex to extract the symbols list
                match = re.search(r"symbols:\s*\[(.*?)\]", x_data, re.DOTALL)
                if match:
                    symbols_str = match.group(1)
                    # Extract individual symbol entries
                    symbols = re.findall(r"\{([^}]+)\}", symbols_str)
                    result = []
                    for symbol in symbols:
                        # Extract key, name, and issuer using regex
                        key = re.search(r"key:\s*'([^']+)'", symbol).group(1)
                        name = re.search(r"name:\s*'([^']+)'", symbol).group(1)
                        issuer = re.search(r"issuer:\s*'([^']+)'", symbol).group(1)
                        # Construct the tuple with the concatenated URL
                        url = f"https://www.borzamalta.com.mt/reports/{key}"
                        result.append((url, key, name, issuer))
                    return result
                else:
                    return "Symbols list not found"
            else:
                return "No x-data attribute found in the 'box' div"
        else:
            return "No 'box' div found inside the parent div"
    else:
        return "No parent div with the specified class found"

# Example usage
url = 'https://www.borzamalta.com.mt/'
BTM = BTM0(url)


import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

from datetime import datetime, timedelta

def transform_and_interpolate(data, TYPE='PRICE'):
    # Trasforma i timestamp in date leggibili
    data_transformed = [(datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'), value) for ts, value in data]
    dates = [datetime.strptime(date, '%Y-%m-%d') for date, _ in data_transformed]
    values = [value for _, value in data_transformed]
    
    # Crea tutte le date nell'intervallo
    all_dates = [min(dates) + timedelta(days=i) for i in range((max(dates) - min(dates)).days + 1)]
    missing_dates = set(all_dates) - set(dates)
    
    # Interpolazione dei dati
    interpolated_data = {
        "first_tuples": [
            (date.strftime('%Y-%m-%d'), values[dates.index(date)] if date in dates else values[dates.index(max(d for d in dates if d < date))]) 
            for date in all_dates
        ],
        "last_tuples": []
    }
    # Gestione di last_tuples in base al tipo (VOLUME o PRICE)
    if TYPE == 'VOLUME':
        # Se TYPE è 'VOLUME', i valori mancanti sono sostituiti con 0
        interpolated_data["last_tuples"] = [
            (date.strftime('%Y-%m-%d'), 0 if date in missing_dates else values[dates.index(date)]) 
            for date in all_dates
        ]
    elif TYPE == 'PRICE':
        # Se TYPE è 'PRICE', i valori mancanti sono sostituiti con l'ultimo valore non nullo
        last_value = None
        for date in all_dates:
            if date in dates:
                last_value = values[dates.index(date)]
                interpolated_data["last_tuples"].append((date.strftime('%Y-%m-%d'), last_value))
            else:
                # Usa l'ultimo valore disponibile
                interpolated_data["last_tuples"].append((date.strftime('%Y-%m-%d'), last_value if last_value is not None else 0))
    return interpolated_data


def extract_data_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Trova il tag <script> contenente 'var points ='
    script_tag = soup.find('script', string=lambda t: t and 'var points =' in t)
    if script_tag:
        script_content = script_tag.string
        first_occurrence = re.search(r'\[([^\]]*)\]', script_content)
        last_occurrence = re.findall(r'\[([^\]]*)\]', script_content)
        def extract_tuples(data_string):
            pairs = re.findall(r'{\s*x\s*:\s*(\d+)\s*,\s*y\s*:\s*([\d.]+)\s*}', data_string)
            return [(int(x), float(y)) for x, y in pairs]
        if first_occurrence and last_occurrence:
            first_string = first_occurrence.group(1)
            last_string = last_occurrence[-1]
            
            first_tuples = extract_tuples(first_string)
            last_tuples = extract_tuples(last_string)
            interpolated_result = {
                "first_occurrence": transform_and_interpolate(first_tuples, TYPE='PRICE'),
                "last_occurrence": transform_and_interpolate(last_tuples, TYPE='VOLUME')
            }
            T = interpolated_result['first_occurrence']['first_tuples'][0][0]
            return interpolated_result, T
        else:
            return None
    else:
        return None

# Esempio d'uso
url = 'https://www.borzamalta.com.mt/reports/1923A'
extract_data_from_url(url)

from datetime import datetime
from tqdm import tqdm

def extract_data_from_urls(urls):
    results = {}
    TX = None  # Inizializza TX come None
    for url in tqdm(urls, desc="Elaborazione URL", unit="URL"):
        try:
            # Esegui l'elaborazione dell'URL
            result, T = extract_data_from_url(url[0])
            if result:
                results[url[2]] = result
                if T:
                    # Converte T in datetime se è una stringa
                    if isinstance(T, str):
                        T = datetime.strptime(T, "%Y-%m-%d")
                    
                    # Aggiorna TX se è il valore minimo o se è la prima iterazione
                    if TX is None or T < TX:
                        TX = T
            else:
                results[url[2]] = None  # Salva None se non vengono trovati dati
        except Exception as e:
            # Stampa l'errore e salva None per l'URL corrente
            print(f"Errore durante l'elaborazione di {url}: {e}")
            results[url[2]] = None  
    return results, TX


results, T = extract_data_from_urls(BTM)


import pandas as pd
import requests
import os
from io import BytesIO
from tempfile import NamedTemporaryFile

def MSEPRX(PP=None):
    url = "https://cdn.borzamalta.com.mt/download/statistics/index_MSEPRX.xls"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Errore nel download: status {response.status_code}")
    if PP is None:
        # Carica direttamente in memoria senza salvare file fisico
        excel_file = BytesIO(response.content)
        df = pd.read_excel(excel_file, header=None)
    else:
        # Salva il file sul disco
        with open(PP, "wb") as f:
            f.write(response.content)
        df = pd.read_excel(PP, header=None)
    # Trova la riga che contiene "Date" nella prima colonna
    idx = df.index[df.iloc[:, 0] == 'Date']
    if len(idx) == 0:
        raise ValueError("Nessuna riga con 'Date' trovata nella prima colonna")
    header_row = idx[0]
    # Usa questa riga come intestazione e prendi tutte le righe successive
    df_clean = df.iloc[header_row + 1:].copy()
    df_clean.columns = df.iloc[header_row]
    # Reset indice
    df_clean.reset_index(drop=True, inplace=True)
    # Converti la colonna Date in datetime
    df_clean['Date'] = pd.to_datetime(df_clean['Date'])
    # Ordina per data crescente
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    # Filtra solo le colonne desiderate
    colonne_desiderate = ['Date', 'Index', '% Change']
    colonne_presenti = [col for col in colonne_desiderate if col in df_clean.columns]
    df_finale = df_clean[colonne_presenti]    
    return df_finale


INDEX = MSEPRX()

import pandas as pd

def TORO_ORSO(df=INDEX):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    def calcola_fase(df, soglia, lookback):
        fasi = []
        for i in range(len(df)):
            prezzo_attuale = df.loc[i, 'Index']
            inizio_finestra = max(0, i - lookback)
            prezzi_passati = df.loc[inizio_finestra:i, 'Index']
            minimo_recente = prezzi_passati.min()
            massimo_recente = prezzi_passati.max()
            variazione_dal_min = (prezzo_attuale - minimo_recente) / minimo_recente
            variazione_dal_max = (prezzo_attuale - massimo_recente) / massimo_recente
            if variazione_dal_min >= soglia:
                fase = 'bull'
            elif variazione_dal_max <= -soglia:
                fase = 'bear'
            else:
                fase = 'neutrale'
            fasi.append(fase)
        return fasi
    # Fase di lungo termine: 20% su 252 giorni
    df['FASE_MERCATO_LUNGO'] = calcola_fase(df, soglia=0.20, lookback=252)
    # Fase di breve termine: 10% su 63 giorni (≈ trimestre)
    df['FASE_MERCATO_BREVE'] = calcola_fase(df, soglia=0.10, lookback=63)
    return df

INDEX = TORO_ORSO()


# Visualizza i risultati
for url, data in results.items():
    print(f"\nURL: {url}")
    print(f"Dati estratti: {data}")

print(T)

T0 = time.time() - T0
print(f"MINUTI DI LETTURA PARI A {int(T0/60)}")


