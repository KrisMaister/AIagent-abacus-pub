import requests
import json
from datetime import datetime, timedelta
import base64
import random

def read_secrets():
    """Read secrets from tokens_secret.txt file"""
    try:
        with open('tokens_secret.txt', 'r') as f:
            content = f.read()
            decoded = base64.b64decode(content).decode('utf-8')
            secrets = {}
            for line in decoded.splitlines():
                if line.startswith('export '):
                    key, value = line.replace('export ', '').split('=', 1)
                    secrets[key] = value.strip('"')
            return secrets
    except Exception as e:
        print(f"Error reading secrets file: {str(e)}")
        return {}

def search_news(query):
    """
    Search for recent news articles related to the query
    """
    secrets = read_secrets()
    news_api_key = secrets.get('NEWS_API_KEY')
    
    if not news_api_key:
        print("Error: NEWS_API_KEY not found in secrets file")
        return None

    # Calculate date range (last 3 days for more recent news)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    # Format dates for API
    from_date = start_date.strftime('%Y-%m-%d')
    to_date = end_date.strftime('%Y-%m-%d')

    # Prepare search terms for Polish election news
    search_terms = [
        'Poland presidential election 2024',
        'Polish election Tusk',
        'Poland politics election',
        'Polish opposition election',
        'Poland voting 2024'
    ]

    all_articles = []
    
    # NewsAPI endpoint for top headlines
    headlines_url = 'https://newsapi.org/v2/top-headlines'
    everything_url = 'https://newsapi.org/v2/everything'

    print("\nSearching for news...")
    
    # First try top headlines for Poland
    params = {
        'country': 'pl',
        'category': 'politics',
        'apiKey': news_api_key,
        'pageSize': 10
    }

    try:
        response = requests.get(headlines_url, params=params)
        print(f"Searching top headlines for Poland")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('articles'):
                all_articles.extend(data['articles'])
                print(f"Found {len(data['articles'])} top headlines")
    except Exception as e:
        print(f"Error during headlines search: {str(e)}")

    # Then search for specific terms
    for term in search_terms:
        params = {
            'q': term,
            'from': from_date,
            'to': to_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': news_api_key,
            'pageSize': 5  # Limit results per term for more focused results
        }

        try:
            response = requests.get(everything_url, params=params)
            print(f"Search term: {term}")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('articles'):
                    # Filter out articles that don't mention Poland or elections
                    relevant_articles = [
                        article for article in data['articles']
                        if any(keyword in (article.get('title', '') + article.get('description', '')).lower()
                              for keyword in ['poland', 'polish', 'election', 'vote', 'tusk', 'duda'])
                    ]
                    all_articles.extend(relevant_articles)
                    print(f"Found {len(relevant_articles)} relevant articles")
            else:
                print(f"Error response: {response.text}")

        except Exception as e:
            print(f"Error during news search: {str(e)}")
            continue

    # Remove duplicates based on titles
    unique_articles = []
    seen_titles = set()
    for article in all_articles:
        title = article.get('title', '').lower()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)

    return unique_articles

def analyze_news_content(articles):
    """
    Analyze news articles to extract key information with randomization
    """
    if not articles:
        return None

    print("\nAnalyzing news content...")
    
    # Extract main topics and events
    main_topics = []
    key_events = []
    
    # Randomly shuffle articles to introduce variation
    shuffled_articles = list(articles)
    random.shuffle(shuffled_articles)
    
    for article in shuffled_articles:
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Clean up title
        if ' - ' in title:
            title = title.split(' - ')[0]
        title = title.replace('BREAKING:', '').replace('UPDATE:', '').strip()
        
        # Only add relevant titles about Polish politics/elections
        if any(keyword in title.lower() for keyword in ['poland', 'polish', 'election', 'vote', 'tusk', 'duda']):
            main_topics.append(title)
        
        # Extract key event from description if it's relevant
        if description and any(keyword in description.lower() for keyword in ['poland', 'polish', 'election', 'vote', 'tusk', 'duda']):
            # Clean up and shorten description if needed
            desc = description.strip()
            if len(desc) > 150:
                desc = desc[:150] + "..."
            key_events.append(desc)

    # Remove duplicates and create a pool of potential topics/events
    main_topics = list(set(main_topics))
    key_events = list(set(key_events))

    # Sort by relevance (presence of key terms) with random weight
    def relevance_score(text):
        text = text.lower()
        score = 0
        keywords = ['election', 'vote', 'poland', 'polish', 'president', 'tusk', 'duda']
        for keyword in keywords:
            if keyword in text:
                score += 1
        # Add small random factor to create variation in ordering
        return score + random.random() * 0.5

    main_topics.sort(key=relevance_score, reverse=True)
    key_events.sort(key=relevance_score, reverse=True)

    # Randomly select number of topics and events to include
    num_topics = random.randint(2, min(4, len(main_topics)))
    num_events = random.randint(1, min(3, len(key_events)))

    return {
        'topics': main_topics[:num_topics],
        'events': key_events[:num_events]
    }

def create_summary_from_news(analysis):
    """
    Create a news summary and an image prompt separately
    Returns a tuple of (news_description, image_prompt)
    """
    if not analysis or not analysis['topics']:
        default_pairs = [
            (
                "Latest updates on Polish democracy and electoral developments",
                "modern parliament building, rays of sunlight, Polish flag colors"
            ),
            (
                "Current state of Polish political landscape and electoral process",
                "ballot boxes, Polish national symbols, white eagle emblem"
            ),
            (
                "Polish electoral system and democratic institutions in focus",
                "voting booths, red and white colors, people silhouettes"
            ),
            (
                "Poland's democratic journey and political transformation",
                "parliament building facade, citizen silhouettes, Polish flag"
            )
        ]
        return random.choice(default_pairs)

    # Create news description from the analysis
    description_parts = []
    
    # Add main topics (up to 2)
    if analysis['topics']:
        description_parts.extend(analysis['topics'][:2])
    
    # Add one key event if available
    if analysis['events']:
        description_parts.append(analysis['events'][0])
    
    # Join all parts with proper punctuation
    news_description = '. '.join(description_parts)

    # Create image prompt
    visual_elements = {
        'buildings': ['parliament building', 'government palace', 'historic architecture'],
        'symbols': ['Polish flag', 'white eagle emblem', 'national symbols'],
        'people': ['citizen silhouettes', 'crowd gathering', 'people voting'],
        'political': ['ballot boxes', 'voting booths', 'election symbols'],
        'effects': ['rays of sunlight', 'dramatic lighting', 'dynamic composition']
    }

    # Select elements for the image prompt
    selected_elements = []
    # Always include one building element
    selected_elements.append(random.choice(visual_elements['buildings']))
    # Add 2-3 more random elements from different categories
    categories = list(visual_elements.keys())
    categories.remove('buildings')  # Remove buildings as we already used it
    for category in random.sample(categories, random.randint(2, 3)):
        selected_elements.append(random.choice(visual_elements[category]))

    # Create the final image prompt
    image_prompt = ', '.join(selected_elements)
    
    return news_description, image_prompt