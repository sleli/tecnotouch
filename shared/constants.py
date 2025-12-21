#!/usr/bin/env python3
"""
Costanti condivise per il sistema distributore sigarette
"""

# Tipi di eventi
EVENT_TYPES = {
    'PROGRAMMING': 'PROGRAMMAZIONE',
    'EVENT': 'EVENTO',
    'BANKNOTE': 'BANCONOTA',
    'COIN': 'MONETA',
    'POS': 'POS',
    'CHANGE': 'RESTO',
    'RECEIPT': 'SCONTRINO',
    'EMAIL': 'EMAIL',
    'ANOMALY': 'ANOMALIA',
    'UPDATE': 'AGGIORNAMENTI'
}

# Metodi di pagamento
PAYMENT_METHODS = {
    'CASH': 'CASH',
    'POS': 'POS',
    'CARD': 'CARD',
    'UNKNOWN': 'UNKNOWN'
}

# Formati data/ora
DATE_FORMATS = {
    'EVENT_TIMESTAMP': '%d/%m/%y %H:%M:%S',
    'API_DATE': '%Y-%m-%d',
    'FILE_TIMESTAMP': '%Y%m%d_%H%M%S',
    'DISPLAY_DATETIME': '%d/%m/%Y %H:%M:%S',
    'DISPLAY_DATE': '%d/%m/%Y'
}

# Limiti sistema
LIMITS = {
    'MAX_MOTORS': 100,
    'MAX_EVENTS_PER_QUERY': 10000,
    'DEFAULT_DAYS_BACK': 30,
    'MAX_DAYS_BACK': 365,
    'AUTO_REFRESH_INTERVAL': 30,  # secondi
    'DOWNLOAD_TIMEOUT': 120       # secondi
}

# Messaggi sistema
MESSAGES = {
    'LOGIN_SUCCESS': '✅ Login effettuato con successo',
    'LOGIN_FAILED': '❌ Login fallito: credenziali errate',
    'DOWNLOAD_STARTED': '🔄 Download eventi avviato',
    'DOWNLOAD_COMPLETED': '✅ Download completato con successo',
    'DOWNLOAD_FAILED': '❌ Download fallito',
    'SIMULATOR_MODE': '🎰 Modalità simulatore attiva',
    'PRODUCTION_MODE': '📡 Connesso al distributore fisico',
    'EXIT_PROGRAMMING': '🚪 Uscita dalla modalità programmazione'
}

# Regex patterns
PATTERNS = {
    'MOTOR_ID': r'M(\d+)',
    'PRICE': r'(\d+[.,]\d{2})',
    'EVENT_NUMBER': r'#(\d+)',
    'IP_ADDRESS': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
}

# Query patterns per eventi
EVENT_QUERY_PATTERNS = {
    'ALL_EVENTS': '*',
    'DATE_RANGE': '*|{start_date}|{end_date}',
    'MOTOR_FILTER': 'M{motor_id}',
    'EVENT_TYPE_FILTER': '{event_type}|{start_date}|{end_date}'
}