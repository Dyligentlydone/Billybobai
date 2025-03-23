import logging
from textblob import TextBlob
from typing import Dict, Any, Optional

class MessageQualityAnalyzer:
    def __init__(self):
        """Initialize the message quality analyzer"""
        pass

    def analyze_message_quality(
        self,
        message_body: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze the quality of a message and its response"""
        try:
            # Analyze customer message
            customer_blob = TextBlob(message_body)
            customer_metrics = {
                'sentiment': customer_blob.sentiment.polarity,
                'subjectivity': customer_blob.sentiment.subjectivity,
                'word_count': len(customer_blob.words),
                'is_question': any(s.endswith('?') for s in customer_blob.sentences)
            }
            
            # Analyze response
            response_blob = TextBlob(response)
            response_metrics = {
                'sentiment': response_blob.sentiment.polarity,
                'subjectivity': response_blob.sentiment.subjectivity,
                'word_count': len(response_blob.words),
                'sentence_count': len(response_blob.sentences)
            }
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(
                customer_metrics,
                response_metrics,
                context
            )
            
            return {
                'customer_metrics': customer_metrics,
                'response_metrics': response_metrics,
                'quality_score': quality_score,
                'is_follow_up': self._needs_follow_up(response)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing message quality: {str(e)}")
            return {
                'customer_metrics': {},
                'response_metrics': {},
                'quality_score': 0.5,  # Default middle score
                'is_follow_up': False
            }
    
    def _calculate_quality_score(
        self,
        customer_metrics: Dict[str, Any],
        response_metrics: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate an overall quality score for the interaction"""
        try:
            # Base score starts at 0.7 (assuming decent quality)
            score = 0.7
            
            # Adjust based on sentiment alignment
            sentiment_diff = abs(customer_metrics['sentiment'] - response_metrics['sentiment'])
            if sentiment_diff < 0.3:  # Good alignment
                score += 0.1
            elif sentiment_diff > 0.7:  # Poor alignment
                score -= 0.1
            
            # Adjust based on response length
            if response_metrics['word_count'] < 10:  # Too short
                score -= 0.2
            elif response_metrics['word_count'] > 100:  # Too long
                score -= 0.1
            
            # Adjust based on question answering
            if customer_metrics['is_question'] and response_metrics['sentence_count'] < 2:
                score -= 0.1
            
            # Cap score between 0 and 1
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logging.error(f"Error calculating quality score: {str(e)}")
            return 0.5  # Default middle score
    
    def _needs_follow_up(self, response: str) -> bool:
        """Determine if the response indicates a need for follow-up"""
        follow_up_phrases = [
            'please let me know',
            'contact us',
            'reach out',
            'get back to you',
            'follow up'
        ]
        
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in follow_up_phrases)
