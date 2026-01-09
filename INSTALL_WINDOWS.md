# Guida Installazione Windows - Dashboard Distributore

## Panoramica

Questa guida ti accompagna nell'installazione del sistema dashboard per il distributore di sigarette su Windows. Il sistema è composto da:
- **Backend Python** (Flask API)
- **Frontend Vue.js** (Dashboard web)
- **Simulatore** (per testing senza hardware)

## Prerequisiti

### Software Necessario

1. **Python 3.11 o superiore**
   - Scarica da: https://www.python.org/downloads/
   - Durante l'installazione: **SPUNTARE "Add Python to PATH"**
   - Verifica: apri CMD e digita `python --version`

2. **Node.js 18 LTS o superiore** (include npm)
   - Scarica da: https://nodejs.org/
   - Installa versione LTS (Long Term Support)
   - Verifica: apri CMD e digita `node --version` e `npm --version`

3. **Accesso Amministratore**
   - Necessario solo per l'installazione iniziale
   - Serve per creare servizi Windows e configurare firewall

### Hardware
- Windows 10 o superiore
- 4GB RAM minimo
- 1GB spazio disco libero

---

## Installazione Rapida (10 minuti)

### Step 1: Configurazione Progetto

1. **Copia il progetto** nella cartella desiderata (es. `C:\tecnotouch\`)

2. **Crea file .env**:
   ```batch
   copy .env.example .env
   ```

3. **Modifica .env** con un editor di testo (Notepad):
   ```env
   DISTRIBUTOR_IP=192.168.1.65      # IP del distributore reale
   DISTRIBUTOR_PORT=1500
   DISTRIBUTOR_PASSWORD=admin        # Username admin
   API_HOST=0.0.0.0
   API_PORT=8000
   FRONTEND_PORT=3000
   DB_PATH=sales_data.db
   ```

   **IMPORTANTE**:
   - `DISTRIBUTOR_IP` determina la modalità al riavvio
   - IP reale = modalità PRODUZIONE
   - `localhost` = modalità SIMULAZIONE

### Step 2: Installazione Automatica

1. **Click destro su `install.bat`**
2. **Seleziona "Esegui come amministratore"**
3. **Attendi il completamento** (5-10 minuti)

Lo script eseguirà automaticamente:
- ✅ Download e installazione NSSM (service manager)
- ✅ Verifica Python, Node.js, npm
- ✅ Installazione dipendenze Python (Flask, requests, ecc.)
- ✅ Installazione dipendenze npm (Vue.js, Vite, Tailwind CSS)
- ✅ Build frontend Vue.js (genera cartella `dist/`)
- ✅ Creazione 3 servizi Windows:
  - `VendingBackendAPI` - Backend Flask (avvio automatico)
  - `VendingFrontend` - Server HTTP per dashboard (avvio automatico)
  - `VendingSimulator` - Simulatore (avvio manuale)
- ✅ Configurazione firewall (porte 3000, 8000)

### Step 3: Primo Avvio

Doppio click su `start.bat`

Dashboard disponibile su: **http://localhost:3000**

---

## Utilizzo Quotidiano

### Avvio Normale

```batch
start.bat
```
Avvia i servizi usando la modalità configurata in `.env`

### Cambio Modalità

#### Passare a Simulazione (per test)
```batch
scripts\switch-to-simulation.bat
```
Questo script:
1. Fa backup di `.env`
2. Imposta `DISTRIBUTOR_IP=localhost`
3. Avvia simulatore
4. Riavvia servizi

Simulatore disponibile su: http://localhost:1500

#### Tornare a Produzione
```batch
scripts\switch-to-production.bat
```
Questo script:
1. Ripristina `.env` originale
2. Ferma simulatore
3. Riavvia servizi produzione

### Arresto Sistema

```batch
stop.bat
```
Ferma tutti i servizi

---

## Gestione Servizi Windows

### Tramite Interfaccia Grafica

1. Premi `Win + R`
2. Digita `services.msc`
3. Cerca "Distributore" o "Vending"

I tre servizi sono:
- **VendingBackendAPI** - Backend API (auto-start)
- **VendingFrontend** - Dashboard web (auto-start)
- **VendingSimulator** - Simulatore (manuale)

### Tramite PowerShell

```powershell
# Visualizza status
Get-Service Vending*

# Avvia servizi
Start-Service VendingBackendAPI, VendingFrontend

# Ferma servizi
Stop-Service VendingBackendAPI, VendingFrontend

# Riavvia servizi
Restart-Service VendingBackendAPI, VendingFrontend
```

---

## Comportamento al Riavvio PC

**Domanda**: "Se il PC si riavvia, cosa parte automaticamente?"

**Risposta**: Parte la modalità configurata nel file `.env`:

| Configurazione .env | Modalità al Riavvio | Servizi Avviati |
|---------------------|---------------------|------------------|
| `DISTRIBUTOR_IP=192.168.1.65` | PRODUZIONE | Backend + Frontend |
| `DISTRIBUTOR_IP=localhost` | SIMULAZIONE | Backend + Frontend<br>(Simulatore va avviato manualmente) |

**Raccomandazione**: Lasciare `.env` sempre in modalità PRODUZIONE. Per test occasionali, usare `switch-to-simulation.bat`.

---

## Accesso da Altri Dispositivi

### Dashboard da Smartphone/Tablet

1. **Trova IP del PC Windows**:
   ```batch
   ipconfig
   ```
   Cerca "Indirizzo IPv4" (es. `192.168.1.100`)

2. **Da smartphone sulla stessa rete**:
   - Apri browser
   - Vai su `http://192.168.1.100:3000`

3. **Installa PWA** (Progressive Web App):
   - Sul browser mobile: Menu → "Aggiungi a schermata Home"
   - Funziona come app nativa!

### Firewall

Il firewall Windows è configurato automaticamente durante install.bat per permettere:
- Porta 3000 (Dashboard)
- Porta 8000 (API)

---

## Troubleshooting

### Problema: "Python non trovato"
**Soluzione**:
1. Reinstalla Python da python.org
2. Durante installazione, spunta "Add Python to PATH"
3. Riavvia CMD e riprova

### Problema: "Node.js non trovato"
**Soluzione**:
1. Installa Node.js LTS da nodejs.org
2. Riavvia CMD
3. Verifica: `node --version`

### Problema: "npm install fallito"
**Soluzione**:
- Verifica connessione internet
- Prova: `cd frontend-vue` poi `npm install`
- Se errore persiste, elimina `node_modules` e riprova

### Problema: "Servizi non partono"
**Soluzione**:
1. Apri `services.msc`
2. Trova servizio "VendingBackendAPI"
3. Click destro → "Proprietà" → Tab "Accesso"
4. Verifica log in `logs\backend-stderr.log`

### Problema: "Dashboard non si carica"
**Soluzione**:
1. Verifica servizi running: `Get-Service Vending*`
2. Prova accesso diretto API: http://localhost:8000/api/health
3. Controlla log: `logs\frontend-stderr.log`
4. Verifica che `frontend-vue\dist\` esista

### Problema: "Porta già in uso"
**Soluzione**:
```powershell
# Trova processo sulla porta 3000
netstat -ano | findstr :3000

# Termina processo (sostituisci PID)
taskkill /PID <numero_PID> /F
```

### Log Files

I log sono disponibili in `logs\`:
- `backend-stdout.log` - Output backend
- `backend-stderr.log` - Errori backend
- `frontend-stdout.log` - Output frontend
- `simulator-stdout.log` - Output simulatore

---

## Disinstallazione

### Rimozione Completa

```batch
uninstall.bat
```

Rimuove:
- Tutti i servizi Windows
- Regole firewall
- NSSM (service manager)

**Non rimuove**:
- Python, Node.js (potrebbero servire per altri progetti)
- File progetto (eliminali manualmente se desiderato)

---

## Struttura File Progetto

```
tecnotouch/
├── .env                          # Configurazione (NON committare)
├── .env.example                  # Template configurazione
├── install.bat                   # Installazione (admin)
├── start.bat                     # Avvio servizi
├── stop.bat                      # Arresto servizi
├── uninstall.bat                 # Disinstallazione (admin)
├── backend/
│   ├── requirements.txt          # Dipendenze Python
│   ├── api_server.py            # Flask API server
│   ├── data_processor.py        # Elaborazione dati
│   ├── cigarette_machine_client.py
│   └── past_events/             # Eventi scaricati (auto)
├── frontend-vue/
│   ├── package.json             # Dipendenze npm
│   ├── src/                     # Codice Vue.js
│   ├── dist/                    # Build produzione (auto)
│   └── node_modules/            # Librerie npm (auto)
├── simulator/
│   ├── requirements.txt         # Dipendenze simulatore
│   ├── vending_machine_simulator.py
│   └── sample_data.json         # Dati test
├── scripts/
│   ├── install-services.ps1     # Script installazione
│   ├── start-services.ps1       # Script avvio
│   ├── switch-to-simulation.ps1 # Switch simulazione
│   └── switch-to-production.ps1 # Switch produzione
└── logs/                         # Log servizi (auto)
```

---

## FAQ

### Q: Posso usare il sistema senza servizi Windows?
**A**: Sì, puoi eseguire gli script manualmente:
```batch
cd backend
python api_server.py --port 8000

# In un altro terminale
cd frontend-vue\dist
python -m http.server 3000
```

### Q: Come aggiorno il frontend dopo modifiche?
**A**:
```batch
cd frontend-vue
npm run build
```
Poi riavvia servizio VendingFrontend

### Q: Posso cambiare le porte?
**A**: Sì, modifica `.env`:
```env
API_PORT=8001
FRONTEND_PORT=3001
```
Poi reinstalla servizi: `uninstall.bat` → `install.bat`

### Q: Il simulatore funziona senza hardware?
**A**: Sì! Il simulatore emula completamente il distributore. Perfetto per sviluppo e test.

### Q: Posso installare su un server Windows sempre acceso?
**A**: Assolutamente! I servizi Windows sono pensati proprio per questo. Partiranno automaticamente all'avvio.

---

## Supporto

### File di Log
Controlla sempre i log prima di chiedere supporto:
```
logs\backend-stderr.log
logs\frontend-stderr.log
logs\simulator-stderr.log
```

### Informazioni Utili per Debug
```powershell
# Versioni software
python --version
node --version
npm --version

# Status servizi
Get-Service Vending* | Format-List

# Test API
curl http://localhost:8000/api/health

# Porte in ascolto
netstat -an | findstr "3000 8000 1500"
```

---

## Note Tecniche

### NSSM (Non-Sucking Service Manager)
- Tool per eseguire programmi come servizi Windows
- Scaricato automaticamente da https://nssm.cc
- Installato in `C:\nssm\nssm.exe`
- Gestisce auto-restart e logging

### Frontend Vue.js
- Framework: Vue 3 + Vite
- Styling: Tailwind CSS
- PWA ready (Progressive Web App)
- Build genera file statici in `dist/`

### Backend Flask
- Python 3.11+
- Flask + Flask-CORS
- Legge configurazione da `.env` (python-dotenv)
- SQLite database per dati vendite

### Configurazione Priorità
1. File `.env` (massima priorità)
2. Variabili ambiente Windows
3. Default hardcoded in `shared/config.py`

---

**Installazione completata! 🎉**

Dashboard: http://localhost:3000
