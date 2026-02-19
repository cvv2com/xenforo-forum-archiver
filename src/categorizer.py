"""
XenForo Forum Archiver - Categorizer Module

This module automatically categorizes content.
"""

import re
from typing import Dict, List, Any, Set
from collections import Counter

from src.utils import setup_logger, clean_html_text
import config


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class ContentCategorizer:
    """Content categorization class"""
    
    def __init__(self, category_rules: Dict[str, Any] = None):
        """
        Args:
            category_rules: Category rules dictionary
        """
        self.category_rules = category_rules or config.CATEGORY_RULES
        self.categorized_posts: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.category_rules.keys()
        }
        self.stats: Dict[str, Any] = {}
    
    def _determine_content_type(self, post: Dict[str, Any]) -> str:
        """
        Determines the content type of the post.
        
        Args:
            post: Post data
        
        Returns:
            Content type (text, image, video, attachment, code, link)
        """
        images_count = len(post.get('images', []))
        videos_count = len(post.get('videos', []))
        attachments_count = len(post.get('attachments', []))
        content_text = post.get('content_text', '')
        
        # Video content
        if videos_count > 0:
            return 'video'
        
        # Image-heavy content
        if images_count > 3:
            return 'image'
        
        # Attachment content
        if attachments_count > 0:
            return 'attachment'
        
        # Code content
        if '<code>' in post.get('content_html', '') or '```' in content_text:
            return 'code'
        
        # Link-heavy content
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(link_pattern, content_text)
        if len(links) > 2:
            return 'link'
        
        # Default: text
        return 'text'
    
    def _extract_tags(self, post: Dict[str, Any]) -> List[str]:
        """
        Extracts tags from the post.
        
        Args:
            post: Post data
        
        Returns:
            List of tags
        """
        tags = []
        content_text = post.get('content_text', '')
        
        # Find hashtags
        hashtags = re.findall(r'#(\w+)', content_text)
        tags.extend(hashtags)
        
        # Find words starting with capital letter (proper nouns)
        words = content_text.split()
        proper_nouns = [word.strip('.,!?;:') for word in words if word and word[0].isupper() and len(word) > 3]
        tags.extend(proper_nouns[:5])  # First 5 proper nouns
        
        # Remove duplicates and convert to lowercase
        tags = list(set([tag.lower() for tag in tags]))
        
        return tags[:10]  # Maximum 10 tags
    
    def _calculate_category_score(self, post: Dict[str, Any], category: str) -> float:
        """
        Calculates the category score for the post.
        
        Args:
            post: Post data
            category: Category name
        
        Returns:
            Score (between 0-1)
        """
        if category not in self.category_rules:
            return 0.0
        
        keywords = self.category_rules[category]['keywords']
        if not keywords:
            return 0.0
        
        content_text = post.get('content_text', '').lower()
        title_text = post.get('title', '').lower()
        
        # Keyword match count
        matches = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Title match (2x weight)
            if keyword_lower in title_text:
                matches += 2
            # Content match
            if keyword_lower in content_text:
                matches += 1
        
        # Normalize
        max_possible_score = len(keywords) * 3  # Max 3 points per keyword
        score = matches / max_possible_score if max_possible_score > 0 else 0.0
        
        return min(score, 1.0)
    
    def categorize_post(self, post: Dict[str, Any]) -> str:
        """
        Categorizes a single post.
        
        Args:
            post: Post data
        
        Returns:
            Category name
        """
        # Calculate score for each category
        scores: Dict[str, float] = {}
        for category in self.category_rules.keys():
            if category != 'other':  # Skip 'other' category from calculation
                score = self._calculate_category_score(post, category)
                scores[category] = score
        
        # Find the category with the highest score
        if scores and max(scores.values()) > 0.1:  # Minimum threshold
            best_category = max(scores, key=scores.get)
        else:
            best_category = 'other'
        
        # Add category and score information to post
        post['category'] = best_category
        post['category_score'] = scores.get(best_category, 0.0)
        post['content_type'] = self._determine_content_type(post)
        
        # Extract tags
        if config.EXTRACT_TAGS:
            post['tags'] = self._extract_tags(post)
        
        return best_category
    
    def categorize_posts(self, posts_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorizes all posts.
        
        Args:
            posts_data: List of post data
        
        Returns:
            Dictionary of categorized posts
        """
        logger.info(f"Categorizing total of {len(posts_data)} posts...")
        
        # Categorize each post
        for post in posts_data:
            category = self.categorize_post(post)
            self.categorized_posts[category].append(post)
        
        # Calculate statistics
        self._calculate_stats(posts_data)
        
        # Print statistics
        self._print_stats()
        
        return self.categorized_posts
    
    def _calculate_stats(self, posts_data: List[Dict[str, Any]]) -> None:
        """
        Calculates categorization statistics.
        
        Args:
            posts_data: List of post data
        """
        total_posts = len(posts_data)
        
        # Category distribution
        category_distribution = {
            category: len(posts) for category, posts in self.categorized_posts.items()
        }
        
        # Content type distribution
        content_types = [post.get('content_type', 'unknown') for post in posts_data]
        content_type_distribution = dict(Counter(content_types))
        
        # Author distribution
        authors = [post.get('author', 'Unknown') for post in posts_data]
        author_distribution = dict(Counter(authors).most_common(10))
        
        # Image/video statistics
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
        """Prints statistics to console."""
        logger.info("\n" + "="*50)
        logger.info("CATEGORIZATION STATISTICS")
        logger.info("="*50)
        
        logger.info(f"\nTotal Posts: {self.stats['total_posts']}")
        
        logger.info("\nCategory Distribution:")
        for category, count in sorted(
            self.stats['category_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = (count / self.stats['total_posts'] * 100) if self.stats['total_posts'] > 0 else 0
            logger.info(f"  {category.capitalize()}: {count} ({percentage:.1f}%)")
        
        logger.info("\nContent Type Distribution:")
        for content_type, count in sorted(
            self.stats['content_type_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            logger.info(f"  {content_type.capitalize()}: {count}")
        
        logger.info("\nMost Active Authors (Top 10):")
        for author, count in list(self.stats['author_distribution'].items())[:10]:
            logger.info(f"  {author}: {count} posts")
        
        logger.info("\nMedia Statistics:")
        logger.info(f"  Total Images: {self.stats['total_images']}")
        logger.info(f"  Total Videos: {self.stats['total_videos']}")
        logger.info(f"  Total Attachments: {self.stats['total_attachments']}")
        
        logger.info("="*50 + "\n")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returns statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.stats
