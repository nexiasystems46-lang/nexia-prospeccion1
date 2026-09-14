import os
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def search_businesses(query, limit=5):
    if not APIFY_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY is missing in environment variables.")

    client = ApifyClient(APIFY_API_KEY)
    
    # We use the popular compass/google-maps-scraper (or apify/google-maps-scraper)
    # The id 'compass/google-maps-scraper' might be an alias. The official one is 'compass/google-maps-scraper'
    # Actually, a safer bet is 'compass/google-maps-extractor' or 'drobnikj/crawler-google-places'
    # Let's use 'compass/google-maps-scraper'
    
    run_input = {
        "searchStringsArray": [query],
        "maxCrawledPlacesPerSearch": limit,
        "language": "es",
    }

    print(f"Searching Apify for: {query} (Limit: {limit})")
    # Using the standard apify google maps scraper
    run = client.actor("apify/google-maps-scraper").call(run_input=run_input)
    
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        if item.get("website"):
            results.append({
                "title": item.get("title", ""),
                "website": item.get("website", ""),
                "phone": item.get("phone", "")
            })
            
    return results
