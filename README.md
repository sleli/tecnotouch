# Tecnotouch - Vending Machine Sales Dashboard

A modern web-based dashboard system for monitoring and analyzing sales data from cigarette vending machines. This project provides real-time sales tracking, visual motor grid monitoring, and comprehensive analytics through an intuitive Progressive Web App (PWA) interface.

## Features

- **Real-time Sales Monitoring**: Track sales, revenue, and performance metrics with auto-refresh every 30 seconds
- **Visual Motor Grid**: Interactive 70+ motor visualization showing product availability and sales status
- **Event Download System**: Automated downloading and archiving of vending machine events
- **Offline Testing**: Built-in simulator for development and testing without physical hardware
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **RESTful API**: Full API support for integration with other systems
- **Docker Support**: Complete containerized deployment for easy setup and scaling

## Architecture

The system consists of three main components:

1. **Frontend**: Modern Vue.js PWA with Tailwind CSS (port 3000)
2. **Backend**: Flask API server handling data processing and machine communication (port 8000)
3. **Simulator**: Flask-based vending machine simulator for offline testing (port 1500)

```
┌─────────────────────────────────────────────────────────┐
│                    Network/Docker                       │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │  Frontend    │    │   Backend    │    │Simulator │ │
│  │  (Vue.js)    │◄───┤   (Flask)    │◄───┤ (Flask)  │ │
│  │  Port 3000   │    │   Port 8000  │    │Port 1500 │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│                            │                            │
│                            ▼                            │
│                   ┌─────────────────┐                  │
│                   │  SQLite DB      │                  │
│                   │  Event Archives │                  │
│                   └─────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## Requirements

### For Local Installation

- Python 3.7+
- Node.js 14+ (for frontend development)
- pip3

### For Docker Installation

- Docker Engine 20.10+
- Docker Compose 1.29+

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/tecnotouch.git
cd tecnotouch
```

### 2. Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your network settings:

```bash
# For testing with simulator
DISTRIBUTOR_IP=localhost
DISTRIBUTOR_PASSWORD=admin

# For production with real vending machine
DISTRIBUTOR_IP=192.168.1.65
DISTRIBUTOR_PASSWORD=your_password

# Optional (have defaults)
API_PORT=8000
FRONTEND_PORT=3000
DISTRIBUTOR_PORT=1500
```

### 3. Install Dependencies

#### macOS/Linux

```bash
# Python dependencies
pip3 install requests flask flask-cors python-dotenv

# Frontend dependencies (optional, for development)
cd frontend-vue
npm install
cd ..
```

#### Windows

```powershell
# Python dependencies
pip3 install requests flask flask-cors python-dotenv

# Frontend dependencies (optional, for development)
cd frontend-vue
npm install
cd ..
```

## Usage

### Option 1: Unified Startup Scripts (Recommended)

The easiest way to start the entire system with a single command.

#### macOS/Linux

```bash
# Interactive menu
./start.sh

# Simulation mode (with simulator)
./start.sh --ip localhost

# Production mode (with real vending machine)
./start.sh --ip 192.168.1.65
```

#### Windows

```powershell
# Interactive menu
start.bat

# Simulation mode (with simulator)
start.bat --ip localhost

# Production mode (with real vending machine)
start.bat --ip 192.168.1.65
```

The scripts automatically:
- Clean Vite cache
- Build Vue.js frontend
- Start API server and frontend
- Handle cleanup on exit (Ctrl+C)

### Option 2: Docker Deployment

#### Simulation Mode (with simulator for testing)

```bash
# Start all containers with simulator
docker-compose --profile simulation up

# In detached mode (background)
docker-compose --profile simulation up -d
```

#### Production Mode (with real vending machine)

```bash
# Start frontend and backend only
docker-compose up

# In detached mode (background)
docker-compose up -d
```

#### Docker Management Commands

```bash
# View logs
docker-compose logs -f              # All services
docker-compose logs -f backend      # Backend only
docker-compose logs -f frontend     # Frontend only

# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes database!)
docker-compose down -v

# Rebuild after code changes
docker-compose build
docker-compose up --build

# Restart individual container
docker-compose restart backend
```

### Option 3: Manual Setup

If you prefer to run components separately:

#### Start API Server

```bash
# Simulation mode
python3 backend/api_server.py --ip localhost --port 8000

# Production mode
python3 backend/api_server.py --ip 192.168.1.65 --port 8000
```

#### Start Frontend

```bash
cd frontend-vue/dist
python3 -m http.server 3000
```

