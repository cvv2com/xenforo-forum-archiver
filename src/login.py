"""
XenForo Forum Archiver - Login Modülü

Bu modül Selenium kullanarak XenForo v2.x forumlarına giriş yapar
ve çerezleri kaydeder/yükler.
"""

import pickle
import time
from pathlib import Path
from typing import Optional

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.utils import setup_logger
import config


logger = setup_logger(__name__, config.LOG_FILE, config.LOG_LEVEL)


def create_chrome_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Chrome WebDriver oluşturur.
    
    Args:
        headless: Headless modda çalışsın mı
    
    Returns:
        Chrome WebDriver instance
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
    
    # Anti-bot önlemleri
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(f'user-agent={config.USER_AGENT}')
    
    # Diğer ayarlar
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # ChromeDriver ve Chrome binary path
    service_kwargs = {}
    if config.CHROMEDRIVER_PATH:
        service_kwargs['executable_path'] = config.CHROMEDRIVER_PATH
    
    if config.CHROME_BINARY_PATH:
        chrome_options.binary_location = config.CHROME_BINARY_PATH
    
    try:
        if service_kwargs:
            service = Service(**service_kwargs)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        # Automation flag'ini kaldır
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        logger.error(f"Chrome WebDriver oluşturulurken hata: {e}")
        raise


def login_and_save_cookies(
    forum_url: str,
    username: str,
    password: str,
    cookies_file: Path = config.COOKIES_FILE,
    headless: bool = False
) -> bool:
    """
    XenForo forumuna Selenium ile giriş yapar ve çerezleri kaydeder.
    
    Args:
        forum_url: Forum ana URL'si
        username: Kullanıcı adı
        password: Şifre
        cookies_file: Çerezlerin kaydedileceği dosya
        headless: Headless modda çalışsın mı
    
    Returns:
        Başarılı ise True, değilse False
    """
    driver = None
    try:
        logger.info(f"Forum login sayfasına gidiliyor: {forum_url}")
        driver = create_chrome_driver(headless=headless)
        
        # Login sayfasına git
        login_url = f"{forum_url.rstrip('/')}/login"
        driver.get(login_url)
        
        # Sayfa yüklenene kadar bekle
        time.sleep(3)
        
        # Login formunu bul ve doldur
        try:
            # XenForo v2.x login form selectors
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            password_field = driver.find_element(By.NAME, "password")
            
            logger.info("Login formu bulundu, bilgiler giriliyor...")
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Login butonunu bul ve tıkla
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Giriş işleminin tamamlanmasını bekle
            time.sleep(5)
            
            # Giriş kontrolü - URL değişikliği veya kullanıcı menüsü varlığı
            current_url = driver.current_url
            
            # Çerezleri kontrol et
            cookies = driver.get_cookies()
            if not cookies:
                logger.error("Login sonrası çerez bulunamadı")
                return False
            
            # Çerezleri kaydet
            cookies_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            logger.info(f"Çerezler başarıyla kaydedildi: {cookies_file}")
            logger.info(f"Toplam {len(cookies)} çerez kaydedildi")
            
            return True
            
        except TimeoutException:
            logger.error("Login formu bulunamadı (timeout)")
            return False
        except NoSuchElementException as e:
            logger.error(f"Login form elemanı bulunamadı: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Login işlemi sırasında hata: {e}")
        return False
    finally:
        if driver:
            driver.quit()


def load_session_with_cookies(
    forum_url: str,
    cookies_file: Path = config.COOKIES_FILE
) -> Optional[requests.Session]:
    """
    Kaydedilmiş çerezlerle bir requests.Session oluşturur.
    
    Args:
        forum_url: Forum ana URL'si
        cookies_file: Çerezlerin bulunduğu dosya
    
    Returns:
        Çerezli session veya None
    """
    if not cookies_file.exists():
        logger.error(f"Çerez dosyası bulunamadı: {cookies_file}")
        return None
    
    try:
        # Çerezleri yükle
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        
        # Session oluştur
        session = requests.Session()
        session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Çerezleri session'a ekle
        for cookie in cookies:
            session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain'),
                path=cookie.get('path', '/')
            )
        
        logger.info(f"Session {len(cookies)} çerez ile oluşturuldu")
        
        # Session'ı test et
        try:
            response = session.get(forum_url, timeout=config.REQUEST_TIMEOUT)
            if response.status_code == 200:
                logger.info("Session başarıyla test edildi")
                return session
            else:
                logger.warning(f"Session test edildi ama beklenmeyen status code: {response.status_code}")
                return session
        except Exception as e:
            logger.error(f"Session test edilirken hata: {e}")
            return session
            
    except Exception as e:
        logger.error(f"Session oluşturulurken hata: {e}")
        return None


def ensure_logged_in(
    forum_url: str,
    username: str,
    password: str,
    cookies_file: Path = config.COOKIES_FILE,
    force_login: bool = False
) -> Optional[requests.Session]:
    """
    Login durumunu kontrol eder ve gerekirse login yapar.
    
    Args:
        forum_url: Forum ana URL'si
        username: Kullanıcı adı
        password: Şifre
        cookies_file: Çerez dosyası
        force_login: Zorla yeniden login yap
    
    Returns:
        Çerezli session veya None
    """
    # Eğer çerez dosyası varsa ve force_login False ise, direkt session yükle
    if cookies_file.exists() and not force_login:
        logger.info("Mevcut çerezler kullanılarak session yükleniyor...")
        session = load_session_with_cookies(forum_url, cookies_file)
        if session:
            return session
    
    # Çerez yoksa veya force_login True ise, yeniden login yap
    logger.info("Yeni login yapılıyor...")
    # İlk login CAPTCHA olabileceği için headless=False
    success = login_and_save_cookies(forum_url, username, password, cookies_file, headless=False)
    
    if success:
        return load_session_with_cookies(forum_url, cookies_file)
    else:
        logger.error("Login başarısız oldu")
        return None
