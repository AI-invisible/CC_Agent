"""
Session and context management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import time


@dataclass
class Message:
    """Message object in conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = field(default_factory=lambda: time.time())
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.tool_results:
            data["tool_results"] = self.tool_results
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary"""
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", time.time()),
            tool_calls=data.get("tool_calls"),
            tool_results=data.get("tool_results"),
            metadata=data.get("metadata", {})
        )

    def to_langchain_message(self) -> Dict[str, Any]:
        """Convert to LangChain message format"""
        message = {
            "role": self.role,
            "content": self.content
        }
        if self.tool_calls:
            message["tool_calls"] = self.tool_calls
        if self.tool_results:
            message["tool_results"] = self.tool_results
        return message


@dataclass
class SessionContext:
    """Session context for managing conversation state"""

    session_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())

    def add_message(self, message: Message) -> None:
        """
        Add message to context

        Args:
            message: Message to add
        """
        self.messages.append(message)
        self.updated_at = time.time()

    def add_user_message(self, content: str, **kwargs) -> Message:
        """
        Add user message

        Args:
            content: Message content
            **kwargs: Additional message metadata

        Returns:
            Message: Created message
        """
        message = Message(role="user", content=content, metadata=kwargs)
        self.add_message(message)
        return message

    def add_assistant_message(self, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Message:
        """
        Add assistant message

        Args:
            content: Message content
            tool_calls: Tool calls made
            **kwargs: Additional message metadata

        Returns:
            Message: Created message
        """
        message = Message(role="assistant", content=content, tool_calls=tool_calls, metadata=kwargs)
        self.add_message(message)
        return message

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """
        Get most recent messages

        Args:
            limit: Number of messages to retrieve

        Returns:
            List[Message]: Recent messages
        """
        return self.messages[-limit:]

    def get_messages_for_llm(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages formatted for LLM

        Args:
            limit: Optional limit on number of messages

        Returns:
            List[Dict[str, Any]]: Messages in LLM format
        """
        messages = self.get_recent_messages(limit) if limit else self.messages
        return [msg.to_langchain_message() for msg in messages]

    def summarize_context(self) -> str:
        """
        Summarize conversation context

        Returns:
            str: Context summary
        """
        if not self.messages:
            return "Empty conversation"

        # Count message types
        user_msgs = sum(1 for m in self.messages if m.role == "user")
        assistant_msgs = sum(1 for m in self.messages if m.role == "assistant")
        tool_calls = sum(1 for m in self.messages if m.tool_calls)

        summary = f"Conversation with {len(self.messages)} messages: "
        summary += f"{user_msgs} user, {assistant_msgs} assistant, "
        summary += f"{tool_calls} messages with tool calls. "

        # Get last user message
        last_user_msg = None
        for msg in reversed(self.messages):
            if msg.role == "user":
                last_user_msg = msg
                break

        if last_user_msg:
            summary += f"Last user input: {last_user_msg.content[:100]}..."

        return summary

    def clear_messages(self) -> None:
        """Clear all messages"""
        self.messages.clear()
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionContext':
        """Create from dictionary"""
        return cls(
            session_id=data["session_id"],
            messages=[Message.from_dict(msg) for msg in data.get("messages", [])],
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )


class SessionManager:
    """Manager for multiple sessions"""

    def __init__(self):
        """Initialize session manager"""
        self._sessions: Dict[str, SessionContext] = {}

    def create_session(self, session_id: Optional[str] = None) -> SessionContext:
        """
        Create a new session

        Args:
            session_id: Optional session ID (auto-generated if not provided)

        Returns:
            SessionContext: Created session
        """
        if not session_id:
            session_id = f"session_{int(time.time() * 1000)}"

        session = SessionContext(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get session by ID

        Args:
            session_id: Session ID

        Returns:
            SessionContext: Session or None if not found
        """
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session

        Args:
            session_id: Session ID

        Returns:
            bool: True if session was deleted
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> List[str]:
        """
        List all session IDs

        Returns:
            List[str]: Session IDs
        """
        return list(self._sessions.keys())

    def clear_all(self) -> None:
        """Clear all sessions"""
        self._sessions.clear()

    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self._sessions)

    def __contains__(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self._sessions

    def __len__(self) -> int:
        """Get number of sessions"""
        return len(self._sessions)