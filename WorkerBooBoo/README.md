# WorkerBooBoo - Workplace Safety Data Visualization

A web application that visualizes workplace injuries and fatalities using OSHA data on an interactive map.

## Features

- **Interactive Map**: Visualize workplace incidents with clustering and filtering
- **OSHA Data Integration**: Real-time data from OSHA enforcement and fatality databases
- **Advanced Search**: Filter by date, industry, location, incident type
- **Statistics Dashboard**: Trends, industry analysis, and safety insights
- **Responsive Design**: Mobile-first interface for field workers and safety professionals

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Mapping**: Mapbox GL JS
- **Backend**: FastAPI (Python)
- **Database**: SQLite (prototype) / PostgreSQL (production)
- **Data Processing**: Python with pandas, requests
- **Styling**: Tailwind CSS + Headless UI

## Quick Start

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Add your Mapbox access token and OSHA API keys
   ```

3. **Run the Application**
   ```bash
   # Backend (Terminal 1)
   cd backend
   uvicorn main:app --reload
   
   # Frontend (Terminal 2)
   cd frontend
   npm run dev
   ```

4. **Access the App**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Data Sources

- OSHA Enforcement Data API
- OSHA Fatality Investigation Data
- Industry classification codes
- Geographic data for mapping

## Project Structure

```
WorkerBooBoo/
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── data/              # Data processing scripts
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## Contributing

This is a prototype for workplace safety awareness. Please ensure all data handling follows privacy and security best practices.
