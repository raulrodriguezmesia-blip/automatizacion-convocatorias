"""
Chatbot API for Convocatoria Management
Exposes endpoints for document processing, convocatoria generation, and conversational interface.
"""

import logging
import os
from typing import Any

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .generator import generate_convocatoria, generate_from_document

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Convocatoria AI Chatbot",
    description="Enterprise chatbot for automated convocatoria management",
    version="1.0.0",
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation history (replace with Redis in production)
conversation_store: dict[str, list[dict[str, str]]] = {}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    use_llm: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: str
    structured_data: dict[str, Any] | None = None


class DocumentProcessRequest(BaseModel):
    use_llm: bool = False


class MetricsSummary(BaseModel):
    predictions_total: int
    drift_alerts: int
    model_accuracy: float
    last_retrain: str | None = None


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Conversational endpoint for managing convocatorias."""
    session_id = request.session_id
    user_msg = request.message.strip()

    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_store[session_id].append({"role": "user", "content": user_msg})

    response_text = ""
    structured = None

    if any(
        kw in user_msg.lower() for kw in ["procesa", "documento", "archivo", "upload", "analiza"]
    ):
        response_text = "Por favor sube el documento usando el endpoint /process-document o adjuntalo en el chat."
    elif any(kw in user_msg.lower() for kw in ["genera", "crea", "redacta", "borrador", "draft"]):
        response_text = "Para generar una convocatoria, necesito los detalles: titulo, fecha, hora, lugar, organizador, descripcion, asistentes y requisitos."
    elif any(kw in user_msg.lower() for kw in ["ayuda", "help", "que puedes", "comandos"]):
        response_text = (
            "Puedo ayudarte a:\n"
            "1. **Procesar documentos** de convocatorias (PDF, DOCX, TXT).\n"
            "2. **Generar borradores** formales a partir de datos estructurados.\n"
            "3. **Responder preguntas** sobre convocatorias existentes.\n\n"
            "Ejemplos: 'Sube el archivo convocatoria.pdf' o 'Genera una convocatoria para reunion Q3'."
        )
    else:
        response_text = (
            f"Entendido: '{user_msg}'. "
            "Para acciones especificas, usa comandos como 'procesa documento', 'genera convocatoria' o 'ayuda'."
        )

    conversation_store[session_id].append({"role": "assistant", "content": response_text})

    return ChatResponse(response=response_text, session_id=session_id, structured_data=structured)


@app.post("/process-document")
async def process_document_endpoint(file: UploadFile = File(...), use_llm: bool = Form(False)):
    """Upload and process a convocatoria document."""
    import tempfile

    suffix = os.path.splitext(file.filename)[1] or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = generate_from_document(tmp_path, use_llm=use_llm)
        return result
    finally:
        os.unlink(tmp_path)


@app.post("/generate", response_model=dict[str, str])
async def generate_endpoint(entities: dict[str, Any], use_llm: bool = False):
    """Generate convocatoria from structured entities."""
    convocatoria = generate_convocatoria(entities, use_llm=use_llm)
    return {"convocatoria": convocatoria}


@app.get("/metrics/summary", response_model=MetricsSummary)
async def metrics_summary():
    """Return AI model metrics for Prometheus/Grafana dashboards."""
    return MetricsSummary(
        predictions_total=0, drift_alerts=0, model_accuracy=0.0, last_retrain=None
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "convocatoria-ai-chatbot"}


if __name__ == "__main__":
    uvicorn.run("chatbot:app", host="0.0.0.0", port=8000, reload=True)
