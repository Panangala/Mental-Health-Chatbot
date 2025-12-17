"""
NLP Preprocessing Module
Handles text preprocessing, tokenization, lemmatization, and normalization
"""

import logging
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Preprocesses text for sentiment analysis and chatbot processing.
    Handles tokenization, lemmatization, and text normalization.
    """
    
    def __init__(self):
        """Initialize preprocessor with NLTK tools"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        logger.info("Text preprocessor initialized")
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text (str): Input text
        
        Returns:
            List[str]: List of tokens (words)
        """
        if not text:
            return []
        
        tokens = word_tokenize(text.lower())
        logger.debug(f"Tokenized '{text[:50]}' into {len(tokens)} tokens")
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove common stopwords from tokens.
        
        Args:
            tokens (List[str]): List of tokens
        
        Returns:
            List[str]: Filtered tokens without stopwords
        """
        filtered = [token for token in tokens if token not in self.stop_words]
        logger.debug(f"Removed {len(tokens) - len(filtered)} stopwords")
        return filtered
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens to their base form.
        
        Args:
            tokens (List[str]): List of tokens
        
        Returns:
            List[str]: Lemmatized tokens
        """
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        return lemmatized
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text: lowercase, remove extra spaces, etc.
        
        Args:
            text (str): Input text
        
        Returns:
            str: Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def preprocess(self, text: str, remove_stopwords_flag: bool = False) -> Dict:
        """
        Complete preprocessing pipeline.
        
        Args:
            text (str): Input text
            remove_stopwords_flag (bool): Whether to remove stopwords
        
        Returns:
            Dict: Preprocessing results
        """
        # Normalize
        normalized = self.normalize_text(text)
        
        # Tokenize
        tokens = self.tokenize(normalized)
        
        # Optional: Remove stopwords
        if remove_stopwords_flag:
            tokens = self.remove_stopwords(tokens)
        
        # Lemmatize
        lemmatized = self.lemmatize(tokens)
        
        return {
            'original_text': text,
            'normalized_text': normalized,
            'tokens': tokens,
            'lemmatized': lemmatized,
            'token_count': len(tokens)
        }


# Module-level instance for reuse
_text_preprocessor = None


def get_text_preprocessor() -> TextPreprocessor:
    """Get or create text preprocessor instance"""
    global _text_preprocessor
    if _text_preprocessor is None:
        _text_preprocessor = TextPreprocessor()
    return _text_preprocessor