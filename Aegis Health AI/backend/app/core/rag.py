import os
import re
import time
from typing import List, Dict, Generator, Any
import google.generativeai as genai

from backend.app.core.vector_db import vector_db
from backend.app.config import settings
from backend.app.services.disease_pred import disease_pred_service

# ============================================================
# AEGIS HEALTH - MASTER SYSTEM PROMPT (Exact User-Defined)
# ============================================================
SYSTEM_PROMPT = """You are Aegis Health, an advanced AI healthcare assistant.

Your behavior rules:

1. Greeting Behavior

* If user says:
  hello
  hi
  hey
  good morning
  good evening

Then:

* greet naturally like ChatGPT
* sound warm and human
* ask about user's health

Example:
"Hello! Welcome to Aegis Health. I'm here to help you with your health concerns. How are you feeling today?"

2. Health Inquiry Flow
   If user says:

* I'm not feeling well
* I feel sick
* I have health issues
* I need help

Then ask:
"I'm sorry to hear that. Could you please describe your symptoms in detail?"

3. Symptom Analysis Rules
   When user provides symptoms:

* analyze symptoms from medical CSV/database only
* use vector retrieval and symptom matching
* identify disease only if confidence is sufficient

4. If Symptoms Match
   Provide:

* disease name
* description
* precautions
* medicines
* treatment suggestions
* diet recommendations

Format responses professionally and naturally.

5. If Symptoms Do NOT Match
   NEVER hallucinate.
   NEVER guess diseases.

Reply politely:
"I'm unable to confidently identify your condition based on the provided symptoms. Please consult a qualified healthcare professional for proper medical diagnosis and treatment."

6. Safety Rules

* Never provide dangerous medical advice
* Never claim guaranteed diagnosis
* Always recommend doctor consultation for severe conditions
* Be conversational and supportive
* Avoid robotic responses
* Do not dump raw database text
* Summarize naturally

7. Response Style

* concise
* natural
* human-like
* empathetic
* structured

You are NOT just a database retriever.
You are a conversational healthcare AI assistant."""

# ============================================================
# Simple in-memory session memory (per session_id)
# ============================================================
session_memory: Dict[str, List[Dict[str, str]]] = {}

# Greeting keywords for intent detection
GREETING_KEYWORDS = {
    "hello", "hi", "hey", "good morning", "good evening", "good afternoon",
    "good night", "greetings", "howdy", "hiya", "heya", "helo", "hii", "hiii"
}

# Unwell keywords for intent detection
UNWELL_KEYWORDS = {
    "not feeling well", "not well", "feeling sick", "feel sick", "i am sick",
    "i'm sick", "not good", "not okay", "not fine", "feeling bad", "feel bad",
    "health issues", "health problem", "need help", "feeling unwell", "unwell",
    "i feel ill", "feeling ill", "i am ill", "not feeling okay", "feeling terrible",
    "feeling horrible", "not feeling good"
}

# Comprehensive Symptom Alias Mapping for intelligent normalization
SYMPTOM_ALIASES = {
    "coughing": "cough",
    "cough": "cough",
    "dry cough": "cough",
    "wet cough": "cough",
    "cough with phlegm": "cough",
    "feverish": "high fever",
    "fever": "high fever",
    "mild fever": "mild fever",
    "high temperature": "high fever",
    "headache": "headache",
    "head ache": "headache",
    "migraine": "headache",
    "vomit": "vomiting",
    "vomiting": "vomiting",
    "nausea": "nausea",
    "nauseous": "nausea",
    "fatigue": "fatigue",
    "tired": "fatigue",
    "tiredness": "fatigue",
    "weakness": "fatigue",
    "stomach pain": "stomach pain",
    "belly pain": "stomach pain",
    "abdominal pain": "abdominal pain",
    "chills": "chills",
    "shivering": "shivering",
    "joint pain": "joint pain",
    "muscle pain": "muscle pain",
    "sore throat": "throat irritation",
    "throat irritation": "throat irritation",
    "runny nose": "runny nose",
    "stuffy nose": "congestion",
    "congestion": "congestion",
    "breathlessness": "breathlessness",
    "shortness of breath": "breathlessness",
    "difficulty breathing": "breathlessness",
    "chest pain": "chest pain",
    "dizziness": "dizziness",
    "dizzy": "dizziness",
    "constipation": "constipation",
    "diarrhoea": "diarrhoea",
    "diarrhea": "diarrhoea",
    "loose motion": "diarrhoea",
    "skin rash": "skin rash",
    "rash": "skin rash",
    "itching": "itching",
    "itchy": "itching",
    "sweating": "sweating",
    "sweat": "sweating"
}

