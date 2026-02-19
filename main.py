"""
XenForo Forum Archiver - Ana Çalıştırma Scripti

Bu script tüm modülleri bir araya getirerek forum içeriklerini
çeker, kategorize eder ve statik web sitesi oluşturur.
"""

import argparse
import sys
from pathlib import Path

import config
from src.utils import setup_logger
from src.login import ensure_logged_in
from src.scraper import XenForoScraper
from src.downloader import MediaDownloader
from src.categorizer import ContentCategorizer
from src.site_generator import WebSiteGenerator


logger = setup_logger('main', config.LOG_FILE, config.LOG_LEVEL)


def parse_arguments():
    """Komut satırı argümanlarını parse eder."""
    parser = argparse.ArgumentParser(
        description='XenForo Forum Archiver - Forum içeriklerini çeker ve statik web sitesi oluşturur',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py                          # Tüm işlemleri yap
  python main.py --scrape-only            # Sadece scraping yap
  python main.py --categorize-only        # Sadece kategorizasyon yap
  python main.py --generate-only          # Sadece site oluştur
  python main.py --no-media               # Medya indirme
  python main.py --force-login            # Zorla yeniden login yap
        """
    )
    
    parser.add_argument('--scrape-only', action='store_true',
                        help='Sadece scraping işlemini yap')
    parser.add_argument('--categorize-only', action='store_true',
                        help='Sadece kategorizasyon işlemini yap (JSON dosyası gerekli)')
    parser.add_argument('--generate-only', action='store_true',
                        help='Sadece site oluşturma işlemini yap (JSON dosyası gerekli)')
    parser.add_argument('--no-media', action='store_true',
                        help='Medya dosyalarını indirme')
    parser.add_argument('--force-login', action='store_true',
                        help='Zorla yeniden login yap')
    parser.add_argument('--config', type=str, default=None,
                        help='Alternatif config dosyası')
    parser.add_argument('--output', type=str, default=None,
                        help='Çıktı dizini (varsayılan: config.OUTPUT_DIR)')
    parser.add_argument('--json-file', type=str, default='scraped_data.json',
                        help='JSON veri dosyası adı (varsayılan: scraped_data.json)')
    
    return parser.parse_args()


def validate_config():
    """Yapılandırma ayarlarını kontrol eder."""
    if not config.FORUM_URL:
        logger.error("FORUM_URL yapılandırma ayarı eksik!")
        return False
    
    if not config.THREAD_URL:
        logger.error("THREAD_URL yapılandırma ayarı eksik!")
        return False
    
    if not config.FORUM_USERNAME or not config.FORUM_PASSWORD:
        logger.warning("Forum kullanıcı adı veya şifre eksik. Public forum varsayılıyor.")
    
    return True


def scrape_forum(session, json_file):
    """Forum scraping işlemini yapar."""
    logger.info("\n" + "="*50)
    logger.info("ADIM 1: FORUM SCRAPING")
    logger.info("="*50)
    
    scraper = XenForoScraper(session, config.FORUM_URL)
    
    success = scraper.scrape_thread(
        config.THREAD_URL,
        delay=config.SCRAPE_DELAY,
        max_pages=config.MAX_PAGES
    )
    
    if not success:
        logger.error("Scraping başarısız oldu!")
        return None
    
    # JSON'a kaydet
    if not scraper.save_to_json(json_file):
        logger.error("JSON kaydedilemedi!")
        return None
    
    return scraper


def categorize_content(scraper_or_json):
    """İçerik kategorizasyonu yapar."""
    logger.info("\n" + "="*50)
    logger.info("ADIM 2: İÇERİK KATEGORİZASYONU")
    logger.info("="*50)
    
    # JSON dosyasından mı yoksa scraper nesnesinden mi veri alalım?
    if isinstance(scraper_or_json, (str, Path)):
        # JSON dosyasından yükle
        scraper = XenForoScraper(None, config.FORUM_URL)
        if not scraper.load_from_json(Path(scraper_or_json)):
            logger.error("JSON dosyası yüklenemedi!")
            return None, None
        posts_data = scraper.posts_data
        thread_info = scraper.thread_info
    else:
        # Scraper nesnesinden al
        posts_data = scraper_or_json.posts_data
        thread_info = scraper_or_json.thread_info
    
    if not posts_data:
        logger.error("İçerik verisi bulunamadı!")
        return None, None
    
    categorizer = ContentCategorizer()
    categorized_posts = categorizer.categorize_posts(posts_data)
    stats = categorizer.get_stats()
    
    return categorized_posts, stats, thread_info


def download_media(session, posts_data):
    """Medya dosyalarını indirir."""
    logger.info("\n" + "="*50)
    logger.info("ADIM 3: MEDYA DOSYALARI İNDİRİLİYOR")
    logger.info("="*50)
    
    downloader = MediaDownloader(session, config.MEDIA_DIR)
    mappings = downloader.download_all_media(posts_data)
    
    return mappings


def generate_website(categorized_posts, stats, thread_info, media_mappings=None):
    """Statik web sitesini oluşturur."""
    logger.info("\n" + "="*50)
    logger.info("ADIM 4: STATİK WEB SİTESİ OLUŞTURULUYOR")
    logger.info("="*50)
    
    templates_dir = config.BASE_DIR / 'templates'
    if not templates_dir.exists():
        logger.error(f"Template dizini bulunamadı: {templates_dir}")
        return False
    
    generator = WebSiteGenerator(
        output_dir=config.OUTPUT_DIR,
        templates_dir=templates_dir,
        thread_info=thread_info,
        categorized_posts=categorized_posts,
        stats=stats,
        media_mappings=media_mappings
    )
    
    success = generator.generate_site(copy_media=True)
    
    return success


def main():
    """Ana fonksiyon."""
    args = parse_arguments()
    
    logger.info("="*50)
    logger.info("XenForo Forum Archiver Başlatıldı")
    logger.info("="*50)
    
    # Config'i kontrol et
    if not validate_config():
        logger.error("Yapılandırma hatası! Çıkılıyor...")
        sys.exit(1)
    
    # Çıktı dizini
    output_dir = Path(args.output) if args.output else config.OUTPUT_DIR
    config.OUTPUT_DIR = output_dir
    
    json_file = config.BASE_DIR / args.json_file
    
    # Sadece site oluşturma modu
    if args.generate_only:
        if not json_file.exists():
            logger.error(f"JSON dosyası bulunamadı: {json_file}")
            sys.exit(1)
        
        categorized_posts, stats, thread_info = categorize_content(json_file)
        if categorized_posts:
            success = generate_website(categorized_posts, stats, thread_info)
            if success:
                logger.info(f"\n✓ Web sitesi başarıyla oluşturuldu: {output_dir}")
            sys.exit(0 if success else 1)
    
    # Sadece kategorizasyon modu
    if args.categorize_only:
        if not json_file.exists():
            logger.error(f"JSON dosyası bulunamadı: {json_file}")
            sys.exit(1)
        
        categorized_posts, stats, thread_info = categorize_content(json_file)
        if categorized_posts:
            logger.info("\n✓ Kategorizasyon başarıyla tamamlandı")
        sys.exit(0 if categorized_posts else 1)
    
    # Login işlemi (scraping için gerekli)
    session = None
    if config.FORUM_USERNAME and config.FORUM_PASSWORD:
        logger.info("Login işlemi başlatılıyor...")
        session = ensure_logged_in(
            config.FORUM_URL,
            config.FORUM_USERNAME,
            config.FORUM_PASSWORD,
            force_login=args.force_login
        )
        
        if not session:
            logger.error("Login başarısız oldu! Public forum mu? Devam ediliyor...")
            import requests
            session = requests.Session()
            session.headers.update({'User-Agent': config.USER_AGENT})
    else:
        logger.info("Kullanıcı bilgileri yok, public forum varsayılıyor...")
        import requests
        session = requests.Session()
        session.headers.update({'User-Agent': config.USER_AGENT})
    
    # Scraping işlemi
    scraper = scrape_forum(session, json_file)
    if not scraper:
        logger.error("Scraping başarısız oldu!")
        sys.exit(1)
    
    logger.info(f"\n✓ Scraping tamamlandı: {len(scraper.posts_data)} post çekildi")
    
    # Sadece scraping modu
    if args.scrape_only:
        logger.info(f"\n✓ Veriler kaydedildi: {json_file}")
        sys.exit(0)
    
    # Kategorizasyon
    categorized_posts, stats, thread_info = categorize_content(scraper)
    if not categorized_posts:
        logger.error("Kategorizasyon başarısız oldu!")
        sys.exit(1)
    
    logger.info("\n✓ Kategorizasyon tamamlandı")
    
    # Medya indirme
    media_mappings = None
    if not args.no_media and config.DOWNLOAD_MEDIA:
        media_mappings = download_media(session, scraper.posts_data)
        logger.info("\n✓ Medya dosyaları indirildi")
    else:
        logger.info("\n⊘ Medya indirme atlandı")
    
    # Web sitesi oluşturma
    success = generate_website(categorized_posts, stats, thread_info, media_mappings)
    
    if success:
        logger.info("\n" + "="*50)
        logger.info("TÜM İŞLEMLER BAŞARIYLA TAMAMLANDI!")
        logger.info("="*50)
        logger.info(f"Web sitesi: {output_dir}")
        logger.info(f"JSON verisi: {json_file}")
        logger.info("="*50)
    else:
        logger.error("\nWeb sitesi oluşturulamadı!")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nİşlem kullanıcı tarafından iptal edildi.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Beklenmeyen hata: {e}")
        sys.exit(1)
