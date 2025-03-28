from flask import Blueprint, send_from_directory
import os

static_bp = Blueprint("static", __name__)

# Path to the static directory
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

@static_bp.route("/static/<path:filename>", methods=["GET"])
def serve_static(filename):
    """
    Serve static files like badge images
    ---
    tags:
      - Static
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: The requested file
      404:
        description: File not found
    """
    return send_from_directory(STATIC_DIR, filename)