from flask import Flask, request, jsonify
import logging
from app.queue.task_manager import TaskManager
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
task_manager = TaskManager(Config.REDIS_URL, Config.CRAWL4AI_CLIENT)

@app.route('/scrape', methods=['POST'])
def create_scraping_task():
    """
    Create a new scraping task
    
    Expected payload:
    {
        "url": "https://example.com",
        "headers": {                # Optional
            "User-Agent": "Custom"
        }
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
        
        # Create task
        headers = data.get('headers')
        task_id = task_manager.create_task(url, headers)
        
        return jsonify({
            "task_id": task_id,
            "status": "queued",
            "message": "Task created successfully"
        }), 202
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/scrape/<task_id>', methods=['GET'])
def get_scraping_result(task_id: str):
    """
    Get the status and result of a scraping task
    """
    try:
        task_data = task_manager.get_task(task_id)
        
        if not task_data:
            return jsonify({
                "error": "Task not found",
                "task_id": task_id
            }), 404
        
        response = {
            "task_id": task_id,
            "status": task_data['status'],
            "created_at": task_data['created_at'],
            "updated_at": task_data['updated_at']
        }
        
        if 'completed_at' in task_data:
            response['completed_at'] = task_data['completed_at']
        
        if task_data['status'] == 'completed':
            response['result'] = task_data['result']
        elif task_data['status'] == 'failed':
            response['error'] = task_data['error']
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching task result: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)