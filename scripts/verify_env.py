#!/usr/bin/env python3
"""Verifica configurazione environment"""
import sys
import os

# Add parent directory to path to import shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Config

print("\n" + "="*60)
print("🔍 VERIFICA CONFIGURAZIONE ENVIRONMENT")
print("="*60)

# Check required variables
required_missing = []
if not Config.DEFAULT_DISTRIBUTOR_IP:
    required_missing.append('DISTRIBUTOR_IP')
if not Config.DEFAULT_USERNAME:
    required_missing.append('DISTRIBUTOR_USERNAME')

print(f"\n📌 Valori Caricati da Config:")
print(f"   DISTRIBUTOR_IP:       {Config.DEFAULT_DISTRIBUTOR_IP or '❌ REQUIRED - NOT SET'}")
print(f"   DISTRIBUTOR_PORT:     {Config.DEFAULT_DISTRIBUTOR_PORT}")
print(f"   DISTRIBUTOR_USERNAME: {Config.DEFAULT_USERNAME or '❌ REQUIRED - NOT SET'}")
print(f"   API_PORT:             {Config.API_PORT}")
print(f"   FRONTEND_PORT:        {Config.FRONTEND_PORT}")
print(f"   DB_PATH:              {Config.DEFAULT_DB_PATH}")

print(f"\n📋 Variabili d'Ambiente (da .env):")
print(f"   DISTRIBUTOR_IP:       {os.getenv('DISTRIBUTOR_IP', '❌ NOT SET')}")
print(f"   DISTRIBUTOR_USERNAME: {os.getenv('DISTRIBUTOR_USERNAME', '❌ NOT SET')}")
print(f"   API_PORT:             {os.getenv('API_PORT', '(using default)')}")

env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_file):
    print(f"\n✅ File .env trovato nella root del progetto")
else:
    print(f"\n⚠️  File .env NON trovato")
    print(f"   Crea .env copiando: cp .env.example .env")

if required_missing:
    print(f"\n❌ ERRORE: Variabili obbligatorie mancanti: {', '.join(required_missing)}")
    print(f"   Impostare queste variabili nel file .env")
    print("="*60 + "\n")
    sys.exit(1)
else:
    print(f"\n✅ Tutte le variabili obbligatorie sono impostate")

print("="*60 + "\n")
