import requests
from typing import List, Dict, Optional
from datetime import datetime, date
import os
import logging
import json
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

def load_api_key() -> Optional[str]:
    """
    Try to load API key from environment variable or tokens file
    """
    # First try environment variable
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if api_key:
        return api_key
    
    # Then try tokens.txt
    try:
        with open('tokens.txt', 'r') as f:
            for line in f:
                if 'ALPHA_VANTAGE_API_KEY' in line:
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        logging.warning("tokens.txt not found")
    except Exception as e:
        logging.warning(f"Error reading tokens.txt: {e}")
    
    return None

def generate_image_prompt(title: str, summary: str) -> str:
    """
    Generates an image prompt directly from the news content.
    
    Args:
        title: The news headline
        summary: The news summary
    
    Returns:
        str: An image generation prompt
    """
    # Clean and combine the text
    combined_text = f"{title}. {summary}"
    
    # Extract the main subject and action from the news
    # Remove common financial jargon to get to the core message
    clean_text = combined_text.replace("according to", "").replace("reported", "")
    
    # Create a simple, direct prompt focusing on the main news point
    prompt = f"Photorealistic visualization of {clean_text}, professional financial photography style"
    
    return prompt

def get_global_market_news() -> List[Dict[str, str]]:
    """
    Fetches and summarizes 5 most recent global market news articles from today.
    
    Returns:
        List[Dict[str, str]]: List of 5 news items, each containing:
            - title: The headline of the news
            - summary: Brief summary of the news
            - date: Publication date
            - time: Publication time
            - image_prompt: Generated prompt for image creation
    """
    api_key = load_api_key()
    if not api_key:
        logging.error("Alpha Vantage API key not found")
        return []
    
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": "financial_markets",
        "sort": "LATEST",
        "limit": 50,
        "apikey": api_key
    }
    
    try:
        logging.info("Fetching news from Alpha Vantage API...")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        # Log the raw response for debugging
        logging.debug(f"Raw API response: {response.text[:500]}...")
        
        data = response.json()
        
        if "feed" not in data:
            if "Note" in data:
                logging.warning(f"API limit message: {data['Note']}")
            logging.error("No 'feed' in response data")
            logging.debug(f"Full response data: {json.dumps(data, indent=2)}")
            return []
        
        # Get today's date
        today = date.today()
        logging.info(f"Filtering news for date: {today}")
        
        # Process and filter today's news items
        news_items = []
        for article in data["feed"]:
            try:
                time_published = article.get("time_published", "")
                if not time_published:
                    continue
                
                pub_datetime = datetime.fromisoformat(time_published)
                
                # Only include articles from today
                if pub_datetime.date() == today:
                    title = article.get("title", "No title available")
                    summary = article.get("summary", "No summary available")
                    news_item = {
                        "title": title,
                        "summary": summary,
                        "date": pub_datetime.strftime("%Y-%m-%d"),
                        "time": pub_datetime.strftime("%H:%M:%S"),
                        "datetime": pub_datetime,  # Used for sorting
                        "image_prompt": generate_image_prompt(title, summary)
                    }
                    news_items.append(news_item)
            except (ValueError, KeyError) as e:
                logging.warning(f"Error processing article: {e}")
                continue
        
        logging.info(f"Found {len(news_items)} news items for today")
        
        if not news_items:
            logging.warning("No news items found for today")
            return []
        
        # Sort by datetime (most recent first) and take top 5
        news_items.sort(key=lambda x: x["datetime"], reverse=True)
        news_items = news_items[:5]
        
        # Remove the datetime field used for sorting
        for item in news_items:
            del item["datetime"]
        
        return news_items
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []

if __name__ == "__main__":
    # Test the function
    news = get_global_market_news()
    if news:
        print("\nTop 5 Most Recent Global Market News Today:")
        print("-" * 50)
        for idx, item in enumerate(news, 1):
            print(f"\n{idx}. {item['title']}")
            print(f"Date: {item['date']}")
            print(f"Time: {item['time']}")
            print(f"Summary: {item['summary']}")
            print(f"\nImage Prompt: {item['image_prompt']}")
            print("-" * 50)
    else:
        print("No news items found for today or there was an error fetching the news.")