# Changelog

## [1.5.4](https://github.com/sknt2024/mongo_vault/compare/v1.5.3...v1.5.4) (2026-02-22)


### Bug Fixes

* Modify DMG upload to use release tag and overwrite ([1768549](https://github.com/sknt2024/mongo_vault/commit/176854963eab4b4dab489d279cf905758bf70b31))

## [1.5.3](https://github.com/sknt2024/mongo_vault/compare/v1.5.2...v1.5.3) (2026-02-22)


### Bug Fixes

* update mongodb tools install for CI ([e5e1075](https://github.com/sknt2024/mongo_vault/commit/e5e1075122464f507330bcaa5be91236ae8b885e))

## [1.5.2](https://github.com/sknt2024/mongo_vault/compare/v1.5.1...v1.5.2) (2026-02-22)


### Bug Fixes

* Modify DMG build workflow to use workflow_run ([9bc8d96](https://github.com/sknt2024/mongo_vault/commit/9bc8d963a0575c6bac405f90ce310ae475726e4f))

## [1.5.1](https://github.com/sknt2024/mongo_vault/compare/v1.5.0...v1.5.1) (2026-02-22)


### Bug Fixes

* Add config file parameter to release-please action ([6cdced9](https://github.com/sknt2024/mongo_vault/commit/6cdced997dcf280ee962f99ef2630e66353bfc00))

## [1.5.0](https://github.com/sknt2024/mongo_vault/compare/v1.4.0...v1.5.0) (2026-02-22)


### Features

* Implement collection selection UI, enabling include/exclude filtering for backup and restore operations, and add a new service for fetching MongoDB collections. ([de63b10](https://github.com/sknt2024/mongo_vault/commit/de63b10559de621c58862a906d32796c926bc03c))

## [1.4.0](https://github.com/sknt2024/mongo_vault/compare/v1.3.0...v1.4.0) (2026-02-22)


### Features

* Add GitHub Actions workflow to build macOS DMG ([13eebbe](https://github.com/sknt2024/mongo_vault/commit/13eebbe65fb93dc316b71118e0483f8177e7a4dc))

## [1.3.0](https://github.com/sknt2024/mongo_vault/compare/v1.2.0...v1.3.0) (2026-02-22)


### Features

* Configure release-please with minor/patch bumping and custom changelog sections, removing pull request header patterns. ([61bf322](https://github.com/sknt2024/mongo_vault/commit/61bf322bf6550d34435e292cf32c220f096c85ce))

## [1.2.0](https://github.com/sknt2024/mongo_vault/compare/v1.1.1...v1.2.0) (2026-02-22)


### Features

* Add version badge and documentation links to README. ([1bf5ed7](https://github.com/sknt2024/mongo_vault/commit/1bf5ed7b09d760dfdd637ef2ba854e99fb599da9))
* configure release-please for simple releases with custom pull request title, header, and footer. ([d67bd2c](https://github.com/sknt2024/mongo_vault/commit/d67bd2cc8daac4cd77623c2fa6fb9cde3aa8c735))
* Modify release workflow and add README update step ([8225977](https://github.com/sknt2024/mongo_vault/commit/8225977f7f1394ace66a550b4dbcacdcc566e884))
* Set up initial project structure for MongoVault, a PyQt6 MongoDB backup and restore GUI. ([77f6d79](https://github.com/sknt2024/mongo_vault/commit/77f6d79b19683974451629067641179c5ba17b48))


### Bug Fixes

* trigger automated release ([f8fdbe1](https://github.com/sknt2024/mongo_vault/commit/f8fdbe1e0e9c19fd68c5e126070616e4106cc12f))

## [1.1.1](https://github.com/sknt2024/mongo_vault/compare/v1.1.0...v1.1.1) (2026-02-22)


### Bug Fixes

* trigger automated release ([f8fdbe1](https://github.com/sknt2024/mongo_vault/commit/f8fdbe1e0e9c19fd68c5e126070616e4106cc12f))

## 📦 Changelog

All notable changes to **MongoVault** will be documented in this file.

The format follows:
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)

---

## [1.1.0] - 2026-02-22

## ✨ Added

### 🎨 UI & Theme System
- Dark macOS theme support
- Light theme support
- Automatic system theme detection
- Manual theme toggle button
- QSS-based modern UI styling
- Improved contrast for logs panel
- Centralized Theme Manager

### ⚙️ Backup Enhancements
- Exclude collections input (comma-separated)
- Parallel collections slider (1–16)
- Background threaded execution (no UI freeze)
- Automatic compression to `.tar.gz`
- Structured backup result reporting

### 🔄 Restore Enhancements
- Replace (`--drop`) restore mode
- Append (safe) restore mode
- Smart duplicate key detection (E11000 parsing)
- Index conflict detection (IndexOptionsConflict)
- Structured restore result handling
- Restore log file generation

### 🏗 Architecture Improvements
- Modular service-layer design
- `command_runner` for centralized command execution
- Structured return objects for backup & restore
- Clean separation of:
  - UI layer
  - Service layer
  - Worker thread layer
  - Utility layer
- Dedicated theme management module
- Centralized constants & version management

---

## 🔧 Improved

- Refactored backup & restore logic
- Improved error handling and reporting
- Removed legacy command execution logic
- Cleaner threading model
- Enhanced log output formatting
- Codebase restructured for scalability
- Improved macOS packaging readiness

---

## 🛠 Fixed

- Import errors after service-layer refactor
- Worker-thread command mismatch
- Undefined timestamp and legacy compression calls
- Inconsistent restore execution paths
- Blocking UI during backup/restore execution

---

## [1.0.0] - 2026-02-20

## 🚀 Initial Release

### ✨ Core Features
- MongoDB Backup (mongodump)
- MongoDB Restore (mongorestore)
- Compressed `.tar.gz` backup generation
- Replace (`--drop`) restore mode
- Append restore mode
- Parallel collections support
- Live logs panel
- PyQt6 macOS desktop GUI
- Basic modular project structure
- macOS `.app` packaging support via PyInstaller

### 🏗 Architecture
- Basic modular separation
- Worker thread execution
- Service-based command building
- Clean UI layout with tabs (Backup / Restore)

---

## [Unreleased]

## 🎯 Planned Features

### 📚 Collection Management
- Dynamic collection selection checkboxes
- Auto-fetch collection names from MongoDB
- Include / Exclude toggle mode
- Select All / Deselect All

### 📊 Progress & Monitoring
- Real-time progress percentage parsing
- Progress bar with estimated completion
- Restore preview mode
- Dry-run restore option

### 🔐 Security Enhancements
- Secure password storage via macOS Keychain
- Encrypted profile storage
- Environment safety warnings for production restores

### 💾 Connection Profiles
- Saved connection profiles
- Environment presets (Dev / UAT / Prod)
- Environment badge indicator (color-coded)
- Confirmation dialog for PROD restore

### 🗑 Retention Management
- Auto-delete old backups
- Configurable retention policy
- Scheduled cleanup on startup

### 📦 Advanced Features
- Drag & Drop restore support
- S3 backup upload integration
- Scheduled backups (Cron integration)
- Backup encryption (AES-256)
- Slack / Email notifications
- CI/CD macOS auto-build workflow
- DMG installer automation

---

## 🏷 Versioning Strategy

MongoVault follows **Semantic Versioning**:


| Type  | Meaning |
|--------|---------|
| MAJOR | Breaking changes |
| MINOR | New features |
| PATCH | Bug fixes |

---

## 📌 Release Guidelines

- UI-only enhancements → MINOR
- New features → MINOR
- Breaking architecture changes → MAJOR
- Bug fixes → PATCH

---

## 🛡 About MongoVault

MongoVault is a secure, modern macOS desktop application designed to provide:

- Reliable MongoDB backup
- Safe restore workflows
- Smart duplicate detection
- Developer-friendly experience
- Production-ready architecture

Built with:
- Python
- PyQt6
- MongoDB Database Tools

---

## 🚀 Current Stable Version


MongoVault has now evolved into a modular, theme-enabled, smart-restore macOS desktop application ready for production expansion.
