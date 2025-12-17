"""
Configuration Module
Handles database, authentication, and Flask settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask Settings
    FLASK_APP = "app.py"
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-this')
    DEBUG = os.getenv('DEBUG', False)
    
    # Database Settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mental_health_chatbot')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('DEBUG', False)
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-this')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # API Settings
    API_KEY = os.getenv('API_KEY', 'test-api-key-123')
    API_VERSION = 'v1'
    
    # Session Settings
    PERMANENT_SESSION_LIFETIME = 3600 * 24  # 24 hours
    SESSION_REFRESH_EACH_REQUEST = False
    
    # Sentiment Analysis Settings
    VADER_THRESHOLD = 0.05
    CRISIS_KEYWORDS = [
        'suicide', 'self harm', 'die', 'death', 'harm',
        'kill myself', 'end it', 'hopeless', 'worthless',
        'overdose', 'cut myself'
    ]
    
    # Emotion Categories
    EMOTION_CATEGORIES = {
        'very_positive': ['happy', 'delighted', 'joyful'],
        'positive': ['good', 'fine', 'okay'],
        'neutral': ['neutral', 'okay'],
        'negative': ['sad', 'upset', 'frustrated'],
        'very_negative': ['depressed', 'hopeless', 'desperate']
    }
    
    # Mental Health States
    MENTAL_STATES = {
        'depression': ['sad', 'hopeless', 'worthless', 'depressed'],
        'anxiety': ['anxious', 'worried', 'nervous', 'panic'],
        'stress': ['stressed', 'overwhelmed', 'tense'],
        'grief': ['sad', 'loss', 'miss', 'gone'],
        'anger': ['angry', 'frustrated', 'mad', 'rage'],
        'happiness': ['happy', 'excited', 'joyful']
    }
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/mental_health_chatbot_test'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration selector
def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig


# Export config
config = get_config()