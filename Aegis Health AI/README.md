# Aegis Health — Full-Stack AI-Powered Conversational Healthcare Platform

Aegis Health is a full-stack, state-of-the-art clinical healthcare assistant designed to empower patients with intelligent health insights. It integrates **Machine Learning classification models** for symptom-based disease diagnostics, a **Conversational Multi-Turn RAG Assistant** utilizing Google Gemini `gemini-2.5-flash` for doctor-like health coaching, and **Multi-Modal AI Vision** for contrast-enhanced Brain MRI radiological scan assessments.

Built with premium clinical aesthetics, Aegis Health implements a responsive glassmorphism dark/light visual design system, animated biological metric cards, native voice-to-text dictation, and audio speech synthesis readouts.

---

## 🏗️ System Architecture & Data Flow

```
   ┌────────────────────────────────────────────────────────┐
   │                     USER (Browser)                     │
   │   - React.js SPA (Vite) + Tailwind CSS + Lucide Icons   │
   │   - Web Speech API (Native Voice Dictation & TTS)      │
   └───────────────────────────┬────────────────────────────┘
                               │ HTTP REST / streaming API
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                  API GATEWAY / FastAPI                 │
   │   - JWT Bearer Authentication & Password Cryptography   │
   │   - CORS Control & Asynchronous Streaming Responses     │
   └─────┬─────────────────────┬──────────────────────┬─────┘
         │                     │                      │
         ▼ (Predict Path)      ▼ (RAG Chat Path)      ▼ (Scan Vision Path)
   ┌───────────┐         ┌───────────┐          ┌───────────┐
   │  Symptom  │         │  Convers  │          │    MRI    │
   │  Checker  │         │  RAG Chat │          │  Vision   │
   │ (Sklearn) │         │ (Gemini)  │          │ (Gemini)  │
   └─────┬─────┘         └─────┬─────┘          └─────┬─────┘
         │                     │                      │
         ▼                     ▼                      ▼
   ┌───────────┐         ┌───────────┐          ┌───────────┐
   │ Diagnostic│         │ Clinical  │          │   Local   │
   │ Datasets  │         │ Vector DB │          │  Keras/   │
   │  (CSVs)   │         │ (In-Mem)  │          │ PIL Image │
   └───────────┘         └───────────┘          └───────────┘
```

### Key Workflow Pillars
1. **Symptom Checker & Predictor**: The user enters or selects symptoms in a card-based chip-grid. The frontend posts the array to `/api/predict`. The backend processes this list through a trained Scikit-learn `RandomForestClassifier` (with Jaccard similarity fallback) mapping against 41 conditions. Standard medical precautions, diets, and medications are retrieved from clinical CSV databases and returned.
2. **Aegis Health AI (Conversational Chatbot)**: A multi-turn dialogue companion. It implements natural language symptom extraction, alias matching, and interactive follow-up collection. If a single symptom is sent, Aegis computes the most common associated additional symptoms from the database and prompts the user with bulleted options. A high-confidence match triggers Gemini `gemini-2.5-flash` to synthesize verified diagnostic facts into a warm, supportive conversation, while keeping session history limits.
3. **Radiological Brain MRI Scanner**: The patient uploads a brain scan JPEG/PNG. The system evaluates the image, resizing and normalizing it, and passes it directly to Gemini's multi-modal vision API to obtain structured observations, confidence margins, and recommended radiology assessments.

---

## 📂 Operational File Map

