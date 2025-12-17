"""
Therapeutic Response Templates
Enhanced with topic and context awareness
"""

def build_therapeutic_response(t5_response, emotion=None, topic=None):
    """
    Enhance T5 response with therapeutic elements based on emotion and topic.
    
    Args:
        t5_response: Base response from T5 model
        emotion: Detected emotion type
        topic: Extracted topic (exam, job, etc.)
    
    Returns:
        Enhanced therapeutic response
    """
    
    response = t5_response
    
    # Add emotion-specific affirmations
    affirmations = {
        'anxiety': "\n\n✓ Remember: It's okay to feel anxious. This feeling is temporary and manageable.",
        'sadness': "\n\n✓ Your feelings are valid. It's okay to grieve or feel down sometimes.",
        'anger': "\n\n✓ Your anger is telling you something important. Listen to what it's saying.",
        'fear': "\n\n✓ Fear is a natural protective emotion. It's okay to feel afraid.",
        'joy': "\n\n✓ I'm genuinely happy for you. Keep nurturing these positive feelings!",
        'neutral': "\n\n✓ Thank you for opening up. We can work through this together."
    }
    
    if emotion and emotion in affirmations:
        response += affirmations[emotion]
    
    # Add topic-specific grounding
    topic_grounding = {
        'exam': "\n\n💡 Focus on what you can control: your preparation, effort, and mindset.",
        'job': "\n\n💡 Remember: Your job doesn't define your worth as a person.",
        'relationship': "\n\n💡 Healthy relationships require communication. Consider expressing how you feel.",
        'family': "\n\n💡 Family relationships are complex. Be compassionate with yourself and them.",
        'health': "\n\n💡 Your health matters. Consider speaking with a healthcare professional if needed.",
        'money': "\n\n💡 Financial stress is real, but it's often solvable with planning.",
        'social': "\n\n💡 Human connection is important. Even small interactions count.",
        'school': "\n\n💡 Education is a journey, not a race. Progress matters more than perfection."
    }
    
    if topic and topic in topic_grounding:
        response += topic_grounding[topic]
    
    # Add closing support
    closing = "\n\nI'm here to listen and support you. What would help most right now?"
    response += closing
    
    return response


# Original templates for fallback if T5 isn't available
def get_template_response(emotion, topic='general'):
    """
    Fallback template responses if T5 model fails.
    Organized by emotion and topic.
    """
    
    templates = {
        'anxiety': {
            'exam': "I can hear the anxiety in what you're sharing. Exam anxiety is really common, and there are proven ways to manage it. What aspect worries you most?",
            'job': "Job anxiety can be overwhelming. Take a breath. What specific part of the situation worries you?",
            'interview': "Interview anxiety is normal. Remember: they want you to succeed too. What's your biggest worry about it?",
            'general': "Anxiety can feel overwhelming, but it's manageable. What would help you feel calmer right now?"
        },
        'sadness': {
            'exam': "Exam outcomes don't define your worth. One test is temporary; your value is permanent. How are you coping?",
            'job': "Losing a job is a real loss. It's okay to grieve it. But this could also be an opportunity. How are you feeling?",
            'relationship': "Relationship pain is deep. That's normal. You're not alone in this. Do you have support around you?",
            'family': "Family sadness runs deep. You're allowed to feel this. What support do you need?",
            'general': "I'm sorry you're feeling sad. That sounds really heavy. I'm here to listen."
        },
        'anger': {
            'job': "Your frustration is valid. Workplace mistreatment is real. What would a fair outcome look like?",
            'relationship': "Anger in relationships often signals unmet needs. What do you need from this situation?",
            'family': "Family anger can be intense. Take a step back if needed. What would help?",
            'general': "Your anger is telling you something important. What's it trying to say?"
        },
        'fear': {
            'exam': "Test fear is about worry of the unknown. What's the actual worst case, and can you handle that?",
            'job': "Job fears often stem from 'what ifs'. Let's look at the actual facts. What's really at risk?",
            'health': "Health fears are deep. Knowledge helps. What would make you feel more informed?",
            'general': "Fear is your mind trying to protect you. But often it's worse than reality. What are you actually afraid of?"
        },
        'joy': {
            'exam': "That's wonderful! Celebrate this achievement. You worked hard for it. How does this change your outlook?",
            'job': "Congratulations! You deserve this. How does this make you feel about yourself?",
            'relationship': "That's beautiful! Joy in relationships is precious. Nurture this.",
            'general': "I'm so happy for you! Hold onto this feeling and share it with others."
        },
        'neutral': {
            'general': "Thank you for sharing. Help me understand better - how are you feeling about all of this?"
        }
    }
    
    # Get emotion-specific templates
    emotion_templates = templates.get(emotion, templates.get('neutral'))
    
    # Try to get topic-specific, fallback to general
    response = emotion_templates.get(topic, emotion_templates.get('general', 
        "I'm here to listen. Please share more about what you're experiencing."))
    
    return response


