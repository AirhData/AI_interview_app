import os
import sys
import json
from typing import Dict, List, Any, Annotated
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from src.config import read_system_prompt, format_cv

class State(TypedDict):
    messages: Annotated[list, add_messages]

class InterviewProcessor:
    def __init__(self, cv_document: Dict[str, Any], job_offer: Dict[str, Any], conversation_history: List[Dict[str, Any]]):
        if not cv_document or 'candidat' not in cv_document:
            raise ValueError("Document CV invalide fourni.")
        if not job_offer:
            raise ValueError("Données de l'offre d'emploi non fournies.")

        self.job_offer = job_offer
        self.cv_data = cv_document['candidat']
        self.conversation_history = conversation_history
        self.llm = self._get_llm()

        self.system_prompt_template = self._load_prompt_template()
        self.graph = self._build_graph()

    def _get_llm(self) -> ChatOpenAI:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            temperature=0.6, 
            model_name="gpt-4o-mini", 
            api_key=openai_api_key
        )

    def _load_prompt_template(self) -> str:
        return read_system_prompt('prompts/rag_prompt_old.txt') 

    def _extract_skills_summary(self) -> str:
        """Extrait un résumé simple des compétences avec niveaux"""
        competences = self.cv_data.get('analyse_competences', [])
        if not competences:
            return "Aucune analyse de compétences disponible."
        
        summary = []
        for comp in competences:
            skill = comp.get('skill', '')
            level = comp.get('level', 'débutant')
            summary.append(f"{skill}: {level}")
        
        return "Niveaux de compétences du candidat: " + " | ".join(summary)

    def _extract_reconversion_info(self) -> str:
        """Extrait les infos de reconversion"""
        reconversion = self.cv_data.get('reconversion', {})
        if not reconversion:
            return ""
        
        is_reconversion = reconversion.get('is_reconversion', False)
        if not is_reconversion:
            return ""
        
        analysis = reconversion.get('analysis', '')
        return f"CANDIDAT EN RECONVERSION: {analysis}"

    def _chatbot_node(self, state: State) -> dict:
        messages = state["messages"]
        formatted_cv_str = format_cv(self.cv_data)
        
        # Extractions simples
        skills_summary = self._extract_skills_summary()
        reconversion_info = self._extract_reconversion_info()

        # Formatage du prompt système avec les nouvelles données
        system_prompt = self.system_prompt_template.format(
            entreprise=self.job_offer.get('entreprise', 'notre entreprise'),
            poste=self.job_offer.get('poste', 'ce poste'),
            mission=self.job_offer.get('mission', 'Non spécifiée'),
            profil_recherche=self.job_offer.get('profil_recherche', 'Non spécifié'),
            competences=self.job_offer.get('competences', 'Non spécifiées'),
            pole=self.job_offer.get('pole', 'Non spécifié'),
            cv=formatted_cv_str,
            skills_analysis=skills_summary,
            reconversion_analysis=reconversion_info
        )
        
        llm_messages = [SystemMessage(content=system_prompt)] + messages
        response = self.llm.invoke(llm_messages)
        return {"messages": [response]}

    def _build_graph(self) -> any:
        graph_builder = StateGraph(State)
        
        graph_builder.add_node("chatbot", self._chatbot_node)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        
        return graph_builder.compile()

    def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        initial_state = self.conversation_history + messages
        return self.graph.invoke({"messages": initial_state})