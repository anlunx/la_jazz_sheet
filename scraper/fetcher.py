import requests
from bs4 import BeautifulSoup

# Define our target venues for the proof of concept
VENUES = [
    {
        "id": "sam_first",
        "name": "Sam First",
        "address": "6171 W Century Blvd #180, Los Angeles, CA 90045",
        "url": "https://www.samfirstbar.com/upcoming-shows"
    },
    {
        "id": "baked_potato",
        "name": "The Baked Potato",
        "address": "3787 Cahuenga Blvd, Studio City, CA 91604",
        "url": "https://www.thebakedpotato.com/events-calendar/"
    }
]

def fetch_raw_text(url):
    """Fetches the webpage and extracts all visible text, stripping heavy HTML."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Use BeautifulSoup to strip scripts, styles, and extract raw text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        # Limit text length to avoid token limits, usually events are in the first 20k chars
        return text[:20000] 
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_all_venues():
    results = []
    for venue in VENUES:
        print(f"Fetching raw data for {venue['name']}...")
        raw_text = fetch_raw_text(venue['url'])
        if raw_text:
            results.append({
                "venue": venue,
                "raw_html_text": raw_text
            })
    return results
