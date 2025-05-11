"""
Task worker for processing validation requests asynchronously.
"""
import os
import json
import signal
import sys
import time
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

from .message_queue import MessageQueue
from ..data_collection.reddit_collector import RedditCollector
from ..analyzer.sentiment_analyzer import SentimentAnalyzer
from ..storage_service.mongodb_storage import StorageService
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class TaskWorker:
    """Worker for processing validation tasks from the message queue."""

    def __init__(self):
        """Initialize the task worker with required services."""
        load_dotenv()
        
        self.message_queue = MessageQueue()
        self.reddit_collector = RedditCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.storage_service = StorageService()
        self.should_stop = False

    def start(self):
        """Start processing tasks from the queue."""
        logger.info("Starting validation task worker")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

        try:
            # Connect to message queue
            self.message_queue.connect()
            self.message_queue.declare_queue("validation_tasks")
            
            # Start consuming messages with retry handling
            self.message_queue.consume("validation_tasks", self.process_task_with_retry)
            
            # Keep the worker running
            while not self.should_stop:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Worker startup failed: {str(e)}")
            sys.exit(1)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal, stopping worker...")
        self.should_stop = True
        self.message_queue.close()
        sys.exit(0)

    def process_task(self, message: Dict[str, Any]):
        """
        Process a validation task.
        
        Args:
            message: Task message containing problem details
        """
        problem_id = message.get("problem_id")
        problem = message.get("problem")
        
        if not problem_id or not problem:
            logger.error("Invalid task message format")
            return

        try:
            logger.info(f"Processing validation task {problem_id}")
            
            # Collect data from Reddit
            posts = self.reddit_collector.collect_posts(
                subreddit_name="startups",  # Could be configurable
                keywords=problem["keywords"],
                time_filter="year",
                limit=100
            )

            # Analyze collected data
            analysis_result = self.sentiment_analyzer.analyze_problem_validation(posts)

            # Store result
            result = {
                "problem_id": problem_id,
                "timestamp": datetime.utcnow().isoformat(),
                "sentiment_summary": analysis_result["sentiment_summary"],
                "engagement_metrics": analysis_result["engagement_metrics"],
                "temporal_analysis": analysis_result["temporal_analysis"],
                "validation_score": analysis_result["validation_score"],
                "confidence_score": analysis_result.get("confidence_score", 0.0),
                "validation_flags": analysis_result.get("validation_flags", []),
                "relevant_posts": posts
            }
            
            self.storage_service.store_validation_result(problem_id, result)
            logger.info(f"Validation task {problem_id} completed successfully")

        except Exception as e:
            logger.error(f"Error processing task {problem_id}: {str(e)}", exc_info=True)
            # Store error status
            error_result = {
                "problem_id": problem_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            self.storage_service.store_validation_result(problem_id, error_result)

    def process_task_with_retry(self, message: Dict[str, Any], max_retries: int = 3, retry_delay: int = 5):
        """
        Process a task with automatic retries on failure.
        
        Args:
            message: Task message to process
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        attempt = 0
        last_error = None

        while attempt < max_retries:
            try:
                self.process_task(message)
                return  # Success, exit retry loop
            except Exception as e:
                attempt += 1
                last_error = e
                if attempt < max_retries:
                    logger.warning(
                        f"Task {message.get('problem_id')} failed (attempt {attempt}/{max_retries}): {str(e)}"
                        f" Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        f"Task {message.get('problem_id')} failed after {max_retries} attempts: {str(e)}",
                        exc_info=True
                    )
                    # Store final failure status
                    self.store_error_result(message.get('problem_id'), str(e))
                    
    def store_error_result(self, problem_id: str, error_message: str):
        """Store error result in storage service."""
        if not problem_id:
            return
            
        error_result = {
            "problem_id": problem_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": error_message
        }
        try:
            self.storage_service.store_validation_result(problem_id, error_result)
        except Exception as e:
            logger.error(f"Failed to store error result: {str(e)}", exc_info=True)

if __name__ == "__main__":
    worker = TaskWorker()
    worker.start()
