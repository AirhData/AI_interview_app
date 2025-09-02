import logging
from langchain_core.tools import tool
from src.services.analysis_service import AnalysisService 
import json
import os
from datetime import datetime
from pydantic.v1 import BaseModel, Field
from typing import List, Dict, Any
from src.models import load_all_models
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewAnalysisArgs(BaseModel):
    """Arguments for the trigger_interview_analysis tool."""
    user_id: str = Field(..., description="The unique identifier for the user, provided in the system prompt.")
    job_offer_id: str = Field(..., description="The unique identifier for the job offer, provided in the system prompt.")
    job_description: str = Field(..., description="The full JSON string of the job offer description.")
    conversation_history: List[Dict[str, Any]] = Field(..., description="The complete conversation history between the user and the agent.")

@tool("trigger_interview_analysis", args_schema=InterviewAnalysisArgs)
def trigger_interview_analysis(user_id: str, job_offer_id: str, job_description: str, conversation_history: List[Dict[str, Any]]):
    """
    Call this tool to end the interview and launch the final analysis.
    You MUST provide all arguments: user_id, job_offer_id, job_description, and the complete conversation_history.
    """
    try:
        logger.info(f"Outil 'trigger_interview_analysis' appelé pour user_id: {user_id} et job_offer_id: {job_offer_id}")
        if '@' in user_id or ' ' in job_offer_id:
             logger.error(f"Appel de l'outil avec des données invalides. User ID: {user_id}, Job Offer ID: {job_offer_id}")
             return "Erreur: Appel de l'outil avec des paramètres invalides. L'analyse n'a pas pu être lancée."
        mongo_client = MongoClient(os.getenv("MONGO_URI"))
        db = mongo_client[os.getenv("MONGO_DB_NAME")]
        collection = db[os.getenv("MONGO_FEEDBACK")]
        
        models = load_all_models()
        analysis_service = AnalysisService(models=models)
        feedback_data = analysis_service.run_analysis(
            conversation_history=conversation_history,
            job_description=job_description
        )
        mongo_document = {
            "user_id": user_id,
            "job_offer_id": job_offer_id,
            "feedback_data": feedback_data,
            "updated_at": datetime.utcnow()
        }
        result = collection.insert_one(mongo_document)
        logger.info(f"Analyse pour l'utilisateur {user_id} terminée et sauvegardée dans MongoDB avec l'ID: {result.inserted_id}")
        
        return "L'analyse a été déclenchée et terminée avec succès."

    except Exception as e:
        logger.error(f"Erreur dans l'outil d'analyse : {e}", exc_info=True)
        return "Une erreur est survenue lors du lancement de l'analyse."