# Emotion-specific follow-up questions
def get_follow_up_question(emotion, topic='general', conversation_length=0):
    """
    Get context-aware follow-up questions.
    Changes based on conversation length (early, middle, late).
    """
    
    follow_ups = {
        'anxiety': {
            'exam': {
                'early': "What specifically about the exam worries you most - the material, the format, or the pressure?",
                'middle': "Have you tried any strategies to manage exam anxiety before?",
                'late': "What's one small step you could take to feel more prepared?"
            },
            'job': {
                'early': "Is this about a specific event, or ongoing job stress?",
                'middle': "How long have you felt this way?",
                'late': "What would help you feel more confident?"
            },
            'default': {
                'early': "What worries you most about this situation?",
                'middle': "How long have you been feeling this way?",
                'late': "What's one thing that could help?"
            }
        },
        'sadness': {
            'exam': {
                'early': "How are you feeling about this exam result?",
                'middle': "Has this affected how you see yourself as a student?",
                'late': "What can you learn from this for next time?"
            },
            'relationship': {
                'early': "How long ago did this happen?",
                'middle': "Do you have support from friends or family?",
                'late': "What's one way you're taking care of yourself?"
            },
            'default': {
                'early': "How long have you been feeling this way?",
                'middle': "Do you have people supporting you?",
                'late': "What's helping, even a little?"
            }
        },
        'anger': {
            'job': {
                'early': "What happened that made you angry?",
                'middle': "How has this affected your work?",
                'late': "What outcome would feel fair to you?"
            },
            'default': {
                'early': "What triggered this anger?",
                'middle': "Is this a one-time or recurring issue?",
                'late': "How can you express this constructively?"
            }
        },
        'fear': {
            'exam': {
                'early': "What's the worst outcome you're imagining?",
                'middle': "Is that outcome actually likely?",
                'late': "What could you do if that happened?"
            },
            'default': {
                'early': "What exactly are you afraid might happen?",
                'middle': "How likely is that actually?",
                'late': "Could you handle it if it did happen?"
            }
        },
        'joy': {
            'default': {
                'early': "Tell me more about what's making you happy!",
                'middle': "How does this change things for you?",
                'late': "How can you hold onto this feeling?"
            }
        }
    }
    
    phase = 'early' if conversation_length < 2 else ('middle' if conversation_length < 5 else 'late')
    
    emotion_data = follow_ups.get(emotion, {})
    topic_data = emotion_data.get(topic, emotion_data.get('default', {}))
    question = topic_data.get(phase, "How are you feeling about what we've discussed?")
    
    return question


# Coping strategies by emotion and topic
def get_coping_strategy(emotion, topic='general'):
    """
    Get emotion and topic-specific coping techniques.
    Evidence-based strategies.
    """
    
    strategies = {
        'anxiety': {
            'exam': "Box breathing: Breathe in for 4, hold for 4, exhale for 4, hold for 4. Repeat 5 times.",
            'job': "Progressive muscle relaxation: Tense and release each muscle group for 5 seconds.",
            'health': "Grounding technique: 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
            'general': "Deep breathing: 4-7-8 technique - inhale 4, hold 7, exhale 8."
        },
        'sadness': {
            'exam': "Reframe: What did you learn? How will you improve? Focus on growth, not failure.",
            'job': "Movement: A 10-minute walk can help shift mood and gain perspective.",
            'relationship': "Self-compassion: Treat yourself as you would a good friend going through this.",
            'general': "Connection: Reach out to someone you trust. You don't have to carry this alone."
        },
        'anger': {
            'general': "Physical release: Intense exercise, cold water on your face, or journaling.",
            'job': "Communication: Write out what you feel, then decide how to express it constructively.",
            'relationship': "Timeout: Take space if needed. Return when you're calmer."
        },
        'fear': {
            'exam': "Visualization: Imagine yourself handling the exam successfully. See it clearly.",
            'job': "Worst case planning: What's the actual worst case? Could you handle it?",
            'health': "Information: Learning about what to expect reduces fear significantly.",
            'general': "Exposure: Small steps toward the feared thing often help."
        },
        'joy': {
            'general': "Celebrate and share: Tell someone you trust. Amplify this feeling."
        }
    }
    
    emotion_strats = strategies.get(emotion, {})
    strategy = emotion_strats.get(topic, emotion_strats.get('general', 
        "Self-care: Do something that nourishes you."))
    
    return strategy