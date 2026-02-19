"""
XenForo Forum Archiver - Configuration File

This file contains all configuration settings for the project.
It reads values from the .env file and provides default values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Forum Configuration
FORUM_URL = os.getenv('FORUM_URL', 'https://forum.example.com')
FORUM_USERNAME = os.getenv('FORUM_USERNAME', '')
FORUM_PASSWORD = os.getenv('FORUM_PASSWORD', '')
THREAD_URL = os.getenv('THREAD_URL', '')

# Scraping Settings
SCRAPE_DELAY = float(os.getenv('SCRAPE_DELAY', '2.5'))
MAX_PAGES = int(os.getenv('MAX_PAGES', '0'))  # 0 = all pages
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'

# Output Settings
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'website_output'))
DOWNLOAD_MEDIA = os.getenv('DOWNLOAD_MEDIA', 'true').lower() == 'true'
MEDIA_DIR = Path(os.getenv('MEDIA_DIR', 'downloaded_media'))

# Categorization Settings
AUTO_CATEGORIZE = os.getenv('AUTO_CATEGORIZE', 'true').lower() == 'true'
EXTRACT_TAGS = os.getenv('EXTRACT_TAGS', 'true').lower() == 'true'

# ChromeDriver Settings
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '')
CHROME_BINARY_PATH = os.getenv('CHROME_BINARY_PATH', '')

# Cookie File
COOKIES_FILE = BASE_DIR / 'forum_cookies.pkl'

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Category Rules
CATEGORY_RULES = {
    'review': {
        'keywords': ['review', 'test', 'analysis', 'evaluation', 'assessment', 'benchmark'],
        'priority': 1
    },
    'guide': {
        'keywords': ['guide', 'how', 'tutorial', 'instruction', 'step by step', 'setup', 'install'],
        'priority': 2
    },
    'news': {
        'keywords': ['news', 'announcement', 'new', 'update', 'release'],
        'priority': 3
    },
    'discussion': {
        'keywords': ['discussion', 'question', 'help', 'support', 'issue'],
        'priority': 4
    },
    'media': {
        'keywords': ['video', 'image', 'picture', 'gallery', 'photo', 'screenshot'],
        'priority': 5
    },
    'other': {
        'keywords': [],
        'priority': 99
    }
}

# Rate Limiting
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'xenforo_archiver.log'
