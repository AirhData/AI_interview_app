import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def load_all_models() -> Dict[str, Any]:
    models = {
        "status": False,
        "deep_learning_analyzer": None,
        "rag_handler": None,
        "llm": None
    }
    
    try:
        from src.core.deep_learning_analyzer import MultiModelInterviewAnalyzer
        models["deep_learning_analyzer"] = MultiModelInterviewAnalyzer()
        logger.info("✅ Deep Learning Analyzer chargé")
    except Exception as e:
        logger.error(f"❌ Erreur chargement Deep Learning Analyzer: {e}")
    
    try:
        from src.core.rag_handler import get_rag_handler
        models["rag_handler"] = get_rag_handler()
        logger.info("✅ RAG Handler chargé")
    except Exception as e:
        logger.error(f"❌ Erreur chargement RAG Handler: {e}")
    
    try:
        from src.config import crew_openai
        models["llm"] = crew_openai()
        logger.info("✅ LLM chargé")
    except Exception as e:
        logger.error(f"❌ Erreur chargement LLM: {e}")
    
    models["status"] = all(v is not None for k, v in models.items() if k != "status")
    
    return models