```
/aegis-health-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI server gateway, CORS, and endpoint routing
│   │   ├── config.py               # Absolute path settings loader & environment configurations
│   │   ├── users_db.json           # Secure local JSON transactional user database
│   │   ├── auth/                   # Identity & Session Security
│   │   │   ├── router.py           # Register, Login, and profile endpoints
│   │   │   └── security.py         # JWT tokens & Cryptographic password hashing
│   │   ├── core/                   # Artificial Intelligence Engines
│   │   │   ├── llm.py              # Google Gemini Generative Model adapters
│   │   │   ├── rag.py              # Conversational state manager, symptom extraction & dialog flows
│   │   │   └── vector_db.py        # In-memory medical guidelines Vector DB seeded from CSVs
│   │   ├── models/                 # Pydantic validation schemas
│   │   │   ├── auth.py             # User registration and token schemas
│   │   │   └── disease.py          # Symptoms lists and prediction schemas
│   │   └── services/               # Diagnostic engines
│   │       ├── disease_pred.py     # Random Forest Classifier & Jaccard join databases
│   │       └── mri_analysis.py     # Radiological contrast image analyzers
│   ├── data/                       # Structured Clinical Reference Library
│   │   ├── description.csv         # Clinical summaries of diseases
│   │   ├── diets.csv               # Dietetic guidelines
│   │   ├── medications.csv         # Standard chemical compound medications
│   │   ├── precautions_df.csv      # Step-by-step precautions
│   │   ├── workout_df.csv          # Workout recommendations
│   │   ├── symptoms_df.csv         # Disease symptom matrix rows
│   │   └── Training.csv            # ML training dataset
│   ├── requirements.txt            # Python platform modules
│   └── .env                        # Local API secrets and configuration keys
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Global dashboard controls
│   │   │   └── Sidebar.jsx         # Sidebar dashboard navigations
│   │   ├── pages/                  # Responsive glassmorphism panels
│   │   │   ├── Login.jsx           # Clean unified clinical authentication card
│   │   │   ├── Dashboard.jsx       # Grid metrics, sleep, cardiac metrics and medicine logs
│   │   │   ├── SymptomChecker.jsx  # Chip-based multi-symptom disease diagnostics
│   │   │   ├── Chat.jsx            # Aegis Health AI chatbot client (voice STT + audio synthesis)
│   │   │   └── MRIAnalyzer.jsx     # Brain MRI Scan multi-modal uploader
│   │   ├── context/                # Global state providers
│   │   │   ├── AuthContext.jsx     # Active login and Axios credential intercepts
│   │   │   └── ThemeContext.jsx    # Light / Dark HSL variables manager
│   │   ├── App.jsx                 # SPA router and protected route guards
│   │   ├── index.css               # keyframe animations, styling variables, and gradients
│   │   └── main.jsx                # SPA renderer mount
│   └── package.json                # Frontend client dependencies
│
├── run.bat                         # Double-click auto-runner batch script
└── .gitignore                      # Clean Git tracking hygiene filters
```

---

## 🛟 Zero-Setup Local Database Framework

To ensure that Aegis Health compiles and runs immediately upon checking out the repository, the architecture uses a zero-setup local framework:
1. **JSON User Store (`app/users_db.json`)**: No external SQL or NoSQL database servers are required. Credentials are saved locally to a transaction-safe JSON file with bcrypt password hashes.
2. **In-Memory Vector DB (`core/vector_db.py`)**: Pre-seeds all clinical guidance directly from the local CSV reference library inside `backend/data/` at startup.
3. **No Machine Learning installation barriers**: If `scikit-learn` or trained pickle models are missing, the diagnosis engine falls back to a custom similarity-matching algorithm, yielding accurate outcomes without compilation errors.

---

## 🛠️ Step-by-Step Installation Guide

### Prerequisites
* **Python**: 3.8 to 3.11 installed
* **Node.js**: 16.x or higher installed

---

### Step 1: Backend Configuration
1. Open a terminal and enter the backend directory:
   ```bash
   cd backend
   ```
2. Build a local virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   * **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
4. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
5. Setup your `.env` configuration file in `backend/.env` with your Gemini key:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   JWT_SECRET=super_secret_healthcare_key_12984710
   ```

---

### Step 2: Frontend Client Configuration
1. Open a second terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```

---

## ⚡ Double-Click Auto-Launcher (`run.bat`)

For developer convenience, we provide a Windows Batch script **[run.bat](file:///d:/Projects/Major%20Project/Aegis%20Health%20AI/run.bat)** in the root folder. 

Double-clicking `run.bat` automatically:
1. Detects and activates your Python virtual environment.
2. Spawns your **FastAPI Backend Web Server** on `http://127.0.0.1:8000`.
3. Spawns your **React Vite Frontend Client** on `http://localhost:5173`.
4. Opens the platform instantly in your browser.

---

## 🔒 Security & Git Hygiene
Aegis Health strictly enforces standard repository hygiene via [.gitignore](file:///d:/Projects/Major%20Project/Aegis%20Health%20AI/.gitignore):
- Local environment files (`.env`, `*.env`) are permanently excluded from tracking.
- Heavy python bytecode (`__pycache__/`, `*.pyc`), virtual environments (`venv/`), and frontend node directories (`node_modules/`) are ignored.
- ML training checkpoints (`*.pkl`, `*.h5`) are excluded to keep the repository lightweight.

---

## 📝 Clinical Disclaimer
*Aegis Health provides automated clinical recommendations for educational and informational purposes only. The platform does not guarantee clinical diagnoses, and users experiencing severe, persistent, or emergency symptoms must consult a licensed medical professional or visit their nearest clinic.*

Developed by **Shobhit Yadav**.
