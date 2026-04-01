# 🚀 MongoVault – Future Enhancements Roadmap

This document outlines planned improvements and advanced features for the MongoVault macOS application.

## 🎨 1. Dark macOS Theme - Done

### Objective

Provide a native macOS dark mode experience that matches system appearance.

### Planned Improvements

- Auto-detect macOS theme (Light / Dark)
- Manual theme toggle inside settings
- Modern styling using Qt stylesheet (QSS)
- Improved contrast for logs panel

### Implementation Approach

- Use QApplication.setStyle()
- Apply custom QSS stylesheet
- Detect macOS appearance via NSAppearance (optional advanced)

## ⚡ 2. Parallel Collections Slider - Done

### Objective

Allow users to optimize performance during backup and restore.

### Feature Details

- Add a slider (1–16 range)
- Display selected value dynamically
- Map value to: --numParallelCollections=<value>

### Benefits

- Faster backups for large databases
- Better performance tuning for Atlas clusters

## 📚 3. Collection Selection Checkboxes - Done

### Objective

Enable granular backup and restore control.

### Backup Mode

- Dynamically fetch collection names:

```bash
mongosh --eval "db.getCollectionNames()"
```

- Show collections in scrollable checkbox list
- Support:
  - Select All
  - Deselect All

### Restore Mode

- Allow **--nsInclude=db.collection**
- Allow **--nsExclude=db.collection**

### Benefits

- Restore specific collections only
- Avoid full database restore

## 📊 4. Progress Bar with Percentage - Done

### Objective

Show real-time operation progress.

### Implementation Options
**Option A – Estimate by File Size**

- Track archive size growth
- Calculate % based on expected size

**Option B – Parse mongodump Output**

- Extract progress lines
- Convert to percentage

### UI Elements

- QProgressBar
- Real-time status label
- Spinner during initialization

## 💾 5. Saved Connection Profiles

### Objective

Allow users to store frequently used MongoDB connections.

### Features

- Save:
  - Connection name
  - URI
  - Default database
  - Environment type

- Dropdown selector for saved profiles

### Storage Method

- JSON config file:

```bash
~/.mongovault/config.json
```

### Future Upgrade

- SQLite local profile storage

## 🔐 6. Secure Password Storage (macOS Keychain)

### Objective

Avoid storing sensitive credentials in plain text.

### Implementation

- Use Python keyring library
- Store credentials in macOS Keychain
- Retrieve securely when profile selected

### Benefits

- No plain-text passwords
- Enterprise-ready security

## 🌍 7. Environment Presets (Dev / UAT / Prod)

### Objective

Simplify switching between environments.

### Features

- Environment dropdown selector
- Pre-configured:
  - DEV
  - UAT
  - PROD

- Color indicator badge:
  - 🟢 DEV
  - 🟡 UAT
  - 🔴 PROD

### Safety Feature

- Confirmation popup before restoring to PROD

## 🗑 8. Retention Policy (Auto-Delete Old Backups)

### Objective

Prevent disk overflow.

### Options

- Keep last N backups (configurable)
- Keep backups newer than X days
- Scheduled cleanup on app start

## Example Policy

Keep last 7 backups per database
Delete anything older automatically

## 📦 9. Drag & Drop Restore

### Objective

Simplify restore workflow.

### Feature

- Drag .tar.gz file directly into app
- Auto-detect:
  - Database name
  - Timestamp
- Show confirmation dialog before restore

### Implementation

- Enable Qt drag events
- Validate file extension
- Auto-fill restore fields
