"""
XenForo Forum Archiver - Site Generator Modülü

Bu modül Jinja2 kullanarak statik HTML web sitesi oluşturur.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.utils import setup_logger, truncate_text, extract_youtube_id, extract_vimeo_id
import config


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class WebSiteGenerator:
    """Statik web sitesi oluşturma sınıfı"""
    
    def __init__(
        self,
        output_dir: Path,
        templates_dir: Path,
        thread_info: Dict[str, Any],
        categorized_posts: Dict[str, List[Dict[str, Any]]],
        stats: Dict[str, Any],
        media_mappings: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            output_dir: Web sitesinin oluşturulacağı dizin
            templates_dir: Jinja2 template'lerinin bulunduğu dizin
            thread_info: Thread bilgileri
            categorized_posts: Kategorize edilmiş postlar
            stats: İstatistikler
            media_mappings: Medya dosyası mapping'leri
        """
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.thread_info = thread_info
        self.categorized_posts = categorized_posts
        self.stats = stats
        self.media_mappings = media_mappings or {}
        
        # Jinja2 environment oluştur
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Custom filters ekle
        self.env.filters['truncate_text'] = truncate_text
        self.env.filters['youtube_id'] = extract_youtube_id
        self.env.filters['vimeo_id'] = extract_vimeo_id
    
    def _update_media_paths(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Post'lardaki medya URL'lerini local path'lerle günceller.
        
        Args:
            posts: Post listesi
        
        Returns:
            Güncellenmiş post listesi
        """
        image_mapping = self.media_mappings.get('images', {})
        attachment_mapping = self.media_mappings.get('attachments', {})
        
        for post in posts:
            # Görselleri güncelle
            for img in post.get('images', []):
                original_url = img.get('data_src') or img.get('src')
                if original_url in image_mapping:
                    img['local_path'] = image_mapping[original_url]
            
            # Ekleri güncelle
            for att in post.get('attachments', []):
                original_url = att.get('url')
                if original_url in attachment_mapping:
                    att['local_path'] = attachment_mapping[original_url]
        
        return posts
    
    def _create_css(self) -> None:
        """Ana CSS dosyasını oluşturur."""
        css_content = """
/* XenForo Forum Archiver - Stil Dosyası */

:root {
    --primary-color: #2196F3;
    --secondary-color: #FFC107;
    --text-color: #333;
    --bg-color: #f5f5f5;
    --card-bg: #ffffff;
    --border-color: #ddd;
    --shadow: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-hover: 0 4px 8px rgba(0,0,0,0.15);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: linear-gradient(135deg, var(--primary-color) 0%, #1976D2 100%);
    color: white;
    padding: 30px 0;
    margin-bottom: 30px;
    box-shadow: var(--shadow);
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

nav {
    background: white;
    padding: 15px 0;
    margin-bottom: 30px;
    box-shadow: var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
}

nav ul {
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
}

nav a {
    color: var(--text-color);
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 5px;
    transition: all 0.3s;
}

nav a:hover {
    background: var(--primary-color);
    color: white;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: var(--card-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: var(--shadow);
    text-align: center;
    transition: transform 0.3s;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-hover);
}

.stat-card h3 {
    color: var(--primary-color);
    font-size: 2rem;
    margin-bottom: 10px;
}

.category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.category-card {
    background: var(--card-bg);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: transform 0.3s;
}

.category-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-hover);
}

.category-header {
    background: var(--primary-color);
    color: white;
    padding: 20px;
}

.category-header h2 {
    font-size: 1.5rem;
}

.category-content {
    padding: 20px;
}

.post-card {
    background: var(--card-bg);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: var(--shadow);
    transition: transform 0.3s;
}

.post-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.post-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid var(--border-color);
}

.post-author {
    font-weight: bold;
    color: var(--primary-color);
}

.post-date {
    color: #666;
    font-size: 0.9rem;
}

.post-content {
    margin-bottom: 15px;
    line-height: 1.8;
}

.post-content img {
    max-width: 100%;
    height: auto;
    border-radius: 5px;
    margin: 10px 0;
    box-shadow: var(--shadow);
}

.post-media {
    margin-top: 15px;
}

.media-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.media-item {
    position: relative;
    overflow: hidden;
    border-radius: 5px;
}

.media-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.3s;
}

.media-item:hover img {
    transform: scale(1.05);
}

.video-container {
    position: relative;
    padding-bottom: 56.25%;
    height: 0;
    overflow: hidden;
    margin: 15px 0;
    border-radius: 5px;
}

.video-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 15px;
}

.tag {
    background: var(--bg-color);
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 0.85rem;
    color: var(--text-color);
}

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 20px 0;
    margin-top: 50px;
}

