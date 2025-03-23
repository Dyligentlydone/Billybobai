from typing import Dict, Tuple
from textblob import TextBlob
import re
from datetime import datetime, timedelta

class MessageQualityAnalyzer:
    def __init__(self):
        self.conversation_history = {}  # Store recent messages for context
        self.response_patterns = {}     # Track common response patterns
        
    def analyze_message_quality(self, 
                              business_id: str,
                              workflow_id: str,
                              customer_message: str,
                              ai_response: str,
                              context: Dict = None) -> Dict:
        """
        Comprehensive message quality analysis
        Returns metrics about message quality
        """
        # Get conversation context
        conv_key = f"{business_id}:{workflow_id}"
        history = self.conversation_history.get(conv_key, [])
        
        # Clean old messages (keep last 24h)
        cutoff = datetime.now() - timedelta(hours=24)
        history = [(t, m) for t, m in history if t > cutoff]
        
        # Add new messages
        history.append((datetime.now(), customer_message))
        history.append((datetime.now(), ai_response))
        self.conversation_history[conv_key] = history
        
        # Analyze customer message
        customer_blob = TextBlob(customer_message)
        customer_metrics = {
            'sentiment': (customer_blob.sentiment.polarity + 1) / 2,  # Convert to 0-1 scale
            'subjectivity': customer_blob.sentiment.subjectivity,
            'urgency': self._detect_urgency(customer_message),
            'complexity': self._measure_complexity(customer_message)
        }
        
        # Analyze AI response
        response_metrics = {
            'tone_match': self._analyze_tone_match(customer_message, ai_response),
            'context_relevance': self._measure_context_relevance(ai_response, history),
            'completeness': self._measure_completeness(customer_message, ai_response),
            'personalization': self._measure_personalization(ai_response),
            'clarity': self._measure_clarity(ai_response)
        }
        
        # Update response patterns
        self._update_patterns(conv_key, ai_response)
        
        # Calculate overall quality score (weighted average)
        weights = {
            'tone_match': 0.25,
            'context_relevance': 0.3,
            'completeness': 0.2,
            'personalization': 0.15,
            'clarity': 0.1
        }
        
        quality_score = sum(
            response_metrics[metric] * weight 
            for metric, weight in weights.items()
        )
        
        return {
            'customer_metrics': customer_metrics,
            'response_metrics': response_metrics,
            'quality_score': quality_score,
            'is_follow_up': self._is_follow_up(history),
            'response_pattern_detected': self._check_response_patterns(conv_key, ai_response)
        }
    
    def _detect_urgency(self, text: str) -> float:
        """Detect urgency level in text (0-1 scale)"""
        urgent_words = {'urgent', 'asap', 'emergency', 'immediately', 'quick'}
        time_words = {'now', 'today', 'tonight', 'asap'}
        
        words = set(text.lower().split())
        urgency_score = (
            len(words & urgent_words) * 0.6 +
            len(words & time_words) * 0.4
        ) / max(len(urgent_words), len(time_words))
        
        return min(1.0, urgency_score)
    
    def _measure_complexity(self, text: str) -> float:
        """Measure text complexity (0-1 scale)"""
        words = text.split()
        if not words:
            return 0
            
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = len(TextBlob(text).sentences)
        
        # Normalize to 0-1 scale
        return min(1.0, (avg_word_length / 10 + sentence_count / 5) / 2)
    
    def _analyze_tone_match(self, customer_msg: str, response: str) -> float:
        """Analyze if response tone matches customer tone (0-1 scale)"""
        customer_blob = TextBlob(customer_msg)
        response_blob = TextBlob(response)
        
        # Compare sentiment polarity and subjectivity
        sentiment_diff = abs(customer_blob.sentiment.polarity - response_blob.sentiment.polarity)
        subjectivity_diff = abs(customer_blob.sentiment.subjectivity - response_blob.sentiment.subjectivity)
        
        # Convert differences to similarity scores (0-1)
        sentiment_match = 1 - (sentiment_diff / 2)  # Divide by 2 as polarity range is -1 to 1
        subjectivity_match = 1 - subjectivity_diff
        
        return (sentiment_match * 0.7 + subjectivity_match * 0.3)
    
    def _measure_context_relevance(self, response: str, history: list) -> float:
        """Measure how relevant the response is to conversation context (0-1 scale)"""
        if not history:
            return 1.0
            
        # Get key terms from recent history
        recent_msgs = ' '.join(msg for _, msg in history[-4:])  # Last 2 exchanges
        key_terms = set(word.lower() for word in TextBlob(recent_msgs).noun_phrases)
        
        if not key_terms:
            return 1.0
            
        # Check how many key terms are referenced in response
        response_terms = set(word.lower() for word in TextBlob(response).noun_phrases)
        
        return min(1.0, len(key_terms & response_terms) / max(1, len(key_terms)))
    
    def _measure_completeness(self, question: str, response: str) -> float:
        """Measure if response completely addresses the question (0-1 scale)"""
        # Extract question words
        question_words = {'what', 'when', 'where', 'who', 'why', 'how', 'which', 'can', 'will', 'should'}
        asked = set(word.lower() for word in question.split()) & question_words
        
        if not asked:
            return 1.0  # No direct questions to answer
            
        # Check if response addresses question types
        response_lower = response.lower()
        addressed = sum(
            1 for q in asked
            if any(marker in response_lower for marker in self._get_answer_markers(q))
        )
        
        return addressed / len(asked)
    
    def _get_answer_markers(self, question_word: str) -> list:
        """Get typical markers for different question types"""
        markers = {
            'what': ['is', 'are', 'means'],
            'when': ['at', 'on', 'in', 'during'],
            'where': ['at', 'in', 'near', 'located'],
            'who': ['by', 'person', 'team'],
            'why': ['because', 'since', 'reason'],
            'how': ['by', 'through', 'using'],
            'can': ['yes', 'no', 'able', 'cannot'],
            'will': ['will', 'going to', 'plan'],
            'should': ['should', 'recommend', 'suggest']
        }
        return markers.get(question_word, [])
    
    def _measure_personalization(self, response: str) -> float:
        """Measure response personalization level (0-1 scale)"""
        personalization_markers = {
            'pronouns': {'you', 'your', 'yours'},
            'greetings': {'hi', 'hello', 'dear'},
            'courtesy': {'please', 'thank', 'appreciate'},
            'acknowledgment': {'understand', 'see', 'know'}
        }
        
        words = set(response.lower().split())
        scores = [
            len(words & markers) / len(markers)
            for markers in personalization_markers.values()
        ]
        
        return sum(scores) / len(scores)
    
    def _measure_clarity(self, text: str) -> float:
        """Measure text clarity (0-1 scale)"""
        sentences = TextBlob(text).sentences
        if not sentences:
            return 0
            
        clarity_scores = []
        for sentence in sentences:
            words = str(sentence).split()
            if not words:
                continue
                
            # Factors affecting clarity:
            # 1. Sentence length (10-20 words is ideal)
            length_score = 1 - min(1, abs(len(words) - 15) / 15)
            
            # 2. Word complexity (length)
            avg_word_length = sum(len(word) for word in words) / len(words)
            complexity_score = 1 - min(1, (avg_word_length - 5) / 5)
            
            # 3. Technical jargon (could be expanded)
            jargon_words = {'utilize', 'implement', 'facilitate', 'leverage'}
            jargon_score = 1 - len(set(words) & jargon_words) / len(words)
            
            clarity_scores.append(
                length_score * 0.4 +
                complexity_score * 0.3 +
                jargon_score * 0.3
            )
        
        return sum(clarity_scores) / len(clarity_scores)
    
    def _is_follow_up(self, history: list) -> bool:
        """Determine if current message is a follow-up"""
        if len(history) < 4:  # Need at least 2 exchanges
            return False
            
        # Check if messages are within 1 hour
        last_msg_time = history[-1][0]
        prev_msg_time = history[-3][0]  # Customer's previous message
        
        return (last_msg_time - prev_msg_time) < timedelta(hours=1)
    
    def _update_patterns(self, conv_key: str, response: str) -> None:
        """Update tracked response patterns"""
        if conv_key not in self.response_patterns:
            self.response_patterns[conv_key] = []
            
        # Store last 100 responses
        self.response_patterns[conv_key] = (
            self.response_patterns[conv_key][-99:] + [response]
        )
    
    def _check_response_patterns(self, conv_key: str, response: str) -> bool:
        """Check if response is too similar to recent responses"""
        if conv_key not in self.response_patterns:
            return False
            
        # Compare with last 5 responses
        recent_responses = self.response_patterns[conv_key][-5:]
        for old_response in recent_responses:
            if self._calculate_similarity(response, old_response) > 0.8:
                return True
                
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (0-1 scale)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