#### Start Simulator (for testing only)

```bash
python3 simulator/vending_machine_simulator.py
```

#### Access Dashboard

Open your browser and navigate to:
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **Simulator**: http://localhost:1500

## Command Line Tools

### Download Events from Vending Machine

```bash
# Download last 30 days (default)
python3 backend/download_events.py

# Custom filename and timeframe (90 days)
python3 backend/download_events.py eventi_$(date +%Y%m%d).html 90

# Download full year
python3 backend/download_events.py eventi_anno.html 365

# With simulator
python3 backend/download_events.py --simulator
```

### Analyze Sales Data

```bash
python3 backend/sales_analyzer.py
```

### Verify Configuration

```bash
python3 scripts/verify_env.py
```

## Project Structure

```
tecnotouch/
├── backend/                          # Backend API server
│   ├── api_server.py                # Flask API server
│   ├── download_events.py           # Event download CLI
│   ├── cigarette_machine_client.py  # Vending machine client
│   ├── sales_analyzer.py            # Sales analytics
│   └── past_events/                 # Event archives (auto-cleanup 30 days)
├── frontend-vue/                    # Vue.js frontend
│   ├── src/                        # Vue source files
│   ├── dist/                       # Production build (gitignored)
│   └── .env                        # Frontend configuration
├── simulator/                       # Vending machine simulator
│   ├── vending_machine_simulator.py
│   └── sample_data.json            # Sample event data
├── shared/                          # Shared configuration
│   └── config.py                   # Central configuration module
├── docker-compose.yml              # Docker orchestration
├── start.sh                        # macOS/Linux startup script
├── start.bat                       # Windows startup script
├── .env.example                    # Configuration template
└── CLAUDE.md                       # Development guidelines
```

## Configuration Details

### Environment Variables

The project uses a unified `.env` file for both local and Docker deployments.

**Required variables:**
- `DISTRIBUTOR_IP` - Vending machine IP (use `localhost` for simulator)
- `DISTRIBUTOR_PASSWORD` - Admin username/password

**Optional variables (with defaults):**
- `API_PORT=8000` - API server port
- `FRONTEND_PORT=3000` - Frontend port
- `DISTRIBUTOR_PORT=1500` - Vending machine port
- `DB_PATH=sales_data.db` - Database file path

### Frontend Auto-Configuration

The frontend automatically detects the server IP using `window.location.hostname`, making it accessible from any device on the network without additional configuration.

## Development

### Frontend Development

```bash
cd frontend-vue
npm install
npm run dev  # Development server with hot-reload
npm run build  # Production build
```

### Cache Busting

For development, the system includes automatic cache busting:
- Timestamp-based JS file versioning
- Meta tags to prevent browser caching
- Auto-reload on file changes

### API Development

The Flask API server provides these endpoints:

- `GET /health` - Health check
- `GET /api/events` - Get events data
- `GET /api/statistics` - Get sales statistics
- `POST /api/download` - Download new events
- And more...

## Troubleshooting

### Port Already in Use

Change ports in `.env`:

```bash
FRONTEND_PORT=3001
API_PORT=8001
```

### Cannot Connect to Vending Machine

1. Verify IP address in `.env`
2. Check network connectivity: `ping 192.168.1.65`
3. Try simulator mode: `./start.sh --ip localhost`

### Docker Container Not Starting

```bash
# Check logs
docker-compose logs backend

# Verify health status
docker ps

# Rebuild containers
docker-compose build --no-cache
docker-compose up
```

### Database Issues

```bash
# Backup database
cp backend/data/sales_data.db backup.db

# Reset database (Docker)
docker-compose down -v
docker-compose up
```

## Data Management

### Event Archives

- Downloaded events are automatically saved to `backend/past_events/`
- Files older than 30 days are automatically cleaned up
- Only JSON files are stored (HTML removed)

### Database

- SQLite database: `backend/data/sales_data.db`
- Contains sales tracking and analytics data
- Automatically created on first run

## Remote Access

The dashboard can be accessed from other devices on the network:

1. Find your machine's IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep inet

   # Windows
   ipconfig
   ```

2. Access from mobile/tablet:
   ```
   http://YOUR_IP:3000
   ```

The frontend automatically connects to the correct API server.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in `CLAUDE.md`

## Acknowledgments

Built with:
- [Vue.js](https://vuejs.org/) - Frontend framework
- [Flask](https://flask.palletsprojects.com/) - Backend framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [Docker](https://www.docker.com/) - Containerization

---

Made with ❤️ for vending machine operators
