# Scout App - AI-Powered Document Scanner

A mobile iOS app that scans documents, converts them to PDF, and processes them using AI-powered backend services. The AI agents automatically rename files and organize them into appropriate folders based on content analysis.

## 🚀 Quick Start (5 Minutes)

### 1. Clone & Setup
```bash
git clone [your-repo-url]
cd scout-app
chmod +x setup.sh
./setup.sh
```

### 2. Start Backend
```bash
./start.sh
```

### 3. Build iOS App
1. Open `frontend/ScoutApp.xcodeproj` in Xcode
2. Build and run on your device/simulator (⌘+R)

That's it! The app will work locally without any additional configuration.

## 📋 Prerequisites

- **macOS** 12.0+ with Xcode 14.0+
- **Python 3.8+** installed
- **iOS device or simulator** with iOS 15.0+
- **Same WiFi network** for device and Mac (for physical device testing)

## ✨ How It Works

1. **📸 Scan Documents**: Use the iOS app to scan documents with your camera
2. **📄 Convert to PDF**: Documents are automatically converted to PDF format
3. **🤖 AI Processing**: Backend AI agents analyze the content and:
   - **📝 Rename**: Generate meaningful filenames based on document content
   - **📁 Organize**: Create appropriate folders and move files automatically
   - **💾 Store**: Save everything locally with metadata tracking

## 🏗️ Architecture

- **Frontend**: iOS app (SwiftUI + VisionKit for scanning)
- **Backend**: Python FastAPI server with AI agent system
- **Storage**: Local file system (Google Drive optional)
- **AI**: OpenAI GPT-4o-mini for content analysis and organization
- **Network**: Local network communication between iOS and backend

## 📁 Project Structure

```
scout-app/
├── setup.sh                   # 🚀 Single setup script
├── start.sh                   # ⚡ Smart backend startup
├── README.md                  # 📖 This file
├── requirements.txt           # 📦 Python dependencies
├── backend/                   # 🐍 Python FastAPI backend
│   ├── app.py                # Main API application
│   ├── config.py             # Configuration management
│   ├── scout_agents/         # 🤖 AI processing agents
│   │   ├── reader_agent.py   # Content analysis
│   │   ├── rename_agent.py   # File renaming
│   │   ├── folder_agent.py   # Folder organization
│   │   └── file_mover_agent.py # File operations
│   ├── tools/                # 🛠️ Agent tools
│   └── local_storage/        # 📁 Processed documents
└── frontend/ScoutApp/        # 📱 iOS SwiftUI app
    ├── ScannerView.swift     # Document scanning
    ├── Network/APIService.swift # Backend communication
    └── Views/                # App screens
```

## 🔧 Configuration

### Basic Usage (Local Only)
No configuration needed! The app works out of the box with local storage.

### Advanced Features (Optional)

#### AI Processing
For enhanced AI features, add your OpenAI API key:
```bash
# Edit .env file
OPENAI_API_KEY=your_openai_api_key_here
```

#### Google Drive Integration - Work in progress
For cloud sync capabilities:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Drive API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to `backend/` directory
5. Add redirect URIs to Google Console:
   - `http://localhost:8000/auth/google/callback`
   - `http://YOUR_LOCAL_IP:8000/auth/google/callback`

## 🌐 Network Configuration

### iOS Simulator
- Automatically uses `localhost:8000`
- No additional setup required

### Physical iOS Device
The `start.sh` script automatically detects when you need network configuration:
- Detects your local IP address
- Updates iOS app configuration
- Shows you the URL to use

## 📱 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed backend status
- `POST /process-local-pdf` - Process PDFs locally (recommended)

### Optional Endpoints (if configured)
- `POST /upload-pdf` - Process PDFs with Google Drive sync
- `GET /auth/google` - Google OAuth flow
- `GET /config` - Configuration information

## 🚨 Troubleshooting

### Common Issues

**"Could not connect to server"**
- Run `./start.sh` again - it will reconfigure network settings
- Ensure iOS device and Mac are on the same WiFi network
- Check that backend is running (look for "Server running" message)

**"Virtual environment not found"**
- Run `./setup.sh` to create the virtual environment
- Check that Python 3.8+ is installed: `python3 --version`

**"Port 8000 in use"**
- The start script will automatically handle this
- Or manually kill the process: `lsof -ti:8000 | xargs kill`

**iOS build errors**
- Clean build folder in Xcode (⌘+Shift+K)
- Ensure Xcode 14.0+ is installed
- Check iOS deployment target is set to 15.0+

**PDF processing fails**
- Check backend logs in terminal
- Verify OpenAI API key if using AI features
- Ensure sufficient disk space in `backend/local_storage/`

### Debug Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check network configuration
curl http://YOUR_IP:8000/config

# View processed files
ls -la backend/local_storage/processed_pdfs/

# Check backend logs
./start.sh  # Logs appear in terminal
```

### Google OAuth Issues

**"redirect_uri_mismatch" error**
- Ensure Google Console has correct redirect URIs
- Check that backend IP matches the configured URIs
- Use the IP address shown by `./start.sh`

**Mobile device can't complete OAuth**
- Ensure firewall allows connections on port 8000
- Add your local IP redirect URI to Google Console
- Test backend accessibility: try `http://YOUR_IP:8000/health` in mobile browser

## 🔍 Testing the App

### Local Testing (No Google Drive)
1. Start backend: `./start.sh`
2. Open iOS app
3. Go to "API Test" tab
4. Click "Test Local PDF Processing"
5. Should see successful processing results

### Full Workflow Testing
1. Start backend: `./start.sh`
2. Open iOS app
3. Tap "Scanner" tab
4. Scan a document
5. Wait for processing to complete
6. Check `backend/local_storage/processed_pdfs/` for organized files

## 🛠️ Development

### Backend Development
```bash
cd backend
source ../venv/bin/activate
python app.py
```

### iOS Development
- Open `frontend/ScoutApp.xcodeproj` in Xcode
- Make changes to Swift files
- Build and run (⌘+R)

### Adding New AI Agents
1. Create new agent in `backend/scout_agents/`
2. Add tools in `backend/tools/`
3. Update orchestrator in `scout_orchestrator.py`
4. Test with local PDF processing

## 📊 File Processing Pipeline

1. **Document Scan** → iOS app captures images
2. **PDF Creation** → Images converted to PDF
3. **Upload** → PDF sent to backend via `/process-local-pdf`
4. **AI Analysis** → Agents analyze content:
   - **Reader Agent**: Extracts text and understands content
   - **Rename Agent**: Suggests meaningful filename
   - **Folder Agent**: Determines appropriate folder structure
   - **File Mover**: Organizes file in correct location
5. **Storage** → File saved with metadata in `local_storage/processed_pdfs/`
6. **Response** → Results returned to iOS app

## 🔐 Security & Privacy

- **Local First**: All processing happens locally by default
- **No Cloud Dependency**: App works completely offline
- **Optional Cloud Sync**: Google Drive integration is entirely optional
- **API Key Management**: Your OpenAI/Google keys stay on your machine
- **Network Security**: Backend only accessible on your local network

## 📝 Environment Variables

Create a `.env` file in the project root (setup.sh creates a template):

```bash
# Development settings
SCOUT_ENV=development
SCOUT_DEBUG=true
SCOUT_HOST=0.0.0.0
SCOUT_PORT=8000

# Optional: AI processing
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Google Drive integration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both simulator and physical device
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

