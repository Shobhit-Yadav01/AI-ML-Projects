import os
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import uvicorn

from backend.app.config import settings
from backend.app.auth.router import router as auth_router, get_current_user
from backend.app.models.disease import SymptomRequest, DiseaseDetailResponse
from backend.app.services.disease_pred import disease_pred_service
from backend.app.services.mri_analysis import mri_analysis_service
from backend.app.core.rag import generate_rag_response, session_memory
from backend.app.core.vector_db import vector_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="State of the art Production-Ready AI Healthcare Platform"
)

# Enable CORS for the frontend React application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in real production setup
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ingest / Preload Vector Database on startup
@app.on_event("startup")
async def startup_event():
    print("Pre-seeding clinical vector store...")
    vector_db.initialize_db()
    print("Pre-loading disease models...")
    disease_pred_service.load_resources()

# Mount routers
app.include_router(auth_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "version": "2.0.0"
    }

# ==========================================
# 1. Symptom & Disease Prediction Endpoints
# ==========================================

@app.get(f"{settings.API_V1_STR}/symptoms")
async def list_symptoms():
    """Returns the list of all recognizable symptoms for search-autocomplete."""
    if not disease_pred_service.is_loaded:
        disease_pred_service.load_resources()
    
    # Return all processed symptoms as a list
    symptoms = sorted(list(disease_pred_service.symptoms_processed.keys()))
    return {"symptoms": symptoms}

@app.post(f"{settings.API_V1_STR}/predict", response_model=DiseaseDetailResponse)
async def predict_disease(payload: SymptomRequest):
    """Predicts potential disease and returns precaution, medications, diet, and workouts."""
    if not payload.symptoms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symptoms list cannot be empty."
        )
    
    result = disease_pred_service.predict_disease(payload.symptoms)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
        
    return result

# ==========================================
# 2. RAG Streaming Chatbot Endpoints
# ==========================================

@app.get(f"{settings.API_V1_STR}/chat/stream")
async def stream_chat(message: str, session_id: str = "default"):
    """Streams RAG-based, context-aware chatbot responses using Gemini."""
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message query parameter is required."
        )
        
    def response_generator():
        # Yield word-by-word streaming
        for chunk in generate_rag_response(message, session_id):
            yield chunk

    return StreamingResponse(response_generator(), media_type="text/plain")

@app.post(f"{settings.API_V1_STR}/chat")
async def post_chat(payload: dict):
    """Accepts chat body, returns a non-streaming or full-text RAG response."""
    message = payload.get("message")
    session_id = payload.get("session_id", "default")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message field is required."
        )
    
    response_text = ""
    for chunk in generate_rag_response(message, session_id):
        response_text += chunk
        
    return {"response": response_text}

@app.post(f"{settings.API_V1_STR}/chat/clear")
async def clear_history(payload: dict):
    session_id = payload.get("session_id", "default")
    if session_id in session_memory:
        session_memory[session_id] = []
    return {"message": "Memory cleared."}

# ==========================================
# 3. Brain MRI Upload & AI Analysis
# ==========================================

@app.post(f"{settings.API_V1_STR}/mri/analyze")
async def analyze_mri(file: UploadFile = File(...)):
    """Accepts brain MRI scans, runs local Keras CNN, and executes Gemini Vision."""
    contents = await file.read()
    print("=== MRI UPLOADER DEBUG ===")
    print("File Name:", file.filename)
    print("File Size:", len(contents), "bytes")
    print("File Content Type:", file.content_type)
    print("First 50 Bytes:", contents[:50])
    print("==========================")

    # 1. Proactive check for empty uploads
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes). Please select a valid visual JPG, JPEG, or PNG image file."
        )

    # 2. Proactive check for Git LFS pointer text metadata
    if contents.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is a Git LFS pointer metadata text file rather than a real image. Please download the actual image from your repository or upload any standard JPEG, JPG, or PNG image from your computer."
        )

    try:
        image = Image.open(io.BytesIO(contents)).convert('RGB')
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file format: {str(e)}. Please upload a PNG, JPEG, or JPG."
        )

    # 1. Run local CNN model (if loaded)
    local_result, local_confidence = mri_analysis_service.run_cnn_classifier(image)
    
    # 2. Run Gemini Vision Radiologist review
    report = mri_analysis_service.analyze_mri_with_gemini(image)
    
    # Enrich report with local CNN classifier data for clinical overlay comparison
    report["local_cnn_result"] = local_result
    report["local_cnn_confidence"] = f"{local_confidence * 100:.1f}%"
    
    return report

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
