import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import openai
import os
import json
from datetime import datetime, timedelta
import random
import uuid
import hashlib
import base64
from io import BytesIO
import threading
import time
from dotenv import load_dotenv
from security import security_manager

print("All imports successful - Deployment version 1.3 - EXCEL EXPORT FIX")

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load API keys from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize rate limiter
print("Initializing Flask-Limiter...")
try:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app
    )
    print("Flask-Limiter initialized successfully")
except Exception as e:
    print(f"Error initializing Flask-Limiter: {e}")
    raise

# Validate that required API keys are set
print(f"DEBUG: OpenAI API key loaded: {openai.api_key[:10] if openai.api_key else 'None'}...")
print(f"DEBUG: NewsAPI key loaded: {news_api_key[:10] if news_api_key else 'None'}...")

if not openai.api_key:
    print("WARNING: OPENAI_API_KEY environment variable is not set")
    # Don't raise error for deployment, just use placeholder
    openai.api_key = "placeholder-key"
if not news_api_key:
    print("WARNING: NEWS_API_KEY environment variable is not set")
    # Don't raise error for deployment, just use placeholder
    news_api_key = "placeholder-key"

# User data file
USERS_FILE = 'users.json'
# Article engagement file
ARTICLES_FILE = 'articles.json'
# Generated images cache
IMAGES_FILE = 'generated_images.json'

# Topic configurations with placeholder images
TOPIC_CONFIGS = {
    'inflation': {
        'query': 'inflation economy',
        'icon': 'fas fa-chart-line',
        'color': 'text-danger',
        'name': 'Inflation & Economy',
        'placeholder': 'https://picsum.photos/400/300?random=1'
    },
    'technology': {
        'query': 'technology AI artificial intelligence',
        'icon': 'fas fa-microchip',
        'color': 'text-primary',
        'name': 'Technology',
        'placeholder': 'https://picsum.photos/400/300?random=2'
    },
    'politics': {
        'query': 'politics government election',
        'icon': 'fas fa-landmark',
        'color': 'text-warning',
        'name': 'Politics',
        'placeholder': 'https://picsum.photos/400/300?random=3'
    },
    'health': {
        'query': 'health medicine healthcare',
        'icon': 'fas fa-heartbeat',
        'color': 'text-success',
        'name': 'Health & Medicine',
        'placeholder': 'https://picsum.photos/400/300?random=4'
    },
    'business': {
        'query': 'business finance market',
        'icon': 'fas fa-briefcase',
        'color': 'text-info',
        'name': 'Business',
        'placeholder': 'https://picsum.photos/400/300?random=5'
    },
    'science': {
        'query': 'science research discovery',
        'icon': 'fas fa-flask',
        'color': 'text-purple',
        'name': 'Science',
        'placeholder': 'https://picsum.photos/400/300?random=6'
    },
    'sports': {
        'query': 'sports football basketball',
        'icon': 'fas fa-football-ball',
        'color': 'text-orange',
        'name': 'Sports',
        'placeholder': 'https://picsum.photos/400/300?random=7'
    },
    'environment': {
        'query': 'environment climate global warming',
        'icon': 'fas fa-leaf',
        'color': 'text-green',
        'name': 'Environment',
        'placeholder': 'https://picsum.photos/400/300?random=8'
    }
}

def load_users():
    """Load users from secure storage"""
    return security_manager.load_users()

def load_users_from_json():
    """Load users from regular JSON file for admin display"""
    try:
        print(f"DEBUG: Checking for users.json file...")
        if os.path.exists('users.json'):
            print(f"DEBUG: users.json file exists, loading...")
            with open('users.json', 'r') as f:
                users = json.load(f)
                print(f"DEBUG: Loaded {len(users)} users from JSON")
                return users
        else:
            print(f"DEBUG: users.json file does not exist")
        return {}
    except Exception as e:
        print(f"Error loading users from JSON: {e}")
        return {}

def save_users(users):
    """Save users to secure storage"""
    return security_manager.save_users(users)

