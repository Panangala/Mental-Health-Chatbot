"""
Sentiment Analysis Module
Handles emotion detection and sentiment scoring using multiple approaches
"""

import logging
from typing import Dict, Tuple, List
from enum import Enum

from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from datetime import datetime, timezone 

logger = logging.getLogger(__name__)


class EmotionCategory(Enum):
    """Emotion categories for mental health context"""
    VERY_NEGATIVE = "very_negative"      # Severe distress
    NEGATIVE = "negative"                # Anxiety, sadness
    SLIGHTLY_NEGATIVE = "slightly_negative"  # Mild concern
    NEUTRAL = "neutral"                 # Balanced, stable
    SLIGHTLY_POSITIVE = "slightly_positive"  # Optimism, hope
    POSITIVE = "positive"               # Good mood, well-being
    VERY_POSITIVE = "very_positive"     # Elation, joy


class CrisisSeverity(Enum):
    """Crisis severity levels"""
    CRITICAL = "critical"              # Immediate danger
    HIGH = "high"                       # Significant risk
    MODERATE = "moderate"              # Concerning but managed
    NONE = "none"                       # No crisis


class MentalHealthKeywords:
    """Keywords associated with mental health states"""
    
    # CRITICAL: Immediate intervention required
    CRISIS_PHRASES = [
        "i want to hurt myself",
        "i want to die",
        "i'm suicidal",
        "i am suicidal",
        "suicidal thoughts",
        "suicide",
        "kill myself",
        "end my life",
        "no point living",
        "life not worth living",
        "better off dead",
        "don't want to live",
        "wish i was dead"
    ]
    
    # CRITICAL: Self-harm indicators
    SELF_HARM_KEYWORDS = [
        "cutting myself",
        "self-harm",
        "self harm",
        "overdose",
        "hanging",
        "jumping off",
        "drowning",
        "slitting wrists",
        "razor blade",
        "cutting",
        "harming myself",
        "hurt myself"
    ]
    
    # MODERATE: Stress and anxiety indicators
    STRESS_KEYWORDS = [
        "stressed", "anxious", "anxiety", "worried", "nervous",
        "overwhelmed", "panic", "panicking", "afraid", "scared", "tension",
        "tense", "uneasy", "agitated", "frantic"
    ]
    
    # MODERATE: Depression indicators
    DEPRESSION_KEYWORDS = [
        "depressed", "depression", "sad", "sadness", "unhappy",
        "hopeless", "hopelessness", "worthless", "empty", "meaningless", "lost",
        "gloomy", "melancholy", "miserable", "down", "low"
    ]
    
    # LOW: Positive indicators
    POSITIVE_KEYWORDS = [
        "happy", "joyful", "good", "great", "wonderful", "amazing",
        "grateful", "blessed", "hopeful", "confident", "peaceful",
        "excited", "proud", "loved", "supported"
    ]


