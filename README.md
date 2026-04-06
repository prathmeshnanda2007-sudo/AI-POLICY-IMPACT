# AI Public Policy Impact Simulator

AI-powered policy simulation platform using Machine Learning to predict economic and environmental impacts of public policy changes.

## Architecture

```
Frontend (React + Tailwind + Recharts)
      ↓
API Calls (Axios)
      ↓
FastAPI Backend (Python)
      ↓
ML Model (Best of RandomForest / LinearReg / GradientBoosting)
      ↓
SQLite Database (Scenarios, History, Training Logs)
      ↓
Charts + Dashboard (Real-time Results)
```

## Quick Start

### 1. Install Frontend Dependencies
```bash
cd AI-POLICY-IMPACT
npm install
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Train ML Model (auto-trains on first backend start)
```bash
cd backend
python -c "from models.ml_model import train_and_select_best; train_and_select_best()"
```

### 4. Start Backend (port 8000)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend (port 5173)
```bash
npm run dev
```

Open **http://localhost:5173** in your browser.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS 3, Recharts, Lucide Icons, Framer Motion |
| Backend | FastAPI, Python 3.11+, Pydantic |
| ML | scikit-learn (RandomForest, GradientBoosting, LinearRegression) |
| Database | SQLite (via sqlite3) |
| Bundler | Vite 6 |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Run policy simulation |
| POST | `/compare` | Compare multiple scenarios |
| POST | `/train` | Retrain ML model |
| GET | `/scenarios` | List saved scenarios |
| POST | `/scenarios` | Save a scenario |
| DELETE | `/scenarios/{id}` | Delete a scenario |
| GET | `/history` | Get simulation history |
| GET | `/model/info` | Get model metadata |
| GET | `/model/feature-importance` | Get feature importance |
| POST | `/sensitivity` | Run sensitivity analysis |
| POST | `/recommend` | Get AI policy recommendation |

## ML Model Details

- **Training data**: 5,000 synthetic policy samples
- **Features**: tax_rate, fuel_price, subsidy, public_spending, interest_rate, environmental_regulation
- **Outputs**: GDP growth, inflation, employment rate, environment score, public satisfaction
- **Best model**: Selected automatically by lowest RMSE
- **R² Score**: ~0.95 (95% variance explained)

## Deployment

### Frontend → Vercel
```bash
npm run build
# Deploy `dist/` to Vercel
```

### Backend → Railway/Render
```bash
# Set environment variables:
# PORT=8000
# Deploy backend/ directory
```

Set `VITE_API_URL` to your deployed backend URL.