def load_articles():
    """Load article engagement data from JSON file"""
    try:
        if os.path.exists(ARTICLES_FILE):
            with open(ARTICLES_FILE, 'r') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_articles(articles):
    """Save article engagement data to JSON file"""
    try:
        with open(ARTICLES_FILE, 'w') as f:
            json.dump(articles, f, indent=2)
        return True
    except:
        return False

def generate_article_id(title, published_at):
    """Generate a unique article ID"""
    content = f"{title}_{published_at}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def is_logged_in():
    """Check if user is logged in with secure session validation"""
    if 'user_id' not in session:
        return False
    
    # Validate session data
    session_data = {
        'user_id': session.get('user_id'),
        'created_at': session.get('created_at')
    }
    
    return security_manager.security.validate_session(session_data)

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_news_image(topic):
    """Get placeholder image for topic - no AI generation"""
    config = TOPIC_CONFIGS.get(topic, TOPIC_CONFIGS['inflation'])
    return config['placeholder']

def create_quick_notes(text):
    """Create quick notes instead of AI summaries"""
    if not text:
        return "No content available for quick notes."
    
    # Simple text processing to create quick notes
    sentences = text.split('.')[:3]  # Take first 3 sentences
    quick_notes = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Only meaningful sentences
            # Add bullet point
            quick_notes.append(f"• {sentence}")
    
    if not quick_notes:
        return "• Key information not available in this format"
    
    return '\n'.join(quick_notes)

def get_demo_news_for_topic(topic, num_articles=1):
    """Get demo news articles when API key is not available"""
    config = TOPIC_CONFIGS.get(topic, TOPIC_CONFIGS['inflation'])
    
    demo_articles = []
    for i in range(num_articles):
        demo_articles.append({
            'id': f"demo_{topic}_{i+1}",
            'title': f"Demo {config['name']} News Article {i+1}",
            'description': f"This is a demo article about {topic}. In a real deployment, you would see actual news articles here when you add your NewsAPI key to the environment variables.",
            'summary': f"• Demo article about {topic}\n• This shows the app is working\n• Add your NewsAPI key to see real news",
            'url': f"https://example.com/demo-{topic}-{i+1}",
            'published_at': "Demo Date",
            'source': "Demo Source",
            'topic': topic,
            'topic_name': config['name'],
            'topic_icon': config['icon'],
            'topic_color': config['color'],
            'likes': 0,
            'dislikes': 0,
            'views': 0,
            'image_url': config['placeholder'],
            'is_generated': False
        })
    
    return demo_articles

def fetch_news_by_topic(topic, num_articles=1):
    """Fetch news articles for a specific topic"""
    try:
        # Check if we have a valid API key
        print(f"DEBUG: Checking API key for {topic}: {news_api_key[:10] if news_api_key else 'None'}...")
        if news_api_key == "placeholder-key" or not news_api_key:
            print(f"WARNING: Using demo data for {topic} - API key not set")
            return get_demo_news_for_topic(topic, num_articles)
        else:
            print(f"DEBUG: Using real API key for {topic}")
        
        config = TOPIC_CONFIGS.get(topic, TOPIC_CONFIGS['inflation'])
        query = config['query']
        
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={news_api_key}"
        response = requests.get(url)
        response.raise_for_status()
        
        articles = response.json().get("articles", [])
        processed_articles = []
        
        # Load existing article data
        article_data = load_articles()
        
        for i, article in enumerate(articles[:num_articles]):
            title = article.get("title", "No Title")
            description = article.get("description") or article.get("content") or ""
            url_link = article.get("url", "")
            published_at = article.get("publishedAt", "")
            source = article.get("source", {}).get("name", "Unknown Source")
            
            # Generate article ID
            article_id = generate_article_id(title, published_at)
            
            # Get engagement data
            engagement = article_data.get(article_id, {
                'likes': 0,
                'dislikes': 0,
                'views': 0,
                'created_at': datetime.now().isoformat()
            })
            
            # Format published date
            if published_at:
                try:
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_date = published_at
            else:
                formatted_date = "Unknown date"
            
            # Get image URL - use actual image from NewsAPI if available, otherwise use placeholder
            url_to_image = article.get("urlToImage")
            if (url_to_image and 
                url_to_image != "null" and 
                url_to_image.strip() and 
                url_to_image.startswith(('http://', 'https://')) and
                any(ext in url_to_image.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])):
                image_url = url_to_image
            else:
                image_url = get_news_image(topic)
            
            # Create quick notes
            quick_notes = create_quick_notes(description)
            
            processed_articles.append({
                'id': article_id,
                'title': title,
                'description': description,
                'summary': quick_notes,
                'url': url_link,
                'published_at': formatted_date,
                'source': source,
                'topic': topic,
                'topic_name': config['name'],
                'topic_icon': config['icon'],
                'topic_color': config['color'],
                'likes': engagement['likes'],
                'dislikes': engagement['dislikes'],
                'views': engagement['views'],
                'image_url': image_url,
                'is_generated': False  # Always false since we're not generating AI images
            })
        
        return processed_articles
    
    except Exception as e:
        print(f"ERROR: Failed to fetch {topic} news: {str(e)}")
        print(f"Falling back to demo data for {topic}")
        return get_demo_news_for_topic(topic, num_articles)

