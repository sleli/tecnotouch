# Distributore Dashboard - Vue.js PWA

Mobile-first Progressive Web App dashboard per il monitoraggio di distributori di sigarette.

## 🚀 Caratteristiche

### 📱 Mobile-First Design
- **Bottom Navigation**: Navigazione nativa iOS/Android-style
- **Touch Optimized**: Target touch 64px+, gesture support
- **Responsive Grid**: Griglia motori adattiva 3-10 colonne
- **PWA Native**: Installabile come app nativa

### 🔧 Funzionalità
- **Dashboard Real-time**: KPI e grafici aggiornati ogni 30s
- **Gestione Motori**: Griglia 70+ motori con status visuale
- **Sistema Alert**: Notifiche critiche con badge
- **Statistiche**: Analisi vendite e performance dettagliate
- **Offline Mode**: Funzionalità offline con cache intelligente

### ⚡ Performance
- **Bundle Optimized**: ~105KB gzipped iniziale
- **Virtual Scrolling**: Performance su grandi dataset
- **Lazy Loading**: Componenti caricati on-demand
- **Service Worker**: Cache avanzata e background sync

## 🏗️ Architettura Tecnica

```
frontend-vue/
├── src/
│   ├── components/          # Componenti riutilizzabili
│   │   ├── BottomNavigation.vue
│   │   ├── MotorGrid.vue
│   │   ├── MotorCard.vue
│   │   └── charts/         # Grafici Chart.js
│   ├── views/              # Pagine principali
│   │   ├── DashboardView.vue
│   │   ├── MotorsView.vue
│   │   ├── AlertsView.vue
│   │   └── StatisticsView.vue
│   ├── stores/             # State management (Pinia)
│   │   ├── app.js          # Store applicazione
│   │   ├── motors.js       # Store motori
│   │   └── alerts.js       # Store alerts
│   ├── composables/        # Logic riutilizzabile
│   │   └── useApi.js       # HTTP client
│   └── utils/
│       └── pwa.js          # PWA utilities
└── public/
    ├── manifest.json       # PWA manifest
    └── sw.js              # Service Worker
```

## 🛠️ Stack Tecnologico

- **Vue 3**: Composition API + `<script setup>`
- **Vite**: Build tool veloce con HMR
- **Pinia**: State management moderno
- **Vue Router**: Routing SPA
- **Tailwind CSS**: Utility-first CSS
- **Chart.js**: Grafici interattivi
- **Workbox**: Service Worker per PWA
- **Lucide Icons**: Icone ottimizzate

## 🚦 Installazione & Avvio

### Prerequisiti
- Node.js 18+
- Python 3.7+
- npm o yarn

### Setup Rapido

```bash
# 1. Installa dipendenze
cd frontend-vue
npm install

# 2. Avvia in sviluppo
npm run dev  # Frontend su http://localhost:5173

# 3. Avvia API backend (terminal separato)
cd ../backend
python3 api_server.py  # API su http://localhost:8000
```

### Produzione - Sistema Unificato

```bash
# Avvio sistema completo (raccomandato)
./start_vue_system.sh

# Opzioni quick:
./start_vue_system.sh --quick-sim   # Modalità simulazione
./start_vue_system.sh --quick-prod  # Modalità produzione
```

Il sistema sarà disponibile su:
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **Simulator** (se attivo): http://localhost:1500

## 📱 Installazione PWA

1. Apri http://localhost:3000 su smartphone
2. Tocca "Aggiungi alla schermata Home" nel browser
3. L'app verrà installata come applicazione nativa

### Funzionalità PWA

- ✅ **Offline Mode**: Funziona senza connessione
- ✅ **Push Notifications**: Alert critici sistema
- ✅ **Background Sync**: Sincronizza azioni offline
- ✅ **Add to Home Screen**: Icona nativa
- ✅ **Full Screen**: Modalità standalone

## 🔧 Configurazione

### Variabili Ambiente

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api

# .env.production
VITE_API_BASE_URL=http://192.168.1.100:8000/api
```

### API Endpoints

Il frontend comunica con gli stessi endpoint Flask del sistema originale:

```javascript
/api/motors           # Lista motori con status
/api/dashboard/stats  # KPI dashboard
/api/statistics/*     # Dati statistiche
/api/download/events  # Download eventi
/api/health          # Health check
```

## 🏭 Deploy Produzione

### Opzione 1: Sistema Semplice (Raccomandato)

```bash
# Build una tantum
cd frontend-vue
npm run build

# Deploy identico a quello attuale
./start_vue_system.sh --quick-prod
```

### Opzione 2: Docker (Opzionale)

```bash
# Build immagine
docker build -t distributore-dashboard .

# Run container
docker run -p 3000:80 -p 8000:8000 distributore-dashboard
```

## 📊 Performance

### Metriche Bundle
- **Initial**: ~105KB gzipped
- **Vendor**: ~35KB (Vue, Router, Pinia)
- **Charts**: ~25KB (Chart.js)
- **Icons**: ~15KB (Lucide)

### Loading Performance
- **First Paint**: <1s su 3G
- **Interactive**: <2s su 3G
- **Offline Ready**: <5s dopo prima visita

## 🔄 Migrazione dal Sistema Esistente

### Zero Downtime
1. Il sistema Vue può girare in parallelo all'esistente
2. **Backend Flask invariato** - nessuna modifica necessaria
3. Switch deploy quando pronto

### Compatibilità
- ✅ **API Backend**: 100% compatibile
- ✅ **Deploy Script**: Stesso pattern `start_system.sh`
- ✅ **Mini PC**: Stessi requisiti di sistema
- ✅ **Rete**: Stessa configurazione 192.168.1.65

## 🐛 Debug & Troubleshooting

### Common Issues

```bash
# Build non funziona
npm run build  # Ricompila assets

# API non raggiungibile
# Verifica che backend/api_server.py sia in running

# PWA non si installa
# Controlla che HTTPS sia attivo (prod) o localhost (dev)

# Grafici non caricano
# Verifica endpoint /api/dashboard/charts
```

### Logs

```bash
# Browser DevTools
Console -> Application -> Service Workers

# Server logs
tail -f /var/log/supervisor/api.log        # API
tail -f /var/log/supervisor/nginx.log      # Frontend
```

## 🔮 Sviluppi Futuri

### Roadmap
- [ ] **Real-time WebSocket**: Updates istantanei via WebSocket
- [ ] **Camera QR**: Scan QR code motori per identificazione rapida
- [ ] **Geofencing**: Alert automatici basati su posizione
- [ ] **Voice Commands**: Controllo vocale per mani libere
- [ ] **AR Overlay**: Realtà aumentata per identificazione motori

### API Extensions
- [ ] **Motor History**: `/api/motors/{id}/history`
- [ ] **Predictive Analytics**: `/api/analytics/predictions`
- [ ] **Maintenance Scheduling**: `/api/maintenance/schedule`

---

## 📞 Support

Per supporto tecnico:
- **Issues**: GitHub Issues
- **Docs**: `/docs` nella root del progetto
- **API Reference**: `/api/docs` (se abilitato)

---

**🎯 Mission**: Trasformare il monitoraggio distributori da desktop-first a mobile-native, mantenendo la semplicità di deploy che ami.