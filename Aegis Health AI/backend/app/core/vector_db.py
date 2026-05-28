import os
import ast
import csv
from typing import List, Dict, Any, Tuple
from backend.app.config import settings
from backend.app.core.llm import get_gemini_client

# Safely import numpy and pandas
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

def read_csv_pure_python(file_path: str) -> List[Dict[str, str]]:
    """Reads a CSV file using Python's standard library, returning a list of dictionaries."""
    results = []
    if not os.path.exists(file_path):
        print(f"Warning: CSV not found at {file_path}")
        return results
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
    except Exception as e:
        print(f"Error reading CSV in vector DB ({file_path}): {e}")
    return results

class HealthcareVectorDB:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.embeddings = []
        self.is_initialized = False

    def initialize_db(self):
        """Load datasets and prepare documents."""
        if self.is_initialized:
            return

        try:
            # Check files in data directory
            desc_path = os.path.join(settings.DATA_DIR, "description.csv")
            prec_path = os.path.join(settings.DATA_DIR, "precautions_df.csv")
            med_path = os.path.join(settings.DATA_DIR, "medications.csv")
            diet_path = os.path.join(settings.DATA_DIR, "diets.csv")
            workout_path = os.path.join(settings.DATA_DIR, "workout_df.csv")

            if not all(os.path.exists(p) for p in [desc_path, prec_path, med_path, diet_path, workout_path]):
                print(f"Vector DB files missing in {settings.DATA_DIR}. Ingestion skipped.")
                return

            if PANDAS_AVAILABLE:
                df_desc = pd.read_csv(desc_path)
                df_prec = pd.read_csv(prec_path)
                df_med = pd.read_csv(med_path)
                df_diet = pd.read_csv(diet_path)
                df_workout = pd.read_csv(workout_path)

                all_diseases = df_desc['Disease'].unique()

                for dis in all_diseases:
                    # 1. Description
                    desc_row = df_desc[df_desc['Disease'] == dis]
                    desc_text = desc_row['Description'].values[0] if not desc_row.empty else ""

                    # 2. Precautions
                    prec_row = df_prec[df_prec['Disease'] == dis]
                    prec_list = []
                    if not prec_row.empty:
                        for i in range(1, 5):
                            val = prec_row[f'Precaution_{i}'].values[0]
                            if pd.notna(val):
                                prec_list.append(str(val))
                    prec_text = ", ".join(prec_list)

                    # 3. Medications
                    med_row = df_med[df_med['Disease'] == dis]
                    meds_list = []
                    if not med_row.empty:
                        raw_med = med_row['Medication'].values[0]
                        try:
                            meds_list = ast.literal_eval(raw_med)
                        except Exception:
                            meds_list = [raw_med]
                    meds_text = ", ".join(meds_list)

                    # 4. Diet
                    diet_row = df_diet[df_diet['Disease'] == dis]
                    diet_list = []
                    if not diet_row.empty:
                        raw_diet = diet_row['Diet'].values[0]
                        try:
                            diet_list = ast.literal_eval(raw_diet)
                        except Exception:
                            diet_list = [raw_diet]
                    diet_text = ", ".join(diet_list)

                    # 5. Workouts
                    workout_row = df_workout[df_workout['disease'] == dis]
                    workout_list = []
                    if not workout_row.empty:
                        workout_list = workout_row['workout'].values.tolist()
                    workout_text = ", ".join(workout_list)

                    # Build semantic text representation
                    rich_text = (
                        f"Disease: {dis}.\n"
                        f"Description: {desc_text}.\n"
                        f"Precautions: Recommended precautions include {prec_text}.\n"
                        f"Medications: Standard prescribed medicines are {meds_text}.\n"
                        f"Dietary Recommendations: Useful food items are {diet_text}.\n"
                        f"Exercise & Workouts: Health routines should involve {workout_text}."
                    )

                    self.documents.append({
                        "disease": dis,
                        "text": rich_text,
                        "description": desc_text,
                        "precautions": prec_list,
                        "medications": meds_list,
                        "diets": diet_list,
                        "workouts": workout_list
                    })
            else:
                # Pure Python RAG Ingestion Fallback
                desc_rows = read_csv_pure_python(desc_path)
                prec_rows = read_csv_pure_python(prec_path)
                med_rows = read_csv_pure_python(med_path)
                diet_rows = read_csv_pure_python(diet_path)
                workout_rows = read_csv_pure_python(workout_path)

                all_diseases = list(set(row.get('Disease', '').strip() for row in desc_rows if row.get('Disease')))

                for dis in all_diseases:
                    # 1. Description
                    desc_text = ""
                    for row in desc_rows:
                        if row.get('Disease', '').strip().lower() == dis.strip().lower():
                            desc_text = row.get('Description', '')
                            break

                    # 2. Precautions
                    prec_list = []
                    for row in prec_rows:
                        if row.get('Disease', '').strip().lower() == dis.strip().lower():
                            for i in range(1, 5):
                                val = row.get(f'Precaution_{i}')
                                if val and str(val).strip() and str(val).lower() != 'nan':
                                    prec_list.append(str(val).strip())
                            break
                    prec_text = ", ".join(prec_list)

                    # 3. Medications
                    meds_list = []
                    for row in med_rows:
                        if row.get('Disease', '').strip().lower() == dis.strip().lower():
                            raw_med = row.get('Medication', '[]')
                            try:
                                meds_list = ast.literal_eval(raw_med)
                            except Exception:
                                meds_list = [raw_med]
                            break
                    meds_text = ", ".join(meds_list)

                    # 4. Diet
                    diet_list = []
                    for row in diet_rows:
                        if row.get('Disease', '').strip().lower() == dis.strip().lower():
                            raw_diet = row.get('Diet', '[]')
                            try:
                                diet_list = ast.literal_eval(raw_diet)
                            except Exception:
                                diet_list = [raw_diet]
                            break
                    diet_text = ", ".join(diet_list)

                    # 5. Workouts
                    workout_list = []
                    for row in workout_rows:
                        if row.get('disease', '').strip().lower() == dis.strip().lower():
                            val = row.get('workout')
                            if val:
                                workout_list.append(str(val).strip())
                    workout_text = ", ".join(workout_list)

                    rich_text = (
                        f"Disease: {dis}.\n"
                        f"Description: {desc_text}.\n"
                        f"Precautions: Recommended precautions include {prec_text}.\n"
                        f"Medications: Standard prescribed medicines are {meds_text}.\n"
                        f"Dietary Recommendations: Useful food items are {diet_text}.\n"
                        f"Exercise & Workouts: Health routines should involve {workout_text}."
                    )

                    self.documents.append({
                        "disease": dis,
                        "text": rich_text,
                        "description": desc_text,
                        "precautions": prec_list,
                        "medications": meds_list,
                        "diets": diet_list,
                        "workouts": workout_list
                    })

            print(f"Vector DB pre-loaded with {len(self.documents)} medical knowledge records.")
            
            # Optionally build embeddings
            self._generate_embeddings()
            self.is_initialized = True
            
        except Exception as e:
            print(f"Error initializing vector database: {e}")

    def _generate_embeddings(self):
        """Generate embeddings using Google Gemini API or fall back gracefully."""
        if not NUMPY_AVAILABLE:
            print("Skipping vector embeddings: NumPy is unavailable.")
            return

        client = get_gemini_client()
        if client is None or not settings.GEMINI_API_KEY:
            print("Skipping vector database embedding generation. Google Generative AI API key is missing. System will use keyword-based semantic matching.")
            return

        print("Generating embeddings for vector database...")
        try:
            texts = [doc['text'] for doc in self.documents]
            response = client.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document"
            )
            
            if 'embedding' in response:
                self.embeddings = [np.array(emb) for emb in response['embedding']]
                print(f"Successfully generated {len(self.embeddings)} document embeddings.")
            elif isinstance(response, dict) and 'embeddings' in response:
                self.embeddings = [np.array(emb['values']) for emb in response['embeddings']]
                print(f"Successfully generated {len(self.embeddings)} document embeddings.")
            else:
                self.embeddings = []
                for text in texts:
                    res = client.embed_content(
                        model="models/text-embedding-004",
                        content=text,
                        task_type="retrieval_document"
                    )
                    self.embeddings.append(np.array(res['embedding']))
                print(f"Generated {len(self.embeddings)} embeddings via individual fallbacks.")
        except Exception as e:
            print(f"Failed to generate embeddings via Gemini: {e}. Falling back to keyword search.")
            self.embeddings = []

    def similarity_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Perform semantic search or fallback matching."""
        if not self.documents:
            self.initialize_db()
        if not self.documents:
            return []

        # If embeddings are available, perform cosine similarity search
        client = get_gemini_client()
        if self.embeddings and NUMPY_AVAILABLE and client and settings.GEMINI_API_KEY:
            try:
                res = client.embed_content(
                    model="models/text-embedding-004",
                    content=query,
                    task_type="retrieval_query"
                )
                query_vector = np.array(res['embedding'])
                
                scores = []
                for i, doc_emb in enumerate(self.embeddings):
                    dot_product = np.dot(query_vector, doc_emb)
                    norm_q = np.linalg.norm(query_vector)
                    norm_d = np.linalg.norm(doc_emb)
                    cos_sim = dot_product / (norm_q * norm_d + 1e-10)
                    scores.append((cos_sim, self.documents[i]))
                
                # Sort by score descending
                scores.sort(key=lambda x: x[0], reverse=True)
                return [item[1] for item in scores[:top_k]]
            except Exception as e:
                print(f"Embedding search failed: {e}. Falling back to fallback text-matching.")

        # Fallback keyword and text overlapping search
        query_words = set(query.lower().split())
        matched_docs = []
        for doc in self.documents:
            overlap = 0
            text_lower = doc['text'].lower()
            for word in query_words:
                if len(word) > 3 and word in text_lower:
                    overlap += 1
            matched_docs.append((overlap, doc))
        
        matched_docs.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matched_docs[:top_k]]

# Singleton instance
vector_db = HealthcareVectorDB()
