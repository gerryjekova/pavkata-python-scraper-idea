from flask import Flask, request, jsonify
from app.queue_manager import TaskManager

app = Flask(__name__)
task_manager = TaskManager()

@app.route('/scrape', methods=['POST'])
def create_scraping_task():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    task_id = task_manager.create_task(url)
    return jsonify({
        'task_id': task_id,
        'status': 'queued'
    })

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    result = task_manager.get_result(task_id)
    if result is None:
        return jsonify({
            'status': 'not_found'
        }), 404
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)