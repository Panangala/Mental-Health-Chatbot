from src.sentiment.analyzer import SentimentAnalyzer
from src.emotion_classifier import EmotionClassifier
from src.response_generation.t5_response_generator import T5ResponseGenerator
from src.chatbot.crisis_handler import CrisisHandler
from src.database.user_manager import UserManager

class HybridMentalHealthChatbot:
    def __init__(self, db_path='database/chatbot.db'):
        self.emotion_classifier = EmotionClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.t5_generator = T5ResponseGenerator('models/t5_finetuned_model')
        self.crisis_handler = CrisisHandler()
        self.user_manager = UserManager(db_path)
        
        print("✅ Hybrid Mental Health Chatbot initialized with T5 context-awareness")
    
    def _extract_topic(self, user_message):
        """Extract the main topic from user message"""
        message_lower = user_message.lower()
        
        topic_keywords = {
            'exam': ['exam', 'test', 'quiz', 'midterm', 'final', 'exam score', 'studied'],
            'job': ['job', 'work', 'interview', 'boss', 'colleague', 'promotion', 'fired', 'resign', 'workplace'],
            'relationship': ['girlfriend', 'boyfriend', 'wife', 'husband', 'partner', 'spouse', 'dating', 'breakup', 'relationship'],
            'family': ['mom', 'dad', 'parent', 'mother', 'father', 'sibling', 'brother', 'sister', 'family'],
            'health': ['sick', 'illness', 'disease', 'pain', 'hurt', 'doctor', 'hospital', 'health'],
            'money': ['money', 'debt', 'financial', 'broke', 'bills', 'rent', 'mortgage'],
            'social': ['friends', 'friend', 'lonely', 'alone', 'social', 'people', 'community'],
            'school': ['school', 'class', 'grade', 'teacher', 'homework', 'assignment'],
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return topic
        
        return 'general'
    
    def _match_emotion_precisely(self, detected_emotion, user_message):
        """Match emotion precisely to what user said"""
        message_lower = user_message.lower()
        
        if 'anxious' in message_lower or 'anxiety' in message_lower:
            return 'anxiety'
        if 'sad' in message_lower or 'sadness' in message_lower or 'depressed' in message_lower:
            return 'sadness'
        if 'angry' in message_lower or 'frustrated' in message_lower:
            return 'anger'
        if 'scared' in message_lower or 'afraid' in message_lower or 'fear' in message_lower:
            return 'fear'
        if 'happy' in message_lower or 'great' in message_lower or 'excited' in message_lower:
            return 'joy'
        
        return detected_emotion or 'neutral'
    
    def process_user_message(self, user_id, user_message):
        """
        Process user message with:
        1. Emotion classification
        2. Sentiment analysis
        3. Crisis detection
        4. T5 generation with context awareness
        5. Database storage
        """
        
        print(f"\n{'='*60}")
        print(f"📝 User ({user_id}): {user_message}")
        print(f"{'='*60}")
        
        # Step 1: Analyze emotion
        emotion_result = self.emotion_classifier.classify_emotion(user_message)
        detected_emotion = emotion_result['primary_emotion']
        print(f"😊 Emotion: {detected_emotion} (confidence: {emotion_result['confidence']:.2f})")
        
        # Step 2: Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze_sentiment(user_message)
        sentiment_score = sentiment['combined_sentiment_score']
        print(f"📊 Sentiment: {sentiment_score:.2f}")
        
        # Step 3: Extract topic and match emotion precisely
        topic = self._extract_topic(user_message)
        precise_emotion = self._match_emotion_precisely(detected_emotion, user_message)
        print(f"🎯 Topic: {topic}")
        print(f"📌 Precise Emotion: {precise_emotion}")
        
        # Step 4: Check for crisis
        is_crisis, crisis_response = self.crisis_handler.get_crisis_response(user_message, sentiment_score)
        print(f"🚨 Crisis: {is_crisis}")
        
        # Step 5: Generate response
        if is_crisis:
            response = crisis_response
            print(f"⚠️ Crisis response triggered")
        else:
            # Use T5 with context awareness
            response = self.t5_generator.generate_response(
                user_input=user_message,
                emotion=precise_emotion,
                topic=topic,
                context_details=None,
                max_length=150
            )
        
        # Step 6: Save to database
        self.user_manager.save_conversation(
            user_id,
            user_message,
            response,
            emotion_result,
            sentiment
        )
        
        print(f"\n🤖 Bot Response:\n{response}")
        print(f"{'='*60}\n")
        
        return {
            'response': response,
            'emotion': precise_emotion,
            'emotion_confidence': emotion_result['confidence'],
            'sentiment': sentiment,
            'is_crisis': is_crisis
        }
    
    def get_user_summary(self, user_id):
        """Get user summary for dashboard"""
        context = self.user_manager.get_user_context(user_id)
        
        emotion_dist = context.get('emotion_distribution', {})
        primary_emotion = max(emotion_dist, key=emotion_dist.get) if emotion_dist else 'unknown'
        
        return {
            'primary_emotion': primary_emotion,
            'average_sentiment': context.get('average_sentiment', 0),
            'total_conversations': context.get('conversation_count', 0),
            'crisis_incidents': context.get('crisis_incidents', 0),
            'emotion_distribution': emotion_dist
        }