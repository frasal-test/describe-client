import os
import asyncio
import logging
import gradio as gr
import aiofiles
from datetime import datetime
from dotenv import load_dotenv

from utils.oracle_storage import OracleCloudStorage
from utils.llm_service import LLMService
from utils.request_manager import RequestManager
from config import TEMP_DIR, LOGGING_CONFIG, SERVER_HOST, SERVER_PORT

module_name = os.path.basename(__file__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Initialize services
oracle_storage = OracleCloudStorage()
llm_service = LLMService()
request_manager = RequestManager()

# Ensure temp directory exists
TEMP_DIR.mkdir(exist_ok=True)

async def process_image(image):
    """Process the uploaded image"""
    logging.info(f"{module_name} - Starting image processing")
    
    if image is None:
        logging.warning(f"{module_name} - No image provided")
        return None, "Please upload an image or take a photo."
    
    logging.info(f"{module_name} - Image received")
    
    # Create request ID
    request_id = request_manager.create_request()
    logging.info(f"{module_name} - Created new request with ID: {request_id}")
    
    # Generate a new filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{request_id}.jpg"
    temp_path = TEMP_DIR / new_filename
    
    # Save PIL image to temporary file
    image.save(str(temp_path))
    logging.info(f"{module_name} - Saved image to temporary path: {temp_path}")
    
    # Update request with temporary file path
    request_manager.update_request(
        request_id,
        status='image_received',
        temp_path=str(temp_path)
    )
    
    # Upload to Oracle Cloud Storage
    logging.info(f"{module_name} - Uploading image to Oracle Cloud Storage: {temp_path}")
    object_name = await oracle_storage.upload_image(str(temp_path), new_filename)
    if not object_name:
        logging.error(f"{module_name} - Failed to upload image to cloud storage")
        return None, "Failed to upload image to cloud storage."
    
    logging.info(f"{module_name} - Image uploaded successfully to cloud storage as: {object_name}")
    
    # Update request with cloud storage path
    request_manager.update_request(
        request_id,
        status='uploaded_to_cloud',
        cloud_path=object_name
    )
    logging.info(f"{module_name} - Request {request_id} updated with cloud path")
    
    # Get image description from LLM
    logging.info(f"{module_name} - Sending image to LLM for analysis: {temp_path}")
    description = await llm_service.analyze_image(str(temp_path))
    if not description:
        logging.error(f"{module_name} - LLM analysis failed or returned empty description")
        return None, "Failed to analyze image."
    
    logging.info(f"{module_name} - Received description from LLM: {description[:50]}...")
    
    # Update request with LLM description
    request_manager.update_request(
        request_id,
        status='analyzed',
        llm_description=description
    )
    logging.info(f"{module_name} - Request {request_id} updated with description")
    
    logging.info(f"{module_name} - Image processing completed for request: {request_id}")
    return request_id, description

async def save_feedback(request_id, approved, note):
    """Save user feedback and note"""
    if not request_id:
        return "No active request. Please upload an image first."
    
    request = request_manager.get_request(request_id)
    if not request:
        return "Invalid request ID."
    
    # Update request with user feedback
    request_manager.update_request(
        request_id,
        status='feedback_received',
        user_feedback=approved,
        user_note=note
    )
    
    # Save metadata to Oracle Cloud Storage
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'description': request['llm_description'],
        'approved': approved,
        'note': note
    }
    
    success = await oracle_storage.save_metadata(request['cloud_path'], metadata)
    if not success:
        return "Failed to save feedback to cloud storage."
    
    # Clean up temporary file
    request_manager.clean_temp_file(request_id)
    
    # Update request status
    request_manager.update_request(
        request_id,
        status='completed'
    )
    
    return "Thank you for your feedback!" if approved else "Thank you for your feedback. We'll improve our descriptions."

