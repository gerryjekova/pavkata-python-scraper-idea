# GITHUB COPILOT MD: 
### Exercise breakdown & solutions

> 1. Project Overview
>> The goal of this project is to develop a Python-based API that accepts a URL as input and returns scraped content from a news/media website. The scraper must dynamically generate or retrieve extraction rules (in JSON format) for each domain and then extract the following media fields (if available):

- **Title**
- **Content**
- **Author**
- **Publish Date**
- **Language**
- **Categories** (multiple allowed)
- **Media Files**:
  - Images
  - Videos
  - Embeds

### Solution

#### 1. Set up the project

1. Create a new Python project.
2. Set up a virtual environment for the project.
3. Install necessary packages such as `requests`, `beautifulsoup4`, and `flask`.

```bash
mkdir news_scraper
cd news_scraper
python -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 flask
```

#### 2. Create the Flask API

1. Create a new file named `app.py` to define the API endpoints.

```python name=app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Scraping logic will be implemented here

    return jsonify({'message': 'Scraping successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)
```

#### 3. Implement the scraper

1. Create a new file named `scraper.py` to handle the scraping logic.

```python name=scraper.py
import requests
from bs4 import BeautifulSoup

def get_extraction_rules(domain):
    # Logic to retrieve or generate extraction rules for the domain
    return {
        'title': {'tag': 'h1', 'class': 'article-title'},
        'content': {'tag': 'div', 'class': 'article-content'},
        'author': {'tag': 'span', 'class': 'author-name'},
        'publish_date': {'tag': 'time', 'class': 'publish-date'},
        'language': {'tag': 'html', 'attr': 'lang'},
        'categories': {'tag': 'a', 'class': 'category-link'},
        'media_files': {
            'images': {'tag': 'img', 'attr': 'src'},
            'videos': {'tag': 'video', 'attr': 'src'},
            'embeds': {'tag': 'iframe', 'attr': 'src'}
        }
    }

def scrape_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    domain = url.split('/')[2]
    rules = get_extraction_rules(domain)
    
    data = {}
    for field, rule in rules.items():
        if field == 'media_files':
            data[field] = {}
            for media_type, media_rule in rule.items():
                data[field][media_type] = [tag.get(media_rule['attr']) for tag in soup.find_all(media_rule['tag'])]
        else:
            tag = soup.find(rule['tag'], class_=rule['class'])
            if tag:
                data[field] = tag.get_text() if field != 'language' else tag.get(rule['attr'])
            else:
                data[field] = None

    return data
```

#### 4. Integrate the scraper with the API

1. Update `app.py` to use the scraper.

```python name=app.py
from flask import Flask, request, jsonify
from scraper import scrape_content

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Scraping logic
    try:
        scraped_data = scrape_content(url)
        return jsonify(scraped_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

#### 5. Test the API

1. Run the Flask application.

```bash
python app.py
```

2. Test the API using a tool like Postman or cURL.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/article"}' http://127.0.0.1:5000/scrape
```

#### 6. Improve the scraper (optional)

1. Add more sophisticated extraction rules.
2. Handle different types of content and edge cases.
3. Add error handling and logging.
```` ▋