"""
Unit tests for Sentiment Analysis module
Tests sentiment detection, emotion categorization, and crisis detection
"""

import unittest
from src.sentiment.analyzer import (
    SentimentAnalyzer,
    EmotionCategory,
    MentalHealthKeywords,
    get_sentiment_analyzer
)


class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for SentimentAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = SentimentAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer.vader)
    
    def test_positive_sentiment(self):
        """Test detection of positive sentiment"""
        result = self.analyzer.analyze_sentiment("I feel great and happy today!")
        self.assertGreater(result['combined_sentiment_score'], 0)
        self.assertIn(result['emotion_category'], [
            EmotionCategory.POSITIVE.value,
            EmotionCategory.VERY_POSITIVE.value
        ])
    
    def test_negative_sentiment(self):
        """Test detection of negative sentiment"""
        result = self.analyzer.analyze_sentiment("I feel terrible and sad")
        self.assertLess(result['combined_sentiment_score'], 0)
        self.assertIn(result['emotion_category'], [
            EmotionCategory.NEGATIVE.value,
            EmotionCategory.VERY_NEGATIVE.value
        ])
    
    def test_neutral_sentiment(self):
        """Test detection of neutral sentiment"""
        result = self.analyzer.analyze_sentiment("The weather is cloudy")
        self.assertEqual(result['emotion_category'], EmotionCategory.NEUTRAL.value)
    
    def test_crisis_detection_suicide_phrase(self):
        """Test detection of suicide-related phrases"""
        result = self.analyzer.analyze_sentiment("I want to kill myself")
        self.assertTrue(result['crisis_detected'])
    
    def test_crisis_detection_self_harm(self):
        """Test detection of self-harm phrases"""
        result = self.analyzer.analyze_sentiment("I'm cutting myself")
        self.assertTrue(result['crisis_detected'])
    
    def test_stress_detection(self):
        """Test detection of stress indicators"""
        result = self.analyzer.analyze_sentiment("I'm feeling anxious and overwhelmed")
        self.assertTrue(result['mental_state_detected']['stress_indicators'])
    
    def test_depression_detection(self):
        """Test detection of depression indicators"""
        result = self.analyzer.analyze_sentiment("I feel hopeless and empty")
        self.assertTrue(result['mental_state_detected']['depression_indicators'])
    
    def test_sentiment_comparison_improvement(self):
        """Test sentiment comparison showing improvement"""
        pre_chat = "I feel terrible and hopeless"
        post_chat = "I feel a bit better now, thank you for listening"
        
        comparison = self.analyzer.compare_sentiments(pre_chat, post_chat)
        self.assertTrue(comparison['improved'])
        self.assertGreater(comparison['sentiment_change'], 0)
    
    def test_sentiment_comparison_degradation(self):
        """Test sentiment comparison showing degradation"""
        pre_chat = "I'm doing okay today"
        post_chat = "Actually, I feel worse now"
        
        comparison = self.analyzer.compare_sentiments(pre_chat, post_chat)
        self.assertTrue(comparison['degraded'])
        self.assertLess(comparison['sentiment_change'], 0)
    
    def test_empty_input(self):
        """Test handling of empty input"""
        result = self.analyzer.analyze_sentiment("")
        self.assertIsNotNone(result)
        self.assertEqual(result['emotion_category'], EmotionCategory.NEUTRAL.value)
    
    def test_none_input(self):
        """Test handling of None input"""
        result = self.analyzer.analyze_sentiment(None)
        self.assertIsNotNone(result)
        self.assertEqual(result['emotion_category'], EmotionCategory.NEUTRAL.value)
    
    def test_emotion_intensity(self):
        """Test emotion intensity calculation"""
        positive = self.analyzer.analyze_sentiment("I'm very happy!!!")
        negative = self.analyzer.analyze_sentiment("I'm very sad...")
        
        self.assertGreater(positive['emotion_intensity'], 0.5)
        self.assertGreater(negative['emotion_intensity'], 0.2)
    
    def test_analyze_sentiment_returns_all_fields(self):
        """Test that sentiment analysis returns all expected fields"""
        result = self.analyzer.analyze_sentiment("Test message")
        
        expected_fields = [
            'raw_text', 'text_normalized', 'vader_scores', 'textblob_polarity',
            'combined_sentiment_score', 'emotion_category', 'emotion_intensity',
            'mental_state_detected', 'crisis_detected', 'analysis_timestamp'
        ]
        
        for field in expected_fields:
            self.assertIn(field, result)
    
    def test_long_text_analysis(self):
        """Test analysis of longer text"""
        long_text = """
        I've been struggling with anxiety lately. Some days are really hard,
        but I'm trying to manage it. I've been having therapy sessions which help.
        I still feel stressed about work, but I'm trying to stay positive.
        """
        result = self.analyzer.analyze_sentiment(long_text)
        self.assertIsNotNone(result['combined_sentiment_score'])
        self.assertTrue(result['mental_state_detected']['stress_indicators'])
    
    def test_special_characters_handling(self):
        """Test handling of special characters and emojis"""
        text = "I'm happy!!! 😊 Things are going great!! 🎉"
        result = self.analyzer.analyze_sentiment(text)
        self.assertIsNotNone(result['combined_sentiment_score'])
    
    def test_get_sentiment_analyzer_singleton(self):
        """Test that get_sentiment_analyzer returns singleton"""
        analyzer1 = get_sentiment_analyzer()
        analyzer2 = get_sentiment_analyzer()
        self.assertIs(analyzer1, analyzer2)


