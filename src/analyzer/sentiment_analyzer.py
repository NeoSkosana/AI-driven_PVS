from transformers import pipeline
from typing import List, Dict, Union
import numpy as np
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """A class to analyze sentiment and extract insights from collected data."""
    
    def __init__(self):
        """Initialize the sentiment analyzer with pre-trained model."""
        self.sentiment_pipeline = pipeline("sentiment-analysis")
        
    def analyze_sentiment(self, text: str) -> Dict[str, Union[str, float]]:
        """Analyze the sentiment of a given text with improved error handling."""
        if not text or len(text.strip()) == 0:
            return {"label": "NEUTRAL", "score": 0.5}
            
        try:
            # Handle text length limitations
            max_length = 512  # Typical limit for transformer models
            if len(text) > max_length:
                # Split into chunks and average sentiment
                chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
                results = [self.sentiment_pipeline(chunk)[0] for chunk in chunks]
                
                # Average scores and determine overall label
                avg_score = sum(r["score"] for r in results) / len(results)
                overall_label = max(set(r["label"] for r in results), 
                                 key=lambda x: sum(1 for r in results if r["label"] == x))
                
                return {"label": overall_label, "score": avg_score}
            
            result = self.sentiment_pipeline(text)[0]
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}

    def analyze_problem_validation(self, posts: List[Dict]) -> Dict:
        """Analyze collected posts with enhanced validation metrics."""
        if not posts:
            return {
                "sentiment_summary": self._calculate_empty_sentiment_summary(),
                "engagement_metrics": self._calculate_empty_engagement_metrics(),
                "temporal_analysis": self._calculate_empty_temporal_analysis(),
                "validation_score": 0.0,
                "confidence_score": 0.0,
                "validation_flags": ["insufficient_data"]
            }
            
        validation_flags = []
        sentiments = []
        
        # Analyze all content with improved context handling
        for post in posts:
            # Combine title and content for better context
            post_text = f"{post['title']} {post['content']}"
            post_sentiment = self.analyze_sentiment(post_text)
            
            # Weight sentiment by post score
            weighted_score = post_sentiment["score"] * (1 + math.log(1 + post["score"]))
            post_sentiment["weighted_score"] = weighted_score
            sentiments.append(post_sentiment)
            
            # Analyze comments for engagement quality
            for comment in post.get('top_comments', []):
                comment_sentiment = self.analyze_sentiment(comment['body'])
                comment_sentiment["weighted_score"] = comment_sentiment["score"] * \
                    (1 + math.log(1 + comment.get("score", 1)))
                sentiments.append(comment_sentiment)
        
        # Calculate metrics
        sentiment_summary = self._calculate_sentiment_summary(sentiments)
        engagement_metrics = self._calculate_engagement_metrics(posts)
        temporal_analysis = self._analyze_temporal_distribution(posts)
        
        # Add validation flags
        if len(posts) < 10:
            validation_flags.append("low_sample_size")
        if engagement_metrics["total_engagement"] < 50:
            validation_flags.append("low_engagement")
        if temporal_analysis["avg_posts_per_day"] < 1:
            validation_flags.append("low_activity")
            
        # Calculate scores
        validation_score = self._calculate_validation_score(
            sentiment_summary,
            engagement_metrics,
            temporal_analysis
        )
        
        # Calculate confidence score based on data quality
        confidence_score = self._calculate_confidence_score(
            len(posts),
            engagement_metrics["total_engagement"],
            temporal_analysis["avg_posts_per_day"]
        )
        
        return {
            "sentiment_summary": sentiment_summary,
            "engagement_metrics": engagement_metrics,
            "temporal_analysis": temporal_analysis,
            "validation_score": validation_score,
            "confidence_score": confidence_score,
            "validation_flags": validation_flags
        }

    def _calculate_empty_sentiment_summary(self) -> Dict:
        """Return empty sentiment summary."""
        return {
            "overall_sentiment": "NEUTRAL",
            "positive_ratio": 0.0,
            "negative_ratio": 0.0,
            "neutral_ratio": 1.0,
            "average_score": 0.5,
            "weighted_average_score": 0.5
        }

    def _calculate_empty_engagement_metrics(self) -> Dict:
        """Return empty engagement metrics."""
        return {
            "avg_score": 0.0,
            "avg_comments": 0.0,
            "total_engagement": 0.0,
            "unique_users": 0
        }

    def _calculate_empty_temporal_analysis(self) -> Dict:
        """Return empty temporal analysis."""
        return {
            "earliest_post": None,
            "latest_post": None,
            "avg_posts_per_day": 0.0,
            "activity_period_days": 0
        }

    def _calculate_sentiment_summary(self, sentiments: List[Dict]) -> Dict:
        """Calculate summary statistics for sentiments."""
        if not sentiments:
            return self._calculate_empty_sentiment_summary()
            
        sentiment_counts = {
            "POSITIVE": 0,
            "NEGATIVE": 0,
            "NEUTRAL": 0
        }
        
        total_score = 0.0
        total_weighted_score = 0.0
        
        for sentiment in sentiments:
            label = sentiment["label"]
            sentiment_counts[label] += 1
            total_score += sentiment["score"]
            total_weighted_score += sentiment.get("weighted_score", sentiment["score"])
        
        total = len(sentiments)
        
        return {
            "overall_sentiment": max(sentiment_counts.items(), key=lambda x: x[1])[0],
            "positive_ratio": sentiment_counts["POSITIVE"] / total,
            "negative_ratio": sentiment_counts["NEGATIVE"] / total,
            "neutral_ratio": sentiment_counts["NEUTRAL"] / total,
            "average_score": total_score / total,
            "weighted_average_score": total_weighted_score / total
        }
    
    def _calculate_engagement_metrics(self, posts: List[Dict]) -> Dict:
        """Calculate engagement metrics from posts."""
        if not posts:
            return self._calculate_empty_engagement_metrics()
            
        scores = [post["score"] for post in posts]
        comments = [post["num_comments"] for post in posts]
        unique_users = len(set(post.get("author", "") for post in posts))
        
        return {
            "avg_score": np.mean(scores),
            "avg_comments": np.mean(comments),
            "total_engagement": sum(scores) + sum(comments),
            "unique_users": unique_users
        }
    
    def _analyze_temporal_distribution(self, posts: List[Dict]) -> Dict:
        """Analyze the temporal distribution of posts."""
        if not posts:
            return self._calculate_empty_temporal_analysis()
            
        dates = [datetime.fromisoformat(post["created_utc"]) for post in posts]
        earliest = min(dates)
        latest = max(dates)
        
        days_span = (latest - earliest).days + 1
        
        return {
            "earliest_post": earliest.isoformat(),
            "latest_post": latest.isoformat(),
            "avg_posts_per_day": len(posts) / days_span if days_span > 0 else len(posts),
            "activity_period_days": days_span
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

    def _calculate_confidence_score(self, 
                                 num_posts: int,
                                 total_engagement: float,
                                 posts_per_day: float) -> float:
        """Calculate a confidence score for the validation results."""
        # Factors affecting confidence:
        # 1. Number of posts (more posts = higher confidence)
        # 2. Total engagement (more engagement = higher confidence)
        # 3. Activity rate (more regular activity = higher confidence)
        
        post_confidence = min(num_posts / 20, 1.0)  # Expects at least 20 posts for max confidence
        engagement_confidence = min(total_engagement / 200, 1.0)  # Expects 200 total engagement for max
        activity_confidence = min(posts_per_day / 3, 1.0)  # Expects 3 posts per day for max
        
        # Weight the factors
        weighted_score = (
            post_confidence * 0.4 +
            engagement_confidence * 0.4 +
            activity_confidence * 0.2
        )
        
        return round(weighted_score, 2)
