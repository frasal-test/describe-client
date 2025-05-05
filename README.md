# Image Description App

A Gradio-based web application for uploading images, generating AI descriptions, and managing feedback.

## Setup

1. Clone the repository
2. Create a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
    pip install -r requirements.txt

4. Create a `.env` file based on `.env.example` with your Oracle Cloud credentials
5. Create a keys directory and place your pem key there
6. Run the application:
    python app.py
7. browse to <your-ip>:3000


## Features

- Upload images or take photos
- Generate AI descriptions
- Provide feedback on descriptions
- Browse images with metadata
- Store images and metadata in Oracle Cloud Storage

## Project Structure

- `app.py`: Main Gradio application
- `utils/`: Utility modules
- `oracle_storage.py`: Oracle Cloud Storage integration
- `llm_service.py`: LLM service for image analysis
- `request_manager.py`: Request tracking and management
- `gradio_image_browser.py`: Gradio-based image browser
- `image_browser.py`: Flask-based image browser
- `config.py`: Application configuration
