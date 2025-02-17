# This is my notes and anything important I need to disclose and link connected to the process in this exercise will be most likely noted here.

### 📁 Resources and 🔗links: 
- [LLM Scraper Repo](https://github.com/mishushakov/llm-scraper)
  - [Shortcut to Code-generation feature information -For LLM Scraper-](https://github.com/mishushakov/llm-scraper?tab=readme-ov-file#code-generation)
- [Crawl4AI Library](https://github.com/unclecode/crawl4ai)
- [Python Code and Project on Replit](https://replit.com/@gerryjekova/WryWhimsicalGigahertz)
- [Copilot in Github Chat](https://github.com/copilot/share/48490026-00a0-8884-a941-5e49e09228c8)


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

--- 
1. My notes - A json format file that must **dynamically** retrieve extraction rules in a JSON format ? 
> I am a little confused on what that means, but I am assuming it means something like 

``` extraction.json
domain.com: {
    title: 
    content:
    author: 
    publish date: 
    language: 
    categories: 
    media files: { 
        images: 
        videos: 
        embeds: 
    }
}
```

# 2 chat 
```
project/
├── main.py
├── requirements.txt
├── config.py
├── app/
│   ├── __init__.py
│   ├── queue_manager.py
│   ├── schema_generator.py
│   ├── scraper.py
│   └── storage.py
└── rules/
    └── domains/
        └── .gitkeep
```

# 3 implementation 
This implementation includes:

POST /scrape

Accepts URL and optional parameters (headers, timeout)
Returns a task ID and initial status
Validates input and handles errors
Returns 202 Accepted status code
GET /scrape/{task_id}

Returns task status and results
Includes error handling
Returns appropriate HTTP status codes
Provides detailed task information
Additional features:

Proper error handling and logging
Input validation
Structured response models
Clear status tracking
Optional parameter support
Would you like me to:

Add request rate limiting?
Implement authentication?
Add more optional parameters?
Show example API usage?
Let me know what aspect you'd like to focus on next!

To use this system:

Start the Redis server:
bash
redis-server
Start Celery workers:
bash
celery -A main.celery worker --loglevel=info
Start the Flask application:
bash
python main.py


The scraper can be used in two ways:

With Crawl4AI (recommended):
Python
scraper = Scraper(crawl4ai_client=crawl4ai_instance)
result = await scraper.scrape(url, schema)
Direct scraping:
Python
scraper = Scraper()
result = await scraper.scrape(
    url,
    schema,
    headers={'User-Agent': 'Custom UA'},
    timeout=30
)

Project structure after Technical Req:
```
scraper_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── settings.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── scraping.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   ├── scraping.py
│   │   └── task.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py
│   │   ├── queue.py
│   │   └── storage.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_crawler/
│   └── test_queue/
├── alembic/
│   └── versions/
├── pyproject.toml
├── requirements.txt
└── README.md
```