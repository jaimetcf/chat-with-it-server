import time
from typing import List, Optional
from firebase_admin import firestore as admin_firestore
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta
from agents.memory import Session


class FirestoreSession(Session):
    """Custom session backed by Firestore for persistent agent memory.
    
    Implements the Session protocol using the existing messages sub-collection
    to maintain conversation history for the OpenAI Agents SDK.
    
    Layout:
      sessions/{session_id}/messages/{message_id}
        - id: str
        - sessionId: str
        - userId: str
        - role: "user" | "assistant"
        - message: str
        - createdAt: server timestamp
        - clientMessageId: str (optional)
    """

    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.client = admin_firestore.client()
        self._messages_collection = (
            self.client.collection("sessions")
            .document(self.session_id)
            .collection("messages")
        )

    async def get_items(self, limit: Optional[int] = None) -> List[dict]:
        """Retrieve conversation history for this session.
        
        Converts Firestore messages to the format expected by the Agents SDK.
        """
        query = self._messages_collection.order_by("createdAt")
        if limit:
            query = query.limit(limit)
        docs = list(query.stream())
        items: List[dict] = []
        for doc in docs:
            data = doc.to_dict() or {}
            message_role = data.get("role")
            message_content = data.get("message", "")
            
            # Convert to Agents SDK format
            if message_role == "user":
                items.append({"role": "user", "content": message_content})
            elif message_role == "assistant":
                items.append({"role": "assistant", "content": message_content})
        
        return items

    async def add_items(self, items: List[dict]) -> None:
        """Store new items for this session.
        
        Converts Agents SDK format to Firestore messages and stores them.
        Ensures proper timestamp ordering by using microsecond-precision timestamps.
        """
        batch = self.client.batch()

        base_datetime = datetime.now()
        
        for i, item in enumerate(items):
            role = item.get("role")
            content = item.get("content", "")
            
            # Skip items that don't match expected roles
            if role not in ["user", "assistant"]:
                continue
            
            # Create datetime with milliecond precision to ensure ordering
            message_datetime = base_datetime + timedelta(milliseconds=i*2)
            
            doc_ref = self._messages_collection.document()
            batch.set(
                doc_ref,
                {
                    "id": doc_ref.id,
                    "sessionId": self.session_id,
                    "userId": self.user_id,
                    "role": role,
                    "message": content,
                    "createdAt": message_datetime
                },
            )
        batch.commit()

    async def pop_item(self) -> Optional[dict]:
        """Remove and return the most recent item from this session."""
        docs = list(
            self._messages_collection.order_by("createdAt", direction=admin_firestore.Query.DESCENDING)
            .limit(1)
            .stream()
        )
        if not docs:
            return None
        
        doc = docs[0]
        data = doc.to_dict() or {}
        message_role = data.get("role")
        message_content = data.get("message", "")
        
        # Convert to Agents SDK format
        if message_role == "user":
            item = {"role": "user", "content": message_content}
        elif message_role == "assistant":
            item = {"role": "assistant", "content": message_content}
        else:
            return None
        
        # Delete the document
        doc.reference.delete()
        return item

    async def clear_session(self) -> None:
        """Clear all items for this session."""
        docs = list(self._messages_collection.stream())
        batch = self.client.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()


