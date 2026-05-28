import os
import pickle
import ast
import csv
from typing import List, Dict, Any, Optional
from backend.app.config import settings

# Gracefully handle numpy and pandas imports
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from fuzzywuzzy import process
except ImportError:
    from difflib import get_close_matches

    class _FallbackProcess:
        @staticmethod
        def extractOne(query, choices):
            matches = get_close_matches(query, choices, n=1, cutoff=0)
            if not matches:
                return None, 0
            match = matches[0]
            score = int(100 if match == query else 80)
            return match, score

    process = _FallbackProcess()

def read_csv_pure_python(file_path: str) -> List[Dict[str, str]]:
    """Reads a CSV file using Python's standard library, returning a list of dictionaries."""
    results = []
    if not os.path.exists(file_path):
        print(f"Warning: CSV file not found at {file_path}")
        return results
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
    except Exception as e:
        print(f"Error reading CSV in pure Python ({file_path}): {e}")
    return results

class DiseasePredictionService:
    def __init__(self):
        self.rf_model = None
        self.s_des = None
        self.precautions = None
        self.workout = None
        self.description = None
        self.medications = None
        self.diets = None
        self.is_loaded = False
        self.disease_symptoms_cache = {} # fallback disease to symptom sets

        # Static symptom list matching legacy trained vector indexes
        self.symptoms_list = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
        self.diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

        self.symptoms_processed = {symptom.replace('_', ' ').lower(): value for symptom, value in self.symptoms_list.items()}

    def load_resources(self):
        if self.is_loaded:
            return True
        try:
            desc_path = os.path.join(settings.DATA_DIR, "description.csv")
            prec_path = os.path.join(settings.DATA_DIR, "precautions_df.csv")
            med_path = os.path.join(settings.DATA_DIR, "medications.csv")
            diet_path = os.path.join(settings.DATA_DIR, "diets.csv")
            work_path = os.path.join(settings.DATA_DIR, "workout_df.csv")
            symptoms_path = os.path.join(settings.DATA_DIR, "symptoms_df.csv")
            model_file = os.path.join(settings.MODEL_DIR, "RandomForest.pkl")

            # Try to load RandomForest model via standard pickle if libraries exist
            if NUMPY_AVAILABLE and os.path.exists(model_file):
                try:
                    with open(model_file, "rb") as f:
                        self.rf_model = pickle.load(f)
                    print("disease_pred: RandomForest model pickle loaded successfully.")
                except Exception as e:
                    print(f"disease_pred: Failed to load RandomForest model ({e}). Fallback logic will handle predictions.")
                    self.rf_model = None
            else:
                print("disease_pred: Scikit-learn not installed or model file missing. Running in pure-Python matching mode.")
                self.rf_model = None

            # Load diagnostic datasets using Pandas if available, otherwise pure Python parser
            if PANDAS_AVAILABLE:
                self.s_des = pd.read_csv(desc_path)
                self.precautions = pd.read_csv(prec_path)
                self.workout = pd.read_csv(work_path)
                self.description = pd.read_csv(desc_path)
                self.medications = pd.read_csv(med_path)
                self.diets = pd.read_csv(diet_path)
                symptoms_rows = pd.read_csv(symptoms_path).to_dict(orient='records')
            else:
                self.s_des = read_csv_pure_python(desc_path)
                self.precautions = read_csv_pure_python(prec_path)
                self.workout = read_csv_pure_python(work_path)
                self.description = read_csv_pure_python(desc_path)
                self.medications = read_csv_pure_python(med_path)
                self.diets = read_csv_pure_python(diet_path)
                symptoms_rows = read_csv_pure_python(symptoms_path)

            # Build high-fidelity Jaccard rules-association engine cache from raw symptom sheets
            self.disease_symptoms_cache = {}
            for row in symptoms_rows:
                disease = row.get("Disease")
                if not disease:
                    continue
                disease_cleaned = disease.strip()
                if disease_cleaned not in self.disease_symptoms_cache:
                    self.disease_symptoms_cache[disease_cleaned] = set()
                
                # Gather all symptom keys in row and clean them
                for k, v in row.items():
                    if k.startswith("Symptom_") and v and str(v).strip():
                        sym_cleaned = str(v).strip().replace('_', ' ').lower()
                        self.disease_symptoms_cache[disease_cleaned].add(sym_cleaned)

            self.is_loaded = True
            print("Disease Prediction resources loaded successfully in backend.")
            return True
        except Exception as e:
            print(f"Failed to load disease prediction resources: {e}")
            return False

    def correct_spelling(self, symptom: str) -> Optional[str]:
        if not self.is_loaded:
            self.load_resources()
        symptom_cleaned = symptom.strip().replace('_', ' ').lower()
        if symptom_cleaned in self.symptoms_processed:
            return symptom_cleaned
            
        closest_match, score = process.extractOne(symptom_cleaned, self.symptoms_processed.keys())
        if score and score >= 80:
            return closest_match
        return None

    def predict_disease(self, symptoms: List[str]) -> Dict[str, Any]:
        if not self.is_loaded:
            if not self.load_resources():
                raise RuntimeError("Resources not available.")

        # Spell correction
        corrected_symptoms = []
        for sym in symptoms:
            corr = self.correct_spelling(sym)
            if corr:
                corrected_symptoms.append(corr)
            else:
                return {"error": f"Symptom '{sym}' is unrecognized. Please try a different spelling."}

        if not corrected_symptoms:
            return {"error": "No recognizable symptoms were provided."}

        predicted_dis = None
        confidence = 0.85 # default

        # Mode A: Scikit-learn RandomForest prediction
        if self.rf_model is not None and NUMPY_AVAILABLE:
            try:
                i_vector = np.zeros(len(self.symptoms_processed))
                for sym in corrected_symptoms:
                    i_vector[self.symptoms_processed[sym]] = 1
                
                pred_index = self.rf_model.predict([i_vector])[0]
                predicted_dis = self.diseases_list.get(pred_index)
            except Exception as e:
                print(f"disease_pred: RandomForest inference failed ({e}). Reverting to Jaccard similarity.")
                predicted_dis = None

        # Mode B: High-Fidelity Jaccard similarity fallback matching rules
        if not predicted_dis:
            matches = []
            for disease, disease_symptoms in self.disease_symptoms_cache.items():
                set_user = set(corrected_symptoms)
                set_disease = set(disease_symptoms)
                
                intersection = len(set_user.intersection(set_disease))
                union = len(set_user.union(set_disease))
                
                # Standard Jaccard index
                jaccard_score = intersection / union if union > 0 else 0.0
                
                # Match percentage of the user's symptoms
                user_match_ratio = intersection / len(set_user) if len(set_user) > 0 else 0.0
                
                # Combined score balancing both criteria
                score = (jaccard_score * 0.4) + (user_match_ratio * 0.6)
                
                if score > 0:
                    matches.append({"disease": disease, "score": score})
            
            if matches:
                matches.sort(key=lambda x: x["score"], reverse=True)
                top_match = matches[0]
                predicted_dis = top_match["disease"]
                # Map score to standard 60-95% confidence range
                confidence = min(0.95, max(0.50, top_match["score"]))
            else:
                # Absolute last default fallback
                predicted_dis = "Common Cold"
                confidence = 0.50

        # Extract diagnostic guidelines details from loaded sheets (handles both Pandas and pure list layouts)
        disease_desc = "No description available."
        disease_precautions = []
        disease_medications = []
        disease_diets = []
        disease_workout = []

        if PANDAS_AVAILABLE:
            # Pandas query logic
            desc_rows = self.description[self.description['Disease'] == predicted_dis]['Description']
            if not desc_rows.empty:
                disease_desc = " ".join(desc_rows.values)

            prec_rows = self.precautions[self.precautions['Disease'] == predicted_dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
            if not prec_rows.empty:
                disease_precautions = [col for col in prec_rows.values[0] if pd.notna(col)]

            med_rows = self.medications[self.medications['Disease'] == predicted_dis]['Medication']
            if not med_rows.empty:
                raw_meds = med_rows.values[0]
                try:
                    disease_medications = ast.literal_eval(raw_meds)
                except Exception:
                    disease_medications = [raw_meds]

            diet_rows = self.diets[self.diets['Disease'] == predicted_dis]['Diet']
            if not diet_rows.empty:
                raw_diets = diet_rows.values[0]
                try:
                    disease_diets = ast.literal_eval(raw_diets)
                except Exception:
                    disease_diets = [raw_diets]

            workout_rows = self.workout[self.workout['disease'] == predicted_dis]['workout']
            if not workout_rows.empty:
                disease_workout = workout_rows.values.tolist()
        else:
            # Pure Python list/dict query logic
            for row in self.description:
                if row.get('Disease', '').strip().lower() == predicted_dis.strip().lower():
                    disease_desc = row.get('Description', 'No description available.')
                    break

            for row in self.precautions:
                if row.get('Disease', '').strip().lower() == predicted_dis.strip().lower():
                    for prec_col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                        val = row.get(prec_col)
                        if val and str(val).strip() and str(val).lower() != 'nan':
                            disease_precautions.append(str(val).strip())
                    break

            for row in self.medications:
                if row.get('Disease', '').strip().lower() == predicted_dis.strip().lower():
                    raw_meds = row.get('Medication', '[]')
                    try:
                        disease_medications = ast.literal_eval(raw_meds)
                    except Exception:
                        disease_medications = [raw_meds]
                    break

            for row in self.diets:
                if row.get('Disease', '').strip().lower() == predicted_dis.strip().lower():
                    raw_diets = row.get('Diet', '[]')
                    try:
                        disease_diets = ast.literal_eval(raw_diets)
                    except Exception:
                        disease_diets = [raw_diets]
                    break

            for row in self.workout:
                if row.get('disease', '').strip().lower() == predicted_dis.strip().lower():
                    val = row.get('workout')
                    if val:
                        disease_workout.append(str(val).strip())

        return {
            "predicted_disease": predicted_dis,
            "confidence": round(confidence, 2),
            "description": disease_desc,
            "precautions": disease_precautions,
            "medications": disease_medications,
            "diets": disease_diets,
            "workout": disease_workout,
            "corrected_symptoms": corrected_symptoms
        }

# Singleton instance
disease_pred_service = DiseasePredictionService()
disease_pred_service.load_resources()