# Session diagnostic state management
session_states: Dict[str, Dict[str, Any]] = {}


def get_or_create_state(session_id: str) -> Dict[str, Any]:
    if session_id not in session_states:
        session_states[session_id] = {
            "collected_symptoms": [],
            "stage": "greeting",
            "last_suggested_symptoms": []
        }
    return session_states[session_id]


def extract_symptoms(text: str) -> List[str]:
    """
    Intelligently extracts, cleans, and normalizes symptoms from natural language text
    using exact phrase matching, alias substitution, and partial matching.
    """
    if not text:
        return []
    
    lowered = text.lower().strip()
    cleaned = re.sub(r'[^\w\s]', ' ', lowered)
    extracted = set()
    
    # 1. Check for standard aliases first
    for alias, standard in SYMPTOM_ALIASES.items():
        if alias in lowered:
            extracted.add(standard)
            
    # 2. Check for explicit matches against valid processed symptoms in database
    valid_symptoms = list(disease_pred_service.symptoms_processed.keys())
    for symptom in valid_symptoms:
        if len(symptom) > 3 and symptom in lowered:
            extracted.add(symptom)
            
    # 3. Handle word boundary matching for variants
    words = cleaned.split()
    for word in words:
        if len(word) < 4:
            continue
        for symptom in valid_symptoms:
            if word in symptom and len(word) >= len(symptom) - 2:
                extracted.add(symptom)
                
    return list(extracted)


def _detect_intent(text: str) -> str:
    """Detects user intent: greeting, unwell, or symptom_query."""
    lowered = text.lower().strip()
    words = set(lowered.replace("?", "").replace("!", "").replace(",", "").split())
    if words & GREETING_KEYWORDS and len(lowered) < 30:
        return "greeting"
    for phrase in UNWELL_KEYWORDS:
        if phrase in lowered:
            return "unwell"
    return "symptom_query"


def get_session_history(session_id: str) -> List[Dict[str, str]]:
    if session_id not in session_memory:
        session_memory[session_id] = []
    return session_memory[session_id]


def add_message_to_history(session_id: str, role: str, content: str):
    if session_id not in session_memory:
        session_memory[session_id] = []
    session_memory[session_id].append({"role": role, "content": content})
    # Keep last 12 messages to stay within context limits
    if len(session_memory[session_id]) > 12:
        session_memory[session_id].pop(0)


