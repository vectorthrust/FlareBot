import google.api_core.exceptions
import pandas as pd
import structlog
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from FlareBot.ai import EmbeddingTaskType, GeminiEmbedding
from FlareBot.retriever.config import RetrieverConfig
import asyncio

logger = structlog.get_logger(__name__)


def _create_collection(
    client: QdrantClient, collection_name: str, vector_size: int
) -> None:
    """
    Creates a Qdrant collection with the given parameters.
    :param collection_name: Name of the collection.
    :param vector_size: Dimension of the vectors.
    """
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )


def generate_collection(
    df_docs: pd.DataFrame,
    qdrant_client: QdrantClient,
    retriever_config: RetrieverConfig,
    embedding_client: GeminiEmbedding,
) -> None:
    """Routine for generating a Qdrant collection for a specific CSV file type."""
    _create_collection(
        qdrant_client, retriever_config.collection_name, retriever_config.vector_size
    )
    logger.info(
        "Created the collection.", collection_name=retriever_config.collection_name
    )

    points = []
    for idx, (_, row) in enumerate(
        df_docs.iterrows(), start=1
    ):
        content = row["content"]

        if not isinstance(content, str):
            logger.warning(
                "Skipping document due to missing or invalid content.",
                filename=row["file_name"],
            )
            continue

        try:
            embedding = embedding_client.embed_content(
                embedding_model=retriever_config.embedding_model,
                task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
                contents=content,
                title=str(row["file_name"]),
            )
        except google.api_core.exceptions.InvalidArgument as e:
            if "400 Request payload size exceeds the limit" in str(e):
                logger.warning(
                    "Skipping document due to size limit.",
                    filename=row["file_name"],
                )
                continue
            logger.exception(
                "Error encoding document (InvalidArgument).",
                filename=row["file_name"],
            )
            continue
        except Exception:
            logger.exception(
                "Error encoding document (general).",
                filename=row["file_name"],
            )
            continue

        payload = {
            "filename": row["file_name"],
            "metadata": row["meta_data"],
            "text": content,
        }

        point = PointStruct(
            id=idx,  
            vector=embedding,
            payload=payload,
        )
        points.append(point)

    if points:
        qdrant_client.upsert(
            collection_name=retriever_config.collection_name,
            points=points,
        )
        logger.info(
            "Collection generated and documents inserted into Qdrant successfully.",
            collection_name=retriever_config.collection_name,
            num_points=len(points),
        )
    else:
        logger.warning("No valid documents found to insert.")


async def store_discord_message(
    message_content: str,
    author_id: str,
    jump_url: str,
    qdrant_client: QdrantClient,
    retriever_config: RetrieverConfig,
    embedding_client: GeminiEmbedding,
) -> None:
    """
    Store a Discord message in the vector database.
    
    Args:
        message_content: The content of the message to store
        author_id: The Discord ID of the message author
        qdrant_client: The Qdrant client instance
        retriever_config: Configuration for the retriever
        embedding_client: The embedding client instance
    """
    try:
        collection_info = qdrant_client.get_collection(retriever_config.collection_name)
        next_id = collection_info.points_count + 1

        timestamp = pd.Timestamp.now()
        
        doc_name = f"discord_msg_{author_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        embedding = embedding_client.embed_content(
            embedding_model=retriever_config.embedding_model,
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
            contents=message_content,
        )

        payload = {
            "filename": jump_url,
            "text": message_content,
            "author_id": author_id,
            "type": "discord_message",
            "timestamp": timestamp.isoformat(),
        }

        point = PointStruct(
            id=next_id,
            vector=embedding,
            payload=payload,
        )

        qdrant_client.upsert(
            collection_name=retriever_config.collection_name,
            points=[point],
        )
        
        logger.info(
            "Successfully stored Discord message in vector database",
            author_id=author_id,
            doc_name=doc_name,
        )
    except Exception as e:
        logger.exception(
            "Failed to store Discord message",
            author_id=author_id,
            error=str(e),
        )
