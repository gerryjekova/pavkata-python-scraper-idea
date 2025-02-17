from flask import Flask, request, jsonify
from app.queue_manager import TaskManager
from app.models import TaskStatus, TaskResponse
from datetime import datetime
import uuid
from typing import Optional
import logging

app = Flask(__name__)
task_manager = TaskManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/scrape', methods=['POST'])
def create_scraping_task():
    """
    Create a new scraping task
    
    Expected JSON payload:
    {
        "url": "https://example.com/article",
        "headers": {                    # Optional
            "User-Agent": "Custom UA"
        },
        "timeout": 30                   # Optional
    }
    """
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Extract optional parameters
        custom_headers = data.get('headers', {})
        timeout = data.get('timeout', 30)
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task with parameters
        task_manager.create_task(
            task_id=task_id,
            url=url,
            headers=custom_headers,
            timeout=timeout
        )
        
        # Create response
        response = TaskResponse(
            task_id=task_id,
            status=TaskStatus.QUEUED,
            created_at=datetime.utcnow()
        )
        
        return jsonify(response.to_dict()), 202

    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/scrape/<task_id>', methods=['GET'])
def get_scraping_result(task_id: str):
    """
    Get the result of a scraping task
    
    Parameters:
        task_id: UUID of the task to check
    """
    try:
        # Validate task_id format
        try:
            uuid.UUID(task_id)
        except ValueError:
            return jsonify({"error": "Invalid task ID format"}), 400
        
        # Get task result
        result = task_manager.get_result(task_id)
        
        if result is None:
            return jsonify({
                "error": "Task not found",
                "task_id": task_id
            }), 404
        
        return jsonify(result.to_dict()), 200

    except Exception as e:
        logger.error(f"Error fetching task result: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)