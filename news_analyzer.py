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
    Create a concise summary from news analysis with randomization, formatted for image generation
    """
    if not analysis or not analysis['topics']:
        default_summaries = [
            "A symbolic visualization of Polish democracy: a modern parliament building with rays of sunlight, digital art style",
            "An artistic representation of Poland's political landscape: ballot boxes and national symbols, digital painting",
            "A conceptual image of Polish electoral process: voting booths with Polish flag colors, modern art style",
            "A dynamic composition showing Poland's democratic journey: parliament building and citizen silhouettes, digital illustration"
        ]
        return random.choice(default_summaries)

    # Extract key themes with variations suitable for image generation
    themes = {
        'tusk': ['Donald Tusk addressing supporters', 'opposition leader in discussion', 'Tusk at campaign rally'],
        'trzaskowski': ['Trzaskowski speaking to crowd', 'Warsaw Mayor at city hall', 'Trzaskowski meeting citizens'],
        'ukrainian': ['Ukrainian community in Poland', 'Poland-Ukraine cooperation', 'international solidarity'],
        'pis': ['government officials in session', 'parliamentary debate scene', 'political assembly'],
        'polls': ['citizens at voting stations', 'election polls visualization', 'public opinion charts'],
        'president': ['presidential office facade', 'official government ceremony', 'state leader address'],
        'mayor': ['city hall meeting', 'local government assembly', 'municipal leadership']
    }

    # Find main narrative from topics and events with randomization
    all_content = ' '.join(random.sample(analysis['topics'] + analysis['events'], 
                                       min(len(analysis['topics'] + analysis['events']), 
                                           random.randint(3, 5)))).lower()

    # Identify present themes and select random variations
    present_themes = []
    for key, variations in themes.items():
        if key in all_content:
            present_themes.append(random.choice(variations))

    # Create image-friendly summary with random elements
    if present_themes:
        # Select random scene setting
        settings = [
            "in a modern political setting",
            "against the backdrop of Warsaw",
            "in the heart of Polish democracy",
            "with national symbols in background",
            "in contemporary Poland"
        ]
        
        # Select random art style
        art_styles = [
            "digital art style",
            "modern illustration",
            "photorealistic rendering",
            "contemporary digital painting",
            "professional photography style"
        ]
        
        # Combine elements into a coherent prompt
        theme_summary = ', '.join(random.sample(present_themes, min(2, len(present_themes))))
        setting = random.choice(settings)
        style = random.choice(art_styles)
        
        templates = [
            f"A dynamic composition showing {theme_summary}, {setting}, {style}",
            f"An artistic visualization of {theme_summary}, {setting}, {style}",
            f"A powerful representation of {theme_summary}, {setting}, {style}",
            f"A compelling scene depicting {theme_summary}, {setting}, {style}"
        ]
        return random.choice(templates)
    else:
        return "A symbolic visualization of Polish democracy: modern parliament building with national symbols, digital art style"

def generate_news_enhanced_prompt(query=None):
    """
    Generate an enhanced prompt based on recent news about Polish elections
    Returns a tuple of (prompt, hashtags)
    """
    # Default hashtags that are always relevant
    base_hashtags = ['Poland', 'PolishElection', 'Democracy', 'Politics']
    
    articles = search_news(query)
    if not articles:
        return "A symbolic visualization of Polish democracy: modern parliament building with national symbols, digital art style", base_hashtags

    analysis = analyze_news_content(articles)
    if not analysis:
        return "A symbolic visualization of Polish democracy: modern parliament building with national symbols, digital art style", base_hashtags

    # Generate dynamic hashtags based on content
    dynamic_hashtags = set()
    all_content = ' '.join(analysis['topics'] + analysis['events']).lower()
    
    # Add hashtags based on key terms
    if 'tusk' in all_content:
        dynamic_hashtags.add('Tusk')
    if 'pis' in all_content:
        dynamic_hashtags.add('PiS')
    if 'opposition' in all_content:
        dynamic_hashtags.add('Opposition')
    if 'president' in all_content:
        dynamic_hashtags.add('President')
    if 'election' in all_content:
        dynamic_hashtags.add('Election2024')
    if 'warsaw' in all_content:
        dynamic_hashtags.add('Warsaw')
    if 'vote' in all_content:
        dynamic_hashtags.add('Vote')
    
    # Combine base and dynamic hashtags, remove duplicates
    all_hashtags = list(set(base_hashtags + list(dynamic_hashtags)))
    
    # Get the summary
    summary = create_summary_from_news(analysis)
    
    return summary, all_hashtags