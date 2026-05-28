import os
from typing import Any

# Safely import google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

# Safely import openai
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

from backend.app.config import settings

class UnifiedLLMAdapter:
    def __init__(self, provider: str, client: Any, model_name: str):
        self.provider = provider
        self.client = client
        self.model_name = model_name

    def generate_content(self, contents: Any, stream: bool = False) -> Any:
        if self.provider == "gemini":
            return self.client.generate_content(contents, stream=stream)
        elif self.provider == "openai":
            prompt = ""
            images = []
            if isinstance(contents, list):
                for item in contents:
                    if isinstance(item, str):
                        prompt = item
                    elif hasattr(item, "save") or hasattr(item, "thumbnail"):  # PIL Image
                        images.append(item)
            else:
                prompt = contents

            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            
            for pil_img in images:
                import io
                import base64
                buffered = io.BytesIO()
                # Optimize image size for visual APIs
                img_copy = pil_img.copy()
                img_copy.thumbnail((512, 512))
                img_copy.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_str}"
                    }
                })

            if stream:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )
                class StreamWrapper:
                    def __init__(self, r):
                        self.r = r
                    def __iter__(self):
                        for chunk in self.r:
                            delta = chunk.choices[0].delta
                            text = getattr(delta, "content", None)
                            if text:
                                class Chunk:
                                    def __init__(self, t):
                                        self.text = t
                                yield Chunk(text)
                return StreamWrapper(response)
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages
                )
                class ResponseWrapper:
                    def __init__(self, r):
                        self.text = r.choices[0].message.content
                return ResponseWrapper(response)

def get_chat_model(model_name: str = None) -> Any:
    # 1. Check if Gemini API Key is configured
    gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if gemini_key and GEMINI_AVAILABLE:
        try:
            genai.configure(api_key=gemini_key)
            selected_model = model_name or "gemini-2.5-flash"
            model = genai.GenerativeModel(selected_model)
            print(f"UnifiedLLM: Initialized Gemini client with model {selected_model}")
            return UnifiedLLMAdapter("gemini", model, selected_model)
        except Exception as e:
            print(f"Error configuring Gemini Generative AI: {e}")

    print("WARNING: No Gemini API key is configured in settings or environment.")
    return None

def get_gemini_client() -> Any:
    """Backwards compatibility shim for vector_db.py"""
    gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not gemini_key or not GEMINI_AVAILABLE:
        return None
    try:
        genai.configure(api_key=gemini_key)
        return genai
    except Exception:
        return None
