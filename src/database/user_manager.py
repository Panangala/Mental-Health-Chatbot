import sqlite3
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional

class UserManager:
    def __init__(self, db_path='database/chatbot.db'):
        # Use absolute path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(project_root, db_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Initialize database if not exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    created_at TEXT,
                    total_conversations INT DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    emotion TEXT,
                    emotion_confidence REAL,
                    sentiment_score REAL,
                    is_crisis INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    emotion TEXT,
                    sentiment_score REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_start TEXT NOT NULL,
                    session_end TEXT,
                    initial_emotion TEXT,
                    initial_sentiment REAL,
                    final_emotion TEXT,
                    final_sentiment REAL,
                    mood_improvement REAL,
                    message_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✓ Database initialized at: {self.db_path}")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def create_user(self, user_id):
        """Create new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now(timezone.utc).isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, created_at)
                VALUES (?, ?)
            ''', (user_id, timestamp))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def save_conversation(self, user_id, user_message, bot_response, emotion_result, sentiment):
        """Save conversation with emotion and sentiment data"""
        try:
            self.create_user(user_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now(timezone.utc).isoformat()
            is_crisis = 1 if sentiment.get('crisis_detected', False) else 0
            
            cursor.execute('''
                INSERT INTO conversations 
                (user_id, user_message, bot_response, emotion, emotion_confidence, 
                 sentiment_score, is_crisis, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_message,
                bot_response,
                emotion_result['primary_emotion'],
                emotion_result['confidence'],
                sentiment['combined_sentiment_score'],
                is_crisis,
                timestamp
            ))
            
            cursor.execute('''
                INSERT INTO mood_tracking (user_id, emotion, sentiment_score, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                emotion_result['primary_emotion'],
                sentiment['combined_sentiment_score'],
                timestamp
            ))
            
            cursor.execute(
                'UPDATE users SET total_conversations = total_conversations + 1 WHERE user_id = ?',
                (user_id,)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_user_history(self, user_id, limit=10):
        """Get user conversation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, bot_response, emotion, sentiment_score, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            conversations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return conversations
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return []
    
    def get_mood_trends(self, user_id, limit=20):
        """Get user mood trends over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT emotion, sentiment_score, timestamp
                FROM mood_tracking
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            moods = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return moods
        except Exception as e:
            print(f"Error retrieving mood trends: {e}")
            return []
    
    def get_emotion_distribution(self, user_id, limit=50):
        """Get emotion distribution for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT emotion, COUNT(*) as count
                FROM mood_tracking
                WHERE user_id = ?
                GROUP BY emotion
                ORDER BY count DESC
                LIMIT ?
            ''', (user_id, limit))
            
            distribution = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            return distribution
        except Exception as e:
            print(f"Error getting emotion distribution: {e}")
            return {}
    
    def get_average_sentiment(self, user_id, limit=50):
        """Get average sentiment score for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT AVG(sentiment_score) as avg_sentiment
                FROM mood_tracking
                WHERE user_id = ?
                LIMIT ?
            ''', (user_id, limit))
            
            result = cursor.fetchone()
            conn.close()
            return result[0] if result[0] else 0
        except Exception as e:
            print(f"Error getting average sentiment: {e}")
            return 0
    
    def get_crisis_count(self, user_id):
        """Get number of crisis incidents for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT COUNT(*) FROM conversations WHERE user_id = ? AND is_crisis = 1',
                (user_id,)
            )
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting crisis count: {e}")
            return 0
    
    def get_user_context(self, user_id):
        """Get comprehensive user context for personalization"""
        try:
            history = self.get_user_history(user_id, limit=5)
            trends = self.get_mood_trends(user_id, limit=10)
            emotion_dist = self.get_emotion_distribution(user_id)
            avg_sentiment = self.get_average_sentiment(user_id)
            crisis_count = self.get_crisis_count(user_id)
            
            return {
                'recent_conversations': history,
                'mood_trends': trends,
                'emotion_distribution': emotion_dist,
                'average_sentiment': avg_sentiment,
                'crisis_incidents': crisis_count,
                'conversation_count': len(history)
            }
        except Exception as e:
            print(f"Error getting user context: {e}")
            return {}
    
    def start_chat_session(self, user_id, initial_emotion, initial_sentiment):
        """Record start of chat session with initial mood"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now(timezone.utc).isoformat()
            
            cursor.execute('''
                INSERT INTO chat_sessions 
                (user_id, session_start, initial_emotion, initial_sentiment)
                VALUES (?, ?, ?, ?)
            ''', (user_id, timestamp, initial_emotion, initial_sentiment))
            
            conn.commit()
            session_id = cursor.lastrowid
            conn.close()
            
            print(f"✓ Chat session started: {session_id}")
            return session_id
        except Exception as e:
            print(f"Error starting chat session: {e}")
            return None
    
    def end_chat_session(self, session_id, final_emotion, final_sentiment):
        """Record end of chat session with final mood"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now(timezone.utc).isoformat()
            
            cursor.execute('SELECT initial_sentiment FROM chat_sessions WHERE id = ?', (session_id,))
            result = cursor.fetchone()
            
            if result:
                initial_sentiment = result[0]
                mood_improvement = final_sentiment - initial_sentiment
                
                cursor.execute('''
                    UPDATE chat_sessions 
                    SET session_end = ?, final_emotion = ?, final_sentiment = ?, mood_improvement = ?
                    WHERE id = ?
                ''', (timestamp, final_emotion, final_sentiment, mood_improvement, session_id))
                
                conn.commit()
                conn.close()
                
                print(f"✓ Chat session ended: {session_id}, Improvement: {mood_improvement:.2f}")
                
                return {
                    'improvement': mood_improvement,
                    'improved': mood_improvement > 0.1,
                    'stable': -0.1 <= mood_improvement <= 0.1,
                    'declined': mood_improvement < -0.1
                }
        except Exception as e:
            print(f"Error ending chat session: {e}")
            return None
    
    def get_session_history(self, user_id, limit=10):
        """Get user's chat session history with mood changes"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, session_start, session_end, initial_emotion, final_emotion, 
                       initial_sentiment, final_sentiment, mood_improvement, message_count
                FROM chat_sessions
                WHERE user_id = ?
                ORDER BY session_start DESC
                LIMIT ?
            ''', (user_id, limit))
            
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return sessions
        except Exception as e:
            print(f"Error retrieving session history: {e}")
            return []
    
    def get_mood_improvement_stats(self, user_id):
        """Get mood improvement statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(mood_improvement) as avg_improvement,
                    SUM(CASE WHEN mood_improvement > 0.1 THEN 1 ELSE 0 END) as improved_sessions,
                    SUM(CASE WHEN mood_improvement < -0.1 THEN 1 ELSE 0 END) as declined_sessions
                FROM chat_sessions
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            total = result[0] or 0
            improved = result[2] or 0
            
            return {
                'total_sessions': total,
                'average_improvement': result[1] or 0,
                'sessions_improved': improved,
                'sessions_declined': result[3] or 0,
                'improvement_rate': (improved / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Error getting improvement stats: {e}")
            return {}