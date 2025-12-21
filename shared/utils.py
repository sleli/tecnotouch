#!/usr/bin/env python3
"""
Utilità condivise per il sistema distributore sigarette
"""

import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from .constants import DATE_FORMATS, PATTERNS


def format_datetime(dt: Union[str, datetime], format_type: str = 'DISPLAY_DATETIME') -> str:
    """Formatta data/ora secondo i formati standard"""
    if isinstance(dt, str):
        try:
            # Prova diversi formati di input
            for fmt in DATE_FORMATS.values():
                try:
                    dt = datetime.strptime(dt, fmt)
                    break
                except ValueError:
                    continue
            else:
                # Se non riusciamo a parsare, proviamo ISO format
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return str(dt)

    if isinstance(dt, datetime):
        return dt.strftime(DATE_FORMATS[format_type])

    return str(dt)


def parse_motor_id(text: str) -> Optional[int]:
    """Estrae l'ID motore da una stringa"""
    match = re.search(PATTERNS['MOTOR_ID'], text)
    return int(match.group(1)) if match else None


def parse_price(text: str) -> Optional[float]:
    """Estrae il prezzo da una stringa"""
    match = re.search(PATTERNS['PRICE'], text)
    if match:
        price_str = match.group(1).replace(',', '.')
        try:
            return float(price_str)
        except ValueError:
            pass
    return None


def parse_event_number(text: str) -> Optional[str]:
    """Estrae il numero evento da una stringa"""
    match = re.search(PATTERNS['EVENT_NUMBER'], text)
    return match.group(1) if match else None


def validate_ip_address(ip: str) -> bool:
    """Valida un indirizzo IP"""
    return bool(re.match(PATTERNS['IP_ADDRESS'], ip))


def get_hours_since_last_sale(last_sale_datetime: Optional[str]) -> Optional[int]:
    """Calcola le ore dall'ultima vendita"""
    if not last_sale_datetime:
        return None

    try:
        last_sale = datetime.fromisoformat(last_sale_datetime.replace('Z', '+00:00'))
        hours = int((datetime.now() - last_sale).total_seconds() / 3600)
        return max(0, hours)
    except (ValueError, TypeError):
        return None


def generate_filename(prefix: str, suffix: str = '', timestamp: bool = True) -> str:
    """Genera nome file con timestamp opzionale"""
    if timestamp:
        ts = datetime.now().strftime(DATE_FORMATS['FILE_TIMESTAMP'])
        return f"{prefix}_{ts}{suffix}"
    return f"{prefix}{suffix}"


def load_json_file(file_path: str) -> Optional[Any]:
    """Carica file JSON con gestione errori"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print(f"❌ Errore nel caricamento file {file_path}: {e}")
        return None


def save_json_file(data: Any, file_path: str, pretty: bool = True) -> bool:
    """Salva dati in file JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        return True
    except (IOError, TypeError) as e:
        print(f"❌ Errore nel salvataggio file {file_path}: {e}")
        return False


def find_latest_file(pattern: str, directory: str = '.') -> Optional[str]:
    """Trova il file più recente che corrisponde al pattern"""
    try:
        files = [f for f in os.listdir(directory) if pattern in f]
        if not files:
            return None
        return max(files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    except OSError:
        return None


def cleanup_old_files(pattern: str, keep_count: int = 10, directory: str = '.') -> int:
    """Rimuove file vecchi mantenendo solo i più recenti"""
    try:
        files = [f for f in os.listdir(directory) if pattern in f]
        if len(files) <= keep_count:
            return 0

        # Ordina per data di modifica (più vecchi prima)
        files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)))

        # Rimuovi i file più vecchi
        files_to_remove = files[:-keep_count]
        removed_count = 0

        for file in files_to_remove:
            try:
                os.remove(os.path.join(directory, file))
                removed_count += 1
            except OSError:
                pass

        return removed_count
    except OSError:
        return 0


def sanitize_filename(filename: str) -> str:
    """Sanifica nome file rimuovendo caratteri non validi"""
    # Rimuovi caratteri non validi per filesystem
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limita lunghezza
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext

    return filename


def get_file_size_mb(file_path: str) -> Optional[float]:
    """Ottieni dimensione file in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except OSError:
        return None


def create_backup_filename(original_path: str) -> str:
    """Crea nome file di backup"""
    directory = os.path.dirname(original_path)
    filename = os.path.basename(original_path)
    name, ext = os.path.splitext(filename)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{name}_backup_{timestamp}{ext}"

    return os.path.join(directory, backup_name)


def extract_brand_from_product_name(product_name: str) -> str:
    """Estrae il nome della marca dal nome prodotto"""
    if not product_name:
        return "UNKNOWN"

    # Rimuovi caratteri speciali e spazi extra
    clean_name = re.sub(r'[^\w\s]', ' ', product_name).strip()

    # Prendi la prima parola come marca
    words = clean_name.split()
    return words[0].upper() if words else "UNKNOWN"


def format_currency(amount: Union[int, float], currency: str = '€') -> str:
    """Formatta importo come valuta"""
    try:
        return f"{currency} {float(amount):.2f}"
    except (ValueError, TypeError):
        return f"{currency} 0.00"


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """Divisione sicura che evita divisione per zero"""
    try:
        return float(numerator) / float(denominator) if denominator != 0 else default
    except (ValueError, TypeError):
        return default


def get_date_range_days(start_date: str, end_date: str) -> int:
    """Calcola numero di giorni tra due date"""
    try:
        start = datetime.strptime(start_date, DATE_FORMATS['API_DATE'])
        end = datetime.strptime(end_date, DATE_FORMATS['API_DATE'])
        return (end - start).days + 1
    except ValueError:
        return 0


def is_recent_timestamp(timestamp: str, hours_threshold: int = 24) -> bool:
    """Verifica se un timestamp è recente"""
    try:
        ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        hours_diff = (datetime.now() - ts).total_seconds() / 3600
        return hours_diff < hours_threshold
    except (ValueError, TypeError):
        return False