# Visual News App

A beautiful, personalized news experience with AI-generated imagery and user preferences.

## Features

- 🎨 Beautiful visual news cards with AI-generated images
- 👤 User authentication and preferences
- 📱 Mobile-friendly swipe interface
- 🎯 Personalized news based on user interests
- 📊 Admin dashboard for user analytics
- 🔄 Real-time news updates

## Local Development

### Prerequisites

- Python 3.7+
- OpenAI API key
- News API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd visual-news-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   NEWS_API_KEY=your_news_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://127.0.0.1:8080`

## Deployment to Render

### Method 1: Using Render Dashboard

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Sign up/Login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure deployment**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3

4. **Set environment variables**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `NEWS_API_KEY`: Your News API key
   - `FLASK_SECRET_KEY`: Generate a secure secret key
   - `HOST`: `0.0.0.0` (for Render)
   - `PORT`: `10000` (Render's default)
   - `FLASK_DEBUG`: `False` (for production)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

### Method 2: Using render.yaml

The project includes a `render.yaml` file for automatic deployment configuration.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes |
| `NEWS_API_KEY` | News API key for fetching news | Yes |
| `FLASK_SECRET_KEY` | Flask secret key for sessions | Yes |
| `HOST` | Server host (default: 127.0.0.1) | No |
| `PORT` | Server port (default: 8080) | No |
| `FLASK_DEBUG` | Debug mode (default: True) | No |

## Project Structure

```
visual-news-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── Procfile              # Alternative deployment config
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── templates/            # HTML templates
│   ├── index.html
│   ├── signup.html
│   └── admin.html
├── static/               # Static assets
│   ├── css/
│   └── js/
├── users.json            # User data storage
├── articles.json         # Article engagement data
└── generated_images.json # AI image cache
```

## API Endpoints

- `GET /` - Main news interface
- `GET /signup` - User registration
- `GET /admin` - Admin dashboard
- `GET /api/news` - Fetch news articles
- `GET /api/user-preferences` - Get user preferences
- `POST /api/user-preferences` - Update user preferences
- `POST /api/article-engagement` - Handle article likes/dislikes

## Security Notes

- Never commit `.env` files to version control
- Use strong, unique secret keys in production
- Regularly rotate API keys
- Monitor API usage and costs

## Support

For issues or questions, please check the admin dashboard at `/admin` or review the application logs.
