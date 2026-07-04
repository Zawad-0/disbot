from __future__ import annotations

from collections import defaultdict, deque


class ConversationMemory:
    def __init__(self, max_messages: int = 8) -> None:
        self._max_messages = max_messages
        self._messages = defaultdict(lambda: deque(maxlen=max_messages))

    def add(self, user_id: str, role: str, content: str) -> None:
        self._messages[user_id].append({"role": role, "content": content})

    def history(self, user_id: str) -> list[dict]:
        return list(self._messages[user_id])

