from flask import Blueprint, jsonify, current_app
import subprocess
import sys
import os
from src.models import db
from src.services.achievement_service import AchievementService

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/generate-sample-data', methods=['POST'])
def generate_sample_data():
    """
    Generate Sample Data
    ---
    tags:
      - Admin
    summary: Triggers the generation of sample data
    description: |
      Executes a script to populate the database with sample data.
      This is an asynchronous process and the response will indicate if the process started.
    responses:
      200:
        description: Sample data generation process started successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Sample data generation completed successfully."
                output:
                  type: string
                  example: "Output from the script..."
      500:
        description: Failed to start or complete sample data generation.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Failed to generate sample data."
                error:
                  type: string
                  example: "Error details..."
                stdout:
                  type: string
                  example: "stdout from script if error..."
    """
    # Construct the absolute path to the script
    # Assuming this admin_routes.py is in src/routes/
    # And the script is in src/scripts/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, '..', 'scripts', 'generate_sample_data_2_with_import.py')

    try:
        # Ensure the script is executable and run it, explicitly setting encoding for output
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.join(current_dir, '..', 'scripts'),
            encoding='utf-8'  # Add this line
        )
        return jsonify({"message": "Sample data generation completed successfully.", "output": result.stdout}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": "Failed to generate sample data.", "error": e.stderr, "stdout": e.stdout}), 500
    except FileNotFoundError:
        return jsonify({"message": "Error: Script not found.", "script_path": script_path}), 500
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred.", "error": str(e)}), 500

@admin_bp.route('/clear-database', methods=['POST'])
def clear_database():
    """
    Clear Database
    ---
    tags:
      - Admin
    summary: Clears all data from the database
    description: |
      Drops all tables, recreates them based on the current models,
      and re-initializes default data (e.g., achievements).
      USE WITH CAUTION - THIS IS A DESTRUCTIVE OPERATION.
    responses:
      200:
        description: Database cleared and initialized successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Database cleared and initialized successfully."
      500:
        description: Failed to clear the database.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Failed to clear database."
                error:
                  type: string
                  example: "Error details..."
    """
    try:
        with current_app.app_context():
            db.drop_all()
            db.create_all()
            # Re-initialize achievements or any other default data setup
            AchievementService.initialize_achievements()
            print("Database cleared and achievements re-initialized successfully.")
        return jsonify({"message": "Database cleared and initialized successfully."}), 200
    except Exception as e:
        print(f"Error clearing database: {str(e)}")
        return jsonify({"message": "Failed to clear database.", "error": str(e)}), 500
