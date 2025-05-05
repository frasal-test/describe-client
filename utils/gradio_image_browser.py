import os
import json
import gradio as gr
from utils.oracle_storage import OracleCloudStorage

"""
Gradio Image Browser

This module provides a web interface for browsing images and their metadata stored in Oracle Cloud Object Storage.
It displays images in a gallery view with associated metadata such as description, notes, approval status, and timestamp.

To launch this image browser, run:
    python -m utils.gradio_image_browser

This will start a Gradio web server for browsing images in your configured Oracle Cloud bucket.
"""

class GradioImageBrowser:
    def __init__(self):
        self.storage = OracleCloudStorage()
        
    def get_images(self):
        """Fetch all images and their metadata from Oracle Cloud Storage"""
        # List all objects in the bucket
        objects = self.storage.object_storage.list_objects(
            namespace_name=self.storage.namespace,
            bucket_name=self.storage.bucket_name
        ).data.objects

        gallery_images = []
        image_paths = []
        metadata_list = []
        
        for obj in objects:
            name = obj.name
            if name.endswith('.metadata.json'):
                continue  # skip metadata files
                
            # Try to get metadata
            metadata_name = f"{name}.metadata.json"
            try:
                metadata_obj = self.storage.object_storage.get_object(
                    namespace_name=self.storage.namespace,
                    bucket_name=self.storage.bucket_name,
                    object_name=metadata_name
                )
                metadata = json.loads(metadata_obj.data.content.decode('utf-8'))
            except Exception:
                metadata = {
                    "timestamp": "",
                    "description": "",
                    "approved": "",
                    "note": ""
                }
            
            # Get the image data
            image_obj = self.storage.object_storage.get_object(
                namespace_name=self.storage.namespace,
                bucket_name=self.storage.bucket_name,
                object_name=name
            )
            
            # Save image to a temporary file
            temp_path = f"/tmp/{name}"
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(image_obj.data.content)
            
            # Format the caption with just the filename for the gallery
            caption = f"{name}"
            
            # Store image path and caption as a tuple for the gallery
            gallery_images.append((temp_path, caption))
            
            # Also keep separate lists for the selected image display
            image_paths.append(temp_path)
            metadata_list.append({
                "filename": name,
                "description": metadata.get("description", ""),
                "note": metadata.get("note", ""),
                "approved": metadata.get("approved", ""),
                "timestamp": metadata.get("timestamp", "")
            })
            
        return gallery_images, image_paths, metadata_list
    
    def launch(self):
        """Launch the Gradio interface"""
        gallery_images, image_paths, metadata_list = self.get_images()
        
        with gr.Blocks(title="Image Browser", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# Image Browser")
            
            with gr.Row():
                gallery = gr.Gallery(
                    value=gallery_images,
                    label="Images",
                    columns=4,
                    rows=3,
                    object_fit="contain",
                    height="auto",
                    show_label=False,
                    elem_id="gallery"
                )
            
            with gr.Row():
                with gr.Column(scale=2):
                    selected_image = gr.Image(
                        label="Selected Image", 
                        elem_id="selected-image",
                        show_label=True,
                        height=400
                    )
                
                with gr.Column(scale=1):
                    filename_display = gr.Textbox(label="Filename", interactive=False)
                    description_display = gr.TextArea(label="Description", interactive=False, lines=4)
                    note_display = gr.TextArea(label="Notes", interactive=False, lines=3)
                    status_display = gr.Textbox(label="Status", interactive=False)
                    timestamp_display = gr.Textbox(label="Timestamp", interactive=False)
            
            def select_image(evt: gr.SelectData):
                index = evt.index
                metadata = metadata_list[index]
                
                # Format the status with emoji
                status_text = "✅ Approved" if metadata["approved"] == True else "❌ Rejected" if metadata["approved"] == False else "⏳ Pending"
                
                return [
                    image_paths[index],
                    metadata["filename"],
                    metadata["description"],
                    metadata["note"],
                    status_text,
                    metadata["timestamp"]
                ]
            
            gallery.select(
                select_image, 
                None, 
                [
                    selected_image, 
                    filename_display, 
                    description_display, 
                    note_display, 
                    status_display, 
                    timestamp_display
                ]
            )
        
        # Launch the interface
        demo.launch(share=False)

if __name__ == "__main__":
    browser = GradioImageBrowser()
    browser.launch()