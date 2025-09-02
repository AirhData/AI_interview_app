import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient
from src.config import load_pdf
from src.agents.cv_agents import CVAgentOrchestrator
from src.agents.scoring_agent import SimpleScoringAgent

logger = logging.getLogger(__name__)

class CVParsingService:
    def __init__(self, models: Dict[str, Any]):
        self.models = models
        self.orchestrator = CVAgentOrchestrator(models.get("llm"))
        self.scoring_agent = SimpleScoringAgent()
        
        # Initialisation MongoDB
        try:
            self.client = MongoClient(os.getenv("MONGO_URI"))
            self.db = self.client[os.getenv("MONGO_DB_NAME")]
            self.candidate_collection = self.db[os.getenv("MONGO_CV_COLLECTION")]
        except:
            self.client = None
            self.candidate_collection = None

    def parse_cv(self, pdf_path: str, user_id: str = None) -> Dict[str, Any]:
        cv_text = load_pdf(pdf_path)
        if not cv_text or not cv_text.strip():
            return self._create_fallback_data()    
        
        logger.info(f"CV text loaded: {len(cv_text)} characters")
        sections = self.orchestrator.split_cv_sections(cv_text)
        logger.info(f"Sections extracted: {list(sections.keys())}")
        cv_data = self.orchestrator.extract_all_sections(sections)
        logger.info(f"CV data extracted: {cv_data is not None}")
        
        if not cv_data or not cv_data.get("candidat") or not self._is_valid_extraction(cv_data):
            logger.warning("Agent extraction failed or incomplete, using fallback extraction")
            return self._create_fallback_data()
        
        logger.info("Calculating skill levels...")
        scores = self.scoring_agent.calculate_scores(cv_data["candidat"])
        if scores and scores.get("analyse_competences"):
            cv_data["candidat"].update(scores)
            skills_count = len(scores.get("analyse_competences", []))
            levels_summary = self._get_levels_summary(scores.get("analyse_competences", []))
            logger.info(f"Skill levels calculated: {skills_count} skills - {levels_summary}")
        else:
            logger.warning("No skill levels calculated, adding empty analysis")
            cv_data["candidat"]["analyse_competences"] = []
        self._save_profile(cv_data, user_id)
        
        return cv_data

    def _save_profile(self, cv_data: Dict[str, Any], user_id: str = None):
        """
        Sauvegarde le CV avec la structure complète incluant la clé 'candidat'
        """
        if self.candidate_collection is None or not isinstance(cv_data, dict):
            return
        
        try:
            # Garder la structure complète avec la clé 'candidat'
            profile_data = cv_data.copy()
            profile_data["created_at"] = datetime.utcnow()
            profile_data["updated_at"] = datetime.utcnow()
            
            if user_id:
                profile_data["user_id"] = user_id
            
            self.candidate_collection.insert_one(profile_data)
            logger.info("CV stocké dans MongoDB avec succès")
        except Exception as e:
            logger.error(f"Erreur stockage CV: {e}")

    def _get_levels_summary(self, competences: List[Dict[str, Any]]) -> str:
        levels_count = {}
        for comp in competences:
            level = comp.get("level", "unknown")
            levels_count[level] = levels_count.get(level, 0) + 1
        return ", ".join([f"{count} {level}" for level, count in levels_count.items()])
    
    def _is_valid_extraction(self, cv_data: Dict[str, Any]) -> bool:
        candidat = cv_data.get("candidat", {})
        has_info = bool(candidat.get("informations_personnelles", {}).get("nom", "").strip())
        has_skills = bool(candidat.get("compétences", {}).get("hard_skills", []) or 
                         candidat.get("compétences", {}).get("soft_skills", []))
        has_experience = bool(candidat.get("expériences", []))
        return has_info or has_skills or has_experience