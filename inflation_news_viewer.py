# Install required packages if not already installed
# !pip install requests

import requests

# Set your API key
news_api_key = "063151f04eab42518ca9bdd3103d5e5b"         # Replace with your actual NewsAPI key

# Step 1: Fetch news articles about inflation
url = f"https://newsapi.org/v2/everything?q=inflation&language=en&apiKey={news_api_key}"

try:
    response = requests.get(url)
    response.raise_for_status()  # checks if request succeeded
    
    articles = response.json().get("articles", [])
    
    # Step 2: Display news articles (without AI summarization for now)
    print("=== INFLATION NEWS ARTICLES ===\n")
    
    for i, article in enumerate(articles[:5]):
        title = article.get("title", "No Title")
        description = article.get("description", "No description available")
        url_link = article.get("url", "No URL available")
        published_at = article.get("publishedAt", "Unknown date")
        
        print(f"Article {i+1}: {title}")
        print(f"Published: {published_at}")
        print(f"Description: {description}")
        print(f"URL: {url_link}")
        print(f"{'-'*80}\n")
        
except requests.exceptions.RequestException as e:
    print(f"Error fetching news: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
