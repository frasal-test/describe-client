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

## Workflow
From examining the code, the application workflow appears to be:

1. User uploads an image through the Gradio interface
2. A unique request ID is generated and tracked
3. The image is temporarily stored locally
4. The image is sent to the server for LLM analysis
5. The image is uploaded to Oracle Cloud Storage
6. The LLM-generated description is displayed to the user
7. User provides feedback (approve/reject) and optional notes
8. Feedback is saved as metadata in Oracle Cloud Storage
9. Temporary files are cleaned up

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

## Technical Details
- Language : Python
- Frontend Framework : Gradio
- Storage : Oracle Cloud Object Storage
- Authentication : Uses environment variables for Oracle Cloud credentials
- Logging : Configured for both file and console output
- License : MIT

## Integration Points
The client integrates with:

1. The server component (for LLM image analysis)
2. Oracle Cloud Storage (for persistent storage)

This client application is designed to be part of a larger system where the server component handles the actual image analysis using multimodal LLMs.