"""
Session Manager Module
Handles user sessions, conversation state, and mood tracking.
"""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class UserSession:
    """Represents a user session with conversation history"""
    
    def __init__(self, session_id: str = None, user_id: str = None):
        """
        Initialize a user session.
        
        Args:
            session_id (str, optional): Custom session ID
            user_id (str, optional): User identifier
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.conversation_history = []
        self.mood_log = []
        self.initial_mood = None
        self.current_mood = None
        self.session_active = True
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """
        Add a message to the conversation history.
        
        Args:
            role (str): 'user' or 'assistant'
            content (str): Message content
            metadata (Dict, optional): Additional metadata
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        self.updated_at = datetime.now()
        logger.info(f"Message added to session {self.session_id}")
    
    def record_mood(self, mood_data: Dict):
        """
        Record mood analysis for the session.
        
        Args:
            mood_data (Dict): Mood analysis data (sentiment, emotion, etc.)
        """
        mood_entry = {
            'timestamp': datetime.now().isoformat(),
            'emotion_category': mood_data.get('emotion_category'),
            'sentiment_score': mood_data.get('combined_sentiment_score'),
            'crisis_detected': mood_data.get('crisis_detected'),
            'mental_state': mood_data.get('mental_state_detected')
        }
        self.mood_log.append(mood_entry)
        
        # Track initial and current mood
        if self.initial_mood is None:
            self.initial_mood = mood_entry
        self.current_mood = mood_entry
        
        logger.info(f"Mood recorded for session {self.session_id}: {mood_entry['emotion_category']}")
    
    def get_mood_change(self) -> Dict:
        """
        Calculate mood change from start to current.
        
        Returns:
            Dict: Mood change information
        """
        if not self.initial_mood or not self.current_mood:
            return {'change': 0, 'improved': False}
        
        initial_score = self.initial_mood.get('sentiment_score', 0)
        current_score = self.current_mood.get('sentiment_score', 0)
        change = current_score - initial_score
        
        return {
            'initial_mood': self.initial_mood['emotion_category'],
            'current_mood': self.current_mood['emotion_category'],
            'sentiment_change': change,
            'improved': change > 0,
            'messages_count': len(self.conversation_history)
        }
    
    def get_summary(self) -> Dict:
        """
        Get session summary.
        
        Returns:
            Dict: Session summary
        """
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': len(self.conversation_history),
            'mood_entries': len(self.mood_log),
            'session_active': self.session_active,
            'mood_change': self.get_mood_change()
        }
    
    def end_session(self):
        """End the session"""
        self.session_active = False
        self.updated_at = datetime.now()
        logger.info(f"Session {self.session_id} ended")


class SessionManager:
    """Manages multiple user sessions"""
    
    def __init__(self):
        """Initialize session manager"""
        self.sessions: Dict[str, UserSession] = {}
        logger.info("Session manager initialized")
    
    def create_session(self, user_id: str = None) -> UserSession:
        """
        Create a new session.
        
        Args:
            user_id (str, optional): User identifier
            
        Returns:
            UserSession: New session
        """
        session = UserSession(user_id=user_id)
        self.sessions[session.session_id] = session
        logger.info(f"Session created: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get a session by ID.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            UserSession: Session or None
        """
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: True if ended, False if not found
        """
        session = self.sessions.get(session_id)
        if session:
            session.end_session()
            logger.info(f"Session {session_id} ended by manager")
            return True
        return False
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get summaries of all active sessions.
        
        Returns:
            List[Dict]: List of session summaries
        """
        return [session.get_summary() for session in self.sessions.values() if session.session_active]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} deleted")
            return True
        return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Remove sessions older than specified hours.
        
        Args:
            max_age_hours (int): Max session age in hours
        """
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_delete = [
            sid for sid, session in self.sessions.items()
            if session.updated_at < cutoff_time
        ]
        
        for sid in to_delete:
            self.delete_session(sid)
        
        logger.info(f"Cleaned up {len(to_delete)} old sessions")


# Singleton instance
_session_manager_instance = None


def get_session_manager() -> SessionManager:
    """Get singleton instance of session manager"""
    global _session_manager_instance
    if _session_manager_instance is None:
        _session_manager_instance = SessionManager()
    return _session_manager_instance