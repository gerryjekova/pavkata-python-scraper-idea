from crawl4ai import Crawler
from crawl4ai.config import BrowserConfig, CrawlerRunConfig

def test_crawler():
    try:
        # Initialize crawler
        browser_config = BrowserConfig(headless=True)
        crawler = Crawler(browser_config=browser_config)
        
        # Test simple crawl
        run_config = CrawlerRunConfig(
            url="https://example.com",
            max_pages=1
        )
        
        # Run crawler
        result = crawler.run(run_config)
        print("Crawler test successful!")
        print("Result:", result)
        
    except Exception as e:
        print("Crawler test failed:", str(e))

if __name__ == "__main__":
    test_crawler()