import os
import logging
from typing import Optional, List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

_embeddings_model = None
_rag_handler_instance = None

VECTOR_STORE_PATH = "/tmp/vector_store" 

def get_embeddings_model():
    global _embeddings_model
    if _embeddings_model is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info("Initialisation du modèle d'embeddings...")
        _embeddings_model = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info("✅ Modèle d'embeddings initialisé avec succès")
    return _embeddings_model

class RAGHandler:
    def __init__(self, knowledge_base_path: str = "/app/knowledge_base", lazy_init: bool = True):
        self.knowledge_base_path = knowledge_base_path
        self.embeddings = None
        self.vector_store = None
        self._initialized = False
        
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        
        if not lazy_init:
            self._initialize()

    def _initialize(self):
        if self._initialized:
            return
        
        logger.info("Initialisation du RAG Handler...")
        self.embeddings = get_embeddings_model()
        
        if self.embeddings is None:
            logger.error("Impossible d'initialiser les embeddings")
            return
        
        self.vector_store = self._load_or_create_vector_store(self.knowledge_base_path)
        self._initialized = True
        logger.info("✅ RAG Handler initialisé avec succès")

    def _load_documents(self, path: str) -> List:
        if not os.path.exists(path):
            logger.warning(f"Répertoire {path} non trouvé")
            return []
            
        loader = DirectoryLoader(
            path,
            glob="**/*.md", 
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        logger.info(f"Chargement des documents depuis : {path}")
        documents = loader.load()
        logger.info(f"✅ {len(documents)} documents chargés")
        return documents

    def _create_vector_store(self, knowledge_base_path: str) -> Optional[FAISS]:
        documents = self._load_documents(knowledge_base_path)
        if not documents:
            logger.warning("Aucun document trouvé - création d'un vector store vide")
            from langchain.schema import Document
            dummy_doc = Document(
                page_content="Document de test pour initialiser le vector store",
                metadata={"source": "dummy"}
            )
            documents = [dummy_doc]
        
        logger.info(f"{len(documents)} documents chargés. Création des vecteurs...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        
        vector_store = FAISS.from_documents(texts, self.embeddings)
        
        vector_store.save_local(VECTOR_STORE_PATH)
        logger.info(f"✅ Vector store créé et sauvegardé dans : {VECTOR_STORE_PATH}")
        
        return vector_store

    def _load_or_create_vector_store(self, knowledge_base_path: str) -> Optional[FAISS]:
        index_path = os.path.join(VECTOR_STORE_PATH, "index.faiss")
        if os.path.exists(index_path):
            logger.info(f"Chargement du vector store existant depuis : {VECTOR_STORE_PATH}")
            return FAISS.load_local(
                VECTOR_STORE_PATH, 
                embeddings=self.embeddings, 
                allow_dangerous_deserialization=True 
            )
        else:
            logger.info("Aucun vector store trouvé. Création d'un nouveau...")
            return self._create_vector_store(knowledge_base_path)

    def get_relevant_feedback(self, query: str, k: int = 1) -> List[str]:
        if not self._initialized:
            self._initialize()
        
        if not self.vector_store:
            logger.warning("Vector store non disponible - retour de conseils génériques")
            return [
                "Préparez vos réponses aux questions comportementales",
                "Montrez votre motivation pour le poste",
                "Donnez des exemples concrets de vos réalisations"
            ]
        
        results = self.vector_store.similarity_search(query, k=k)
        feedback = [doc.page_content for doc in results if doc.page_content.strip()]
        
        if not feedback:
            return ["Conseil général: Préparez-vous bien pour les entretiens futurs."]
            
        return feedback

def get_rag_handler() -> Optional[RAGHandler]:
    global _rag_handler_instance
    if _rag_handler_instance is None:
        _rag_handler_instance = RAGHandler(lazy_init=True)
    return _rag_handler_instance