def fetch_multi_topic_news(topics, num_articles_per_topic=1):
    """Fetch news from multiple topics and sort by popularity"""
    all_articles = []
    
    for topic in topics:
        articles = fetch_news_by_topic(topic, num_articles_per_topic)
        all_articles.extend(articles)
    
    # Sort by popularity (likes - dislikes) and then by views
    all_articles.sort(key=lambda x: (x.get('likes', 0) - x.get('dislikes', 0), x.get('views', 0)), reverse=True)
    
    return all_articles

@app.route('/')
def index():
    """Main page - show news even if not logged in"""
    if is_logged_in():
        return render_template('index.html')
    else:
        # Show a public version with limited functionality
        return render_template('public_index.html')

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    """Sign up page with preferences"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        preferences = request.form.getlist('preferences')
        
        # Validate inputs
        if not name or not phone or not password:
            flash('Please fill in all fields', 'error')
            return render_template('signup.html')
        
        if not preferences:
            flash('Please select at least one topic of interest', 'error')
            return render_template('signup.html')
        
        # Create user securely
        result = security_manager.create_user(name, phone, password, preferences)
        
        if result.get('success'):
            user_id = result['user_id']
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_preferences'] = preferences
            session['created_at'] = datetime.now().isoformat()
            flash(f'Welcome {name}! Your account has been created securely.', 'success')
            return redirect(url_for('index'))
        else:
            flash(result.get('error', 'Error creating account. Please try again.'), 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Login page"""
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        
        if not phone or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        # Authenticate user
        result = security_manager.authenticate_user(phone, password)
        
        if result.get('success'):
            user_data = result['user_data']
            session['user_id'] = result['user_id']
            session['user_name'] = user_data['name']
            session['user_preferences'] = user_data.get('preferences', [])
            session['created_at'] = datetime.now().isoformat()
            flash(f'Welcome back {user_data["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash(result.get('error', 'Invalid credentials'), 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/api/news')
