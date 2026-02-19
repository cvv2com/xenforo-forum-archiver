"""
XenForo Forum Archiver - Scraper Modülü

Bu modül BeautifulSoup kullanarak XenForo v2.x forumlarından
içerik çeker ve parse eder.
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from src.utils import setup_logger, clean_html_text
import config


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class XenForoScraper:
    """XenForo v2.x forum scraper sınıfı"""
    
    def __init__(self, session: requests.Session, base_url: str):
        """
        Args:
            session: Çerezli requests session
            base_url: Forum ana URL'si
        """
        self.session = session
        self.base_url = base_url.rstrip('/')
        self.posts_data: List[Dict[str, Any]] = []
        self.thread_title = ""
        self.thread_info: Dict[str, Any] = {}
    
    def get_total_pages(self, thread_url: str) -> int:
        """
        Thread'in toplam sayfa sayısını bulur.
        
        Args:
            thread_url: Thread URL'si
        
        Returns:
            Toplam sayfa sayısı
        """
        try:
            logger.info(f"Thread sayfa sayısı kontrol ediliyor: {thread_url}")
            response = self.session.get(thread_url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Thread başlığını al
            title_elem = soup.select_one('h1.p-title-value')
            if title_elem:
                self.thread_title = clean_html_text(title_elem.get_text())
                logger.info(f"Thread başlığı: {self.thread_title}")
            
            # Sayfalama elementini bul
            pagination = soup.select_one('nav.pageNav')
            if not pagination:
                logger.info("Sayfalama bulunamadı, tek sayfa varsayılıyor")
                return 1
            
            # Son sayfa linkini bul
            last_page_link = pagination.select_one('a[data-last]')
            if last_page_link:
                last_page_url = last_page_link.get('href', '')
                # URL'den page parametresini çıkar
                parsed = urlparse(last_page_url)
                params = parse_qs(parsed.query)
                if 'page' in params:
                    total_pages = int(params['page'][0])
                    logger.info(f"Toplam sayfa sayısı: {total_pages}")
                    return total_pages
            
            # Alternatif: tüm sayfa linklerini kontrol et
            page_links = pagination.select('a.pageNav-page')
            if page_links:
                page_numbers = []
                for link in page_links:
                    page_num_text = link.get_text(strip=True)
                    if page_num_text.isdigit():
                        page_numbers.append(int(page_num_text))
                if page_numbers:
                    total_pages = max(page_numbers)
                    logger.info(f"Toplam sayfa sayısı (alternatif): {total_pages}")
                    return total_pages
            
            logger.info("Sayfa sayısı belirlenemedi, tek sayfa varsayılıyor")
            return 1
            
        except Exception as e:
            logger.error(f"Toplam sayfa sayısı alınırken hata: {e}")
            return 1
    
    def _parse_post(self, article: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Tek bir post elementini parse eder.
        
        Args:
            article: BeautifulSoup article elementi
        
        Returns:
            Post verisi dictionary
        """
        try:
            post_data: Dict[str, Any] = {}
            
            # Post ID
            post_id = article.get('data-content', '')
            post_data['post_id'] = post_id.split('-')[-1] if post_id else ''
            
            # Yazar bilgisi
            author_elem = article.select_one('a[data-user-id]')
            if author_elem:
                post_data['author'] = clean_html_text(author_elem.get_text())
                post_data['author_id'] = author_elem.get('data-user-id', '')
            else:
                post_data['author'] = 'Unknown'
                post_data['author_id'] = ''
            
            # Tarih
            date_elem = article.select_one('time[datetime]')
            if date_elem:
                post_data['date'] = date_elem.get('datetime', '')
                post_data['date_text'] = clean_html_text(date_elem.get_text())
            else:
                post_data['date'] = ''
                post_data['date_text'] = ''
            
            # İçerik
            content_elem = article.select_one('div.bbWrapper')
            if content_elem:
                post_data['content_html'] = str(content_elem)
                post_data['content_text'] = clean_html_text(content_elem.get_text())
            else:
                post_data['content_html'] = ''
                post_data['content_text'] = ''
            
            # Görseller
            images = []
            img_elements = article.select('div.bbWrapper img')
            for img in img_elements:
                img_data = {
                    'src': img.get('src', ''),
                    'data_src': img.get('data-src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                }
                # Görsel URL'sini mutlak URL'ye çevir
                if img_data['src']:
                    img_data['src'] = urljoin(self.base_url, img_data['src'])
                if img_data['data_src']:
                    img_data['data_src'] = urljoin(self.base_url, img_data['data_src'])
                images.append(img_data)
            post_data['images'] = images
            
            # Videolar (YouTube, Vimeo embeds)
            videos = []
            # YouTube iframes
            youtube_iframes = article.select('iframe[src*="youtube.com"], iframe[src*="youtu.be"]')
            for iframe in youtube_iframes:
                videos.append({
                    'type': 'youtube',
                    'src': iframe.get('src', ''),
                    'title': iframe.get('title', '')
                })
            
            # Vimeo iframes
            vimeo_iframes = article.select('iframe[src*="vimeo.com"]')
            for iframe in vimeo_iframes:
                videos.append({
                    'type': 'vimeo',
                    'src': iframe.get('src', ''),
                    'title': iframe.get('title', '')
                })
            
            post_data['videos'] = videos
            
            # Ekler (attachments)
            attachments = []
            attachment_elements = article.select('a.file-preview')
            for att in attachment_elements:
                attachments.append({
                    'url': urljoin(self.base_url, att.get('href', '')),
                    'title': clean_html_text(att.get_text()),
                    'filename': att.get('data-attachment-filename', '')
                })
            post_data['attachments'] = attachments
            
            # Alıntılar (quotes)
            quotes = []
            quote_elements = article.select('blockquote.bbCodeBlock')
            for quote in quote_elements:
                quote_author_elem = quote.select_one('div.bbCodeBlock-title')
                quote_content_elem = quote.select_one('div.bbCodeBlock-expandContent')
                
                quotes.append({
                    'author': clean_html_text(quote_author_elem.get_text()) if quote_author_elem else '',
                    'content': clean_html_text(quote_content_elem.get_text()) if quote_content_elem else ''
                })
            post_data['quotes'] = quotes
            
            return post_data
            
        except Exception as e:
            logger.error(f"Post parse edilirken hata: {e}")
            return None
    
    def scrape_page(self, page_url: str) -> List[Dict[str, Any]]:
        """
        Tek sayfadaki tüm postları scrape eder.
        
        Args:
            page_url: Sayfa URL'si
        
        Returns:
            Post verisi listesi
        """
        posts = []
        try:
            logger.info(f"Sayfa scraping yapılıyor: {page_url}")
            response = self.session.get(page_url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Tüm post elementlerini bul
            articles = soup.select('article.message')
            logger.info(f"Sayfada {len(articles)} post bulundu")
            
            for article in articles:
                post_data = self._parse_post(article)
                if post_data:
                    posts.append(post_data)
            
            return posts
            
        except Exception as e:
            logger.error(f"Sayfa scrape edilirken hata: {e}")
            return posts
    
    def scrape_thread(self, thread_url: str, delay: float = 2.5, max_pages: int = 0) -> bool:
        """
        Thread'in tüm sayfalarını scrape eder.
        
        Args:
            thread_url: Thread URL'si
            delay: Sayfalar arası bekleme süresi (saniye)
            max_pages: Maksimum sayfa sayısı (0 = tümü)
        
        Returns:
            Başarılı ise True
        """
        try:
            # Toplam sayfa sayısını al
            total_pages = self.get_total_pages(thread_url)
            
            # Max pages kontrolü
            if max_pages > 0:
                total_pages = min(total_pages, max_pages)
            
            logger.info(f"Toplam {total_pages} sayfa scrape edilecek")
            
            # Thread bilgilerini kaydet
            self.thread_info = {
                'url': thread_url,
                'title': self.thread_title,
                'total_pages': total_pages,
                'base_url': self.base_url
            }
            
            # Her sayfayı scrape et
            for page_num in range(1, total_pages + 1):
                # Sayfa URL'sini oluştur
                if page_num == 1:
                    page_url = thread_url
                else:
                    # XenForo v2 sayfalama formatı
                    separator = '&' if '?' in thread_url else '?'
                    page_url = f"{thread_url}{separator}page={page_num}"
                
                logger.info(f"Sayfa {page_num}/{total_pages} işleniyor...")
                
                # Sayfayı scrape et
                posts = self.scrape_page(page_url)
                self.posts_data.extend(posts)
                
                # Rate limiting
                if page_num < total_pages:
                    logger.info(f"{delay} saniye bekleniyor...")
                    time.sleep(delay)
            
            logger.info(f"Toplam {len(self.posts_data)} post scrape edildi")
            return True
            
        except Exception as e:
            logger.error(f"Thread scrape edilirken hata: {e}")
            return False
    
    def save_to_json(self, filename: Path) -> bool:
        """
        Scrape edilen veriyi JSON dosyasına kaydeder.
        
        Args:
            filename: JSON dosya yolu
        
        Returns:
            Başarılı ise True
        """
        try:
            filename.parent.mkdir(parents=True, exist_ok=True)
            
            output_data = {
                'thread_info': self.thread_info,
                'total_posts': len(self.posts_data),
                'posts': self.posts_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Veri JSON dosyasına kaydedildi: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"JSON kaydedilirken hata: {e}")
            return False
    
    def load_from_json(self, filename: Path) -> bool:
        """
        JSON dosyasından veri yükler.
        
        Args:
            filename: JSON dosya yolu
        
        Returns:
            Başarılı ise True
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.thread_info = data.get('thread_info', {})
            self.posts_data = data.get('posts', [])
            self.thread_title = self.thread_info.get('title', '')
            
            logger.info(f"Veri JSON dosyasından yüklendi: {filename}")
            logger.info(f"Toplam {len(self.posts_data)} post yüklendi")
            return True
            
        except Exception as e:
            logger.error(f"JSON yüklenirken hata: {e}")
            return False
