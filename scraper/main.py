import os
import json
from dotenv import load_dotenv
from fetcher import fetch_all_venues
from parser import parse_venue_data

# Load environment variables from .env file
load_dotenv()

OUTPUT_FILE = "../real_entries/events.json"
REPORT_FILE = "email_report.txt"

def get_event_key(event):
    """Creates a unique identifier for an event to check for duplicates."""
    return f"{event.get('date', '')}_{event.get('artist', '')}_{event.get('time', '')}_{event.get('venue', {}).get('name', '')}"

def main():
    print("Starting AI Scraping Process...")
    
    # Load existing events to diff against
    existing_events = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_events = json.load(f)
        except Exception as e:
            print(f"Error loading existing events: {e}")
            
    existing_keys = {get_event_key(e) for e in existing_events}
    
    venue_data_list = fetch_all_venues()
    all_events = []
    new_events = []
    
    for item in venue_data_list:
        print(f"Parsing extracted text for {item['venue']['name']} using AI...")
        events = parse_venue_data(item['venue'], item['raw_html_text'])
        
        if events:
            print(f"Successfully extracted {len(events)} events for {item['venue']['name']}.")
            for e in events:
                all_events.append(e)
                if get_event_key(e) not in existing_keys:
                    new_events.append(e)
                    
        else:
            print(f"Failed to extract real events for {item['venue']['name']}.")
            
    # Guarantee we sort all events chronologically
    all_events.sort(key=lambda x: f"{x.get('date', '9999-99-99')}T{x.get('time', '00:00')}")
            
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Save ALL events to real_entries/events.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
        
    print(f"\nDone! Scraped total of {len(all_events)} events saved to {OUTPUT_FILE}")
    print(f"Found {len(new_events)} completely new events.")
    
    # Build the email report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        if not new_events:
            f.write("Scraper Report: No new shows were added to the calendar today.\n")
        else:
            f.write(f"Scraper Report: {len(new_events)} NEW shows added to the LA Jazz Sheet!\n\n")
            for e in new_events:
                f.write(f"- {e.get('date')} at {e.get('time')}: {e.get('artist')} @ {e.get('venue', {}).get('name', 'Unknown')}\n")
                if "personnel" in e and e["personnel"]:
                    personnel_str = ", ".join([f"{p.get('name')} ({p.get('instrument')})" for p in e["personnel"]])
                    f.write(f"  Lineup: {personnel_str}\n")
                f.write(f"  Tickets: {e.get('ticketLink', '#')}\n\n")

if __name__ == "__main__":
    main()
