# Scout App - Complete Setup Guide

This document provides a step-by-step guide for colleagues to clone and run the Scout App locally.

## 🎯 What This App Does

- **Document Scanning**: iOS app scans documents using the device camera
- **PDF Creation**: Converts scanned images to PDF format
- **AI Processing**: Backend processes PDFs with intelligent naming and categorization
- **Local Storage**: All files stored locally (no cloud dependency required)
- **Optional Cloud Sync**: Google Drive integration available for enhanced features

## 🚀 Quick Start (5 Minutes)

### 1. Clone the Repository
```bash
git clone [your-repo-url]
cd scout-app
```

### 2. Run Automated Setup
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure for Mobile Device
```bash
./configure_network.sh
```

### 4. Start Backend Server
```bash
./start_backend.sh
```

### 5. Build iOS App
1. Open `frontend/ScoutApp.xcodeproj` in Xcode
2. Build and run on your device/simulator

## 📋 Prerequisites

- **macOS** 12.0+ with Xcode 14.0+
- **Python 3.8+** installed
- **iOS device or simulator** with iOS 15.0+
- **Same WiFi network** for device and Mac

## 🛠️ Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.sh` | Complete automated setup | `./setup.sh` |
| `configure_network.sh` | Configure IP for mobile testing | `./configure_network.sh` |
| `start_backend.sh` | Start backend server | `./start_backend.sh` |
| `start_dev.sh` | Complete dev environment | `./start_dev.sh` |

## 🌐 Network Configuration

### For iOS Simulator
- Backend: `http://localhost:8000`
- Works automatically after setup

### For Physical Device
1. Run `./configure_network.sh`
2. Ensure same WiFi network
3. Use IP shown by script (e.g., `http://192.168.1.100:8000`)

## 📱 How to Use

1. **Launch iOS app** on device/simulator
2. **Tap "Document Scanner"** to scan documents
3. **Take photos** or scan multiple pages
4. **Tap "Save as PDF"** to process
5. **Backend processes** the document with AI

## 🔧 Project Structure

```
scout-app/
├── setup.sh                   # 🚀 Main setup script
├── configure_network.sh       # 🌐 Network configuration
├── start_backend.sh           # ⚡ Backend startup
├── start_dev.sh              # 🛠️ Complete dev environment
├── .env.example              # ⚙️ Environment template
├── .gitignore                # 🚫 Git ignore rules
├── README.md                 # 📖 Detailed documentation
├── backend/                  # 🐍 Python FastAPI backend
│   ├── app.py               # Main application
│   ├── local_storage/       # 📁 Processed PDFs
│   └── scout_agents/        # 🤖 AI processing
└── frontend/ScoutApp/       # 📱 iOS SwiftUI app
    ├── ScannerView.swift    # Document scanning
    └── Network/APIService.swift # Backend communication
```

## 🚨 Troubleshooting

### Common Issues

**"Could not connect to server"**
- Run `./configure_network.sh`
- Check same WiFi network
- Verify backend is running

**"Virtual environment not found"**
- Run `./setup.sh` again
- Check Python 3 installation

**"Port 8000 in use"**
- Kill existing process: `lsof -ti:8000 | xargs kill`
- Or change port in scripts

**iOS build errors**
- Clean build folder (⌘+Shift+K)
- Check Xcode version compatibility

### Getting Help

1. Check console logs in Xcode
2. Check backend terminal output
3. Verify network connectivity:
   ```bash
   curl http://YOUR_IP:8000/health
   ```

## 🔐 Optional Configuration

### AI Processing (OpenAI)
```bash
# Edit .env file
OPENAI_API_KEY=your-api-key-here
```

### Google Drive Integration
```bash
# Edit .env file  
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Xcode 14.0+ installed
- [ ] Repository cloned
- [ ] `./setup.sh` completed successfully
- [ ] `./configure_network.sh` run (for mobile)
- [ ] Backend starts without errors
- [ ] iOS app builds in Xcode
- [ ] Document scanning works
- [ ] PDFs processed successfully

## 🎉 Success!

If you can scan a document and see it processed in the backend logs, you're all set! The app will:

1. ✅ Save PDF locally on iOS device
2. ✅ Send to backend for processing  
3. ✅ Save processed PDF with metadata locally
4. ✅ Return AI suggestions for naming/organization

## 📚 Next Steps

- Explore the full README.md for advanced features
- Configure AI processing with API keys
- Set up Google Drive integration (optional)
- Customize processing logic in `backend/scout_agents/`

---

**Need Help?** Check the detailed README.md or create an issue with your error logs.