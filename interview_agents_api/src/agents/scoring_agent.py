import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SimpleScoringAgent:
    
    def calculate_scores(self, candidat_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        if not candidat_data or not isinstance(candidat_data, dict):
            return {"analyse_competences": []}
            
        skills_data = candidat_data.get("compétences", {})
        skills_list = self._extract_skills_list(skills_data)
        
        if not skills_list:
            return {"analyse_competences": []}

        skill_analysis = []
        
        for skill in skills_list:
            level = self._determine_skill_level(skill, candidat_data)
            skill_analysis.append({
                "skill": skill,
                "level": level
            })
        
        return {"analyse_competences": skill_analysis}

    def _extract_skills_list(self, skills_data: Dict[str, Any]) -> List[str]:
        """Extrait la liste des compétences"""
        skills_list = []
        
        if isinstance(skills_data, dict):
            skills_list.extend(skills_data.get("hard_skills", []))
            skills_list.extend(skills_data.get("soft_skills", []))
        elif isinstance(skills_data, list):
            skills_list = [item.get("nom") for item in skills_data if item.get("nom")]
        
        return [skill for skill in skills_list if skill and isinstance(skill, str) and skill.strip()]

    def _determine_skill_level(self, skill: str, candidat_data: Dict[str, Any]) -> str:
        """Détermine le niveau d'une compétence selon des règles simples"""
        
        frequency = self._count_skill_mentions(skill, candidat_data)
        max_duration = self._get_max_duration_for_skill(skill, candidat_data)
        has_pro_experience = self._has_professional_experience(skill, candidat_data)
        
        # Règles simples de classification
        if has_pro_experience and max_duration >= 3.0:
            return "expert"
        elif has_pro_experience and max_duration >= 1.0:
            return "avance"
        elif frequency >= 3 or max_duration >= 0.5:
            return "intermediaire"
        else:
            return "debutant"

    def _count_skill_mentions(self, skill: str, candidat_data: Dict[str, Any]) -> int:
        """Compte le nombre de mentions de la compétence"""
        skill_lower = skill.lower()
        total_mentions = 0
        
        # Recherche dans toutes les sections
        all_text = self._get_all_text_content(candidat_data).lower()
        total_mentions = all_text.count(skill_lower)
        
        return total_mentions

    def _get_max_duration_for_skill(self, skill: str, candidat_data: Dict[str, Any]) -> float:
        """Trouve la durée maximum d'utilisation de la compétence"""
        skill_lower = skill.lower()
        max_duration = 0.0
        
        experiences_key = "expériences" if "expériences" in candidat_data else "experiences_professionnelles"
        experiences = candidat_data.get(experiences_key, [])
        
        if not isinstance(experiences, list):
            return 0.0
        
        for exp in experiences:
            if not isinstance(exp, dict):
                continue
                
            exp_text = json.dumps(exp, ensure_ascii=False).lower()
            
            if skill_lower in exp_text:
                duration = self._calculate_experience_duration(exp)
                max_duration = max(max_duration, duration)
        
        return max_duration

    def _has_professional_experience(self, skill: str, candidat_data: Dict[str, Any]) -> bool:
        """Vérifie si la compétence a été utilisée en contexte professionnel"""
        skill_lower = skill.lower()
        
        experiences_key = "expériences" if "expériences" in candidat_data else "experiences_professionnelles"
        experiences = candidat_data.get(experiences_key, [])
        
        if not isinstance(experiences, list):
            return False
        
        for exp in experiences:
            if not isinstance(exp, dict):
                continue
                
            exp_text = json.dumps(exp, ensure_ascii=False).lower()
            if skill_lower in exp_text:
                return True
        
        return False

    def _get_all_text_content(self, candidat_data: Dict[str, Any]) -> str:
        """Récupère tout le contenu textuel du CV"""
        all_content = []
        
        # Expériences
        experiences_key = "expériences" if "expériences" in candidat_data else "experiences_professionnelles"
        for exp in candidat_data.get(experiences_key, []):
            if isinstance(exp, dict):
                all_content.append(json.dumps(exp, ensure_ascii=False))
        
        # Projets
        projects = candidat_data.get("projets", {})
        if isinstance(projects, dict):
            for project_type in ["professional", "personal"]:
                for project in projects.get(project_type, []):
                    if isinstance(project, dict):
                        all_content.append(json.dumps(project, ensure_ascii=False))
        
        # Formations
        for formation in candidat_data.get("formations", []):
            if isinstance(formation, dict):
                all_content.append(json.dumps(formation, ensure_ascii=False))
        
        return " ".join(all_content)

    def _calculate_experience_duration(self, exp: Dict[str, Any]) -> float:
        """Calcule la durée d'une expérience en années"""
        start_date_str = exp.get("date_debut", exp.get("start_date", ""))
        end_date_str = exp.get("date_fin", exp.get("end_date", ""))
        
        if not isinstance(start_date_str, str):
            start_date_str = str(start_date_str) if start_date_str else ""
        if not isinstance(end_date_str, str):
            end_date_str = str(end_date_str) if end_date_str else ""
        
        return self._calculate_duration_in_years(start_date_str, end_date_str)

    def _calculate_duration_in_years(self, start_date_str: str, end_date_str: str) -> float:
        """Calcule la durée entre deux dates en années"""
        start_date = self._parse_date(start_date_str)
        end_date = self._parse_date(end_date_str)
        
        if start_date and end_date:
            if end_date < start_date:
                return 0.0
            return (end_date - start_date).days / 365.25
        
        return 0.0

    def _parse_date(self, date_str: str) -> datetime:
        """Parse une date de manière simple"""
        if not date_str or not isinstance(date_str, str):
            return None
            
        date_str_lower = date_str.lower().strip()
        if date_str_lower in ["aujourd'hui", "maintenant", "en cours", "current", "présent", "actuellement"]:
            return datetime.now()
        
        # Extraction simple de l'année
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', date_str)
        if year_match:
            year = int(year_match.group(1))
            return datetime(year, 1, 1)
        
        return None

# Alias pour maintenir la compatibilité
ScoringAgent = SimpleScoringAgent
ImprovedScoringAgent = SimpleScoringAgent