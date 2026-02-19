"""
XenForo Forum Archiver - Yardımcı Fonksiyonlar

Bu modül projede kullanılan yardımcı fonksiyonları içerir.
"""

import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urljoin


def setup_logger(name: str, log_file: Optional[Path] = None, level: str = 'INFO') -> logging.Logger:
    """
    Logger yapılandırması oluşturur.
    
    Args:
        name: Logger adı
        log_file: Log dosyası yolu (opsiyonel)
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Yapılandırılmış logger nesnesi
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Formatter oluştur
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (eğer belirtilmişse)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def sanitize_filename(filename: str) -> str:
    """
    Dosya adını güvenli hale getirir.
    
    Args:
        filename: Orijinal dosya adı
    
    Returns:
        Güvenli dosya adı
    """
    # Geçersiz karakterleri kaldır
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Birden fazla boşluğu tek boşluğa çevir
    filename = re.sub(r'\s+', ' ', filename)
    # Başındaki ve sonundaki boşlukları kaldır
    filename = filename.strip()
    # Maksimum uzunluk kontrolü
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Byte cinsinden dosya boyutunu okunabilir formata çevirir.
    
    Args:
        size_bytes: Byte cinsinden boyut
    
    Returns:
        Okunabilir format (KB, MB, GB)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def extract_domain(url: str) -> str:
    """
    URL'den domain adını çıkarır.
    
    Args:
        url: Tam URL
    
    Returns:
        Domain adı
    """
    parsed = urlparse(url)
    return parsed.netloc


def is_valid_url(url: str) -> bool:
    """
    URL'nin geçerli olup olmadığını kontrol eder.
    
    Args:
        url: Kontrol edilecek URL
    
    Returns:
        True/False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Göreceli URL'yi mutlak URL'ye çevirir.
    
    Args:
        base_url: Ana URL
        relative_url: Göreceli URL
    
    Returns:
        Mutlak URL
    """
    return urljoin(base_url, relative_url)


def extract_youtube_id(url: str) -> Optional[str]:
    """
    YouTube URL'sinden video ID'sini çıkarır.
    
    Args:
        url: YouTube URL'si
    
    Returns:
        Video ID veya None
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_vimeo_id(url: str) -> Optional[str]:
    """
    Vimeo URL'sinden video ID'sini çıkarır.
    
    Args:
        url: Vimeo URL'si
    
    Returns:
        Video ID veya None
    """
    pattern = r'vimeo\.com\/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def clean_html_text(text: str) -> str:
    """
    HTML metnini temizler.
    
    Args:
        text: HTML metni
    
    Returns:
        Temizlenmiş metin
    """
    # Birden fazla boşluğu tek boşluğa çevir
    text = re.sub(r'\s+', ' ', text)
    # Başındaki ve sonundaki boşlukları kaldır
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int = 150, suffix: str = '...') -> str:
    """
    Metni belirtilen uzunlukta keser.
    
    Args:
        text: Orijinal metin
        max_length: Maksimum uzunluk
        suffix: Kesim sonrası eklenecek suffix
    
    Returns:
        Kesilmiş metin
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix
