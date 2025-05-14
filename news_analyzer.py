import requests
import json
from datetime import datetime, timedelta
import base64

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
    Analyze news articles to extract key information
    """
    if not articles:
        return None

    print("\nAnalyzing news content...")
    
    # Extract main topics and events
    main_topics = []
    key_events = []
    
    for article in articles:
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

    # Remove duplicates and sort by length
    main_topics = list(set(main_topics))
    key_events = list(set(key_events))

    # Sort by relevance (presence of key terms)
    def relevance_score(text):
        text = text.lower()
        score = 0
        keywords = ['election', 'vote', 'poland', 'polish', 'president', 'tusk', 'duda']
        for keyword in keywords:
            if keyword in text:
                score += 1
        return score

    main_topics.sort(key=relevance_score, reverse=True)
    key_events.sort(key=relevance_score, reverse=True)

    return {
        'topics': main_topics[:3],  # Top 3 most relevant topics
        'events': key_events[:2]    # Top 2 most relevant events
    }

def create_summary_from_news(analysis):
    """
    Create a concise summary from news analysis
    """
    if not analysis or not analysis['topics']:
        return "Polish presidential election campaign with focus on democratic values"

    # Extract key themes
    themes = {
        'tusk': 'Tusk\'s opposition',
        'trzaskowski': 'Trzaskowski',
        'ukrainian': 'Ukrainian refugees',
        'pis': 'PiS party',
        'polls': 'election polls',
        'president': 'presidency',
        'mayor': 'Warsaw Mayor'
    }

    # Find main narrative from topics and events
    all_content = ' '.join(analysis['topics'] + analysis['events']).lower()
    
    main_themes = []
    for keyword, theme in themes.items():
        if keyword in all_content:
            main_themes.append(theme)

    # Create a concise summary
    if 'trzaskowski' in all_content and 'polls' in all_content:
        return "Create a political cartoon showing Trzaskowski's lead in presidential polls, with focus on the shifting political landscape in Poland"
    elif 'ukrainian' in all_content and 'election' in all_content:
        return "Create a political cartoon depicting Polish presidential candidates balancing between domestic priorities and Ukrainian refugee support"
    elif 'pis' in all_content and 'opposition' in all_content:
        return "Create a political cartoon showing the political battle between PiS and opposition in Polish presidential race"
    else:
        return "Create a political cartoon about the current Polish presidential election campaign and its key candidates"

def generate_news_enhanced_prompt(topic_description):
    """
    Generate an image prompt based on current news
    """
    print(f"\nGenerating prompt for: {topic_description}")

    # Search for news articles
    articles = search_news(topic_description)
    
    if not articles:
        print("No news articles found. Using basic prompt.")
        return "Create a political cartoon about Polish elections, focusing on democratic process and political change", ['politics', 'poland', 'election']

    # Analyze the news content
    analysis = analyze_news_content(articles)
    
    if not analysis or not analysis['topics']:
        print("Could not analyze news content. Using basic prompt.")
        return "Create a political cartoon about Polish elections, showing the competition between political parties", ['politics', 'poland', 'election']

    # Create concise summary prompt
    prompt = create_summary_from_news(analysis)

    # Generate hashtags
    hashtags = {'politics', 'poland', 'election', 'democracy', 'polska', 'polishpolitics'}
    
    # Add specific hashtags based on content
    if 'trzaskowski' in prompt.lower():
        hashtags.add('trzaskowski')
    if 'tusk' in prompt.lower():
        hashtags.add('tusk')
    if 'pis' in prompt.lower():
        hashtags.add('pis')
    if 'ukrainian' in prompt.lower():
        hashtags.update(['ukraine', 'refugees'])

    print("\nPrompt generated successfully!")
    return prompt, list(hashtags)

if __name__ == "__main__":
    # Test the functionality
    test_query = "Polish presidential election"
    prompt, hashtags = generate_news_enhanced_prompt(test_query)
    
    print("\nGenerated Prompt:")
    print("=" * 50)
    print(prompt)
    print("\nHashtags:")
    print(" ".join([f"#{tag}" for tag in hashtags]))