def _get_gemini_model(system_instruction: str) -> genai.GenerativeModel:
    """Returns an authenticated Gemini model."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please add it to backend/.env"
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction
    )


def generate_rag_response(user_query: str, session_id: str = "default") -> Generator[str, None, None]:
    """
    Intelligent conversational healthcare AI assistant flow:
    1. Greeting / Unwell detection
    2. Symptom collection, normalization, and memory integration
    3. Weak symptoms checking with follow-up symptom suggestions
    4. Database/CSV-backed disease prediction & confidence check
    5. Fallback warning or warm doctor-like RAG summarization via Gemini 2.5
    """
    history = get_session_history(session_id)
    state = get_or_create_state(session_id)
    
    # Self-heal: If history is empty (e.g. cleared), reset session state
    if not history:
        state["collected_symptoms"] = []
        state["stage"] = "greeting"
        state["last_suggested_symptoms"] = []
        
    intent = _detect_intent(user_query)
    
    # ----------------------------------------------------------
    # Flow 1: Greeting Behavior
    # ----------------------------------------------------------
    if intent == "greeting":
        state["collected_symptoms"] = []
        state["last_suggested_symptoms"] = []
        state["stage"] = "greeting"
        
        greeting_text = (
            "Hello! Welcome to Aegis Health 😊\n"
            "I'm here to help you with your health concerns and wellness. How are you feeling today?"
        )
        words = greeting_text.split(" ")
        full_resp = ""
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            full_resp += token
            yield token
            time.sleep(0.01)
            
        add_message_to_history(session_id, "user", user_query)
        add_message_to_history(session_id, "assistant", full_resp)
        return

    # ----------------------------------------------------------
    # Flow 2: Health Inquiry / Sick Flow
    # ----------------------------------------------------------
    if intent == "unwell":
        state["stage"] = "collecting"
        
        unwell_text = "I'm sorry to hear that. Could you please describe your symptoms in detail?"
        words = unwell_text.split(" ")
        full_resp = ""
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            full_resp += token
            yield token
            time.sleep(0.01)
            
        add_message_to_history(session_id, "user", user_query)
        add_message_to_history(session_id, "assistant", full_resp)
        return

    # ----------------------------------------------------------
    # Flow 3: Symptom Processing & Follow-up
    # ----------------------------------------------------------
    lowered_query = user_query.lower().strip()
    confirmed_symptoms = []
    
    # Check if they are responding to active follow-up bullet points
    if state["last_suggested_symptoms"]:
        is_positive = any(yes in lowered_query for yes in ["yes", "yeah", "yep", "sure", "both", "all", "have them", "i do"])
        is_negative = any(no in lowered_query for no in ["no", "none", "not really", "nah", "don't have", "do not"])
        
        if is_positive:
            # Assume all suggested symptoms are present
            confirmed_symptoms.extend(state["last_suggested_symptoms"])
            state["last_suggested_symptoms"] = []
        elif is_negative:
            state["last_suggested_symptoms"] = []
        else:
            # Check if they explicitly mentioned any of the suggested symptoms
            for sym in state["last_suggested_symptoms"]:
                if sym in lowered_query:
                    confirmed_symptoms.append(sym)
            if confirmed_symptoms:
                state["last_suggested_symptoms"] = []

    # Extract symptoms from their natural language input
    extracted = extract_symptoms(user_query)
    new_symptoms = list(set(extracted + confirmed_symptoms))
    
    if new_symptoms:
        state["collected_symptoms"] = list(set(state["collected_symptoms"] + new_symptoms))
        state["stage"] = "collecting"
        
    collected_symptoms = state["collected_symptoms"]
    
    # Case A: User sent a message with no symptoms detected yet
    if not collected_symptoms:
        # Check if it is a general information query that we can fulfill via vector RAG
        relevant_docs = vector_db.similarity_search(user_query, top_k=3)
        context_str = "\n\n".join([doc["text"] for doc in relevant_docs]) if relevant_docs else ""
        
        prompt = (
            f"You are Aegis Health, a caring clinical AI assistant. "
            f"The user is asking a general health question or didn't specify symptoms.\n"
            f"User Query: {user_query}\n\n"
            f"If relevant, here is verified clinical library information to formulate your answer:\n{context_str}\n\n"
            f"Please respond naturally and warmly. If they seem unwell, ask them to describe their symptoms."
        )
        
        try:
            model = _get_gemini_model(SYSTEM_PROMPT)
            response = model.generate_content(prompt, stream=True)
            full_response = ""
            for chunk in response:
                try:
                    if chunk.text:
                        full_response += chunk.text
                        yield chunk.text
                except Exception:
                    pass
            add_message_to_history(session_id, "user", user_query)
            add_message_to_history(session_id, "assistant", full_response)
        except Exception as e:
            yield f"⚠️ Aegis Health encountered an error: {str(e)}"
        return

    # Case B: Exactly 1 symptom collected -> Ask follow-up question
    if len(collected_symptoms) == 1:
        single_sym = collected_symptoms[0]
        
        # Look for matching diseases to collect related symptoms
        matching_diseases = []
        for disease, symptoms_set in disease_pred_service.disease_symptoms_cache.items():
            if single_sym in symptoms_set:
                matching_diseases.append((disease, symptoms_set))
                
        frequency_map = {}
        for disease, symptoms_set in matching_diseases:
            for sym in symptoms_set:
                if sym != single_sym and sym not in collected_symptoms:
                    frequency_map[sym] = frequency_map.get(sym, 0) + 1
                    
        # Select top 5 related symptoms
        suggested = sorted(frequency_map.items(), key=lambda x: x[1], reverse=True)[:5]
        suggested_symptoms = [sym[0] for sym in suggested]
        
        if not suggested_symptoms:
            # Fallback list of common symptoms
            suggested_symptoms = ["fever", "headache", "fatigue", "nausea", "sore throat"]
            
        state["last_suggested_symptoms"] = suggested_symptoms
        
        bullets = "\n".join([f"• {sym}" for sym in suggested_symptoms])
        follow_up_text = (
            f"I understand you are experiencing **{single_sym}**. "
            f"To help me provide an accurate analysis, could you tell me if you are also experiencing any of the following:\n\n{bullets}"
        )
        
        words = follow_up_text.split(" ")
        full_resp = ""
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            full_resp += token
            yield token
            time.sleep(0.01)
            
        add_message_to_history(session_id, "user", user_query)
        add_message_to_history(session_id, "assistant", full_resp)
        return

    # Case C: 2 or more symptoms collected -> Perform Disease Prediction
    try:
        prediction = disease_pred_service.predict_disease(collected_symptoms)
        
        # Apply Low Confidence Rule (threshold is 0.35)
        if "error" in prediction or prediction.get("confidence", 0.0) < 0.35:
            low_conf_text = (
                "I'm unable to confidently identify your condition based on the provided symptoms. "
                "Please consult a qualified healthcare professional for proper medical diagnosis and treatment."
            )
            words = low_conf_text.split(" ")
            full_resp = ""
            for i, word in enumerate(words):
                token = word + (" " if i < len(words) - 1 else "")
                full_resp += token
                yield token
                time.sleep(0.01)
                
            add_message_to_history(session_id, "user", user_query)
            add_message_to_history(session_id, "assistant", full_resp)
            
            # Reset state for next cycle
            state["collected_symptoms"] = []
            state["last_suggested_symptoms"] = []
            state["stage"] = "ready"
            return

        # High confidence prediction exists -> Formulate doctor-like conversational summary
        precautions_str = "\n".join([f"- {p}" for p in prediction["precautions"]])
        meds_str = ", ".join(prediction["medications"])
        diets_str = ", ".join(prediction["diets"])
        
        prompt = (
            f"Construct a highly supportive, conversational clinical response as Aegis Health. "
            f"Adhere strictly to the verified facts provided below and do not guess any other disease.\n\n"
            f"VERIFIED CLINICAL DATA:\n"
            f"- Identified Condition: {prediction['predicted_disease']}\n"
            f"- Match Confidence: {int(prediction['confidence'] * 100)}%\n"
            f"- Description: {prediction['description']}\n"
            f"- Necessary Precautions:\n{precautions_str}\n"
            f"- Standard Medications: {meds_str}\n"
            f"- Recommended Diets: {diets_str}\n\n"
            f"REQUIREMENTS:\n"
            f"1. Sound warm and friendly—behave like a compassionate family doctor.\n"
            f"2. Convert raw medical descriptions and diets into fluent paragraphs.\n"
            f"3. Highlight precautions in a clean bulleted format.\n"
            f"4. Be short, concise, and clean. Avoid giant blocks of text.\n"
            f"5. End with a professional disclaimer advising doctor validation for severe or persistent conditions."
        )
        
        model = _get_gemini_model(SYSTEM_PROMPT)
        response = model.generate_content(prompt, stream=True)
        
        full_response = ""
        for chunk in response:
            try:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
                elif getattr(chunk, "parts", None):
                    # Handle safety filters returning empty text but containing valid parts
                    for part in chunk.parts:
                        if hasattr(part, "text") and part.text:
                            full_response += part.text
                            yield part.text
            except Exception:
                pass
                
        add_message_to_history(session_id, "user", user_query)
        add_message_to_history(session_id, "assistant", full_response)
        
        # Reset state after successful diagnosis
        state["collected_symptoms"] = []
        state["last_suggested_symptoms"] = []
        state["stage"] = "ready"

    except Exception as e:
        error_msg = f"⚠️ Aegis Health encountered an error during symptom analysis: {str(e)}"
        print(f"[RAG/DIAG ERROR] {e}")
        yield error_msg
