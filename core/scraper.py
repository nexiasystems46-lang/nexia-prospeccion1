import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def scrape_website(url):
    if not FIRECRAWL_API_KEY:
        raise ValueError("FIRECRAWL_API_KEY is missing in environment variables.")
        
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        # Scrape a single URL using Firecrawl
        scrape_result = app.scrape_url(url, params={'formats': ['markdown']})
        
        # Depending on firecrawl version, response might vary
        if isinstance(scrape_result, dict):
            return scrape_result.get('markdown', '')
        return str(scrape_result)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
