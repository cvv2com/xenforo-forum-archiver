"""
XenForo Forum Archiver - Categorizer Tests

This file contains test scenarios for the ContentCategorizer class.
"""

import unittest
from pathlib import Path
import sys

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.categorizer import ContentCategorizer
import config


class TestContentCategorizer(unittest.TestCase):
    """Test scenarios for ContentCategorizer class"""
    
    def setUp(self):
        """Run before each test"""
        self.categorizer = ContentCategorizer()
        
        # Test data
        self.sample_posts = [
            {
                'post_id': '1',
                'author': 'Test User 1',
                'content_text': 'This is a review post. It was tested and analyzed.',
                'content_html': '<p>This is a review post. It was tested and analyzed.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '2',
                'author': 'Test User 2',
                'content_text': 'How to install? Step by step guide.',
                'content_html': '<p>How to install? Step by step guide.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '3',
                'author': 'Test User 3',
                'content_text': 'New update announcement! Great news.',
                'content_html': '<p>New update announcement! Great news.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '4',
                'author': 'Test User 4',
                'content_text': 'I want to start a discussion on this topic. To ask questions and get help.',
                'content_html': '<p>I want to start a discussion on this topic. To ask questions and get help.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            },
            {
                'post_id': '5',
                'author': 'Test User 5',
                'content_text': 'Video sharing.',
                'content_html': '<p>Video sharing.</p>',
                'images': [],
                'videos': [{'type': 'youtube', 'src': 'https://youtube.com/watch?v=test'}],
                'attachments': []
            },
            {
                'post_id': '6',
                'author': 'Test User 6',
                'content_text': 'Just a post.',
                'content_html': '<p>Just a post.</p>',
                'images': [],
                'videos': [],
                'attachments': []
            }
        ]
    
    def test_categorize_post_review(self):
        """Review category test"""
        post = self.sample_posts[0]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'review')
        self.assertIn('category', post)
        self.assertIn('content_type', post)
    
    def test_categorize_post_guide(self):
        """Guide category test"""
        post = self.sample_posts[1]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'guide')
    
    def test_categorize_post_news(self):
        """News category test"""
        post = self.sample_posts[2]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'news')
    
    def test_categorize_post_discussion(self):
        """Discussion category test"""
        post = self.sample_posts[3]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'discussion')
    
    def test_categorize_post_media(self):
        """Media category test"""
        post = self.sample_posts[4]
        category = self.categorizer.categorize_post(post)
        # May fall into media category because it contains video
        self.assertIn(category, ['media', 'other'])
    
    def test_categorize_post_other(self):
        """Other category test"""
        post = self.sample_posts[5]
        category = self.categorizer.categorize_post(post)
        self.assertEqual(category, 'other')
    
    def test_categorize_posts(self):
        """Batch categorization test"""
        categorized = self.categorizer.categorize_posts(self.sample_posts)
        
        # Check that all categories are in the dictionary
        for category in config.CATEGORY_RULES.keys():
            self.assertIn(category, categorized)
        
        # Check that total post count is preserved
        total_categorized = sum(len(posts) for posts in categorized.values())
        self.assertEqual(total_categorized, len(self.sample_posts))
    
    def test_determine_content_type_video(self):
        """Video content type test"""
        post = self.sample_posts[4]
        content_type = self.categorizer._determine_content_type(post)
        self.assertEqual(content_type, 'video')
    
    def test_determine_content_type_text(self):
        """Text content type test"""
        post = self.sample_posts[0]
        content_type = self.categorizer._determine_content_type(post)
        self.assertEqual(content_type, 'text')
    
    def test_extract_tags(self):
        """Tag extraction test"""
        post = {
            'content_text': 'This is a #test #python post. Python is a great language.'
        }
        tags = self.categorizer._extract_tags(post)
        
        # At least one tag should be extracted
        self.assertGreater(len(tags), 0)
        
        # Check that hashtags are extracted
        self.assertIn('test', tags)
        self.assertIn('python', tags)
    
    def test_calculate_stats(self):
        """Statistics calculation test"""
        self.categorizer.categorize_posts(self.sample_posts)
        stats = self.categorizer.get_stats()
        
        # Check that statistics are calculated
        self.assertIn('total_posts', stats)
        self.assertEqual(stats['total_posts'], len(self.sample_posts))
        self.assertIn('category_distribution', stats)
        self.assertIn('content_type_distribution', stats)
        self.assertIn('author_distribution', stats)
    
    def test_empty_posts_list(self):
        """Empty posts list test"""
        categorized = self.categorizer.categorize_posts([])
        
        # All categories should be empty for empty list
        for posts in categorized.values():
            self.assertEqual(len(posts), 0)
    
    def test_custom_category_rules(self):
        """Custom category rules test"""
        custom_rules = {
            'technology': {
                'keywords': ['python', 'code', 'program'],
                'priority': 1
            },
            'other': {
                'keywords': [],
                'priority': 99
            }
        }
        
        categorizer = ContentCategorizer(category_rules=custom_rules)
        
        post = {
            'post_id': '1',
            'content_text': 'Python programming language',
            'content_html': '<p>Python programming language</p>',
            'images': [],
            'videos': [],
            'attachments': []
        }
        
        category = categorizer.categorize_post(post)
        self.assertEqual(category, 'technology')


def run_tests():
    """Run tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
