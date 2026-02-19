"""
XenForo Forum Archiver - Categorizer Modülü

Bu modül içerikleri otomatik olarak kategorize eder.
"""

import re
from typing import Dict, List, Any, Set
from collections import Counter

from src.utils import setup_logger, clean_html_text
import config


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class ContentCategorizer:
    """İçerik kategorizasyon sınıfı"""
    
    def __init__(self, category_rules: Dict[str, Any] = None):
        """
        Args:
            category_rules: Kategori kuralları dictionary
        """
        self.category_rules = category_rules or config.CATEGORY_RULES
        self.categorized_posts: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.category_rules.keys()
        }
        self.stats: Dict[str, Any] = {}
    
    def _determine_content_type(self, post: Dict[str, Any]) -> str:
        """
        Post'un içerik tipini belirler.
        
        Args:
            post: Post verisi
        
        Returns:
            İçerik tipi (text, image, video, attachment, code, link)
        """
        images_count = len(post.get('images', []))
        videos_count = len(post.get('videos', []))
        attachments_count = len(post.get('attachments', []))
        content_text = post.get('content_text', '')
        
        # Video içerik
        if videos_count > 0:
            return 'video'
        
        # Görsel ağırlıklı içerik
        if images_count > 3:
            return 'image'
        
        # Ek dosya içerik
        if attachments_count > 0:
            return 'attachment'
        
        # Kod içerik
        if '<code>' in post.get('content_html', '') or '```' in content_text:
            return 'code'
        
        # Link ağırlıklı içerik
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(link_pattern, content_text)
        if len(links) > 2:
            return 'link'
        
        # Varsayılan: text
        return 'text'
    
    def _extract_tags(self, post: Dict[str, Any]) -> List[str]:
        """
        Post'tan etiketleri çıkarır.
        
        Args:
            post: Post verisi
        
        Returns:
            Etiket listesi
        """
        tags = []
        content_text = post.get('content_text', '')
        
        # Hashtag'leri bul
        hashtags = re.findall(r'#(\w+)', content_text)
        tags.extend(hashtags)
        
        # Büyük harfle başlayan kelimeleri bul (proper nouns)
        words = content_text.split()
        proper_nouns = [word.strip('.,!?;:') for word in words if word and word[0].isupper() and len(word) > 3]
        tags.extend(proper_nouns[:5])  # İlk 5 proper noun
        
        # Tekrarları kaldır ve küçük harfe çevir
        tags = list(set([tag.lower() for tag in tags]))
        
        return tags[:10]  # Maksimum 10 etiket
    
    def _calculate_category_score(self, post: Dict[str, Any], category: str) -> float:
        """
        Post için kategori skorunu hesaplar.
        
        Args:
            post: Post verisi
            category: Kategori adı
        
        Returns:
            Skor (0-1 arası)
        """
        if category not in self.category_rules:
            return 0.0
        
        keywords = self.category_rules[category]['keywords']
        if not keywords:
            return 0.0
        
        content_text = post.get('content_text', '').lower()
        title_text = post.get('title', '').lower()
        
        # Keyword eşleşme sayısı
        matches = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Başlıkta eşleşme (2x ağırlık)
            if keyword_lower in title_text:
                matches += 2
            # İçerikte eşleşme
            if keyword_lower in content_text:
                matches += 1
        
        # Normalize et
        max_possible_score = len(keywords) * 3  # Her keyword için max 3 puan
        score = matches / max_possible_score if max_possible_score > 0 else 0.0
        
        return min(score, 1.0)
    
    def categorize_post(self, post: Dict[str, Any]) -> str:
        """
        Tek bir post'u kategorize eder.
        
        Args:
            post: Post verisi
        
        Returns:
            Kategori adı
        """
        # Her kategori için skor hesapla
        scores: Dict[str, float] = {}
        for category in self.category_rules.keys():
            if category != 'diger':  # 'diger' kategorisini hesaplamadan atla
                score = self._calculate_category_score(post, category)
                scores[category] = score
        
        # En yüksek skora sahip kategoriyi bul
        if scores and max(scores.values()) > 0.1:  # Minimum threshold
            best_category = max(scores, key=scores.get)
        else:
            best_category = 'diger'
        
        # Post'a kategori ve skor bilgisini ekle
        post['category'] = best_category
        post['category_score'] = scores.get(best_category, 0.0)
        post['content_type'] = self._determine_content_type(post)
        
        # Etiketleri çıkar
        if config.EXTRACT_TAGS:
            post['tags'] = self._extract_tags(post)
        
        return best_category
    
    def categorize_posts(self, posts_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Tüm postları kategorize eder.
        
        Args:
            posts_data: Post verisi listesi
        
        Returns:
            Kategorize edilmiş postlar dictionary
        """
        logger.info(f"Toplam {len(posts_data)} post kategorize ediliyor...")
        
        # Her post'u kategorize et
        for post in posts_data:
            category = self.categorize_post(post)
            self.categorized_posts[category].append(post)
        
        # İstatistikleri hesapla
        self._calculate_stats(posts_data)
        
        # İstatistikleri yazdır
        self._print_stats()
        
        return self.categorized_posts
    
    def _calculate_stats(self, posts_data: List[Dict[str, Any]]) -> None:
        """
        Kategorizasyon istatistiklerini hesaplar.
        
        Args:
            posts_data: Post verisi listesi
        """
        total_posts = len(posts_data)
        
        # Kategori dağılımı
        category_distribution = {
            category: len(posts) for category, posts in self.categorized_posts.items()
        }
        
        # İçerik tipi dağılımı
        content_types = [post.get('content_type', 'unknown') for post in posts_data]
        content_type_distribution = dict(Counter(content_types))
        
        # Yazar dağılımı
        authors = [post.get('author', 'Unknown') for post in posts_data]
        author_distribution = dict(Counter(authors).most_common(10))
        
        # Görsel/video istatistikleri
        total_images = sum(len(post.get('images', [])) for post in posts_data)
        total_videos = sum(len(post.get('videos', [])) for post in posts_data)
        total_attachments = sum(len(post.get('attachments', [])) for post in posts_data)
        
        self.stats = {
            'total_posts': total_posts,
            'category_distribution': category_distribution,
            'content_type_distribution': content_type_distribution,
            'author_distribution': author_distribution,
            'total_images': total_images,
            'total_videos': total_videos,
            'total_attachments': total_attachments
        }
    
    def _print_stats(self) -> None:
        """İstatistikleri konsola yazdırır."""
        logger.info("\n" + "="*50)
        logger.info("KATEGORİZASYON İSTATİSTİKLERİ")
        logger.info("="*50)
        
        logger.info(f"\nToplam Post: {self.stats['total_posts']}")
        
        logger.info("\nKategori Dağılımı:")
        for category, count in sorted(
            self.stats['category_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = (count / self.stats['total_posts'] * 100) if self.stats['total_posts'] > 0 else 0
            logger.info(f"  {category.capitalize()}: {count} (%{percentage:.1f})")
        
        logger.info("\nİçerik Tipi Dağılımı:")
        for content_type, count in sorted(
            self.stats['content_type_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            logger.info(f"  {content_type.capitalize()}: {count}")
        
        logger.info("\nEn Aktif Yazarlar (Top 10):")
        for author, count in list(self.stats['author_distribution'].items())[:10]:
            logger.info(f"  {author}: {count} post")
        
        logger.info("\nMedya İstatistikleri:")
        logger.info(f"  Toplam Görsel: {self.stats['total_images']}")
        logger.info(f"  Toplam Video: {self.stats['total_videos']}")
        logger.info(f"  Toplam Ek Dosya: {self.stats['total_attachments']}")
        
        logger.info("="*50 + "\n")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        İstatistikleri döndürür.
        
        Returns:
            İstatistik dictionary
        """
        return self.stats
