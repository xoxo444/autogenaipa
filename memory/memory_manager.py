from typing import List, Dict, Any, Optional
from memory.vector_store import VectorStore


class MemoryManager:
    """
    Long-term memory manager for the assistant.

    Handles:
    - Storing memories
    - Semantic retrieval
    - Future memory management
    """

    def __init__(self):
        print("Initializing Memory Manager...")

        self.store = VectorStore()

        print("Memory Manager Ready!")

    def remember(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Save a new memory.
        """

        if not text or not text.strip():
            return

        self.store.add(
            text=text.strip(),
            metadata=metadata or {},
        )

    def recall(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories.
        """

        if not query.strip():
            return []

        memories = self.store.search(
            query=query,
            k=k,
        )

        return memories

    def remember_user_fact(self, fact: str):
        """
        Save a user-specific fact.
        """

        self.remember(
            text=fact,
            metadata={
                "type": "user_fact"
            }
        )

    def remember_conversation(self, message: str):
        """
        Save a conversation message.
        """

        self.remember(
            text=message,
            metadata={
                "type": "conversation"
            }
        )

    def search_user_memories(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve only user facts.
        """

        memories = self.recall(query, k * 2)

        return [
            memory
            for memory in memories
            if memory["metadata"].get("type") == "user_fact"
        ][:k]

    def get_all_memories(self) -> List[Dict[str, Any]]:
        """
        Return every stored memory.
        """

        return self.store.metadata

    def clear(self):
        """
        Clear all memories.
        """

        self.store.metadata.clear()

        self.store.index.reset()

        self.store.save()

    def memory_count(self) -> int:
        """
        Total number of memories.
        """

        return len(self.store.metadata)