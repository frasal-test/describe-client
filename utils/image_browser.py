import os
import json
from flask import Flask, jsonify, render_template_string
from utils.oracle_storage import OracleCloudStorage

"""
Image Browser Flask App

This module provides a web interface for browsing images and their metadata stored in Oracle Cloud Object Storage.
It lists images, displays thumbnails, and shows associated metadata such as description, notes, approval status, and timestamp.

To launch this image browser, run:
    python -m utils.image_browser

This will start a local Flask server for browsing images in your configured Oracle Cloud bucket.
"""

app = Flask(__name__)
storage = OracleCloudStorage()

@app.route('/images')
def list_images():
    # List all objects in the bucket
    objects = storage.object_storage.list_objects(
        namespace_name=storage.namespace,
        bucket_name=storage.bucket_name
    ).data.objects

    images = []
    for obj in objects:
        name = obj.name
        if name.endswith('.metadata.json'):
            continue  # skip metadata files
        # Try to get metadata
        metadata_name = f"{name}.metadata.json"
        try:
            metadata_obj = storage.object_storage.get_object(
                namespace_name=storage.namespace,
                bucket_name=storage.bucket_name,
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
        # Generate a presigned URL for the image (or use a direct link if public)
        image_url = f"/image/{name}"
        images.append({
            "name": name,
            "url": image_url,
            "description": metadata.get("description", ""),
            "note": metadata.get("note", ""),
            "approved": metadata.get("approved", ""),
            "timestamp": metadata.get("timestamp", "")
        })
    return jsonify(images)

@app.route('/image/<path:object_name>')
def get_image(object_name):
    # Stream the image from object storage
    obj = storage.object_storage.get_object(
        namespace_name=storage.namespace,
        bucket_name=storage.bucket_name,
        object_name=object_name
    )
    from flask import Response
    return Response(obj.data.content, mimetype='image/webp')

@app.route('/')
def index():
    # Modern HTML page using Bootstrap 5, with improved column widths and font sizes
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Browser</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8f9fa; }
            .table th, .table td { vertical-align: middle; }
            .img-thumb { max-width: 80px; max-height: 80px; border-radius: 0.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.08);}
            .status-badge { font-size: 1em; }
            .note-cell { max-width: 200px; white-space: pre-line; }
            .desc-cell { min-width: 350px; max-width: 500px; white-space: pre-line; font-size: 1rem; }
            .filename-cell { max-width: 120px; font-size: 0.85em; color: #555; word-break: break-all; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <h1 class="mb-4 text-primary">Image Browser</h1>
            <div class="card shadow-sm">
                <div class="card-body">
                    <table class="table table-hover align-middle" id="images-table">
                        <thead class="table-light">
                            <tr>
                                <th>Thumbnail</th>
                                <th>File Name</th>
                                <th>Description</th>
                                <th>Note</th>
                                <th>Status</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        <script>
            fetch('/images').then(r => r.json()).then(images => {
                const tbody = document.querySelector('#images-table tbody');
                images.forEach(img => {
                    const status = img.approved === true
                        ? '<span class="badge bg-success status-badge">Approved</span>'
                        : (img.approved === false
                            ? '<span class="badge bg-danger status-badge">Rejected</span>'
                            : '<span class="badge bg-secondary status-badge">Pending</span>');
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>
                            <a href="${img.url}" target="_blank" rel="noopener">
                                <img src="${img.url}" alt="thumbnail" class="img-thumb">
                            </a>
                        </td>
                        <td class="filename-cell"><span class="text-monospace">${img.name}</span></td>
                        <td class="desc-cell">${img.description}</td>
                        <td class="note-cell">${img.note}</td>
                        <td>${status}</td>
                        <td><span class="text-muted">${img.timestamp}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
