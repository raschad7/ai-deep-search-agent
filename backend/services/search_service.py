import os
import trafilatura
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def get_search_results(query):
    api_key = os.getenv("TAVILY_API_KEY")

    try:
        tavily = TavilyClient(api_key=api_key)
        
        print(f"Tavily is finding links for: '{query}'...")

        # Get the links from Tavily
        response = tavily.search(
            query=query, 
            search_depth="basic", 
            max_results=3,
            exclude_domains=["youtube.com", "vimeo.com", "tiktok.com"]
        )
        
        results = response.get("results", [])
        if not results:
            return []

        # Visit each link and extract CLEAN text
        cleaned_results = []
        
        for i, res in enumerate(results, 1):
            url = res.get('url')
            title = res.get('title')
            
            print(f"\n Scraping Source {i}: {url}...")
            
            # Download the page
            downloaded = trafilatura.fetch_url(url)
            
            # Extract the useful text
            clean_text = trafilatura.extract(downloaded)
            
            if clean_text:
                print(f"Successfully scraped {len(clean_text)} chars from {url}")
                pass
            else:
                print(f"Could not scrape {url}, using snippet.")
                clean_text = res.get('content', 'No content available.')

            cleaned_results.append({
                "source_id": i,
                "title": title,
                "url": url,
                "content": clean_text
            })
            
        return cleaned_results

    except Exception as e:
        print(f" Error: {e}")
        return []
