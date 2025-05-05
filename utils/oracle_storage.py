import os
import json
import logging
import oci
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

module_name = os.path.basename(__file__)

class OracleCloudStorage:
    def __init__(self):
        """Initialize Oracle Cloud Storage client with credentials from .env file"""
        try:
            self.config = {
                "user": os.getenv("OCI_USER"),
                "key_file": os.getenv("OCI_KEY_FILE"),
                "fingerprint": os.getenv("OCI_FINGERPRINT"),
                "tenancy": os.getenv("OCI_TENANCY"),
                "region": os.getenv("OCI_REGION")
            }
            
            self.namespace = os.getenv("OCI_NAMESPACE")
            self.bucket_name = os.getenv("OCI_BUCKET_NAME")
            
            # Initialize the Object Storage client
            self.object_storage = oci.object_storage.ObjectStorageClient(self.config)
            
            logging.info(f"{module_name} - Oracle Cloud Storage client initialized successfully")
        except Exception as e:
            logging.error(f"{module_name} - Failed to initialize Oracle Cloud Storage client: {str(e)}")
            raise
    
    async def upload_image(self, file_path, object_name=None):
        """
        Upload an image to Oracle Cloud Object Storage
        
        Args:
            file_path (str): Path to the image file
            object_name (str, optional): Name to use for the object in storage
                                        If None, uses the filename
        
        Returns:
            str: Object name in storage if successful
            None: If upload fails
        """
        try:
            if not object_name:
                object_name = Path(file_path).name
            
            with open(file_path, 'rb') as file_data:
                self.object_storage.put_object(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    put_object_body=file_data.read()
                )
            
            logging.info(f"{module_name} - Successfully uploaded {file_path} to {object_name}")
            return object_name
        except Exception as e:
            logging.error(f"{module_name} - Failed to upload {file_path}: {str(e)}")
            return None
    
    async def save_metadata(self, object_name, metadata):
        """
        Save metadata for an image in Oracle Cloud Object Storage
        
        Args:
            object_name (str): Name of the object in storage
            metadata (dict): Metadata to save
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            metadata_object_name = f"{object_name}.metadata.json"
            metadata_json = json.dumps(metadata).encode('utf-8')
            
            self.object_storage.put_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=metadata_object_name,
                put_object_body=metadata_json
            )
            
            logging.info(f"{module_name} - Successfully saved metadata for {object_name}")
            return True
        except Exception as e:
            logging.error(f"{module_name} - Failed to save metadata for {object_name}: {str(e)}")
            return False