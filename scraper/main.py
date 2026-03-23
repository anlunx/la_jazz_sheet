import os
import json
from dotenv import load_dotenv
from fetcher import fetch_all_venues
from parser import parse_venue_data

# Load environment variables from .env file
load_dotenv()

OUTPUT_FILE = "../real_entries/events.json"

def main():
    print("Starting AI Scraping Process...")
    
    venue_data_list = fetch_all_venues()
    all_events = []
    
    for item in venue_data_list:
        print(f"Parsing extracted text for {item['venue']['name']} using AI...")
        events = parse_venue_data(item['venue'], item['raw_html_text'])
        
        if events:
            print(f"Successfully extracted {len(events)} events for {item['venue']['name']}.")
            all_events.extend(events)
        else:
            print(f"Failed to extract real events for {item['venue']['name']}.")
            
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save all events to real_entries/events.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
        
    print(f"\nDone! Scraped to-tal of {len(all_events)} events saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
