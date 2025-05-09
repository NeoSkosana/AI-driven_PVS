import praw
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

class RedditCollector:
    """
    A class to handle Reddit data collection for problem validation.
    """
    
    def __init__(self):
        """Initialize the Reddit API client."""
        load_dotenv()
        
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'Micro-SaaS-Validator/1.0')
        )
        
    def find_relevant_subreddits(self, keywords: List[str], limit: int = 5) -> List[str]:
        """
        Search for relevant subreddits based on keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of subreddits to return
            
        Returns:
            List of relevant subreddit names
        """
        subreddits = set()
        for keyword in keywords:
            for subreddit in self.reddit.subreddit('all').search(keyword, limit=limit):
                subreddits.add(subreddit.subreddit.display_name)
        return list(subreddits)[:limit]
    
    def collect_posts(self, subreddit_name: str, 
                     keywords: List[str],
                     time_filter: str = 'month',
                     limit: int = 100,
                     min_score: int = 10) -> List[Dict]:
        """
        Collect posts from a subreddit filtered by keywords and engagement metrics.
        
        Args:
            subreddit_name: Name of the subreddit to collect from
            keywords: List of keywords to filter posts
            time_filter: Time filter for posts (day, week, month, year, all)
            limit: Maximum number of posts to collect
            min_score: Minimum score (upvotes) for posts
            
        Returns:
            List of dictionaries containing post data
        """
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)
        
        for post in subreddit.top(time_filter=time_filter, limit=limit):
            # Check if any keyword is in post title or body
            if any(keyword.lower() in post.title.lower() or 
                  keyword.lower() in post.selftext.lower() 
                  for keyword in keywords):
                
                if post.score >= min_score:
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'content': post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                        'url': post.url,
                        'subreddit': subreddit_name
                    }
                    
                    # Collect top comments
                    post_data['top_comments'] = self._get_top_comments(post)
                    posts.append(post_data)
                    
        return posts
    
    def _get_top_comments(self, post, limit: int = 5) -> List[Dict]:
        """
        Get top comments from a post.
        
        Args:
            post: PRAW post object
            limit: Maximum number of comments to collect
            
        Returns:
            List of dictionaries containing comment data
        """
        comments = []
        post.comments.replace_more(limit=0)  # Remove MoreComments objects
        
        for comment in post.comments[:limit]:
            comments.append({
                'id': comment.id,
                'body': comment.body,
                'score': comment.score,
                'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat()
            })
            
        return comments
