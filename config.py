"""
XenForo Forum Archiver - Yapılandırma Dosyası

Bu dosya projenin tüm yapılandırma ayarlarını içerir.
.env dosyasından değerleri okur ve varsayılan değerler sağlar.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent

# Forum Yapılandırması
FORUM_URL = os.getenv('FORUM_URL', 'https://forum.example.com')
FORUM_USERNAME = os.getenv('FORUM_USERNAME', '')
FORUM_PASSWORD = os.getenv('FORUM_PASSWORD', '')
THREAD_URL = os.getenv('THREAD_URL', '')

# Scraping Ayarları
SCRAPE_DELAY = float(os.getenv('SCRAPE_DELAY', '2.5'))
MAX_PAGES = int(os.getenv('MAX_PAGES', '0'))  # 0 = tüm sayfalar
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'

# Çıktı Ayarları
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', 'website_output'))
DOWNLOAD_MEDIA = os.getenv('DOWNLOAD_MEDIA', 'true').lower() == 'true'
MEDIA_DIR = Path(os.getenv('MEDIA_DIR', 'downloaded_media'))

# Kategorizasyon Ayarları
AUTO_CATEGORIZE = os.getenv('AUTO_CATEGORIZE', 'true').lower() == 'true'
EXTRACT_TAGS = os.getenv('EXTRACT_TAGS', 'true').lower() == 'true'

# ChromeDriver Ayarları
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '')
CHROME_BINARY_PATH = os.getenv('CHROME_BINARY_PATH', '')

# Çerez Dosyası
COOKIES_FILE = BASE_DIR / 'forum_cookies.pkl'

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Kategori Kuralları
CATEGORY_RULES = {
    'inceleme': {
        'keywords': ['inceleme', 'review', 'test', 'deneme', 'analiz', 'değerlendirme'],
        'priority': 1
    },
    'rehber': {
        'keywords': ['rehber', 'guide', 'nasıl', 'tutorial', 'anlatım', 'adım adım', 'kurulum'],
        'priority': 2
    },
    'haber': {
        'keywords': ['haber', 'news', 'duyuru', 'announcement', 'yeni', 'güncelleme'],
        'priority': 3
    },
    'tartisma': {
        'keywords': ['tartışma', 'discussion', 'soru', 'question', 'yardım', 'help'],
        'priority': 4
    },
    'medya': {
        'keywords': ['video', 'resim', 'image', 'galeri', 'gallery', 'foto'],
        'priority': 5
    },
    'diger': {
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
