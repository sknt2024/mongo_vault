# 🛡 MongoVault

<p align="center">
  <img src="mongo_vault_icon.png" width="180" alt="MongoVault Icon">
</p>

<p align="center">
  <b>Professional macOS MongoDB Backup & Restore Tool</b>
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/sknt2024/mongo_vault?style=flat-square" />
  <img src="https://github.com/sknt2024/mongo_vault/actions/workflows/release-please.yml/badge.svg" />
  <img src="https://img.shields.io/github/downloads/sknt2024/mongo_vault/total?style=flat-square" />
  <img src="https://img.shields.io/github/license/sknt2024/mongo_vault?style=flat-square" />
  <img src="https://img.shields.io/badge/platform-macOS-black?style=flat-square" />
</p>

---

📘 **Documentation**
- [Changelog](CHANGELOG.md)
- [License](LICENSE)

---

## 🧠 Overview

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
- Custom macOS app icon & DMG installer

---

## 🖥 Requirements

- macOS (Intel or Apple Silicon)
- Python 3.10+
- MongoDB Database Tools

Install tools:

```bash
brew tap mongodb/brew
brew install mongodb-database-tools
```

## 📦 Installation (Development)

```bash
git clone https://github.com/sknt2024/mongo_vault.git
cd mongo_vault

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
pyinstaller --windowed --noconfirm \
  --name MongoVault \
  --icon assets/icon.icns \
  --add-data "version.txt:." \
  run.py
```

The app will be in the `dist` folder.

**dist/MongoVault.app**

## 💿 Download

Download the latest DMG from:

👉 Releases Page
https://github.com/sknt2024/mongo_vault/releases