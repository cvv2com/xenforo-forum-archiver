"""
XenForo Forum Archiver - Categorizer Testleri

Bu dosya ContentCategorizer sınıfının test senaryolarını içerir.
"""

import unittest
from pathlib import Path
import sys

# Proje kök dizinini path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.categorizer import ContentCategorizer
import config


class TestContentCategorizer(unittest.TestCase):
    """ContentCategorizer sınıfı için test senaryoları"""
    
    def setUp(self):
        """Her testten önce çalışır"""
        self.categorizer = ContentCategorizer()
        
        # Test verisi
        self.sample_posts = [
            {
                'post_id': '1',
                'author': 'Test User 1',
                'content_text': 'Bu bir inceleme yazısıdır. Test edildi ve analiz yapıldı.',
                'content_html': '<p>Bu bir inceleme yazısıdır. Test edildi ve analiz yapıldı.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '2',
                'author': 'Test User 2',
                'content_text': 'Nasıl kurulum yapılır? Adım adım rehber.',
                'content_html': '<p>Nasıl kurulum yapılır? Adım adım rehber.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '3',
                'author': 'Test User 3',
                'content_text': 'Yeni güncelleme duyurusu! Harika bir haber.',
                'content_html': '<p>Yeni güncelleme duyurusu! Harika bir haber.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '4',
                'author': 'Test User 4',
                'content_text': 'Bu konu hakkında ne düşünüyorsunuz? Tartışalım.',
                'content_html': '<p>Bu konu hakkında ne düşünüyorsunuz? Tartışalım.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '5',
                'author': 'Test User 5',
                'content_text': 'Video paylaşımı.',
                'content_html': '<p>Video paylaşımı.</p>',
                'images': [],
                'videos': [{'type': 'youtube', 'src': 'https://youtube.com/watch?v=test'}],
                'attachments': []
            },
            {
                'post_id': '6',
                'author': 'Test User 6',
                'content_text': 'Sadece bir paylaşım.',
                'content_html': '<p>Sadece bir paylaşım.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            }
        ]
    
    def test_categorize_post_inceleme(self):
        """İnceleme kategorisi testi"""
        post = self.sample_posts[0]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'inceleme')
        self.assertIn('category', post)
        self.assertIn('content_type', post)
    
    def test_categorize_post_rehber(self):
        """Rehber kategorisi testi"""
        post = self.sample_posts[1]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'rehber')
    
    def test_categorize_post_haber(self):
        """Haber kategorisi testi"""
        post = self.sample_posts[2]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'haber')
    
    def test_categorize_post_tartisma(self):
        """Tartışma kategorisi testi"""
        post = self.sample_posts[3]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'tartisma')
    
    def test_categorize_post_medya(self):
        """Medya kategorisi testi"""
        post = self.sample_posts[4]
        category = self.categorizer.categorize_post(post)
        # Video içerdiği için medya kategorisine düşebilir
        self.assertIn(category, ['medya', 'diger'])
    
    def test_categorize_post_diger(self):
        """Diğer kategorisi testi"""
        post = self.sample_posts[5]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'diger')
    
    def test_categorize_posts(self):
        """Toplu kategorizasyon testi"""
        categorized = self.categorizer.categorize_posts(self.sample_posts)
        
        # Tüm kategorilerin dictionary'de olduğunu kontrol et
        for category in config.CATEGORY_RULES.keys():
            self.assertIn(category, categorized)
        
        # Toplam post sayısının korunduğunu kontrol et
        total_categorized = sum(len(posts) for posts in categorized.values())
        self.assertEqual(total_categorized, len(self.sample_posts))
    
    def test_determine_content_type_video(self):
        """Video içerik tipi testi"""
        post = self.sample_posts[4]
        content_type = self.categorizer._determine_content_type(post)
        self.assertEqual(content_type, 'video')
    
    def test_determine_content_type_text(self):
        """Text içerik tipi testi"""
        post = self.sample_posts[0]
        content_type = self.categorizer._determine_content_type(post)
        self.assertEqual(content_type, 'text')
    
    def test_extract_tags(self):
        """Etiket çıkarma testi"""
        post = {
            'content_text': 'Bu bir #test #python paylaşımıdır. Python güzel bir dildir.'
        }
        tags = self.categorizer._extract_tags(post)
        
        # En az bir etiket çıkarılmalı
        self.assertGreater(len(tags), 0)
        
        # Hashtag'lerin çıkarıldığını kontrol et
        self.assertIn('test', tags)
        self.assertIn('python', tags)
    
    def test_calculate_stats(self):
        """İstatistik hesaplama testi"""
        self.categorizer.categorize_posts(self.sample_posts)
        stats = self.categorizer.get_stats()
        
        # İstatistiklerin hesaplandığını kontrol et
        self.assertIn('total_posts', stats)
        self.assertEqual(stats['total_posts'], len(self.sample_posts))
        self.assertIn('category_distribution', stats)
        self.assertIn('content_type_distribution', stats)
        self.assertIn('author_distribution', stats)
    
    def test_empty_posts_list(self):
        """Boş post listesi testi"""
        categorized = self.categorizer.categorize_posts([])
        
        # Boş liste için tüm kategoriler boş olmalı
        for posts in categorized.values():
            self.assertEqual(len(posts), 0)
    
    def test_custom_category_rules(self):
        """Özel kategori kuralları testi"""
        custom_rules = {
            'teknoloji': {
                'keywords': ['python', 'kod', 'program'],
                'priority': 1
            },
            'diger': {
                'keywords': [],
                'priority': 99
            }
        }
        
        categorizer = ContentCategorizer(category_rules=custom_rules)
        
        post = {
            'post_id': '1',
            'content_text': 'Python programlama dili',
            'content_html': '<p>Python programlama dili</p>',
            'images': [],
            'videos': [],
            'attachments': []
        }
        
        category = categorizer.categorize_post(post)
        self.assertEqual(category, 'teknoloji')


def run_tests():
    """Testleri çalıştır"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
