import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from src.response_generation.templates import build_therapeutic_response
import os

class T5ResponseGenerator:
    def __init__(self, model_path='models/t5_finetuned_model'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ T5 model loaded from {model_path}")
        except Exception as e:
            print(f"❌ Error loading T5 model: {e}")
            self.model = None
            self.tokenizer = None
    
    def _extract_topic(self, user_input):
        """Extract topic from user message"""
        message_lower = user_input.lower()
        
        topic_keywords = {
            'exam': ['exam', 'test', 'quiz', 'midterm', 'final'],
            'job': ['job', 'work', 'interview', 'boss', 'promotion'],
            'relationship': ['girlfriend', 'boyfriend', 'partner', 'breakup'],
            'family': ['mom', 'dad', 'parent', 'family'],
            'health': ['sick', 'illness', 'doctor', 'hospital', 'health'],
            'money': ['money', 'debt', 'financial', 'bills', 'rent'],
            'social': ['friend', 'lonely', 'social', 'people'],
            'school': ['school', 'class', 'grade', 'homework'],
        }
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return topic
        
        return None
    
    def _remove_repetition(self, text):
        """Remove repeated sentences from text"""
        sentences = text.split('. ')
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in seen:
                seen.add(sentence)
                unique_sentences.append(sentence)
        
        # Rejoin with proper punctuation
        result = '. '.join(unique_sentences)
        if result and not result.endswith('.'):
            result += '.'
        
        return result
    
    def generate_response(self, user_input, emotion=None, topic=None, context_details=None, max_length=150):
        """
        Generate response using fine-tuned T5 model.
        Keep it simple - let T5 do what it's trained for.
        
        Args:
            user_input: The user's message
            emotion: Detected emotion
            topic: Extracted topic (optional, for templates)
            context_details: Additional context (optional)
            max_length: Max response length
        
        Returns:
            Therapeutic response
        """
        
        if self.model is None:
            return "I'm having trouble processing your request. Please try again."
        
        try:
            # Simple prompt - just the therapy context
            # Let T5 do what it was fine-tuned for
            input_text = f"therapy: {user_input}"
            
            print(f"📝 T5 Input: {input_text}")
            
            # Tokenize
            input_ids = self.tokenizer.encode(input_text, return_tensors='pt').to(self.device)
            
            # Generate response from fine-tuned model
            # Higher repetition penalty to reduce repetition
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    num_beams=4,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=3.0,  # INCREASED from 2.0 to reduce repetition
                    early_stopping=True,
                    no_repeat_ngram_size=3  # Prevent 3-word phrases from repeating
                )
            
            # Decode T5 output
            base_response = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Remove any repeated sentences
            base_response = self._remove_repetition(base_response)
            
            print(f"🤖 T5 Output: {base_response}")
            
            # Extract topic if not provided
            if not topic:
                topic = self._extract_topic(user_input)
            
            # Enhance with therapeutic templates
            final_response = build_therapeutic_response(base_response, emotion, topic)
            
            print(f"✨ Final Response: {final_response[:100]}...")
            
            return final_response
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return "I understand you're going through something difficult. Please share more about what you're experiencing."
    
    def generate_response_batch(self, user_inputs, emotions=None, topics=None):
        """Generate responses for multiple inputs"""
        
        if self.model is None:
            return ["Model not loaded"] * len(user_inputs)
        
        responses = []
        for i, user_input in enumerate(user_inputs):
            emotion = emotions[i] if emotions and i < len(emotions) else None
            topic = topics[i] if topics and i < len(topics) else None
            response = self.generate_response(user_input, emotion, topic)
            responses.append(response)
        
        return responses