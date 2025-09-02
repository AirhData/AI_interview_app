import os
import logging
import json
from typing import TypedDict, Annotated, Sequence, Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from tools.analysis_tools import trigger_interview_analysis

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
    user_id: str
    job_offer_id: str
    job_description: str

class GraphInterviewProcessor:
    """
    Cette classe encapsule la logique d'un entretien en utilisant LangGraph.
    Elle prépare toutes les données nécessaires à l'initialisation.
    """
    def __init__(self, payload: Dict[str, Any]):
        logging.info("Initialisation de GraphInterviewProcessor...")
        
        self.user_id = payload["user_id"]
        self.job_offer_id = payload["job_offer_id"]
        self.job_offer = payload["job_offer"]
        self.cv_data = payload.get("cv_document", {}).get('candidat', {})

        if not self.cv_data:
            raise ValueError("Données du candidat non trouvées dans le payload.")

        self.system_prompt_template = self._load_prompt_template('prompts/rag_prompt_old.txt')
        self.formatted_cv_str = self._format_cv_for_prompt()
        self.skills_summary = self._extract_skills_summary()
        self.reconversion_info = self._extract_reconversion_info()
        
        self.agent_runnable = self._create_agent_runnable()
        self.graph = self._build_graph()
        logging.info("GraphInterviewProcessor initialisé avec succès.")

    def _load_prompt_template(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging.error(f"Fichier prompt introuvable: {file_path}")
            return "Vous êtes un assistant RH."

    def _format_cv_for_prompt(self) -> str:
        return json.dumps(self.cv_data, indent=2, ensure_ascii=False)

    def _extract_skills_summary(self) -> str:
        competences = self.cv_data.get('analyse_competences', [])
        if not competences: return "Aucune analyse de compétences disponible."
        summary = [f"{comp.get('skill', '')}: {comp.get('level', 'débutant')}" for comp in competences]
        return "Niveaux de compétences du candidat: " + " | ".join(summary)

    def _extract_reconversion_info(self) -> str:
        reconversion = self.cv_data.get('reconversion', {})
        if reconversion.get('is_reconversion'):
            return f"CANDIDAT EN RECONVERSION: {reconversion.get('analysis', '')}"
        return "Le candidat n'est pas identifié comme étant en reconversion."

    def _create_agent_runnable(self) -> Runnable:
        """Crée une chaîne (runnable) qui agit comme notre agent."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt_content}"),
            MessagesPlaceholder(variable_name="messages"),
        ])
        llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.7)
        tools = [trigger_interview_analysis]
        llm_with_tools = llm.bind_tools(tools)
        return prompt | llm_with_tools

    def _agent_node(self, state: AgentState):
        """Prépare le prompt et appelle le runnable de l'agent."""
        job_description_str = json.dumps(self.job_offer, ensure_ascii=False)
        
        system_prompt_content = self.system_prompt_template.format(
            user_id=state['user_id'],
            job_offer_id=state['job_offer_id'],
            entreprise=self.job_offer.get('entreprise', 'notre entreprise'),
            poste=self.job_offer.get('poste', 'ce poste'),
            mission=self.job_offer.get('mission', 'Non spécifiée'),
            profil_recherche=self.job_offer.get('profil_recherche', 'Non spécifié'),
            competences=self.job_offer.get('competences', 'Non spécifiées'),
            pole=self.job_offer.get('pole', 'Non spécifié'),
            cv=self.formatted_cv_str,
            skills_analysis=self.skills_summary,
            reconversion_analysis=self.reconversion_info,
            job_description=job_description_str
        )
        
        response = self.agent_runnable.invoke({
            "system_prompt_content": system_prompt_content,
            "messages": state["messages"]
        })

        return {"messages": [response]}

    def _router(self, state: AgentState) -> str:
        """Route le flux du graphe en fonction de la dernière réponse de l'agent."""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            if any(tool_call.get('name') == 'trigger_interview_analysis' for tool_call in last_message.tool_calls):
                return "call_final_tool"
            return "call_tool"
        return "end_turn"

    def _final_analysis_node(self, state: AgentState):
        """
        Appelle l'outil d'analyse finale. Construit les arguments manuellement
        à partir de l'état du graphe pour garantir la fiabilité.
        """
        conversation_history = []
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                continue
            conversation_history.append({"role": role, "content": msg.content})

        tool_input = {
            "user_id": state['user_id'],
            "job_offer_id": state['job_offer_id'],
            "job_description": state['job_description'],
            "conversation_history": conversation_history
        }
        
        trigger_interview_analysis.invoke(tool_input)
        return {}

    def _build_graph(self) -> any:
        """Construit et compile le graphe d'états."""
        tool_node = ToolNode([trigger_interview_analysis])
        
        graph = StateGraph(AgentState)
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", tool_node)
        graph.add_node("final_tool_node", self._final_analysis_node) 
        
        graph.set_entry_point("agent")
        
        graph.add_conditional_edges(
            "agent",
            self._router,
            {
                "call_tool": "tools",
                "call_final_tool": "final_tool_node",
                "end_turn": END
            }
        )
        
        graph.add_edge("tools", "agent")
        graph.add_edge("final_tool_node", END)
        
        return graph.compile()

    def invoke(self, messages: List[Dict[str, Any]]):
        """Point d'entrée pour lancer une conversation dans le graphe."""
        langchain_messages = [HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) for m in messages]
        
        if not langchain_messages:
            logging.info("Historique de conversation vide. Ajout d'un message de démarrage interne.")
            langchain_messages.append(HumanMessage(content="Bonjour, je suis prêt à commencer l'entretien."))
            
        initial_state = {
            "user_id": self.user_id,
            "job_offer_id": self.job_offer_id,
            "messages": langchain_messages,
            "job_description": json.dumps(self.job_offer, ensure_ascii=False),
        }
        
        final_state = self.graph.invoke(initial_state)
        
        if not final_state or not final_state.get('messages'):
            logging.error("L'état final est vide ou ne contient pas de messages.")
            return {"response": "Erreur: Impossible de générer une réponse.", "status": "finished"}
        last_message = final_state['messages'][-1]
        status = "finished" if hasattr(last_message, 'tool_calls') and last_message.tool_calls else "interviewing"
        response_content = last_message.content
        
        return {
            "response": response_content,
            "status": status
        }