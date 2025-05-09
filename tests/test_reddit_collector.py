import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.reddit_collector import RedditCollector

@pytest.fixture
def mock_reddit():
    """Create a mock PRAW Reddit instance."""
    with patch('praw.Reddit') as mock:
        yield mock

def test_reddit_collector_init(mock_reddit):
    """Test RedditCollector initialization."""
    collector = RedditCollector()
    assert collector.reddit is not None

def test_find_relevant_subreddits(mock_reddit):
    """Test finding relevant subreddits."""
    # Setup mock
    mock_subreddit = MagicMock()
    mock_search_result = MagicMock()
    mock_search_result.subreddit.display_name = "test_subreddit"
    mock_subreddit.search.return_value = [mock_search_result]
    mock_reddit.return_value.subreddit.return_value = mock_subreddit
    
    collector = RedditCollector()
    result = collector.find_relevant_subreddits(["test"], limit=1)
    
    assert len(result) == 1
    assert result[0] == "test_subreddit"

def test_collect_posts(mock_reddit):
    """Test collecting posts from a subreddit."""
    # Setup mock
    mock_subreddit = MagicMock()
    mock_post = MagicMock()
    mock_post.id = "test_id"
    mock_post.title = "Test Title"
    mock_post.selftext = "Test Content"
    mock_post.score = 100
    mock_post.num_comments = 10
    mock_post.created_utc = 1620000000
    mock_post.url = "https://reddit.com/r/test/test_id"
    
    mock_comment = MagicMock()
    mock_comment.id = "comment_id"
    mock_comment.body = "Test Comment"
    mock_comment.score = 50
    mock_comment.created_utc = 1620000000
    
    mock_post.comments = [mock_comment]
    mock_post.comments.replace_more = MagicMock()
    
    mock_subreddit.top.return_value = [mock_post]
    mock_reddit.return_value.subreddit.return_value = mock_subreddit
    
    collector = RedditCollector()
    result = collector.collect_posts(
        "test_subreddit",
        ["test"],
        time_filter="month",
        limit=1
    )
    
    assert len(result) == 1
    assert result[0]["id"] == "test_id"
    assert result[0]["title"] == "Test Title"
    assert result[0]["score"] == 100
    assert len(result[0]["top_comments"]) == 1
    assert result[0]["top_comments"][0]["id"] == "comment_id"
