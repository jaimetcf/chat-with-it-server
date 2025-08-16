"""Documentation-only Firestore models.

This file documents the Firestore collections and document shapes used by the
system to facilitate maintenance and onboarding. It is not imported or used by
any runtime Python code.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, Literal, List


@dataclass
class Session:
    """Represents a persistent conversation session for a user.

    Conceptually: a session is a sequence of messages exchanged between a user
    and the AI agent. Sessions do not have a fixed start/stop lifecycle; they
    persist indefinitely until explicitly deleted by the user. A user can
    resume a session at any time and continue the conversation, with all prior
    messages retained.

    Storage path: sessions/{sessionId}
    Subcollection: messages (the conversation turns within the session)
    """

    sessionId: str
    userId: str
    name: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


@dataclass
class Message:
    """Conceptually: a single turn in the conversation between the user and the AI.

    Each message captures who spoke (via `role` -> 'user' | 'assistant'), the text
    content, and when it was created. The UI renders messages in chronological
    order to present the session transcript.

    Storage path: sessions/{sessionId}/messages/{messageId}
    Fields mirror writes in server/functions/main.py.
    """

    id: str
    sessionId: str
    userId: str
    role: Literal["user", "assistant"]
    message: str
    createdAt: Optional[datetime] = None
    clientMessageId: Optional[str] = None


@dataclass
class VectorEmbedding:
    """Represents a vector embedding for a text chunk from a processed file.

    Each document in the vector_embeddings collection stores a single embedding
    vector along with metadata about the source text chunk and file. This enables
    semantic search across user documents.

    Storage path: vector_embeddings/{vectorDocumentId}
    Fields mirror writes in server/functions/vector_storage.py.
    """

    id: str
    user_id: str
    file_name: str
    file_document_id: str
    chunk_index: int
    chunk_text: str
    chunk_length: int
    total_chunks: int
    embedding_model: str
    embedding_dimensions: int
    embedding_vector: list[float]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ProcessedFile:
    """Represents metadata about a file that has been processed through the vectorization pipeline.

    Each document in the processed_files collection stores metadata about a file
    that has been successfully processed, including information about the extracted
    content, generated embeddings, and processing status.

    Storage path: processed_files/{fileDocumentId}
    Fields mirror writes in server/functions/vector_storage.py.
    """

    id: str
    user_id: str
    file_name: str
    file_type: Literal["PDF", "IMAGE", "UNKNOWN"]
    total_chunks: int
    total_tokens: int
    embedding_model: str
    embedding_dimensions: int
    vector_count: int
    processing_status: Literal["completed", "failed", "processing"]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserVectorStores:
    """Represents the OpenAI vector stores associated with a user.

    Each document in the user_vector_stores collection stores the OpenAI vector store IDs
    that are associated with a specific user. This enables tracking which vector stores
    belong to which user for proper access control and management.

    Storage path: user_vector_stores/{userId}
    """
    user_id: str
    vector_store_ids: List[str]


@dataclass
class DocumentProcessingStatus:
    """Represents the real-time processing status of a document for user notifications.

    Each document in the document_processing_status collection tracks the current
    processing state of a file, enabling real-time updates to the frontend about
    document processing progress.

    Storage path: document_processing_status/{userId}_{fileName}
    Document ID format: {userId}_{fileName} (e.g., "user123_document.pdf")
    """

    user_id: str
    file_name: str
    status: Literal["uploading", "processing", "vectorizing", "completed", "failed", "deleting"]
    error_message: Optional[str] = None
    progress_percentage: Optional[int] = None
    file_id: Optional[str] = None  # OpenAI file ID for deletion purposes
    vector_store_id: Optional[str] = None  # OpenAI vector store ID for deletion purposes
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
