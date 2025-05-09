import pytest
from src.analyzer.sentiment_analyzer import SentimentAnalyzer
from datetime import datetime

def test_sentiment_analyzer_init():
    """Test SentimentAnalyzer initialization."""
    analyzer = SentimentAnalyzer()
    assert analyzer.sentiment_pipeline is not None

def test_analyze_sentiment_empty_text():
    """Test sentiment analysis with empty text."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_sentiment("")
    
    assert result["label"] == "NEUTRAL"
    assert result["score"] == 0.5

def test_analyze_problem_validation_empty_posts():
    """Test problem validation with empty posts list."""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze_problem_validation([])
    
    assert "sentiment_summary" in result
    assert "engagement_metrics" in result
    assert "temporal_analysis" in result
    assert "validation_score" in result
    assert result["validation_score"] == 0.0

def test_analyze_problem_validation():
    """Test problem validation with sample posts."""
    analyzer = SentimentAnalyzer()
    
    # Sample post data
    posts = [
        {
            "title": "Great solution for a common problem",
            "content": "This really helps solve a pain point",
            "score": 100,
            "num_comments": 10,
            "created_utc": datetime.utcnow().isoformat(),
            "top_comments": [
                {
                    "body": "Very useful tool!",
                    "score": 50,
                    "created_utc": datetime.utcnow().isoformat()
                }
            ]
        }
    ]
    
    result = analyzer.analyze_problem_validation(posts)
    
    assert 0 <= result["validation_score"] <= 1
    assert "sentiment_summary" in result
    assert "engagement_metrics" in result
    assert "temporal_analysis" in result
    
    # Check engagement metrics
    assert result["engagement_metrics"]["avg_score"] == 100.0
    assert result["engagement_metrics"]["avg_comments"] == 10.0
    assert result["engagement_metrics"]["total_engagement"] == 110.0
