from transformers import pipeline
from typing import List, Dict, Union
import numpy as np
from datetime import datetime

class SentimentAnalyzer:
    """
    A class to analyze sentiment and extract insights from collected data.
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer with pre-trained model."""
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        
    def analyze_sentiment(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze the sentiment of a given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment label and score
        """
        if not text or len(text.strip()) == 0:
            return {"label": "NEUTRAL", "score": 0.5}
            
        result = self.sentiment_pipeline(text)[0]
        return result
    
    def analyze_problem_validation(self, posts: List[Dict]) -> Dict:
        """
        Analyze collected posts to validate problem statements.
        
        Args:
            posts: List of post dictionaries from RedditCollector
            
        Returns:
            Dictionary containing analysis results
        """
        if not posts:
            return {
                "sentiment_summary": {},
                "engagement_metrics": {},
                "temporal_analysis": {},
                "validation_score": 0.0
            }
            
        # Analyze sentiment for all posts and comments
        sentiments = []
        for post in posts:
            # Analyze post sentiment
            post_sentiment = self.analyze_sentiment(f"{post['title']} {post['content']}")
            sentiments.append(post_sentiment)
            
            # Analyze comments sentiment
            for comment in post.get('top_comments', []):
                comment_sentiment = self.analyze_sentiment(comment['body'])
                sentiments.append(comment_sentiment)
        
        # Calculate sentiment summary
        sentiment_summary = self._calculate_sentiment_summary(sentiments)
        
        # Calculate engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(posts)
        
        # Perform temporal analysis
        temporal_analysis = self._analyze_temporal_distribution(posts)
        
        # Calculate overall validation score
        validation_score = self._calculate_validation_score(
            sentiment_summary,
            engagement_metrics,
            temporal_analysis
        )
        
        return {
            "sentiment_summary": sentiment_summary,
            "engagement_metrics": engagement_metrics,
            "temporal_analysis": temporal_analysis,
            "validation_score": validation_score
        }
    
    def _calculate_sentiment_summary(self, sentiments: List[Dict]) -> Dict:
        """Calculate summary statistics for sentiments."""
        if not sentiments:
            return {
                "overall_sentiment": "NEUTRAL",
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 1.0,
                "average_score": 0.5
            }
            
        sentiment_counts = {
            "POSITIVE": 0,
            "NEGATIVE": 0,
            "NEUTRAL": 0
        }
        
        total_score = 0.0
        
        for sentiment in sentiments:
            label = sentiment["label"]
            sentiment_counts[label] += 1
            total_score += sentiment["score"]
        
        total = len(sentiments)
        
        return {
            "overall_sentiment": max(sentiment_counts.items(), key=lambda x: x[1])[0],
            "positive_ratio": sentiment_counts["POSITIVE"] / total,
            "negative_ratio": sentiment_counts["NEGATIVE"] / total,
            "neutral_ratio": sentiment_counts["NEUTRAL"] / total,
            "average_score": total_score / total
        }
    
    def _calculate_engagement_metrics(self, posts: List[Dict]) -> Dict:
        """Calculate engagement metrics from posts."""
        if not posts:
            return {
                "avg_score": 0.0,
                "avg_comments": 0.0,
                "total_engagement": 0.0
            }
            
        scores = [post["score"] for post in posts]
        comments = [post["num_comments"] for post in posts]
        
        return {
            "avg_score": np.mean(scores),
            "avg_comments": np.mean(comments),
            "total_engagement": sum(scores) + sum(comments)
        }
    
    def _analyze_temporal_distribution(self, posts: List[Dict]) -> Dict:
        """Analyze the temporal distribution of posts."""
        if not posts:
            return {
                "earliest_post": None,
                "latest_post": None,
                "avg_posts_per_day": 0.0
            }
            
        dates = [datetime.fromisoformat(post["created_utc"]) for post in posts]
        earliest = min(dates)
        latest = max(dates)
        
        days_span = (latest - earliest).days + 1
        
        return {
            "earliest_post": earliest.isoformat(),
            "latest_post": latest.isoformat(),
            "avg_posts_per_day": len(posts) / days_span if days_span > 0 else len(posts)
        }
    
    def _calculate_validation_score(self, 
                                 sentiment_summary: Dict,
                                 engagement_metrics: Dict,
                                 temporal_analysis: Dict) -> float:
        """
        Calculate an overall problem validation score.
        
        This score combines sentiment analysis, engagement metrics, and temporal distribution
        to provide a single metric indicating the validity of the problem statement.
        
        Returns:
            Float between 0 and 1, where higher values indicate stronger problem validation
        """
        # Weight factors for different components
        SENTIMENT_WEIGHT = 0.4
        ENGAGEMENT_WEIGHT = 0.4
        TEMPORAL_WEIGHT = 0.2
        
        # Calculate sentiment score
        sentiment_score = (
            sentiment_summary["positive_ratio"] * 1.0 +
            sentiment_summary["neutral_ratio"] * 0.5 +
            sentiment_summary["negative_ratio"] * 0.0
        )
        
        # Normalize engagement metrics
        max_engagement = 1000  # Threshold for maximum engagement
        engagement_score = min(engagement_metrics["total_engagement"] / max_engagement, 1.0)
        
        # Calculate temporal score
        # Higher score for more recent and consistent activity
        avg_posts_threshold = 5  # Threshold for good daily post average
        temporal_score = min(temporal_analysis["avg_posts_per_day"] / avg_posts_threshold, 1.0)
        
        # Combine scores with weights
        validation_score = (
            sentiment_score * SENTIMENT_WEIGHT +
            engagement_score * ENGAGEMENT_WEIGHT +
            temporal_score * TEMPORAL_WEIGHT
        )
        
        return round(validation_score, 2)