/* Responsive */
@media (max-width: 768px) {
    header h1 {
        font-size: 1.8rem;
    }
    
    .stats-grid,
    .category-grid {
        grid-template-columns: 1fr;
    }
    
    nav ul {
        flex-direction: column;
        align-items: center;
    }
}

/* Dark mode ready */
@media (prefers-color-scheme: dark) {
    :root {
        --text-color: #e0e0e0;
        --bg-color: #1a1a1a;
        --card-bg: #2d2d2d;
        --border-color: #444;
    }
}
"""
        css_dir = self.output_dir / 'css'
        css_dir.mkdir(parents=True, exist_ok=True)
        
        css_file = css_dir / 'style.css'
        css_file.write_text(css_content, encoding='utf-8')
        
        logger.info(f"CSS dosyası oluşturuldu: {css_file}")
    
    def generate_index_page(self) -> None:
        """Ana sayfa HTML'ini oluşturur."""
        logger.info("Ana sayfa oluşturuluyor...")
        
        template = self.env.get_template('index.html')
        
        # Kategorilere göre post sayılarını hazırla
        category_data = []
        for category, posts in self.categorized_posts.items():
            if posts:
                category_data.append({
                    'name': category,
                    'count': len(posts),
                    'posts': posts[:5]  # İlk 5 post
                })
        
        html_content = template.render(
            thread_info=self.thread_info,
            categories=category_data,
            stats=self.stats,
            generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        output_file = self.output_dir / 'index.html'
        output_file.write_text(html_content, encoding='utf-8')
        
        logger.info(f"Ana sayfa oluşturuldu: {output_file}")
    
    def generate_category_pages(self) -> None:
        """Kategori sayfalarını oluşturur."""
        logger.info("Kategori sayfaları oluşturuluyor...")
        
        template = self.env.get_template('category.html')
        
        for category, posts in self.categorized_posts.items():
            if not posts:
                continue
            
            # Medya path'lerini güncelle
            posts = self._update_media_paths(posts)
            
            html_content = template.render(
                category=category,
                posts=posts,
                thread_info=self.thread_info,
                stats=self.stats
            )
            
            output_file = self.output_dir / f'{category}.html'
            output_file.write_text(html_content, encoding='utf-8')
            
            logger.info(f"Kategori sayfası oluşturuldu: {output_file} ({len(posts)} post)")
    
    def generate_post_pages(self) -> None:
        """Tekil post sayfalarını oluşturur."""
        logger.info("Post sayfaları oluşturuluyor...")
        
        template = self.env.get_template('post.html')
        
        posts_dir = self.output_dir / 'posts'
        posts_dir.mkdir(parents=True, exist_ok=True)
        
        total_posts = sum(len(posts) for posts in self.categorized_posts.values())
        generated = 0
        
        for category, posts in self.categorized_posts.items():
            posts = self._update_media_paths(posts)
            
            for post in posts:
                post_id = post.get('post_id', generated)
                
                html_content = template.render(
                    post=post,
                    category=category,
                    thread_info=self.thread_info
                )
                
                output_file = posts_dir / f'post_{post_id}.html'
                output_file.write_text(html_content, encoding='utf-8')
                
                generated += 1
        
        logger.info(f"{generated}/{total_posts} post sayfası oluşturuldu")
    
    def copy_media_files(self, media_dir: Path) -> None:
        """Medya dosyalarını web sitesi dizinine kopyalar."""
        if not media_dir.exists():
            logger.warning(f"Medya dizini bulunamadı: {media_dir}")
            return
        
        logger.info("Medya dosyaları kopyalanıyor...")
        
        dest_dir = self.output_dir / media_dir.name
        
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        
        shutil.copytree(media_dir, dest_dir)
        
        logger.info(f"Medya dosyaları kopyalandı: {dest_dir}")
    
    def generate_site(self, copy_media: bool = True) -> bool:
        """
        Tüm web sitesini oluşturur.
        
        Args:
            copy_media: Medya dosyalarını kopyalasın mı
        
        Returns:
            Başarılı ise True
        """
        try:
            logger.info("Web sitesi oluşturuluyor...")
            
            # Çıktı dizinini oluştur
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # CSS oluştur
            self._create_css()
            
            # Sayfaları oluştur
            self.generate_index_page()
            self.generate_category_pages()
            self.generate_post_pages()
            
            # Medya dosyalarını kopyala
            if copy_media and self.media_mappings:
                media_base = config.MEDIA_DIR
                if media_base.exists():
                    self.copy_media_files(media_base)
            
            logger.info(f"Web sitesi başarıyla oluşturuldu: {self.output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Web sitesi oluşturulurken hata: {e}")
            return False
