import os
import json
from google import genai
from google.genai import types

def parse_venue_data(venue_info, raw_text):
    """
    Sends the raw text to the Gemini API and asks it to extract jazz events matching our strict schema.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_actual_api_key_here":
        print(f"⚠️ Mocking LLM response for {venue_info['name']} because GEMINI_API_KEY is not set.")
        # Return mock data matching our schema if no key exists
        return [{
            "date": "2026-03-28",
            "time": "8:00 PM",
            "artist": f"Mocking Artist at {venue_info['name']}",
            "venue": {
                "name": venue_info["name"],
                "address": venue_info["address"]
            },
            "personnel": [
                {"name": "Mock Musician", "instrument": "Piano"}
            ],
            "priceRange": "$25",
            "ticketLink": venue_info["url"]
        }]

    # Try standard model setup
    try:
        client = genai.Client() # Assumes GEMINI_API_KEY is an environment variable
        
        prompt = f"""
        You are an expert data extractor. I am giving you raw, messy text scraped from the website of a jazz club.
        The club is: {venue_info['name']} located at {venue_info['address']}.
        
        Extract all upcoming jazz performances and output them as a JSON array EXACTLY matching this schema:
        [
          {{
            "date": "YYYY-MM-DD",
            "time": "HH:MM PM",
            "artist": "Main Artist or Band Name",
            "venue": {{
              "name": "{venue_info['name']}",
              "address": "{venue_info['address']}"
            }},
            "personnel": [
              {{ "name": "Musician Name", "instrument": "Instrument played" }}
            ],
            "priceRange": "$XX",
            "ticketLink": "URL to buy tickets if found, else Use {venue_info['url']}"
          }}
        ]
        
        CRITICAL RULES:
        1. Extract the full band personnel if it is listed in the text! This is the most important feature.
        2. Attempt to infer standard jazz instruments if not explicitly listed but obvious from context.
        3. Make sure dates are in YYYY-MM-DD format based on the current year (assume 2026).
        4. ONLY return the raw valid JSON array. Do not include markdown codeblocks (no ```json). 
        
        RAW TEXT:
        {raw_text}
        """

        # Generate response using gemini-2.5-flash which is fast and great for structured data
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            )
        )
        
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        # Parse the JSON string
        events = json.loads(response_text)
        return events

    except Exception as e:
        print(f"Error parsing data with LLM for {venue_info['name']}: {e}")
        return []
