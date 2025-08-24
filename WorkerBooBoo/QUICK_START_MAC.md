# WorkerBooBoo - Mac Quick Start Guide

## 🚀 Get Started on macOS in 5 Minutes

WorkerBooBoo is a comprehensive workplace safety data visualization platform that shows workplace injuries and fatalities on an interactive map using OSHA data.

## 📋 Prerequisites

- **Python 3.8+** - Install via [Homebrew](https://brew.sh/) or [python.org](https://www.python.org/downloads/)
- **Node.js 16+** - Install via [Homebrew](https://brew.sh/) or [nodejs.org](https://nodejs.org/)
- **Git** - Usually pre-installed, or install via Homebrew

### Install with Homebrew (Recommended)
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Node.js
brew install python node

# Verify installations
python3 --version
node --version
npm --version
```

## 🛠️ Installation & Setup

### Option 1: One-Click Startup (Easiest)
1. **Open Terminal** and navigate to the WorkerBooBoo folder
2. **Run the startup script**:
   ```bash
   cd WorkerBooBoo
   ./start_all.sh
   ```
3. **Your browser will automatically open** to the application
4. **Keep the terminal open** - it's running both services

### Option 2: Manual Setup (Step by Step)

#### Step 1: Start the Backend
```bash
cd WorkerBooBoo/backend

# Install Python dependencies
pip3 install -r requirements.txt

# Seed the database with sample data
python3 seed_data.py

# Start the backend server
python3 main.py
```

#### Step 2: Start the Frontend (in a new terminal)
```bash
cd WorkerBooBoo/frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

### Option 3: Individual Scripts
- **Backend only**: `./start_backend.sh`
- **Frontend only**: `./start_frontend.sh`

## 🌐 Access the Application

Once running, you can access:
- **Frontend App**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🗄️ Database Setup

The application uses SQLite by default for prototyping. To seed the database with sample data:

```bash
cd backend
python3 seed_data.py
```

This will create:
- Sample workplace incidents across the US
- Industry classifications
- Geographic data for mapping

## 🗺️ Mapbox Configuration

For the interactive map to work, you'll need a Mapbox access token:

1. Sign up at [Mapbox](https://www.mapbox.com/)
2. Get your access token
3. Update `frontend/src/pages/MapView.tsx` line 25:
   ```typescript
   mapboxgl.accessToken = 'your_actual_token_here'
   ```

## 📊 Features

### Dashboard
- Overview statistics
- Recent incidents
- Quick navigation
- Safety tips

### Interactive Map
- Geographic visualization of incidents
- Filtering by type, industry, location, date
- Incident details on click
- Color-coded markers (red=fatalities, orange=injuries, yellow=other)

### Statistics
- Trend analysis over time
- Geographic distribution
- Industry breakdowns
- Financial impact analysis

### Data Management
- OSHA data integration
- Real-time updates
- Comprehensive filtering
- Export capabilities

## 🔧 Configuration

### Environment Variables

#### Backend (env.example)
```bash
DATABASE_URL=sqlite:///./workplace_safety.db
OSHA_API_KEY=your_osha_api_key
MAPBOX_ACCESS_TOKEN=your_mapbox_token
HOST=0.0.0.0
PORT=8000
```

#### Frontend (env.example)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token
```

## 📁 Project Structure

```
WorkerBooBoo/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── database.py         # Database models
│   ├── models.py           # Pydantic models
│   ├── routers/            # API endpoints
│   ├── data_processor.py   # OSHA data processing
│   ├── seed_data.py        # Database seeding
│   ├── tests/              # Backend test suite
│   ├── pytest.ini          # pytest configuration
│   └── run_tests.py        # Test runner script
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── __tests__/      # Frontend test suite
│   │   └── App.tsx         # Main app
│   ├── package.json        # Dependencies
│   ├── vite.config.ts      # Vite configuration
│   └── tailwind.config.js  # Styling
├── start_all.sh            # macOS startup script
├── start_backend.sh        # Backend startup script
├── start_frontend.sh       # Frontend startup script
├── TESTING.md              # Comprehensive testing guide
└── README.md               # This file
```

## 🧪 Testing

The application includes a comprehensive testing framework to ensure code quality:

### Backend Testing
```bash
cd backend
python3 run_tests.py all         # All tests with coverage
python3 run_tests.py quick       # Fast test run
python3 run_tests.py maps        # Maps tests only
python3 run_tests.py stats       # Statistics tests only
python3 run_tests.py incidents   # Incidents tests only
```

### Frontend Testing
```bash
cd frontend
npm run test:run                 # Run all tests once
npm run test                     # Watch mode
npm run test:ui                  # Interactive UI
npm run test:coverage            # With coverage report
```

For detailed testing information, see [TESTING.md](../TESTING.md)

## 🚨 Troubleshooting

### Common Issues

#### Backend won't start
- Check Python version: `python3 --version`
- Install dependencies: `pip3 install -r requirements.txt`
- Check port availability: `lsof -i :8000`

#### Frontend won't start
- Check Node.js version: `node --version`
- Install dependencies: `npm install`
- Check port availability: `lsof -i :5173`

#### Map not loading
- Verify Mapbox token is set correctly
- Check browser console for errors
- Ensure backend is running and accessible

#### Database errors
- Run `python3 seed_data.py` to recreate sample data
- Check file permissions for SQLite database
- Verify Python dependencies are installed

#### Permission denied errors
- Make scripts executable: `chmod +x *.sh`
- Check file permissions: `ls -la *.sh`

### Error Messages

| Error | Solution |
|-------|----------|
| "Module not found" | Run `pip3 install -r requirements.txt` |
| "Port already in use" | Kill process using the port or change port in config |
| "Database locked" | Close any other applications using the database |
| "Mapbox token invalid" | Update token in MapView.tsx |
| "Permission denied" | Run `chmod +x *.sh` |

## 🔒 Security Notes

- This is a prototype application
- Sample data is fictional and for demonstration only
- In production, implement proper authentication and authorization
- Secure API endpoints and validate all inputs
- Use HTTPS in production environments

## 📈 Next Steps

### For Development
1. Implement real OSHA API integration
2. Add user authentication and roles
3. Create incident reporting forms
4. Add real-time notifications
5. Implement data export functionality

### For Production
1. Deploy to cloud platform (AWS, Azure, GCP)
2. Set up PostgreSQL database
3. Configure proper logging and monitoring
4. Implement rate limiting and security headers
5. Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- **Documentation**: Check this README and API docs
- **Issues**: Report bugs and feature requests
- **OSHA Resources**: [www.osha.gov](https://www.osha.gov)

## 📄 License

This project is for educational and demonstration purposes. Please ensure compliance with OSHA data usage policies and applicable regulations.

---

**Remember**: Workplace safety is everyone's responsibility. This tool helps raise awareness and improve safety practices through data-driven insights.

## 🍎 macOS Specific Tips

- **Terminal**: Use Terminal.app or iTerm2 for better experience
- **Homebrew**: Install development tools easily with `brew install`
- **Python**: Use `python3` command (not `python`)
- **Ports**: Use `lsof -i :PORT` to check port usage
- **Permissions**: Scripts need `chmod +x` to be executable
- **Browser**: `open` command opens URLs in default browser
