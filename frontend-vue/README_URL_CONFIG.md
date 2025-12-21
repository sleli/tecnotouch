# 🌐 Sistema di Configurazione URL Centralizzato

Questo documento descrive il nuovo sistema centralizzato per la gestione degli URL in tutto il progetto.

## 📋 Problema Risolto

Prima di questa implementazione, il progetto aveva URL hardcoded in vari file, causando problemi quando si accedeva all'applicazione da dispositivi mobili sulla stessa rete. Gli smartphone ottenevano errori `TypeError: Load failed` perché tentavano di chiamare `localhost:8000` invece dell'IP del server.

## 🛠️ Soluzione Implementata

### 1. **File di Configurazione Centralizzato**
- **File**: `frontend-vue/src/config/urls.js`
- **Scopo**: Unico punto di controllo per tutti gli URL del sistema
- **Funzionalità**: Rilevamento automatico dell'ambiente (localhost vs rete)

### 2. **Configurazione di Rete**
```javascript
const NETWORK_CONFIG = {
  SERVER_IP: '192.168.1.18',           // IP del server nella tua rete
  VENDING_MACHINE_IP: '192.168.1.65',  // IP del distributore
  PORTS: {
    FRONTEND_DEV: 3001,  // Frontend sviluppo
    FRONTEND_PROD: 3000, // Frontend produzione
    API_SERVER: 8000,    // Server API
    SIMULATOR: 1500,     // Simulatore
    VENDING_MACHINE: 1500 // Distributore
  }
}
```

### 3. **Rilevamento Automatico**
Il sistema rileva automaticamente da dove viene acceduto:

- **🖥️ Da localhost** (macchina di sviluppo): usa `localhost:8000`
- **📱 Da rete** (smartphone, tablet): usa `192.168.1.18:8000`

### 4. **File di Ambiente**
- `.env.local`: Forza l'uso dell'IP di rete anche in sviluppo
- `.env.development`: Configurazione sviluppo
- `.env.production`: Configurazione produzione

## 📡 URL Disponibili

### Sviluppo
- **Frontend**: http://192.168.1.18:3001/
- **API**: http://192.168.1.18:8000/api
- **Simulatore**: http://192.168.1.18:1500/

### Produzione
- **Frontend**: http://192.168.1.18:3000/
- **API**: http://192.168.1.18:8000/api
- **Distributore**: http://192.168.1.65:1500/

## 🚀 Come Usare

### Per Sviluppatori
Non serve cambiare nulla nel codice! Usa semplicemente:

```javascript
import { API_BASE_URL } from '@/config/urls'

// L'URL sarà automaticamente quello giusto
fetch(`${API_BASE_URL}/motors`)
```

### Per Cambiare IP di Rete
Modifica **solo** il file `frontend-vue/src/config/urls.js`:

```javascript
const NETWORK_CONFIG = {
  SERVER_IP: '192.168.1.XX', // <-- Cambia solo questo
  // ...resto invariato
}
```

## 📱 Test Mobile

1. **Avvia i server**:
   ```bash
   # Backend
   cd backend && python3 api_server.py --ip 0.0.0.0 --port 8000

   # Frontend
   cd frontend-vue && npm run dev -- --host --port 3001
   ```

2. **Accedi da smartphone**:
   - Stesso WiFi del server
   - Apri: `http://192.168.1.18:3001/`
   - ✅ Ora funziona senza errori!

## 🔧 Debug

Per vedere quale URL viene usato, controlla i log del browser:
```
🌍 URL Config - Hostname: 192.168.1.18 | Dev: true | Localhost: false
🚀 URL Configuration loaded: { environment: 'development-network', apiBase: 'http://192.168.1.18:8000/api' }
```

## 📂 File Modificati

- ✅ `frontend-vue/src/config/urls.js` - **NUOVO**: Configurazione centralizzata
- ✅ `frontend-vue/src/stores/app.js` - Usa configurazione centralizzata
- ✅ `frontend-vue/.env.local` - **NUOVO**: Forza IP di rete
- ✅ `frontend-vue/.env.example` - Aggiornato con IP di rete
- ✅ `frontend-vue/.env.production` - **NUOVO**: Configurazione produzione
- ✅ `frontend-vue/vite.config.js` - Cache PWA aggiornata

## ✅ Risultato

- ❌ **Prima**: `TypeError: Load failed` su smartphone
- ✅ **Ora**: Funziona perfettamente su tutti i dispositivi!

---
*Sistema implementato il 24/09/2025 - Ora un unico punto controlla tutti gli URL!* 🎯