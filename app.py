from flask import Flask, request, jsonify
from flask_cors import CORS
from src.hybrid_chatbot import HybridMentalHealthChatbot
import uuid
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key-change-this'

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    chatbot = HybridMentalHealthChatbot()
    
    # Generate JWT token
    def generate_token(user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    # Verify JWT token
    def verify_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload['user_id']
        except:
            return None
    
    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            data = request.json or {}
            email = data.get('email', 'user')
            
            user_id = f"{email}_{uuid.uuid4().hex[:8]}"
            token = generate_token(user_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'token': token,
                    'user': {
                        'user_id': user_id,
                        'email': email
                    }
                },
                'message': 'Login successful'
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    def register():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            data = request.json or {}
            email = data.get('email')
            username = data.get('username')
            
            if not email or not username:
                return jsonify({'success': False, 'error': 'Missing fields'}), 400
            
            user_id = f"{username}_{uuid.uuid4().hex[:8]}"
            
            return jsonify({
                'success': True,
                'data': {
                    'user_id': user_id,
                    'email': email,
                    'username': username
                },
                'message': 'Registration successful'
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/chat/session/create', methods=['POST', 'OPTIONS'])
    def create_session():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '') if auth_header else None
            
            user_id = verify_token(token) if token else None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            session_id = str(uuid.uuid4())
            
            return jsonify({
                'success': True,
                'data': {
                    'session_id': session_id,
                    'user_id': user_id
                }
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/chat/session/start', methods=['POST', 'OPTIONS'])
    def start_chat_session():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '') if auth_header else None
            
            user_id = verify_token(token) if token else None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.json or {}
            initial_emotion = data.get('emotion', 'neutral')
            initial_sentiment = data.get('sentiment_score', 0)
            
            session_id = chatbot.user_manager.start_chat_session(
                user_id, 
                initial_emotion, 
                initial_sentiment
            )
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'initial_emotion': initial_emotion,
                'initial_sentiment': initial_sentiment
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/chat/session/end/<int:session_id>', methods=['POST', 'OPTIONS'])
    def end_chat_session(session_id):
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '') if auth_header else None
            
            user_id = verify_token(token) if token else None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.json or {}
            final_emotion = data.get('emotion', 'neutral')
            final_sentiment = data.get('sentiment_score', 0)
            
            improvement = chatbot.user_manager.end_chat_session(
                session_id,
                final_emotion,
                final_sentiment
            )
            
            return jsonify({
                'success': True,
                'improvement': improvement
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/chat/message', methods=['POST', 'OPTIONS'])
    def chat_message():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '') if auth_header else None
            
            user_id = verify_token(token) if token else None
            
            if not user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            data = request.json or {}
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({'success': False, 'error': 'Empty message'}), 400
            
            result = chatbot.process_user_message(user_id, message)
            
            return jsonify({
                'success': True,
                'response': result['response'],
                'analysis': {
                    'primary_emotion': result['emotion'],
                    'emotion_confidence': result['emotion_confidence'],
                    'sentiment_score': result['sentiment']['combined_sentiment_score'],
                    'is_crisis': result['is_crisis']
                }
            }), 200
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/user/<user_id>/sessions', methods=['GET'])
    def user_sessions(user_id):
        try:
            limit = request.args.get('limit', 10, type=int)
            sessions = chatbot.user_manager.get_session_history(user_id, limit)
            
            return jsonify({
                'success': True,
                'sessions': sessions
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/user/<user_id>/improvement-stats', methods=['GET'])
    def improvement_stats(user_id):
        try:
            stats = chatbot.user_manager.get_mood_improvement_stats(user_id)
            
            return jsonify({
                'success': True,
                'stats': stats
            }), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/user/<user_id>/summary', methods=['GET'])
    def user_summary(user_id):
        try:
            summary = chatbot.get_user_summary(user_id)
            
            return jsonify({
                'user_id': user_id,
                'summary': summary
            }), 200
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/<user_id>/history', methods=['GET'])
    def user_history(user_id):
        try:
            limit = request.args.get('limit', 10, type=int)
            history = chatbot.user_manager.get_user_history(user_id, limit)
            
            return jsonify({
                'user_id': user_id,
                'history': history
            }), 200
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/<user_id>/mood-trends', methods=['GET'])
    def mood_trends(user_id):
        try:
            limit = request.args.get('limit', 20, type=int)
            trends = chatbot.user_manager.get_mood_trends(user_id, limit)
            
            return jsonify({
                'user_id': user_id,
                'trends': trends
            }), 200
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'}), 200
    
    @app.route('/health', methods=['GET'])
    def health_root():
        return jsonify({'status': 'ok'}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)