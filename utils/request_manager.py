import logging
import asyncio
import uuid
import os
from pathlib import Path

module_name = os.path.basename(__file__)

class RequestManager:
    def __init__(self):
        """Initialize the request manager to track concurrent requests"""
        self.requests = {}  # Dictionary to track all requests
        logging.info(f"{module_name} - Request manager initialized")
    
    def create_request(self):
        """
        Create a new request with a unique ID
        
        Returns:
            str: Unique request ID
        """
        request_id = str(uuid.uuid4())
        self.requests[request_id] = {
            'status': 'created',
            'temp_path': None,
            'cloud_path': None,
            'llm_description': None,
            'user_feedback': None,
            'user_note': None
        }
        logging.info(f"{module_name} - Created new request with ID: {request_id}")
        return request_id
    
    def update_request(self, request_id, **kwargs):
        """
        Update a request with new information
        
        Args:
            request_id (str): ID of the request to update
            **kwargs: Key-value pairs to update in the request
        
        Returns:
            bool: True if successful, False otherwise
        """
        if request_id not in self.requests:
            logging.error(f"{module_name} - Request ID {request_id} not found")
            return False
        
        for key, value in kwargs.items():
            self.requests[request_id][key] = value
        
        logging.info(f"{module_name} - Updated request {request_id}: {kwargs}")
        return True
    
    def get_request(self, request_id):
        """
        Get information about a request
        
        Args:
            request_id (str): ID of the request
        
        Returns:
            dict: Request information
            None: If request not found
        """
        if request_id not in self.requests:
            logging.error(f"{module_name} - Request ID {request_id} not found")
            return None
        
        return self.requests[request_id]
    
    def clean_temp_file(self, request_id):
        """
        Delete the temporary file associated with a request
        
        Args:
            request_id (str): ID of the request
        
        Returns:
            bool: True if successful, False otherwise
        """
        request = self.get_request(request_id)
        if not request or not request['temp_path']:
            return False
        
        try:
            temp_path = request['temp_path']
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logging.info(f"{module_name} - Deleted temporary file: {temp_path}")
            return True
        except Exception as e:
            logging.error(f"{module_name} - Failed to delete temporary file: {str(e)}")
            return False