class SentimentAnalyzer:
    """
    Sentiment analysis engine for detecting emotions in user messages.
    Uses multiple approaches for robust sentiment detection.
    """
    
    def __init__(self):
        """Initialize sentiment analyzer with VADER"""
        self.vader = SentimentIntensityAnalyzer()
        logger.info("Sentiment analyzer initialized")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Comprehensive sentiment analysis of user input.
        
        Args:
            text (str): User's input text
        
        Returns:
            Dict: Sentiment analysis results including scores and emotional state
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid input for sentiment analysis")
            return self._get_default_sentiment()
        
        # Normalize text
        text_lower = text.lower().strip()
        
        # Check for crisis indicators (CRITICAL)
        crisis_detected, crisis_severity = self._detect_crisis_indicators(text_lower)
        
        # VADER sentiment analysis
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment analysis
        textblob_analysis = TextBlob(text)
        textblob_polarity = textblob_analysis.sentiment.polarity
        
        # Combine scores
        combined_score = self._combine_sentiment_scores(vader_scores, textblob_polarity)
        
        # Detect specific mental health states
        mental_state = self._detect_mental_state(text_lower)
        
        # Determine emotion category
        emotion_category = self._categorize_emotion(combined_score)
        
        return {
            'raw_text': text,
            'text_normalized': text_lower,
            'vader_scores': vader_scores,
            'textblob_polarity': textblob_polarity,
            'combined_sentiment_score': combined_score,
            'emotion_category': emotion_category.value,
            'emotion_intensity': self._get_emotion_intensity(combined_score),
            'mental_state_detected': mental_state,
            'crisis_detected': crisis_detected,
            'crisis_severity': crisis_severity.value,
            'analysis_timestamp': self._get_timestamp()
        }
    
    def _detect_crisis_indicators(self, text: str) -> Tuple[bool, CrisisSeverity]:
        """
        Detect crisis phrases indicating severe distress or self-harm intent.
        
        Args:
            text (str): Normalized text (lowercase)
        
        Returns:
            Tuple[bool, CrisisSeverity]: Whether crisis detected and severity level
        """
        if not text:
            return False, CrisisSeverity.NONE
        
        # Check for crisis phrases (CRITICAL severity)
        for phrase in MentalHealthKeywords.CRISIS_PHRASES:
            if phrase in text:
                logger.warning(f"🚨 CRISIS INDICATOR DETECTED: '{phrase}' in text: {text}")
                return True, CrisisSeverity.CRITICAL
        
        # Check for self-harm keywords (CRITICAL severity)
        for keyword in MentalHealthKeywords.SELF_HARM_KEYWORDS:
            if keyword in text:
                logger.warning(f"🚨 SELF-HARM INDICATOR DETECTED: '{keyword}' in text: {text}")
                return True, CrisisSeverity.CRITICAL
        
        # No crisis detected
        return False, CrisisSeverity.NONE
    
    def _detect_mental_state(self, text: str) -> Dict[str, bool]:
        """
        Detect specific mental health states from text.
        Improved to avoid false matches by requiring word boundaries.
        
        Args:
            text (str): Normalized text (lowercase)
        
        Returns:
            Dict: Detected mental states
        """
        import re
        
        def has_keyword(text: str, keywords: List[str]) -> bool:
            """Check if any keyword appears in text (word boundary aware)"""
            for kw in keywords:
                # Use word boundary for better matching
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text):
                    return True
            return False
        
        states = {
            'stress_indicators': has_keyword(text, MentalHealthKeywords.STRESS_KEYWORDS),
            'depression_indicators': has_keyword(text, MentalHealthKeywords.DEPRESSION_KEYWORDS),
            'positive_indicators': has_keyword(text, MentalHealthKeywords.POSITIVE_KEYWORDS),
            'self_harm_indicators': any(kw in text for kw in MentalHealthKeywords.SELF_HARM_KEYWORDS)
        }
        return states
    
    def _combine_sentiment_scores(self, vader_scores: Dict, textblob_polarity: float) -> float:
        """
        Combine multiple sentiment scores for robust analysis.
        
        Args:
            vader_scores (Dict): VADER sentiment scores
            textblob_polarity (float): TextBlob polarity score
        
        Returns:
            float: Combined sentiment score [-1, 1]
        """
        # VADER compound score (normalized to -1, 1)
        vader_compound = vader_scores.get('compound', 0)
        
        # TextBlob polarity is already in [-1, 1]
        textblob_score = textblob_polarity
        
        # Weighted average (VADER 60%, TextBlob 40%)
        combined = (vader_compound * 0.6) + (textblob_score * 0.4)
        
        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, combined))
    
    def _categorize_emotion(self, sentiment_score: float) -> EmotionCategory:
        """
        Categorize sentiment score into emotion categories.
        
        Args:
            sentiment_score (float): Combined sentiment score [-1, 1]
        
        Returns:
            EmotionCategory: Categorized emotion
        """
        if sentiment_score <= -0.75:
            return EmotionCategory.VERY_NEGATIVE
        elif sentiment_score <= -0.25:
            return EmotionCategory.NEGATIVE
        elif sentiment_score <= -0.05:
            return EmotionCategory.SLIGHTLY_NEGATIVE
        elif sentiment_score <= 0.05:
            return EmotionCategory.NEUTRAL
        elif sentiment_score <= 0.25:
            return EmotionCategory.SLIGHTLY_POSITIVE
        elif sentiment_score <= 0.75:
            return EmotionCategory.POSITIVE
        else:
            return EmotionCategory.VERY_POSITIVE
    
    def _get_emotion_intensity(self, sentiment_score: float) -> float:
        """
        Calculate emotion intensity (0-1 scale).
        
        Args:
            sentiment_score (float): Sentiment score
        
        Returns:
            float: Intensity score 0-1
        """
        return abs(sentiment_score)
    
    def _get_default_sentiment(self) -> Dict:
        """Return default sentiment analysis result"""
        return {
            'raw_text': '',
            'text_normalized': '',
            'vader_scores': {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0},
            'textblob_polarity': 0,
            'combined_sentiment_score': 0,
            'emotion_category': EmotionCategory.NEUTRAL.value,
            'emotion_intensity': 0,
            'mental_state_detected': {
                'stress_indicators': False,
                'depression_indicators': False,
                'positive_indicators': False,
                'self_harm_indicators': False
            },
            'crisis_detected': False,
            'crisis_severity': CrisisSeverity.NONE.value,
            'analysis_timestamp': self._get_timestamp()
        }
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def compare_sentiments(self, text1: str, text2: str) -> Dict:
        """
        Compare sentiment between two texts (e.g., pre and post-chat).
        
        Args:
            text1 (str): First text (pre-chat)
            text2 (str): Second text (post-chat)
        
        Returns:
            Dict: Comparison results including change metrics
        """
        analysis1 = self.analyze_sentiment(text1)
        analysis2 = self.analyze_sentiment(text2)
        
        sentiment_change = analysis2['combined_sentiment_score'] - analysis1['combined_sentiment_score']
        
        return {
            'pre_sentiment': analysis1,
            'post_sentiment': analysis2,
            'sentiment_change': sentiment_change,
            'improved': sentiment_change > 0.1,
            'degraded': sentiment_change < -0.1,
            'stable': -0.1 <= sentiment_change <= 0.1
        }


# Module-level instance for reuse
_sentiment_analyzer = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create sentiment analyzer instance"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer