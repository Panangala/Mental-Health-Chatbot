"""
Unit tests for NLP Preprocessing module
Tests tokenization, lemmatization, normalization, and stopword removal
"""

import unittest
from src.nlp.preprocessor import TextPreprocessor, get_text_preprocessor


class TestTextPreprocessor(unittest.TestCase):
    """Test cases for TextPreprocessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.preprocessor = TextPreprocessor()
    
    def test_tokenization(self):
        """Test text tokenization"""
        text = "I am feeling anxious"
        tokens = self.preprocessor.tokenize(text)
        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)
        self.assertIn('anxious', tokens)
    
    def test_normalization(self):
        """Test text normalization"""
        text = "  I AM Feeling ANXIOUS  "
        normalized = self.preprocessor.normalize_text(text)
        self.assertEqual(normalized, "i am feeling anxious")
    
    def test_lemmatization(self):
        """Test token lemmatization"""
        tokens = ["running", "runs", "cried", "crying"]
        lemmatized = self.preprocessor.lemmatize(tokens)
        self.assertIsInstance(lemmatized, list)
        self.assertEqual(len(lemmatized), len(tokens))
    
    def test_stopword_removal(self):
        """Test stopword removal"""
        tokens = ["i", "am", "feeling", "anxious", "today"]
        filtered = self.preprocessor.remove_stopwords(tokens)
        self.assertNotIn("i", filtered)
        self.assertNotIn("am", filtered)
        self.assertIn("feeling", filtered)
        self.assertIn("anxious", filtered)
    
    def test_preprocess_full_pipeline(self):
        """Test complete preprocessing pipeline"""
        text = "I am feeling really anxious and stressed"
        result = self.preprocessor.preprocess(text)
        
        self.assertIn('original_text', result)
        self.assertIn('normalized_text', result)
        self.assertIn('tokens', result)
        self.assertIn('lemmatized', result)
        self.assertIn('token_count', result)
        
        self.assertEqual(result['original_text'], text)
        self.assertGreater(result['token_count'], 0)
    
    def test_preprocess_with_stopword_removal(self):
        """Test preprocessing with stopword removal"""
        text = "I am feeling anxious"
        result = self.preprocessor.preprocess(text, remove_stopwords_flag=True)
        
        # Should have fewer tokens than without stopword removal
        result_without = self.preprocessor.preprocess(text, remove_stopwords_flag=False)
        self.assertLess(len(result['lemmatized']), len(result_without['lemmatized']))
    
    def test_empty_input(self):
        """Test handling of empty input"""
        result = self.preprocessor.preprocess("")
        self.assertEqual(result['token_count'], 0)
        self.assertEqual(len(result['tokens']), 0)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        text = "I'm feeling anxious!!! What should I do???"
        result = self.preprocessor.preprocess(text)
        self.assertGreater(result['token_count'], 0)


class TestPreprocessorSingleton(unittest.TestCase):
    """Test singleton pattern for preprocessor"""
    
    def test_singleton(self):
        """Test that get_text_preprocessor returns singleton"""
        preprocessor1 = get_text_preprocessor()
        preprocessor2 = get_text_preprocessor()
        self.assertIs(preprocessor1, preprocessor2)


if __name__ == '__main__':
    unittest.main()