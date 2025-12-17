"""
Emotion Classification using BERT
Advanced NLP technique for detecting user emotional states
"""

from transformers import pipeline
import logging

logger = logging.getLogger(__name__)


class EmotionClassifier:
    """
    BERT-based emotion classifier for mental health conversations
    Detects: sadness, anxiety, joy, anger, neutral, fear
    """
    
    def __init__(self):
        """Initialize emotion classification model"""
        logger.info("Loading emotion classification model...")
        try:
            # Using BERT fine-tuned on emotions (from HuggingFace)
            self.classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=3
            )
            logger.info("✓ Emotion classifier loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load emotion classifier: {e}")
            self.classifier = None
    
    def classify_emotion(self, text):
        """
        Classify emotion from user text
        
        Args:
            text (str): User message
            
        Returns:
            dict: {
                'primary_emotion': str (highest confidence),
                'confidence': float (0-1),
                'all_emotions': list of dicts with label and score,
                'is_crisis': bool (detects crisis keywords)
            }
        """
        if not self.classifier:
            return self._default_emotion()
        
        try:
            # Get emotion predictions
            predictions = self.classifier(text[:512])  # Limit to 512 chars
            
            if not predictions or not predictions[0]:
                return self._default_emotion()
            
            # Get top emotion
            top_emotions = predictions[0]
            primary = top_emotions[0]
            
            # Check for crisis indicators
            crisis_keywords = [
                'kill myself', 'suicide', 'want to die', 'no point living',
                'end it all', 'hurt myself', 'self harm', 'overdose',
                'jump', 'harm'
            ]
            is_crisis = any(keyword in text.lower() for keyword in crisis_keywords)
            
            result = {
                'primary_emotion': primary['label'],
                'confidence': round(primary['score'], 3),
                'all_emotions': [
                    {
                        'emotion': emotion['label'],
                        'confidence': round(emotion['score'], 3)
                    }
                    for emotion in top_emotions
                ],
                'is_crisis': is_crisis
            }
            
            logger.debug(f"Emotion detected: {result['primary_emotion']} ({result['confidence']})")
            return result
            
        except Exception as e:
            logger.error(f"Emotion classification error: {e}")
            return self._default_emotion()
    
    def _default_emotion(self):
        """Return default emotion structure"""
        return {
            'primary_emotion': 'neutral',
            'confidence': 0.0,
            'all_emotions': [{'emotion': 'neutral', 'confidence': 1.0}],
            'is_crisis': False
        }
    
    def get_emotion_context(self, emotion):
        """
        Get contextual response guidance based on emotion
        
        Args:
            emotion (str): Emotion label
            
        Returns:
            dict: Response guidance
        """
        emotion_context = {
            'sadness': {
                'tone': 'empathetic',
                'approach': 'validation and support',
                'keywords': ['understand', 'valid', 'support', 'help']
            },
            'anxiety': {
                'tone': 'calming',
                'approach': 'grounding and reassurance',
                'keywords': ['calm', 'manage', 'tools', 'control']
            },
            'anger': {
                'tone': 'non-judgmental',
                'approach': 'acknowledgment and channeling',
                'keywords': ['understand', 'valid', 'express', 'move forward']
            },
            'fear': {
                'tone': 'reassuring',
                'approach': 'grounding and support',
                'keywords': ['safe', 'support', 'manageable', 'together']
            },
            'joy': {
                'tone': 'positive',
                'approach': 'encouragement',
                'keywords': ['great', 'celebrate', 'continue']
            },
            'neutral': {
                'tone': 'professional',
                'approach': 'informational',
                'keywords': ['help', 'suggest', 'available']
            }
        }
        
        return emotion_context.get(emotion, emotion_context['neutral'])