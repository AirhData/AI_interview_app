import json
import logging
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process

logger = logging.getLogger(__name__)

class CVAgentOrchestrator:
    def __init__(self, llm):
        self.llm = llm
        self._create_agents()
    
    def _create_agents(self):
        self.section_splitter = Agent(
            role="Analyseur de Structure de CV",
            goal="Découper intelligemment un CV en sections thématiques",
            backstory="Expert en analyse documentaire spécialisé dans la reconnaissance de structures de CV.",
            verbose=False,
            llm=self.llm
        )
        
        self.contact_extractor = Agent(
            role="Extracteur d'informations de contact",
            goal="Extraire les coordonnées du candidat",
            backstory="Expert en extraction d'informations de contact avec précision.",
            verbose=False,
            llm=self.llm
        )
        
        self.skills_extractor = Agent(
            role="Extracteur de compétences",
            goal="Identifier hard skills et soft skills",
            backstory="Spécialiste en identification de compétences techniques et comportementales.",
            verbose=False,
            llm=self.llm
        )
        
        self.experience_extractor = Agent(
            role="Extracteur d'expériences",
            goal="Extraire les expériences professionnelles",
            backstory="Expert en analyse de parcours professionnels.",
            verbose=False,
            llm=self.llm
        )
        
        self.project_extractor = Agent(
            role="Extracteur de projets",
            goal="Identifier projets professionnels et personnels",
            backstory="Spécialiste en identification de projets significatifs.",
            verbose=False,
            llm=self.llm
        )
        
        self.education_extractor = Agent(
            role="Extracteur de formations",
            goal="Extraire formations et diplômes",
            backstory="Expert en analyse de parcours académiques.",
            verbose=False,
            llm=self.llm
        )
        
        self.reconversion_detector = Agent(
            role="Détecteur de reconversion",
            goal="Analyser les changements de carrière",
            backstory="Conseiller d'orientation expert en transitions de carrière.",
            verbose=False,
            llm=self.llm
        )
        
        self.profile_builder = Agent(
            role="Constructeur de profil",
            goal="Assembler le profil candidat final",
            backstory="Expert en structuration de données JSON.",
            verbose=False,
            llm=self.llm
        )
    
    def split_cv_sections(self, cv_content: str) -> Dict[str, str]:
        task = Task(
            description=f"Analyser ce CV et l'organiser en sections: {cv_content}",
            expected_output="""JSON avec sections: contact, experiences, projects, education, skills, other""",
            agent=self.section_splitter
        )
        
        crew = Crew(
            agents=[self.section_splitter],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            telemetry=False
        )
        
        result = crew.kickoff()
        return self._parse_sections_result(result)
    
    def extract_all_sections(self, sections: Dict[str, str]) -> Dict[str, Any]:
        # Créer les tâches avec les sections en input
        tasks = self._create_extraction_tasks(sections)
        
        crew = Crew(
            agents=[
                self.contact_extractor,
                self.skills_extractor,
                self.experience_extractor,
                self.project_extractor,
                self.education_extractor,
                self.reconversion_detector,
                self.profile_builder
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,  # Activer pour debug
            telemetry=False
        )
        
        # Passer les sections comme inputs
        inputs = {
            "contact": sections.get("contact", ""),
            "experiences": sections.get("experiences", ""),
            "projects": sections.get("projects", ""),
            "education": sections.get("education", ""),
            "skills": sections.get("skills", ""),
            "other": sections.get("other", "")
        }
        
        logger.info(f"Starting crew with inputs: {list(inputs.keys())}")
        result = crew.kickoff(inputs=inputs)
        logger.info(f"Crew completed. Raw result: {result.raw if hasattr(result, 'raw') else str(result)[:200]}...")
        
        return self._parse_final_result(result)
    
    def _create_extraction_tasks(self, sections: Dict[str, str]) -> List[Task]:
        contact_task = Task(
            description=(
                "Voici la section contact du CV : {contact}\n"
                "Extraire précisément le nom, email, téléphone et localisation du candidat."
            ),
            expected_output='{"nom": "...", "email": "...", "numero_de_telephone": "...", "localisation": "..."}',
            agent=self.contact_extractor
        )
        
        skills_task = Task(
            description=(
                "Voici les sections pertinentes du CV :\n"
                "Expériences: {experiences}\n"
                "Projets: {projects}\n"
                "Compétences: {skills}\n"
                "Extraire toutes les compétences techniques (hard skills) et comportementales (soft skills) mentionnées."
            ),
            expected_output='{"hard_skills": ["compétence1", "compétence2"], "soft_skills": ["compétence1", "compétence2"]}',
            agent=self.skills_extractor
        )
        
        experience_task = Task(
            description=(
                "Voici la section expériences du CV : {experiences}\n"
                "Extraire toutes les expériences professionnelles avec poste, entreprise, dates et responsabilités."
            ),
            expected_output='[{"Poste": "titre", "Entreprise": "nom", "start_date": "date", "end_date": "date", "responsabilités": ["resp1", "resp2"]}]',
            agent=self.experience_extractor
        )
        
        project_task = Task(
            description=(
                "Voici les sections projets et expériences du CV :\n"
                "Projets: {projects}\n"
                "Identifier et extraire les projets professionnels et personnels distincts des responsabilités générales."
            ),
            expected_output='{"professional": [{"title": "titre", "technologies": ["tech1"], "outcomes": ["résultat1"]}], "personal": []}',
            agent=self.project_extractor
        )
        
        education_task = Task(
            description=(
                "Voici la section formations du CV : {education}\n"
                "Extraire toutes les formations, diplômes et certifications avec institution et dates."
            ),
            expected_output='[{"degree": "diplôme", "institution": "établissement", "start_date": "date", "end_date": "date"}]',
            agent=self.education_extractor
        )
        
        reconversion_task = Task(
            description=(
                "En analysant les expériences extraites précédemment, déterminer si le candidat est en reconversion professionnelle. "
                "Chercher des changements de secteur, de type de poste ou des transitions significatives."
            ),
            expected_output='{"reconversion_analysis": {"is_reconversion": true, "analysis": "Explication détaillée..."}}',
            agent=self.reconversion_detector,
            context=[experience_task]
        )
        
        profile_task = Task(
            description=(
                "Assembler toutes les informations extraites des tâches précédentes en un profil candidat complet. "
                "Créer un JSON valide avec une clé 'candidat' contenant toutes les sections."
            ),
            expected_output=(
                '{"candidat": {'
                '"informations_personnelles": {...}, '
                '"compétences": {...}, '
                '"expériences": [...], '
                '"projets": {...}, '
                '"formations": [...], '
                '"reconversion": {...}'
                '}}'
            ),
            agent=self.profile_builder,
            context=[contact_task, skills_task, experience_task, project_task, education_task, reconversion_task]
        )
        
        return [contact_task, skills_task, experience_task, project_task, education_task, reconversion_task, profile_task]
    
    def _parse_sections_result(self, result) -> Dict[str, str]:
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        if '```json' in result_str:
            result_str = result_str.split('```json')[1].split('```')[0].strip()
        elif '```' in result_str:
            parts = result_str.split('```')
            if len(parts) >= 3:
                result_str = parts[1].strip()
        
        parsed = json.loads(result_str)
        
        # Assurer que toutes les sections nécessaires existent
        default_sections = {
            "contact": "",
            "experiences": "",
            "projects": "",
            "education": "",
            "skills": "",
            "other": ""
        }
        
        for key in default_sections:
            if key not in parsed:
                parsed[key] = default_sections[key]
        
        return parsed
    
    def _parse_final_result(self, result) -> Dict[str, Any]:
        result_str = result.raw if hasattr(result, 'raw') else str(result)
        
        if '```json' in result_str:
            result_str = result_str.split('```json')[1].split('```')[0].strip()
        elif '```' in result_str:
            parts = result_str.split('```')
            if len(parts) >= 3:
                result_str = parts[1].strip()
        
        return json.loads(result_str)