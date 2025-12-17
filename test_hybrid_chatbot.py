"""
Test the Hybrid Mental Health Chatbot
"""
from src.hybrid_chatbot import HybridMentalHealthChatbot
import json

print("\n" + "="*70)
print("HYBRID MENTAL HEALTH CHATBOT TEST")
print("="*70 + "\n")

# Initialize chatbot
print("Initializing chatbot...")
chatbot = HybridMentalHealthChatbot()
print("✓ Chatbot loaded!\n")

# Test inputs
test_inputs = [
    "I'm really stressed about my exam tomorrow",
    "My boss keeps criticizing my work and I feel terrible",
    "I feel so lonely and isolated",
    "I'm having constant anxiety",
]

# Process each message
for i, user_input in enumerate(test_inputs, 1):
    print(f"\n--- Test {i} ---")
    print(f"User: {user_input}")
    
    result = chatbot.process_message(user_input)
    
    print(f"\nBot: {result['response']}")
    print(f"\nAnalysis:")
    print(f"  Emotion: {result['emotion']} (confidence: {result['confidence']})")
    print(f"  Sentiment: {result['sentiment']['compound']} (neg:{result['sentiment']['negative']}, pos:{result['sentiment']['positive']})")
    print(f"  Crisis: {'🚨 YES' if result['is_crisis'] else '✓ No'}")
    if result['suggestions']:
        print(f"  Suggestions:")
        for suggestion in result['suggestions']:
            print(f"    • {suggestion}")
    print("-" * 70)

print("\n✓ All tests completed!")