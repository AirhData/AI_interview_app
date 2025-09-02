import json
import logging
from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, models: Dict[str, Any]):
        self.models = models
        self.analyzer = models.get("deep_learning_analyzer")
        self.rag_handler = models.get("rag_handler")
        self.llm = models.get("llm")
        self._create_report_agent()

    def _create_report_agent(self):
        self.report_agent = Agent(
            role='Rédacteur de Rapports Synthétiques',
            goal='Générer un feedback pertinent à partir du déroulement de l\'entretien',
            backstory=(
                "Spécialisé dans le recrutement et les ressources humaines, capable d'évaluer les candidats "
                "sur la communication et la pertinence des réponses en fonction des questions posées, rédige "
                "en un rapport clair, un feedback détaillé sur le candidat."
            ),
            allow_delegation=False,
            verbose=False,
            llm=self.llm
        )

    def run_analysis(self, conversation_history: List[Dict[str, Any]], job_description: str) -> Dict[str, Any]:
        if not self.analyzer:
            return {"error": "Analyzer non disponible"}

        structured_analysis = self.analyzer.run_full_analysis(conversation_history, job_description)
        
        rag_feedback = []
        if self.rag_handler:
            rag_feedback = self._get_contextual_feedback(structured_analysis)
        
        report = self._generate_final_report(structured_analysis, rag_feedback)
        
        return report

    def _get_contextual_feedback(self, structured_analysis: Dict[str, Any]) -> List[str]:
        rag_feedback = []
        
        if structured_analysis.get("intent_analysis"):
            for intent in structured_analysis["intent_analysis"]:
                query = f"Conseils pour un candidat qui cherche à {intent['labels'][0]}"
                rag_feedback.extend(self.rag_handler.get_relevant_feedback(query))
        
        if structured_analysis.get("sentiment_analysis"):
            for sentiment_group in structured_analysis["sentiment_analysis"]:
                for sentiment in sentiment_group:
                    if sentiment['label'] == 'stress' and sentiment['score'].item() > 0.6:
                        rag_feedback.extend(
                            self.rag_handler.get_relevant_feedback("gestion du stress en entretien")
                        )
        
        return list(set(rag_feedback))

    def _generate_final_report(
        self, 
        structured_analysis: Dict[str, Any], 
        rag_feedback: List[str]
    ) -> Dict[str, Any]:
        
        task = Task(
            description=(
                f"Tu es un rédacteur expert en RH. Ta mission est de rédiger un rapport d'évaluation final. "
                f"Tu dois utiliser deux sources d'information principales : "
                f"1. Les données d'analyse structurées de l'entretien : '{json.dumps(structured_analysis, indent=2)}'. "
                f"2. Une liste de conseils et de feedback pertinents issus de notre base de connaissances : '{chr(10).join(rag_feedback)}'. "
                f"Ta tâche est de synthétiser ces informations en un rapport cohérent et actionnable."
            ),
            expected_output=(
                "Un rapport final exceptionnel basé sur l'analyse fournie. Le rapport doit être structuré comme suit: "
                "1. **Résumé et Score d'Adéquation** : Synthétise le score de similarité sémantique et donne un aperçu global. "
                "2. **Analyse Comportementale** : Interprète les résultats de l'analyse de sentiment et d'intention pour décrire le comportement du candidat. "
                "3. **Adéquation Sémantique avec le Poste** : Explique ce que signifie le score de similarité. "
                "4. **Points Forts & Axes d'Amélioration Personnalisés** : Utilise les données d'analyse pour identifier les points à améliorer. "
                "Ensuite, intègre de manière fluide et naturelle les conseils pertinents pour proposer des pistes d'amélioration concrètes et personnalisées. "
                "5. **Recommandation Finale**."
            ),
            agent=self.report_agent
        )

        crew = Crew(
            agents=[self.report_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            telemetry=False
        )

        result = crew.kickoff()
        return {"analysis_report": result.raw if hasattr(result, 'raw') else str(result)}