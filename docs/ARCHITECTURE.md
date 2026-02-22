# MongoVault Architecture

┌───────────────────────────────┐
│           UI Layer            │
│  (PyQt6 Tabs & Components)    │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│        Controller Layer       │
│   (Event Handlers & Routing)  │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│        Service Layer          │
│  - Backup Service             │
│  - Restore Service            │
│  - Profile Service            │
│  - Retention Service          │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│        Worker Threads         │
│  (QThread - Non Blocking)     │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│   MongoDB CLI Tools           │
│ mongodump / mongorestore      │
└───────────────────────────────┘