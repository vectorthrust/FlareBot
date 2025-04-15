from dataclasses import dataclass
from qdrant_client import QdrantClient
from FlareBot.ai import GeminiEmbedding
from FlareBot.retriever.config import RetrieverConfig

@dataclass
class AppState:
    """Global application state container"""
    qdrant_client: QdrantClient | None = None
    retriever_config: RetrieverConfig | None = None
    embedding_client: GeminiEmbedding | None = None

# Global state instance
app_state = AppState() 