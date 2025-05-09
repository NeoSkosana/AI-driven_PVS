from typing import List, Dict, Optional
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

class StorageService:
    """
    A class to handle data storage and retrieval using MongoDB.
    """
    
    def __init__(self):
        """Initialize MongoDB connection."""
        load_dotenv()
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongodb_uri)
        self.db = self.client['problem_validation']
        
    def store_collected_data(self, data: Dict, problem_id: str) -> str:
        """
        Store collected data with analysis results.
        
        Args:
            data: Dictionary containing collected posts and analysis results
            problem_id: Unique identifier for the problem statement
            
        Returns:
            ID of the stored document
        """
        collection = self.db.collected_data
        
        document = {
            'problem_id': problem_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    def get_problem_data(self, problem_id: str) -> Optional[Dict]:
        """
        Retrieve collected data for a specific problem.
        
        Args:
            problem_id: Unique identifier for the problem statement
            
        Returns:
            Dictionary containing the stored data or None if not found
        """
        collection = self.db.collected_data
        document = collection.find_one({'problem_id': problem_id})
        
        return document if document else None
    
    def update_analysis_results(self, problem_id: str, analysis_results: Dict) -> bool:
        """
        Update analysis results for a specific problem.
        
        Args:
            problem_id: Unique identifier for the problem statement
            analysis_results: New analysis results to store
            
        Returns:
            True if update was successful, False otherwise
        """
        collection = self.db.collected_data
        
        result = collection.update_one(
            {'problem_id': problem_id},
            {
                '$set': {
                    'data.analysis_results': analysis_results,
                    'last_updated': datetime.utcnow().isoformat()
                }
            }
        )
        
        return result.modified_count > 0
    
    def list_problems(self, limit: int = 100) -> List[Dict]:
        """
        List all problem statements with their latest analysis results.
        
        Args:
            limit: Maximum number of problems to return
            
        Returns:
            List of dictionaries containing problem data
        """
        collection = self.db.collected_data
        
        problems = collection.find(
            {},
            {'problem_id': 1, 'timestamp': 1, 'data.analysis_results': 1}
        ).limit(limit)
        
        return list(problems)
    
    def delete_problem_data(self, problem_id: str) -> bool:
        """
        Delete all data associated with a problem statement.
        
        Args:
            problem_id: Unique identifier for the problem statement
            
        Returns:
            True if deletion was successful, False otherwise
        """
        collection = self.db.collected_data
        
        result = collection.delete_one({'problem_id': problem_id})
        return result.deleted_count > 0