# Create Gradio interface
with gr.Blocks(title="Image Description App") as app:
    gr.Markdown("# Image Description App")
    gr.Markdown("Upload an image or take a photo, and get an AI-generated description.")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Upload or Capture Image", sources=["upload"])
            upload_button = gr.Button("Process Image")
        
        with gr.Column():
            request_id_output = gr.Textbox(visible=False)
            description_output = gr.Textbox(label="Image Description", lines=5)
    
    with gr.Row():
        with gr.Column():
            approve_button = gr.Button("✓ Approve Description")
        with gr.Column():
            reject_button = gr.Button("✗ Reject Description")
    
    note_input = gr.Textbox(label="Additional Notes (Optional)", lines=2)
    feedback_output = gr.Textbox(label="Status")
    
    # New: Acknowledge message row (hidden by default)
    with gr.Row(visible=False) as ack_row:
        ack_message = gr.Markdown("**Recorded**")
        restart_button = gr.Button("Restart")
    
    # Set up event handlers
    def log_and_process_image(img):
        logging.info(f"{module_name} - Upload button clicked - processing image")
        result = asyncio.run(process_image(img))
        logging.info(f"{module_name} - Image processing completed, returning result: {result[1][:30]}...")
        return result

    def log_and_approve_feedback(req_id, note):
        logging.info(f"{module_name} - Approve button clicked - request ID: {req_id}, note: {note[:30] if note else 'None'}")
        result = asyncio.run(save_feedback(req_id, True, note))
        logging.info(f"{module_name} - Feedback saved (approved): {result}")
        return result

    def log_and_reject_feedback(req_id, note):
        logging.info(f"{module_name} - Reject button clicked - request ID: {req_id}, note: {note[:30] if note else 'None'}")
        result = asyncio.run(save_feedback(req_id, False, note))
        logging.info(f"{module_name} - Feedback saved (rejected): {result}")
        return result

    def show_acknowledge(*args):
        # Show the acknowledge row, hide approve/reject buttons, and disable all other inputs/buttons
        return (
            gr.update(visible=True),   # ack_row
            gr.update(visible=False),  # approve_button
            gr.update(visible=False),  # reject_button
            gr.update(interactive=False),  # image_input
            gr.update(interactive=False),  # upload_button
            gr.update(interactive=False),  # note_input
        )

    def reset_ui(*args):
        # Reset all fields, hide acknowledge row, and re-enable all inputs/buttons
        return (
            None,  # image_input
            "",    # request_id_output
            "",    # description_output
            "",    # note_input
            "",    # feedback_output
            gr.update(visible=False),      # ack_row
            gr.update(visible=True, interactive=True),   # approve_button
            gr.update(visible=True, interactive=True),   # reject_button
            gr.update(interactive=True),   # image_input
            gr.update(interactive=True),   # upload_button
            gr.update(interactive=True),   # note_input
        )

    upload_button.click(
        fn=log_and_process_image,
        inputs=[image_input],
        outputs=[request_id_output, description_output]
    )

    approve_button.click(
        fn=log_and_approve_feedback,
        inputs=[request_id_output, note_input],
        outputs=[feedback_output],
        queue=False
    ).then(
        fn=show_acknowledge,
        inputs=[],
        outputs=[ack_row, approve_button, reject_button, image_input, upload_button, note_input]
    )

    reject_button.click(
        fn=log_and_reject_feedback,
        inputs=[request_id_output, note_input],
        outputs=[feedback_output],
        queue=False
    ).then(
        fn=show_acknowledge,
        inputs=[],
        outputs=[ack_row, approve_button, reject_button, image_input, upload_button, note_input]
    )

    restart_button.click(
        fn=reset_ui,
        inputs=[],
        outputs=[
            image_input,
            request_id_output,
            description_output,
            note_input,
            feedback_output,
            ack_row,
            approve_button,
            reject_button,
            image_input,
            upload_button,
            note_input
        ]
    )

if __name__ == "__main__":
    app.launch(server_name=SERVER_HOST, server_port=SERVER_PORT)