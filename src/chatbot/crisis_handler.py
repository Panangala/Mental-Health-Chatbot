"""
Enhanced Crisis Handler for Mental Health Chatbot
Handles crisis detection, formatting, and provides resources
"""

from src.hf_config import CRISIS_KEYWORDS, CRISIS_RESOURCES, RELAXATION_TIPS
import random

class CrisisHandler:
    def __init__(self):
        self.crisis_threshold = 0.80
        self.crisis_keywords = CRISIS_KEYWORDS
        
    def detect_crisis(self, text, sentiment_score):
        """
        Detect crisis indicators from user input and sentiment
        Returns: (is_crisis: bool, severity: float, keywords_found: list)
        """
        text_lower = text.lower()
        found_keywords = []
        max_severity = 0
        
        # Check for crisis keywords (handle both list and dict)
        if isinstance(self.crisis_keywords, dict):
            for keyword, severity in self.crisis_keywords.items():
                if keyword in text_lower:
                    found_keywords.append((keyword, severity))
                    max_severity = max(max_severity, severity)
        else:
            # If it's a list, just check for presence
            for keyword in self.crisis_keywords:
                if keyword in text_lower:
                    found_keywords.append((keyword, 0.9))
                    max_severity = 0.9
        
        # Combine keyword severity with sentiment
        if sentiment_score < -0.7 and found_keywords:
            max_severity = min(1.0, max_severity + 0.1)
        
        is_crisis = max_severity >= self.crisis_threshold
        
        return is_crisis, max_severity, found_keywords
    
    def format_crisis_response(self, severity_level, keywords_found=None):
        """Format crisis response with proper structure"""
        
        if severity_level >= 0.90:
            urgency = "🚨 IMMEDIATE SUPPORT NEEDED"
            color_indicator = "🔴"
        elif severity_level >= 0.85:
            urgency = "⚠️ URGENT SUPPORT RECOMMENDED"
            color_indicator = "🟠"
        else:
            urgency = "⚡ SUPPORT AVAILABLE"
            color_indicator = "🟡"
        
        response = f"""
{color_indicator} {urgency}

I'm genuinely concerned about what you've shared. You don't have to face this alone.

💙 PLEASE REACH OUT TO SOMEONE:
- Call 988 (Suicide & Crisis Lifeline)
- Text "HELLO" to 741741 (Crisis Text Line)
- Go to nearest emergency room
- Call 911 if in immediate danger

I'm here to listen and support you through this.
"""
        
        return response
    
    def get_crisis_response(self, text, sentiment_score):
        """
        Main method to get formatted crisis response if crisis detected
        Returns: (is_crisis: bool, formatted_response: str or None)
        """
        is_crisis, severity, keywords = self.detect_crisis(text, sentiment_score)
        
        if is_crisis:
            formatted_response = self.format_crisis_response(severity, keywords)
            return True, formatted_response
        
        return False, None