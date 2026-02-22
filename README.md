# 🛡 MongoVault

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)]()

📘 **Documentation**
- [Changelog](CHANGELOG.md)
- [License](LICENSE)


**MongoVault** is a professional macOS desktop application for MongoDB Backup & Restore built with PyQt6.

It provides a modern GUI for running `mongodump` and `mongorestore` with enterprise-grade features like:

- 🔄 Backup & Restore (compressed `.tar.gz`)
- ⚡ Parallel collections support
- 📊 Live logs panel
- 🗑 Replace or Append restore modes
- 📂 File & folder picker
- 🖥 Native macOS desktop app

---

## 🚀 Features

- Modern PyQt6 GUI
- Non-blocking execution (QThread)
- Restore mode selector (Safe / Replace)
- Log streaming in real time
- macOS-ready `.app` packaging

---

## 🖥 Requirements

- macOS (Intel or Apple Silicon)
- Python 3.10+
- MongoDB Database Tools

Install tools:

```bash
brew install mongodb-database-tools
```

## 📦 Installation

```bash
git clone https://github.com/your-org/mongovault.git
cd mongovault

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

```

Run:

```bash
python3 run.py
```

## 📦 Build macOS App

```bash
pip install pyinstaller
pyinstaller --windowed --onefile run.py
```

The app will be in the `dist` folder.

**dist/MongoVault.app**

## 🔐 Security

Future versions will include:

- macOS Keychain integration
- Secure profile storage
- Environment safety guards
  
