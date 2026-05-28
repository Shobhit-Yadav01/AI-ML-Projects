from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SymptomRequest(BaseModel):
    symptoms: List[str]

class DiseaseDetailResponse(BaseModel):
    predicted_disease: str
    description: str
    precautions: List[str]
    medications: List[str]
    diets: List[str]
    workout: List[str]
    corrected_symptoms: List[str]

class AllSymptomsResponse(BaseModel):
    symptoms: List[str]
