"""
XenForo Forum Archiver - Downloader Modülü

Bu modül görseller, videolar ve ek dosyaları indirir.
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from src.utils import setup_logger, sanitize_filename, format_file_size
import config


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


class MediaDownloader:
    """Medya dosyaları indirme sınıfı"""
    
    def __init__(self, session: requests.Session, output_dir: Path):
        """
        Args:
            session: Requests session
            output_dir: İndirilen dosyaların kaydedileceği dizin
        """
        self.session = session
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.images_dir = output_dir / 'images'
        self.attachments_dir = output_dir / 'attachments'
        self.thumbnails_dir = output_dir / 'thumbnails'
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        self.downloaded_files: Dict[str, str] = {}
    
    def _get_filename_from_url(self, url: str) -> str:
        """
        URL'den dosya adını çıkarır.
        
        Args:
            url: Dosya URL'si
        
        Returns:
            Dosya adı
        """
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        if not filename:
            filename = f"file_{hash(url)}"
        return sanitize_filename(filename)
    
    def _download_file(
        self,
        url: str,
        output_path: Path,
        max_retries: int = config.MAX_RETRIES
    ) -> Optional[Path]:
        """
        Tek bir dosyayı indirir.
        
        Args:
            url: Dosya URL'si
            output_path: Kaydedilecek dosya yolu
            max_retries: Maksimum deneme sayısı
        
        Returns:
            İndirilen dosya yolu veya None
        """
        # Daha önce indirilmiş mi kontrol et
        if url in self.downloaded_files:
            return Path(self.downloaded_files[url])
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT, stream=True)
                response.raise_for_status()
                
                # Dosya boyutunu al
                total_size = int(response.headers.get('content-length', 0))
                
                # Dosyayı indir
                with open(output_path, 'wb') as f:
                    if total_size == 0:
                        f.write(response.content)
                    else:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                
                logger.debug(f"İndirildi: {output_path.name} ({format_file_size(output_path.stat().st_size)})")
                self.downloaded_files[url] = str(output_path)
                return output_path
                
            except Exception as e:
                logger.warning(f"İndirme denemesi {attempt + 1}/{max_retries} başarısız: {url} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(config.RETRY_DELAY)
                else:
                    logger.error(f"Dosya indirilemedi: {url}")
                    return None
    
    def download_images(self, posts_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Tüm görselleri indirir.
        
        Args:
            posts_data: Post verisi listesi
        
        Returns:
            URL -> local path mapping
        """
        logger.info("Görseller indiriliyor...")
        
        # Tüm görsel URL'lerini topla
        image_urls = set()
        for post in posts_data:
            for img in post.get('images', []):
                url = img.get('data_src') or img.get('src')
                if url:
                    image_urls.add(url)
        
        logger.info(f"Toplam {len(image_urls)} görsel bulundu")
        
        # İndir
        image_mapping = {}
        with tqdm(total=len(image_urls), desc="Görseller", unit="dosya") as pbar:
            for url in image_urls:
                filename = self._get_filename_from_url(url)
                output_path = self.images_dir / filename
                
                # Aynı isimde dosya varsa numara ekle
                counter = 1
                while output_path.exists() and url not in self.downloaded_files:
                    name_parts = filename.rsplit('.', 1)
                    if len(name_parts) == 2:
                        output_path = self.images_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                    else:
                        output_path = self.images_dir / f"{filename}_{counter}"
                    counter += 1
                
                result = self._download_file(url, output_path)
                if result:
                    image_mapping[url] = str(output_path.relative_to(self.output_dir.parent))
                
                pbar.update(1)
        
        logger.info(f"{len(image_mapping)} görsel başarıyla indirildi")
        return image_mapping
    
    def download_attachments(self, posts_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Tüm ek dosyaları indirir.
        
        Args:
            posts_data: Post verisi listesi
        
        Returns:
            URL -> local path mapping
        """
        logger.info("Ek dosyalar indiriliyor...")
        
        # Tüm ek dosya URL'lerini topla
        attachment_urls = set()
        for post in posts_data:
            for att in post.get('attachments', []):
                url = att.get('url')
                if url:
                    attachment_urls.add(url)
        
        logger.info(f"Toplam {len(attachment_urls)} ek dosya bulundu")
        
        # İndir
        attachment_mapping = {}
        with tqdm(total=len(attachment_urls), desc="Ek dosyalar", unit="dosya") as pbar:
            for url in attachment_urls:
                filename = self._get_filename_from_url(url)
                output_path = self.attachments_dir / filename
                
                # Aynı isimde dosya varsa numara ekle
                counter = 1
                while output_path.exists() and url not in self.downloaded_files:
                    name_parts = filename.rsplit('.', 1)
                    if len(name_parts) == 2:
                        output_path = self.attachments_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                    else:
                        output_path = self.attachments_dir / f"{filename}_{counter}"
                    counter += 1
                
                result = self._download_file(url, output_path)
                if result:
                    attachment_mapping[url] = str(output_path.relative_to(self.output_dir.parent))
                
                pbar.update(1)
        
        logger.info(f"{len(attachment_mapping)} ek dosya başarıyla indirildi")
        return attachment_mapping
    
    def download_youtube_thumbnails(self, posts_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        YouTube videolarının thumbnail'larını indirir.
        
        Args:
            posts_data: Post verisi listesi
        
        Returns:
            Video ID -> thumbnail path mapping
        """
        logger.info("YouTube thumbnail'ları indiriliyor...")
        
        from src.utils import extract_youtube_id
        
        # YouTube video ID'lerini topla
        video_ids = set()
        for post in posts_data:
            for video in post.get('videos', []):
                if video.get('type') == 'youtube':
                    video_id = extract_youtube_id(video.get('src', ''))
                    if video_id:
                        video_ids.add(video_id)
        
        logger.info(f"Toplam {len(video_ids)} YouTube videosu bulundu")
        
        # Thumbnail'ları indir
        thumbnail_mapping = {}
        with tqdm(total=len(video_ids), desc="YouTube thumbnails", unit="dosya") as pbar:
            for video_id in video_ids:
                # YouTube thumbnail URL formatı
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                filename = f"youtube_{video_id}.jpg"
                output_path = self.thumbnails_dir / filename
                
                result = self._download_file(thumbnail_url, output_path)
                if result:
                    thumbnail_mapping[video_id] = str(output_path.relative_to(self.output_dir.parent))
                
                pbar.update(1)
        
        logger.info(f"{len(thumbnail_mapping)} YouTube thumbnail başarıyla indirildi")
        return thumbnail_mapping
    
    def download_all_media(self, posts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tüm medya dosyalarını indirir.
        
        Args:
            posts_data: Post verisi listesi
        
        Returns:
            Tüm mapping'leri içeren dictionary
        """
        mappings = {
            'images': self.download_images(posts_data),
            'attachments': self.download_attachments(posts_data),
            'youtube_thumbnails': self.download_youtube_thumbnails(posts_data)
        }
        
        total_downloaded = (
            len(mappings['images']) +
            len(mappings['attachments']) +
            len(mappings['youtube_thumbnails'])
        )
        
        logger.info(f"Toplam {total_downloaded} medya dosyası indirildi")
        return mappings
