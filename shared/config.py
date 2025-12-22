#!/usr/bin/env python3
"""
Configurazioni centralizzate per il sistema distributore sigarette
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Carica .env dalla root del progetto
load_dotenv()


class Config:
    """Configurazioni centrali del sistema"""

    # Distributore
    DEFAULT_DISTRIBUTOR_IP = os.getenv('DISTRIBUTOR_IP')
    DEFAULT_DISTRIBUTOR_PORT = int(os.getenv('DISTRIBUTOR_PORT', '1500'))
    DEFAULT_USERNAME = os.getenv('DISTRIBUTOR_USERNAME')

    # API Server
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))

    # Frontend
    FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', '3000'))

    # Database
    DEFAULT_DB_PATH = os.getenv('DB_PATH', 'sales_data.db')

    # File Output
    EVENTS_FILE_PREFIX = "events_"
    JSON_SUFFIX = "_events_only.json"
    COMPLETE_JSON_SUFFIX = "_complete.json"

    # Headers HTTP standardizzati
    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    LOGIN_HEADERS = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1'
    }

    JSON_HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    @classmethod
    def get_distributor_url(cls, ip: str = None) -> str:
        """Genera URL distributore"""
        ip = ip or cls.DEFAULT_DISTRIBUTOR_IP
        return f"http://{ip}:{cls.DEFAULT_DISTRIBUTOR_PORT}"

    @classmethod
    def get_api_url(cls, host: str = None, port: int = None) -> str:
        """Genera URL API server"""
        host = host or cls.API_HOST
        port = port or cls.API_PORT
        return f"http://{host}:{port}"

    @classmethod
    def is_simulator_ip(cls, ip: str) -> bool:
        """Verifica se l'IP è quello del simulatore"""
        return ip in ['localhost', '127.0.0.1', 'simulator']

    @classmethod
    def validate_required(cls):
        """Valida che le variabili obbligatorie siano impostate"""
        missing = []

        if not cls.DEFAULT_DISTRIBUTOR_IP:
            missing.append('DISTRIBUTOR_IP')
        if not cls.DEFAULT_USERNAME:
            missing.append('DISTRIBUTOR_USERNAME')

        if missing:
            raise ValueError(
                f"Variabili d'ambiente obbligatorie mancanti: {', '.join(missing)}\n"
                f"Creare file .env copiando .env.example e impostare i valori richiesti."
            )

    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Carica configurazioni da variabili d'ambiente"""
        return {
            'distributor_ip': os.getenv('DISTRIBUTOR_IP', cls.DEFAULT_DISTRIBUTOR_IP),
            'api_port': int(os.getenv('API_PORT', cls.API_PORT)),
            'db_path': os.getenv('DB_PATH', cls.DEFAULT_DB_PATH),
            'frontend_port': int(os.getenv('FRONTEND_PORT', cls.FRONTEND_PORT))
        }


class Endpoints:
    """Endpoint API standardizzati"""

    # Distributore/Simulatore endpoints
    LOGIN = "/login"
    LOGIN_CHECK = "/login_check"
    EVENTS_PAGE = "/events2"
    EVENTS_QUERY = "/events2_query"
    ADMIN_EXIT = "/admin_index_back"

    # API Server endpoints
    API_DASHBOARD = "/api/dashboard"
    API_MOTORS = "/api/motors"
    API_MOTOR_DETAIL = "/api/motor/{motor_id}"
    API_STATISTICS_OVERVIEW = "/api/statistics/overview"
    API_STATISTICS_BY_BRAND = "/api/statistics/by-brand"
    API_STATISTICS_TRANSACTIONS = "/api/statistics/transactions"
    API_DOWNLOAD_EVENTS = "/api/download-events"
    API_DOWNLOAD_STATUS = "/api/download-status"
    API_DOWNLOAD_INFO = "/api/download-info"
    API_HEALTH = "/api/health"