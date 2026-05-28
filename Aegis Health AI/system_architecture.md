# Aegis Health System Architecture & Data Flow

![Aegis Health System Architecture & Data Flow Diagram](system_architecture.png)

Below is the complete system architecture and clinical data flow map of the Aegis Health platform, visualizing how requests originate in the React client, route through the FastAPI API gateway, integrate with local datasets and machine learning caches, and utilize Google Gemini multi-modal endpoints for diagnostics and conversation.

---

## 📊 System Flowchart

```mermaid
flowchart TD
    %% Styling and colors
    classDef client fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef gateway fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef service fill:#faf5ff,stroke:#7e22ce,stroke-width:2px,color:#581c87;
    classDef storage fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    classDef external fill:#fdf2f8,stroke:#db2777,stroke-width:2px,color:#831843;

    %% Nodes
    subgraph Frontend ["Frontend Client (React.js SPA)"]
        Chat["Aegis Health AI Chat (Chat.jsx)"]:::client
        Predictor["Symptom Checker (SymptomChecker.jsx)"]:::client
        MRI["MRI Scan Analyzer (MRIAnalyzer.jsx)"]:::client
    end

    subgraph Backend ["Backend Gateway (FastAPI API)"]
        Router["API Gateway / Routers"]:::gateway
        
        subgraph Core ["Core Execution Layer"]
            RAG["RAG Diagnostic Agent (rag.py)"]:::service
            SymptomML["ML Classifier Engine (disease_pred.py)"]:::service
            MRIVision["Multi-Modal Scan Service (mri_analysis.py)"]:::service
        end
    end

    subgraph Data ["Data & Storage Layer"]
        UserDB["Local JSON DB (users_db.json)"]:::storage
        CSVs["Clinical Datasets (CSVs)"]:::storage
        VectorDB["In-Memory Vector DB"]:::storage
    end

    subgraph External ["External Services"]
        GeminiAPI["Google Gemini 2.5 Flash API"]:::external
    end

    %% Connections
    Chat -->|1. GET /api/chat/stream| Router
    Predictor -->|2. POST /api/predict| Router
    MRI -->|3. POST /api/mri/analyze| Router

    Router -->|Authenticate & Log| UserDB
    
    RAG -->|Query Embeddings| VectorDB
    VectorDB -->|Pre-seeded at startup| CSVs
    
    SymptomML -->|Predict & Join| CSVs
    
    RAG -->|4. Dynamic Follow-up/Prompt| GeminiAPI
    MRIVision -->|5. Image Analysis Payload| GeminiAPI

    GeminiAPI -->|6. Token Stream| RAG
    GeminiAPI -->|7. Radiological Report| MRIVision

    RAG -->|8. Final Doctor-like Stream| Chat
    SymptomML -->|9. Disease Diagnosis & Diet| Predictor
    MRIVision -->|10. Radiological Metrics| MRI
```

---

## ⚙️ Architectural Data Flow Breakdown

### 1. Conversational Chat Pathway (RAG)
1. **User Query Input**: The user speaks or types into the Aegis Health AI input on `Chat.jsx`. The message is transmitted via HTTP stream GET request to `/api/chat/stream`.
2. **State & Symptom Extraction**: `rag.py` intercepts the query, parses symptoms using custom alias mapping, and normalizes inputs against the database.
3. **Weak Symptom Follow-Up**: If exactly one symptom is detected, the engine finds related symptoms from the clinical CSVs and streams follow-up choices back to `Chat.jsx`.
4. **Gemini 2.5 flash synthesis**: If multiple symptoms are collected, `rag.py` executes predictions, retrieves precautions and diets from the local clinical database, and formats a compassionate clinical summary via Google Gemini `gemini-2.5-flash` to stream back to the UI.

### 2. Predictive Classification Pathway
1. **Grid Selection**: The patient selects multiple symptom chips in `SymptomChecker.jsx` and clicks **Predict Disease**.
2. **ML Classification**: The backend POST endpoint `/api/predict` passes the vectorized array to the RandomForest Classifier (with Jaccard fallback).
3. **Database Join**: Aegis joins the predicted disease with descriptions, medications, precautions, and dietary recommendations from the CSV datasets.
4. **Structured Results**: Returns structured JSON containing specific diagnosis and health guidelines to map directly onto visual charts and reminders.

### 3. Radiological Scan Pathway
1. **Scan Upload**: The user drops a Brain MRI JPEG/PNG into `MRIAnalyzer.jsx`.
2. **Normalization & Payload**: The image is validated, resized, and encoded.
3. **Multi-Modal Assessment**: `mri_analysis.py` transmits the image directly to Gemini API endpoints.
4. **Diagnostic Metrics**: The API returns anatomical observations, confidence scores, and specialist recommendations, rendering beautiful progress meters and radiology records.
