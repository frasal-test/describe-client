import logging
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

module_name = os.path.basename(__file__)

class LLMService:
    def __init__(self):
        """Initialize the LLM service with API details from .env file"""
        self.api_url = os.getenv("LLM_API_URL", "https://api.example.com/analyze")
        self.api_key = os.getenv("LLM_API_KEY", "")
        logging.info(f"{module_name} - LLM service initialized")
    
    async def analyze_image(self, image_path):
        """
        Send an image to the LLM API for analysis
        """
        try:
            logging.info(f"{module_name} - Image received for analysis: {image_path}")
            prompt = "Describe the uploaded image in full detail, applying your expertise as a highly scrupulous image analysis agent. Carefully observe and report every visible element, no matter how small, and provide a thorough, context-aware description. Analyze the relationships, interactions, and possible intentions of objects and subjects in the image. Ensure your description is precise, comprehensive, and avoids assumptions not supported by the image content."
            system_prompt = "You are an expert image analysis agent. Your task is to provide extremely detailed, accurate, and context-aware descriptions of images. You never miss any detail, no matter how small, and you always strive to understand and explain the context, relationships, and concepts present in the image. Your analysis should be thorough, objective, and insightful, covering not only visible objects but also their arrangement, interactions, possible intentions, emotions, and any relevant background information. Always avoid assumptions not supported by the image, and ensure your description is clear, precise, and comprehensive."

            data = aiohttp.FormData()
            data.add_field('prompt', prompt)
            data.add_field('system_prompt', system_prompt)
            data.add_field('max_tokens', '4000')
            data.add_field('temperature', '0.5')
            data.add_field('images', open(image_path, 'rb'), filename=os.path.basename(image_path), content_type='image/png')

            headers = {
                'X-API-Key': self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('output', '')
                    else:
                        logging.error(f"{module_name} - LLM API error: {response.status}")
                        return None
        except Exception as e:
            logging.error(f"{module_name} - Failed to analyze image {image_path}: {str(e)}")
            return None