"""
Interactive Response Generator
Creates adaptive, step-by-step therapeutic responses
"""

import random

class InteractiveResponseGenerator:
    def __init__(self):
        self.conversation_phases = {
            'initial': ['acknowledgment', 'follow_up'],
            'depth': ['clarification', 'exploration'],
            'support': ['suggestion', 'coping'],
            'closing': ['affirmation', 'offer_help']
        }
    
    def generate_interactive_response(self, user_message, emotion, sentiment_score, conversation_history):
        """Generate adaptive response based on sentiment and conversation stage"""
        
        history_length = len(conversation_history)
        style = self._determine_style(sentiment_score)
        
        if history_length == 0:
            return self._initial_response(user_message, emotion, style)
        elif history_length < 3:
            return self._exploration_response(user_message, emotion, style)
        elif history_length < 6:
            return self._support_response(emotion, style)
        else:
            return self._closing_response(emotion, style)
    
    def _determine_style(self, sentiment_score):
        """Determine response style based on sentiment"""
        
        # Very negative: empathetic and warm
        if sentiment_score < -0.6:
            return 'empathetic'
        
        # Neutral/slightly negative: balanced
        elif -0.6 <= sentiment_score < 0.2:
            return 'balanced'
        
        # Positive: direct and practical
        else:
            return 'direct'
    
    def _initial_response(self, user_message, emotion, style):
        """First response - adapt to user's sentiment"""
        
        if style == 'empathetic':
            return self._initial_empathetic(emotion)
        elif style == 'direct':
            return self._initial_direct(emotion)
        else:
            return self._initial_balanced(emotion)
    
    def _initial_empathetic(self, emotion):
        """Warm, understanding opening"""
        
        initial = {
            'sadness': "I'm really sorry you're going through this. That must feel overwhelming. Can you tell me more about what happened?",
            'anxiety': "I can hear the worry in what you're saying. That must be difficult. What's making you most anxious right now?",
            'anger': "Your frustration is completely valid. I hear you. What happened that made you feel this way?",
            'fear': "Fear is a heavy emotion. Thank you for sharing this with me. What are you most afraid of?",
            'joy': "That's wonderful! I'm so happy for you! What made this moment special?"
        }
        
        return initial.get(emotion, initial['sadness'])
    
    def _initial_direct(self, emotion):
        """Straightforward, practical opening"""
        
        initial = {
            'sadness': "I hear you. What specific step would help you feel better right now?",
            'anxiety': "Let's break down what's worrying you. What's the first concern?",
            'anger': "What needs to happen for you to feel heard?",
            'fear': "What specifically are you afraid of? Let's address it.",
            'joy': "That's great! How can you build on this momentum?"
        }
        
        return initial.get(emotion, initial['sadness'])
    
    def _initial_balanced(self, emotion):
        """Mix of empathy and practicality"""
        
        initial = {
            'sadness': "I understand this is difficult. What's been the hardest part for you?",
            'anxiety': "That sounds stressful. When did this worry start?",
            'anger': "Your frustration makes sense. What triggered this feeling?",
            'fear': "That fear is valid. What would help you feel safer?",
            'joy': "That's wonderful! How are you feeling about it?"
        }
        
        return initial.get(emotion, initial['sadness'])
    
    def _exploration_response(self, user_message, emotion, style):
        """Second/third response - explore deeper"""
        
        if style == 'empathetic':
            return self._explore_empathetic(emotion)
        elif style == 'direct':
            return self._explore_direct(emotion)
        else:
            return self._explore_balanced(emotion)
    
    def _explore_empathetic(self, emotion):
        """Empathetic exploration"""
        
        explore = {
            'sadness': "That sounds really painful. How has this been affecting your daily life? I'm here to listen.",
            'anxiety': "I can imagine how exhausting this must be. Have you had any moments of relief?",
            'anger': "That's so frustrating. How long have you been feeling this way?",
            'fear': "I understand why you're worried. Have you talked to anyone about this fear?",
            'joy': "This is beautiful. Who are you sharing this happiness with?"
        }
        
        return random.choice([explore.get(emotion, explore['sadness'])])
    
    def _explore_direct(self, emotion):
        """Direct exploration"""
        
        explore = {
            'sadness': "What specific area is affected most - work, relationships, health?",
            'anxiety': "What's the worst case scenario you're imagining?",
            'anger': "What outcome would resolve this for you?",
            'fear': "What's one small step you could take?",
            'joy': "What's next for you with this?"
        }
        
        return random.choice([explore.get(emotion, explore['sadness'])])
    
    def _explore_balanced(self, emotion):
        """Balanced exploration"""
        
        explore = {
            'sadness': "I understand this is tough. What's been helping you cope so far, even a little?",
            'anxiety': "How long have you been dealing with this? What usually helps calm you?",
            'anger': "What do you need right now? What would help?",
            'fear': "What would make you feel more in control?",
            'joy': "How can you nurture this feeling?"
        }
        
        return random.choice([explore.get(emotion, explore['sadness'])])
    
    def _support_response(self, emotion, style):
        """Mid-conversation - offer support"""
        
        if style == 'empathetic':
            return self._support_empathetic(emotion)
        elif style == 'direct':
            return self._support_direct(emotion)
        else:
            return self._support_balanced(emotion)
    
    def _support_empathetic(self, emotion):
        """Empathetic support"""
        
        support = {
            'sadness': "You're showing real strength in opening up. You deserve compassion - starting with yourself. Try one small activity you enjoy today, even if you don't feel like it.",
            'anxiety': "Managing anxiety takes courage. You're doing great. Try box breathing: in for 4, hold 4, out for 4, hold 4.",
            'anger': "Your anger is valid and powerful. Channel it: write, move, create. Get it out safely.",
            'fear': "Facing fear is brave. Visualize yourself handling this successfully. See yourself calm and capable.",
            'joy': "Hold onto this feeling. You've earned this happiness. Keep celebrating!"
        }
        
        return support.get(emotion, support['sadness'])
    
    def _support_direct(self, emotion):
        """Direct support with practical tips"""
        
        support = {
            'sadness': "Action step: Do one thing today that's good for you, no matter how small.",
            'anxiety': "Break it down: List your worries. Which ones can you control?",
            'anger': "Exercise, write, or talk it out. Get the energy moving.",
            'fear': "Face it gradually. Small steps build confidence.",
            'joy': "Document this moment. Remember why this matters."
        }
        
        return support.get(emotion, support['sadness'])
    
    def _support_balanced(self, emotion):
        """Balanced support"""
        
        support = {
            'sadness': "You're handling this well by reaching out. One thing that might help: gentle movement or talking to someone you trust.",
            'anxiety': "This is manageable. Try slowing your breathing or talking through your concerns.",
            'anger': "Express this safely - physically, creatively, or verbally.",
            'fear': "Small steps help. What's one thing you could do to feel more prepared?",
            'joy': "Celebrate this! What's one way you can honor this moment?"
        }
        
        return support.get(emotion, support['sadness'])
    
    def _closing_response(self, emotion, style):
        """Later conversation - reinforce and offer resources"""
        
        if style == 'empathetic':
            return self._closing_empathetic(emotion)
        elif style == 'direct':
            return self._closing_direct(emotion)
        else:
            return self._closing_balanced(emotion)
    
    def _closing_empathetic(self, emotion):
        """Empathetic closing"""
        
        closing = {
            'sadness': "You've shown incredible strength. Remember: healing isn't linear, and you don't have to do it alone. Professional support is available if you need it.",
            'anxiety': "You're managing something difficult. Be proud of yourself. Would it help to explore more resources?",
            'anger': "Your anger has taught you something. You're capable of working through this.",
            'fear': "You're facing something scary, and that takes courage. You're not alone.",
            'joy': "Keep this going. You deserve this happiness."
        }
        
        return closing.get(emotion, closing['sadness'])
    
    def _closing_direct(self, emotion):
        """Direct closing"""
        
        closing = {
            'sadness': "Next step: Consider talking to a therapist. Would that be helpful?",
            'anxiety': "You're making progress. What's your action plan moving forward?",
            'anger': "You've identified the problem. Now, what's your solution?",
            'fear': "You've gotten this far. What's your next step?",
            'joy': "Keep building on this. What's your plan?"
        }
        
        return closing.get(emotion, closing['sadness'])
    
    def _closing_balanced(self, emotion):
        """Balanced closing"""
        
        closing = {
            'sadness': "You're handling this well by seeking support. Remember, professional help is available whenever you need it.",
            'anxiety': "You're learning to manage this. How are you feeling about moving forward?",
            'anger': "You understand what's happened. How do you want to move forward?",
            'fear': "You're working through this courageously. What comes next?",
            'joy': "This is wonderful progress. How can you maintain this?"
        }
        
        return closing.get(emotion, closing['sadness'])