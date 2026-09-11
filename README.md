# AI-Enhanced Sophisticated Phishing Detection System Using Multi-Modal Machine Learning and Explainable AI

## Overview
A production-grade full-stack cybersecurity application designed to detect sophisticated phishing attempts across SMS, Emails, and URLs/Domains. 

### Architecture Stack
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI (Python 3.10+) + Uvicorn
- **Database**: MongoDB (via Motor async driver & PyMongo)
- **Machine Learning**: Scikit-Learn, XGBoost, PyTorch, Transformers (DistilBERT), SHAP, LIME
- **Containerization**: Docker & Docker Compose

## Repository Structure
```
pishing/
├── backend/            # FastAPI application & MongoDB database management
├── frontend/           # React TypeScript UI with Vite & Tailwind CSS
├── ml/                 # Data preprocessing, feature engineering, models & reports
│   ├── datasets/       # SMS, Email, and URL public datasets
│   ├── preprocessing/  # Data cleaning & pipeline transformations
│   ├── features/       # Feature extraction algorithms (URL, Domain, NLP)
│   ├── training/       # Model training & validation pipelines
│   ├── evaluation/     # Metric computation & visualizations
│   ├── explainability/ # SHAP/LIME XAI logic
│   └── saved_models/   # Serialized model weights & vectorizers
├── tests/              # Real-world test samples, unit, and integration tests
├── reports/            # Generated metrics, confusion matrices & research reports
└── docker-compose.yml  # Multi-container service orchestrator
```

## Setup & Running

### Option 1: Local Development
1. **Backend**:
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Option 2: Docker Compose
```bash
docker-compose up --build
```
