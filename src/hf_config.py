"""
HuggingFace Configuration and Resources
Mental health crisis keywords, resources, and support materials
"""

# Crisis detection keywords
CRISIS_KEYWORDS = [
    'kill myself', 'suicide', 'want to die', 'no point living',
    'end it all', 'hurt myself', 'self harm', 'overdose',
    'jump', 'harm', 'death', 'dying', 'dead'
]

# Crisis resources
CRISIS_RESOURCES = {
    'US': {
        'name': 'National Suicide Prevention Lifeline',
        'number': '988',
        'url': 'https://suicidepreventionlifeline.org'
    },
    'US_TEXT': {
        'name': 'Crisis Text Line',
        'number': 'Text HOME to 741741',
        'url': 'https://www.crisistextline.org'
    },
    'INTERNATIONAL': {
        'name': 'International Association for Suicide Prevention',
        'url': 'https://www.iasp.info/resources/Crisis_Centres/'
    }
}

# Relaxation techniques
RELAXATION_TIPS = [
    'Try deep breathing: inhale for 4 counts, hold for 4, exhale for 4',
    'Progressive muscle relaxation: tense and release each muscle group',
    '5-4-3-2-1 grounding: name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste',
    'Take a short walk in nature',
    'Listen to calming music',
    'Practice meditation',
    'Drink a warm beverage',
    'Journal your thoughts and feelings',
    'Do a gentle yoga routine',
    'Spend time with a pet'
]

# Mental health resources
MENTAL_HEALTH_RESOURCES = [
    'Psychology Today: https://www.psychologytoday.com',
    'NAMI (National Alliance on Mental Illness): https://www.nami.org',
    'Mental Health America: https://www.mhanational.org',
    'SAMHSA National Helpline: 1-800-662-4357'
]

# Emotion categories for response templates
EMOTION_CATEGORIES = {
    'sadness': {
        'keywords': ['sad', 'depressed', 'down', 'unhappy', 'miserable'],
        'response_tone': 'empathetic'
    },
    'anxiety': {
        'keywords': ['anxious', 'nervous', 'worried', 'stressed', 'panic'],
        'response_tone': 'calming'
    },
    'anger': {
        'keywords': ['angry', 'frustrated', 'mad', 'irritated', 'furious'],
        'response_tone': 'understanding'
    },
    'fear': {
        'keywords': ['scared', 'afraid', 'terrified', 'frightened'],
        'response_tone': 'reassuring'
    },
    'joy': {
        'keywords': ['happy', 'excited', 'great', 'wonderful', 'fantastic'],
        'response_tone': 'positive'
    }
}