@limiter.limit("30 per minute")
def api_news():
    """API endpoint to fetch news - no authentication required"""
    user_preferences = session.get('user_preferences', [])
    topics = request.args.getlist('topics')
    if not topics:
        topics = user_preferences
    
    num_articles = min(request.args.get('num_articles', 1, type=int), 50)  # Limit max articles
    
    if not topics:
        # If no topics provided and no user preferences, use default topics
        topics = ['inflation', 'economy']
    
    if len(topics) == 1:
        articles = fetch_news_by_topic(topics[0], num_articles)
    else:
        articles_per_topic = max(1, num_articles // len(topics))
        articles = fetch_multi_topic_news(topics, articles_per_topic)
        articles = articles[:num_articles]
    
    return jsonify(articles)

@app.route('/api/swipe', methods=['POST'])
@require_auth
def api_swipe():
    """API endpoint to handle swipe actions"""
    data = request.get_json()
    action = data.get('action')
    topic = data.get('topic')
    
    if not action or not topic:
        return jsonify({'error': 'Missing action or topic'}), 400
    
    users = load_users()
    user_id = session['user_id']
    
    if user_id in users:
        if action == 'like':
            users[user_id]['liked_topics'][topic] = users[user_id]['liked_topics'].get(topic, 0) + 1
        else:
            users[user_id]['passed_topics'][topic] = users[user_id]['passed_topics'].get(topic, 0) + 1
        
        save_users(users)
    
    return jsonify({'success': True})

@app.route('/api/article-engagement', methods=['POST'])
@require_auth
def api_article_engagement():
    """API endpoint to handle article likes/dislikes"""
    data = request.get_json()
    article_id = data.get('article_id')
    action = data.get('action')
    is_active = data.get('is_active', True)
    
    if not article_id or not action:
        return jsonify({'error': 'Missing article_id or action'}), 400
    
    articles = load_articles()
    
    if article_id not in articles:
        articles[article_id] = {
            'likes': 0,
            'dislikes': 0,
            'views': 0,
            'created_at': datetime.now().isoformat()
        }
    
    if action == 'like':
        if is_active:
            articles[article_id]['likes'] += 1
        else:
            articles[article_id]['likes'] = max(0, articles[article_id]['likes'] - 1)
    elif action == 'dislike':
        if is_active:
            articles[article_id]['dislikes'] += 1
        else:
            articles[article_id]['dislikes'] = max(0, articles[article_id]['dislikes'] - 1)
    
    save_articles(articles)
    
    return jsonify({
        'success': True,
        'likes': articles[article_id]['likes'],
        'dislikes': articles[article_id]['dislikes']
    })

@app.route('/api/topics')
@require_auth
def api_topics():
    """API endpoint to get available topics - requires authentication"""
    return jsonify(TOPIC_CONFIGS)

@app.route('/api/user-preferences')
@require_auth
def api_user_preferences():
    """API endpoint to get user preferences - requires authentication"""
    user_preferences = session.get('user_preferences', [])
    return jsonify({
        'preferences': user_preferences,
        'available_topics': TOPIC_CONFIGS
    })

@app.route('/api/user-preferences', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def update_user_preferences():
    """API endpoint to update user preferences - requires authentication"""
    data = request.get_json()
    preferences = data.get('preferences', [])
    
    if not preferences:
        return jsonify({'error': 'No preferences provided'}), 400
    
    # Update preferences securely
    user_id = session['user_id']
    result = security_manager.update_user_preferences(user_id, preferences)
    
    if result.get('success'):
        session['user_preferences'] = preferences
        return jsonify({'success': True, 'preferences': preferences})
    else:
        return jsonify({'error': result.get('error', 'Failed to update preferences')}), 400

@app.route('/admin')
def admin():
    """Admin page to view all user data - requires authentication"""
    # Check if user is authenticated as admin
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Load users from the actual users.json file (not encrypted)
    users = load_users_from_json()
    articles = load_articles()
    
    # Debug: Print user count
    print(f"DEBUG: Admin loaded {len(users)} users")
    print(f"DEBUG: Users data: {list(users.keys()) if users else 'No users'}")
    
    # Calculate some statistics
    total_users = len(users)
    users_with_preferences = len([u for u in users.values() if u.get('preferences')])
    total_articles = len(articles)
    
    return render_template('admin.html', 
                         users=users, 
                         articles=articles,
                         total_users=total_users,
                         users_with_preferences=users_with_preferences,
                         total_articles=total_articles)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple admin credentials (in production, use environment variables)
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid admin credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Admin logged out successfully!', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/export/csv')
def export_users_csv():
    """Export user data to CSV file - requires admin authentication"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Load users data
        users = load_users_from_json()
        
        if not users:
            return jsonify({'error': 'No user data available'}), 404
        
        # Prepare data for CSV
        csv_data = []
        for user_id, user_data in users.items():
            csv_data.append({
                'User ID': user_id,
                'Name': user_data.get('name', 'N/A'),
                'Phone': user_data.get('phone', 'N/A'),
                'Email': user_data.get('email', 'N/A'),
                'Created At': user_data.get('created_at', 'N/A'),
                'Preferences': ', '.join(user_data.get('preferences', [])) if user_data.get('preferences') else 'None',
                'Liked Topics Count': len(user_data.get('liked_topics', {})),
                'Passed Topics Count': len(user_data.get('passed_topics', {})),
                'Total Engagements': len(user_data.get('liked_topics', {})) + len(user_data.get('passed_topics', {}))
            })
        
        # Create CSV content
        import csv
        output = io.StringIO()
        fieldnames = ['User ID', 'Name', 'Phone', 'Email', 'Created At', 'Preferences', 'Liked Topics Count', 'Passed Topics Count', 'Total Engagements']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visual_news_users_{timestamp}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500

@app.route('/admin/export/excel')
def export_users_excel():
    """Export user data to Excel-compatible CSV file - requires admin authentication"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Load users data
        users = load_users_from_json()
        
        if not users:
            return jsonify({'error': 'No user data available'}), 404
        
        # Prepare data for Excel-compatible CSV
        csv_data = []
        for user_id, user_data in users.items():
            csv_data.append({
                'User ID': user_id,
                'Name': user_data.get('name', 'N/A'),
                'Phone': user_data.get('phone', 'N/A'),
                'Email': user_data.get('email', 'N/A'),
                'Created At': user_data.get('created_at', 'N/A'),
                'Preferences': ', '.join(user_data.get('preferences', [])) if user_data.get('preferences') else 'None',
                'Liked Topics Count': len(user_data.get('liked_topics', {})),
                'Passed Topics Count': len(user_data.get('passed_topics', {})),
                'Total Engagements': len(user_data.get('liked_topics', {})) + len(user_data.get('passed_topics', {}))
            })
        
        # Create CSV content
        import csv
        output = io.StringIO()
        fieldnames = ['User ID', 'Name', 'Phone', 'Email', 'Created At', 'Preferences', 'Liked Topics Count', 'Passed Topics Count', 'Total Engagements']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visual_news_users_{timestamp}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500

@app.route('/admin/export/csv')
def export_users_csv():
    """Export user data to CSV file (backup option)"""
    try:
        # Load users data
        users = load_users_from_json()
        
        if not users:
            return jsonify({'error': 'No user data available'}), 404
        
        # Prepare data for CSV
        csv_data = []
        for user_id, user_data in users.items():
            csv_data.append({
                'User ID': user_id,
                'Name': user_data.get('name', 'N/A'),
                'Phone': user_data.get('phone', 'N/A'),
                'Email': user_data.get('email', 'N/A'),
                'Created At': user_data.get('created_at', 'N/A'),
                'Preferences': ', '.join(user_data.get('preferences', [])) if user_data.get('preferences') else 'None',
                'Liked Topics Count': len(user_data.get('liked_topics', {})),
                'Passed Topics Count': len(user_data.get('passed_topics', {})),
                'Total Engagements': len(user_data.get('liked_topics', {})) + len(user_data.get('passed_topics', {}))
            })
        
        # Create CSV content
        import csv
        output = io.StringIO()
        fieldnames = ['User ID', 'Name', 'Phone', 'Email', 'Created At', 'Preferences', 'Liked Topics Count', 'Passed Topics Count', 'Total Engagements']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visual_news_users_{timestamp}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500

if __name__ == '__main__':
    # Get host and port from environment variables, with defaults for production
    host = os.getenv('HOST', '0.0.0.0')  # Changed default to 0.0.0.0 for Render
    port = int(os.getenv('PORT', 10000))  # Render uses port 10000
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'  # Disable debug in production
    
    print(f"Starting server on {host}:{port}")
    print(f"Host binding: {host} (should be 0.0.0.0 for Render)")
    app.run(debug=debug, host=host, port=port)
