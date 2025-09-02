import logging
import sys
import os
import json
import tempfile
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from bson import ObjectId

from src.models import load_all_models
from src.services.cv_service import CVParsingService
from src.services.analysis_service import AnalysisService
from services.graph_service import GraphInterviewProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs('/tmp/feedbacks', exist_ok=True)

app = FastAPI(
    title="AIrh Interview Assistant",
    description="API pour l'analyse de CV et la simulation d'entretiens d'embauche avec analyse asynchrone.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialisation des services ---
logger.info("Chargement des modèles et initialisation des services...")
models = load_all_models()
cv_service = CVParsingService(models)
logger.info("Services initialisés.")


# --- Définition des modèles Pydantic ---
class Feedback(BaseModel):
    status: str
    feedback_data: Optional[Dict[str, Any]] = None

class HealthCheck(BaseModel):
    status: str = "ok"

# --- Endpoint de santé ---
@app.get("/", response_model=HealthCheck, tags=["Status"])
async def health_check():
    return HealthCheck()

# --- Endpoint principal pour la simulation d'entretien ---
@app.post("/simulate-interview/")
async def simulate_interview(request: Request):
    """
    Ce endpoint reçoit les données de l'entretien, instancie le processeur de graphe
    et lance la conversation.
    """
    # CORRECTION : Récupérer l'instance du logger pour garantir sa disponibilité dans le scope de la fonction.
    logger = logging.getLogger(__name__)
    try:
        payload = await request.json()
        
        if not all(k in payload for k in ["user_id", "job_offer_id", "cv_document", "job_offer"]):
            raise HTTPException(status_code=400, detail="Données manquantes dans le payload (user_id, job_offer_id, cv_document, job_offer).")
            
        logger.info(f"Début de la simulation pour l'utilisateur : {payload['user_id']}")
        
        processor = GraphInterviewProcessor(payload)
        result = processor.invoke(payload.get("messages", []))
        
        return JSONResponse(content=result)

    except ValueError as ve:
        logger.error(f"Erreur de validation des données : {ve}", exc_info=True)
        return JSONResponse(content={"error": str(ve)}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur interne dans le endpoint simulate-interview: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Une erreur interne est survenue sur le serveur de l'assistant."},
            status_code=500
        )

# --- Endpoint pour l'analyse de CV ---
@app.post("/parse-cv/", tags=["CV Parsing"])
async def parse_cv(
    file: UploadFile = File(...), 
    user_id: str = Query(None, description="ID de l'utilisateur pour lier le CV")
):
    """
    Analyse un fichier CV (PDF) et le stocke automatiquement dans MongoDB.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Fichier PDF requis")
    
    contents = await file.read()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        result = await run_in_threadpool(cv_service.parse_cv, tmp_path, user_id)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
    if not result:
        raise HTTPException(status_code=500, detail="Échec de l'extraction des données du CV.")
        
    return result

# --- Démarrage de l'application (pour un test local) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)