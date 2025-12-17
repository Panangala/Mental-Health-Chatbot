"""
Unit Tests for Flask API
Tests all API endpoints and functionality.
"""

import unittest
import json
from app import create_app
from src.chatbot.session_manager import get_session_manager


class TestFlaskAPI(unittest.TestCase):
    """Test Flask API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.session_manager = get_session_manager()
    
    def tearDown(self):
        """Clean up after tests"""
        # Clear all sessions
        session_ids = list(self.session_manager.sessions.keys())
        for sid in session_ids:
            self.session_manager.delete_session(sid)
    
    # ===== HEALTH CHECK TESTS =====
    
    def test_health_check(self):
        """Test /health endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['status'] == 'healthy')
        self.assertIn('timestamp', data)
    
    def test_api_health(self):
        """Test /api/health endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['status'] == 'operational')
    
    # ===== SESSION CREATION TESTS =====
    
    def test_create_session(self):
        """Test creating a new session"""
        response = self.client.post('/api/session', 
            json={},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
        self.assertIn('user_id', data)
    
    def test_create_session_with_user_id(self):
        """Test creating session with custom user_id"""
        response = self.client.post('/api/session',
            json={'user_id': 'test_user_123'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['user_id'], 'test_user_123')
    
    # ===== SESSION RETRIEVAL TESTS =====
    
    def test_get_session(self):
        """Test retrieving session info"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Get session
        response = self.client.get(f'/api/session/{session_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['session']['session_id'], session_id)
    
    def test_get_nonexistent_session(self):
        """Test getting nonexistent session"""
        response = self.client.get('/api/session/nonexistent_id')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ===== CHAT TESTS =====
    
    def test_chat_basic(self):
        """Test basic chat functionality"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Send message
        response = self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'Hello, how are you?'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('response', data)
        self.assertIn('sentiment_analysis', data)
        self.assertIn('response_type', data)
    
    def test_chat_missing_session_id(self):
        """Test chat without session_id"""
        response = self.client.post('/api/chat',
            json={'message': 'Hello'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_chat_missing_message(self):
        """Test chat without message"""
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        response = self.client.post('/api/chat',
            json={'session_id': session_id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_chat_invalid_session_id(self):
        """Test chat with invalid session_id"""
        response = self.client.post('/api/chat',
            json={
                'session_id': 'invalid_session',
                'message': 'Hello'
            },
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_chat_crisis_detection(self):
        """Test crisis detection in chat"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Send crisis message
        response = self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'I want to hurt myself'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['sentiment_analysis']['crisis_detected'])
        self.assertTrue(data['requires_escalation'])
        self.assertIn('988', data['response'])
    
    def test_chat_positive_emotion(self):
        """Test positive emotion detection"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Send positive message
        response = self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'I feel great today!'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response_type'], 'POSITIVE_EMOTION')
    
    # ===== HISTORY TESTS =====
    
    def test_get_history_empty(self):
        """Test getting history for new session"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Get history
        response = self.client.get(f'/api/chat/{session_id}/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message_count'], 0)
    
    def test_get_history_with_messages(self):
        """Test getting history with messages"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Send messages
        self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'Hello'
            },
            content_type='application/json'
        )
        
        self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'How are you?'
            },
            content_type='application/json'
        )
        
        # Get history
        response = self.client.get(f'/api/chat/{session_id}/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message_count'], 4)  # 2 user + 2 assistant
        self.assertGreater(len(data['history']), 0)
    
    # ===== MOOD TESTS =====
    
    def test_get_mood_empty(self):
        """Test getting mood for new session"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Get mood
        response = self.client.get(f'/api/mood/{session_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_get_mood_with_change(self):
        """Test mood change calculation"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # Send negative message
        self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'I feel terrible'
            },
            content_type='application/json'
        )
        
        # Send positive message
        self.client.post('/api/chat',
            json={
                'session_id': session_id,
                'message': 'I feel better now'
            },
            content_type='application/json'
        )
        
        # Get mood
        response = self.client.get(f'/api/mood/{session_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        mood_change = data['mood_change']
        self.assertIn('initial_mood', mood_change)
        self.assertIn('current_mood', mood_change)
        self.assertGreater(len(data['mood_log']), 0)
    
    # ===== SESSION END TESTS =====
    
    def test_end_session(self):
        """Test ending a session"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        # End session
        response = self.client.delete(f'/api/session/{session_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_end_nonexistent_session(self):
        """Test ending nonexistent session"""
        response = self.client.delete('/api/session/nonexistent_id')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ===== STATS TESTS =====
    
    def test_get_stats(self):
        """Test getting system stats"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('active_sessions', data)
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/api/nonexistent_endpoint')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_chat_no_json_data(self):
        """Test chat with no JSON data"""
        response = self.client.post('/api/chat')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    # ===== INTEGRATION TESTS =====
    
    def test_full_conversation_flow(self):
        """Test full conversation flow"""
        # Create session
        create_response = self.client.post('/api/session',
            json={},
            content_type='application/json'
        )
        session_id = json.loads(create_response.data)['session_id']
        
        messages = [
            'I am feeling anxious',
            'The strategies help',
            'I feel better'
        ]
        
        for msg in messages:
            response = self.client.post('/api/chat',
                json={
                    'session_id': session_id,
                    'message': msg
                },
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Check session
        session_response = self.client.get(f'/api/session/{session_id}')
        session_data = json.loads(session_response.data)
        self.assertEqual(session_data['session']['message_count'], 6)  # 3 user + 3 assistant
    
    def test_multiple_sessions(self):
        """Test multiple concurrent sessions"""
        session_ids = []
        
        # Create 3 sessions
        for i in range(3):
            response = self.client.post('/api/session',
                json={},
                content_type='application/json'
            )
            session_id = json.loads(response.data)['session_id']
            session_ids.append(session_id)
        
        # Send message in each
        for sid in session_ids:
            response = self.client.post('/api/chat',
                json={
                    'session_id': sid,
                    'message': 'Hello'
                },
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Check stats
        stats_response = self.client.get('/api/stats')
        stats_data = json.loads(stats_response.data)
        self.assertEqual(stats_data['active_sessions'], 3)


if __name__ == '__main__':
    unittest.main()