class TestEmotionCategorization(unittest.TestCase):
    """Test emotion categorization logic"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_categorize_very_negative(self):
        """Test very negative emotion categorization"""
        category = self.analyzer._categorize_emotion(-0.9)
        self.assertEqual(category, EmotionCategory.VERY_NEGATIVE)
    
    def test_categorize_negative(self):
        """Test negative emotion categorization"""
        category = self.analyzer._categorize_emotion(-0.5)
        self.assertEqual(category, EmotionCategory.NEGATIVE)
    
    def test_categorize_slightly_negative(self):
        """Test slightly negative emotion categorization"""
        category = self.analyzer._categorize_emotion(-0.1)
        self.assertEqual(category, EmotionCategory.SLIGHTLY_NEGATIVE)
    
    def test_categorize_neutral(self):
        """Test neutral emotion categorization"""
        category = self.analyzer._categorize_emotion(0)
        self.assertEqual(category, EmotionCategory.NEUTRAL)
    
    def test_categorize_slightly_positive(self):
        """Test slightly positive emotion categorization"""
        category = self.analyzer._categorize_emotion(0.1)
        self.assertEqual(category, EmotionCategory.SLIGHTLY_POSITIVE)
    
    def test_categorize_positive(self):
        """Test positive emotion categorization"""
        category = self.analyzer._categorize_emotion(0.5)
        self.assertEqual(category, EmotionCategory.POSITIVE)
    
    def test_categorize_very_positive(self):
        """Test very positive emotion categorization"""
        category = self.analyzer._categorize_emotion(0.9)
        self.assertEqual(category, EmotionCategory.VERY_POSITIVE)


class TestMentalHealthKeywords(unittest.TestCase):
    """Test mental health keyword definitions"""
    
    def test_crisis_phrases_not_empty(self):
        """Test that crisis phrases are defined"""
        self.assertGreater(len(MentalHealthKeywords.CRISIS_PHRASES), 0)
    
    def test_stress_keywords_not_empty(self):
        """Test that stress keywords are defined"""
        self.assertGreater(len(MentalHealthKeywords.STRESS_KEYWORDS), 0)
    
    def test_depression_keywords_not_empty(self):
        """Test that depression keywords are defined"""
        self.assertGreater(len(MentalHealthKeywords.DEPRESSION_KEYWORDS), 0)
    
    def test_positive_keywords_not_empty(self):
        """Test that positive keywords are defined"""
        self.assertGreater(len(MentalHealthKeywords.POSITIVE_KEYWORDS), 0)


if __name__ == '__main__':
    unittest.main()