# REstackAI — Fund Administration Platform

A full-stack fund administration dashboard for managing real-estate fund assets, leasing, and operations.

## Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Frontend | React 19, Vite, React Router DOM                |
| Backend  | Python 3, Flask, PyJWT, bcrypt                   |
| Database | MongoDB                                          |

## Project Structure

```
Claude_fund_admin/
├── api/                    # Python Flask backend
│   ├── config.py           # MongoDB & JWT configuration
│   ├── app.py              # Flask API (auth endpoints)
│   └── requirements.txt    # Python dependencies
├── ui/                     # React frontend
│   ├── src/
│   │   ├── components/     # Shared components (Sidebar, Topbar)
│   │   ├── pages/          # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Landing.jsx     # Command Center dashboard
│   │   │   ├── Leasing.jsx
│   │   │   ├── Assets.jsx
│   │   │   └── Settings.jsx
│   │   ├── data/           # JSON data files (no hardcoded values)
│   │   ├── App.jsx         # Route definitions
│   │   └── main.jsx        # Entry point
│   └── package.json
└── README.md
```

## Prerequisites

- **Node.js** >= 18
- **Python** >= 3.10
- **MongoDB** running on `localhost:27017`

## Getting Started

### 1. Backend (API)

```bash
cd api
pip install -r requirements.txt
python app.py
```

The API starts on **http://localhost:5000**.

### 2. Frontend (UI)

```bash
cd ui
npm install
npm run dev
```

The UI starts on **http://localhost:5173**.

## API Endpoints

| Method | Endpoint         | Description                  |
| ------ | ---------------- | ---------------------------- |
| POST   | `/api/register`  | Register a new user          |
| POST   | `/api/login`     | Login with email & password  |
| GET    | `/api/health`    | Check MongoDB connection     |

### Register

```json
POST /api/register
{
  "email": "user@example.com",
  "password": "secret123",
  "name": "John Doe"
}
```

### Login

```json
POST /api/login
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Both return a JWT token and user object on success.

## Configuration

Edit `api/config.py` to change:

- `MONGO_URI` — MongoDB connection string
- `MONGO_DB_NAME` — Database name (default: `fund_admin`)
- `JWT_SECRET_KEY` — Secret for signing tokens (change in production)
- `JWT_ACCESS_TOKEN_EXPIRES_HOURS` — Token expiry (default: 24h)
