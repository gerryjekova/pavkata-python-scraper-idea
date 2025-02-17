# This is my notes and anything important I need to disclose and link connected to the process in this exercise will be most likely noted here.

### 📁 Resources and 🔗links: 
- [LLM Scraper Repo](https://github.com/mishushakov/llm-scraper)
  - [Shortcut to Code-generation feature information -For LLM Scraper-](https://github.com/mishushakov/llm-scraper?tab=readme-ov-file#code-generation)
- []()
- []()
- []()


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
domain.com {
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