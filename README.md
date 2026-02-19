# XenForo Forum Archiver

**XenForo v2.x forumlarından üye-only içerikleri otomatik olarak çekip, kategorize edip, statik bir web sitesine dönüştüren Python aracı.**

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-yellow)

## 📋 İçindekiler

- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
  - [Gereksinimler](#gereksinimler)
  - [Kali Linux Kurulumu](#kali-linux-kurulumu)
  - [Windows Kurulumu](#windows-kurulumu)
  - [macOS Kurulumu](#macos-kurulumu)
  - [Docker ile Kurulum](#docker-ile-kurulum)
- [Yapılandırma](#yapılandırma)
- [Kullanım](#kullanım)
- [Çıktı Yapısı](#çıktı-yapısı)
- [Sorun Giderme](#sorun-giderme)
- [Yasal Uyarı](#yasal-uyarı)
- [Katkıda Bulunma](#katkıda-bulunma)
- [Lisans](#lisans)

## ✨ Özellikler

- 🔐 **Selenium ile Otomatik Giriş**: Üye-only forumlar için otomatik login desteği
- 📄 **100+ Sayfa Desteği**: Sınırsız sayfa scraping özelliği ile tam thread arşivleme
- 🖼️ **Medya İndirme**: Görsel, video, ek dosya otomatik indirme
- 🏷️ **Otomatik Kategorizasyon**: İçerikleri anahtar kelime tabanlı otomatik kategorize etme
- 🌐 **Statik Web Sitesi**: Responsive, modern tasarımlı HTML web sitesi oluşturma
- 🛡️ **CloudFlare Koruması**: CloudFlare korumalı siteler için destek
- 🔄 **XenForo REST API**: Alternatif API modu desteği
- ⚡ **Rate Limiting**: Anti-ban koruması ve rate limiting
- 📊 **Detaylı İstatistikler**: İçerik analizi ve raporlama
- 🎨 **Dark Mode Ready**: Modern CSS ile hazır dark mode desteği

## 🚀 Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- Google Chrome veya Chromium tarayıcı
- ChromeDriver (Chrome sürümü ile uyumlu)
- Git
- 2GB+ boş disk alanı (medya dosyaları için)

### Kali Linux Kurulumu

#### 1. Sistem Güncellemesi ve Python Kurulumu

```bash
# Sistem paketlerini güncelle
sudo apt update && sudo apt upgrade -y

# Python ve pip'i yükle
sudo apt install python3 python3-pip python3-venv -y

# Git'i yükle
sudo apt install git -y

# Python sürümünü kontrol et (3.9+ olmalı)
python3 --version
```

#### 2. Chrome/Chromium ve ChromeDriver Kurulumu

```bash
# Chromium tarayıcıyı yükle
sudo apt install chromium chromium-driver -y

# ChromeDriver'ın yüklendiğini doğrula
chromedriver --version

# Alternatif: Google Chrome yüklemek isterseniz
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb
# sudo apt-get install -f -y
```

#### 3. Projeyi Klonlama ve Kurulum

```bash
# Projeyi klonla
git clone https://github.com/cvv2com/xenforo-forum-archiver.git
cd xenforo-forum-archiver

# Virtual environment oluştur
python3 -m venv venv

# Virtual environment'ı aktifleştir
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Alternatif: setup.py ile kurulum
pip install -e .
```

#### 4. Yapılandırma

```bash
# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle
nano .env
```

#### 5. Headless Mod (Kali CLI için önerilen)

Eğer GUI olmayan bir ortamda çalışıyorsanız (örn. Kali Linux SSH üzerinden):

```bash
# .env dosyasında headless mod'u aktifleştir
echo "HEADLESS_MODE=true" >> .env

# X virtual framebuffer yükle (opsiyonel)
sudo apt install xvfb -y

# Xvfb ile çalıştırma (gerekirse)
xvfb-run python main.py
```

### Windows Kurulumu

#### 1. Python Kurulumu

1. Python'u [python.org](https://www.python.org/downloads/) adresinden indirin (3.9+)
2. Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin
3. Kurulumu tamamlayın

```powershell
# PowerShell'de Python sürümünü kontrol edin
python --version
```

#### 2. Git Kurulumu

1. Git'i [git-scm.com](https://git-scm.com/download/win) adresinden indirin
2. Varsayılan ayarlarla kurun

```powershell
# Git sürümünü kontrol edin
git --version
```

#### 3. Chrome ve ChromeDriver Kurulumu

1. **Google Chrome'u indirin ve kurun**: [google.com/chrome](https://www.google.com/chrome/)

2. **Chrome sürümünüzü kontrol edin**:
   - Chrome'u açın
   - Adres çubuğuna `chrome://version` yazın
   - Sürüm numarasını not edin (örn: 120.0.6099.109)

3. **ChromeDriver'ı indirin**:
   - [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads) adresine gidin
   - Chrome sürümünüze uygun ChromeDriver'ı indirin
   - ZIP'i açın ve `chromedriver.exe` dosyasını bir klasöre koyun (örn: `C:\chromedriver\`)

4. **ChromeDriver'ı PATH'e ekleyin** (opsiyonel):
   - Windows Arama'da "Environment Variables" yazın
   - "Edit the system environment variables" seçeneğini açın
   - "Environment Variables" butonuna tıklayın
   - "System variables" altında "Path" seçin ve "Edit" tıklayın
   - "New" butonuna tıklayıp ChromeDriver klasörünü ekleyin (örn: `C:\chromedriver\`)

#### 4. Projeyi Klonlama ve Kurulum

```powershell
# PowerShell veya CMD açın

# Projeyi klonlayın
git clone https://github.com/cvv2com/xenforo-forum-archiver.git
cd xenforo-forum-archiver

# Virtual environment oluşturun
python -m venv venv

# Virtual environment'ı aktifleştirin
# PowerShell için:
.\venv\Scripts\Activate.ps1

# CMD için:
.\venv\Scripts\activate.bat

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

#### 5. Yapılandırma

```powershell
# .env dosyası oluşturun
copy .env.example .env

# .env dosyasını Notepad ile düzenleyin
notepad .env

# ChromeDriver yolunu .env dosyasına ekleyin (PATH'e eklemediyseniz):
# CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe
```

### macOS Kurulumu

#### 1. Homebrew Kurulumu (yoksa)

```bash
# Homebrew'i kur
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Python ve Git Kurulumu

```bash
# Python 3.9+ ve Git'i yükle
brew install python@3.11 git

# Python sürümünü kontrol et
python3 --version
```

#### 3. Chrome ve ChromeDriver Kurulumu

```bash
# Google Chrome'u yükle
brew install --cask google-chrome

# ChromeDriver'ı yükle
brew install --cask chromedriver

# ChromeDriver'ı doğrula
chromedriver --version

# İlk çalıştırmada güvenlik uyarısı alabilirsiniz:
xattr -d com.apple.quarantine $(which chromedriver)
```

#### 4. Projeyi Klonlama ve Kurulum

```bash
# Projeyi klonla
git clone https://github.com/cvv2com/xenforo-forum-archiver.git
cd xenforo-forum-archiver

# Virtual environment oluştur
python3 -m venv venv

# Virtual environment'ı aktifleştir
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

#### 5. Yapılandırma

```bash
# .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle (varsayılan text editör)
nano .env
# veya
open -e .env
```

### Docker ile Kurulum

Docker kullanarak projeyi izole bir ortamda çalıştırabilirsiniz.

#### Dockerfile

Projeye `Dockerfile` oluşturun:

```dockerfile
FROM python:3.11-slim

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    git \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# ChromeDriver ortam değişkenlerini ayarla
ENV CHROME_BINARY_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Varsayılan komut
CMD ["python", "main.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  xenforo-archiver:
    build: .
    container_name: xenforo-archiver
    volumes:
      - ./website_output:/app/website_output
      - ./downloaded_media:/app/downloaded_media
      - ./.env:/app/.env
    environment:
      - HEADLESS_MODE=true
    stdin_open: true
    tty: true
```

#### Docker Kullanımı

```bash
# Docker image'ı oluştur
docker-compose build

# Çalıştır
docker-compose run --rm xenforo-archiver

# Alternatif: Direkt Docker komutları
docker build -t xenforo-archiver .
docker run -v $(pwd)/website_output:/app/website_output -v $(pwd)/.env:/app/.env xenforo-archiver
```

## ⚙️ Yapılandırma

### .env Dosyası

`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```bash
# Forum Bilgileri
FORUM_URL=https://forum.example.com
FORUM_USERNAME=your_username
FORUM_PASSWORD=your_password

# Çekilecek Thread URL'si
THREAD_URL=https://forum.example.com/threads/your-thread.12345/

# Scraping Ayarları
SCRAPE_DELAY=2.5              # Sayfalar arası bekleme süresi (saniye)
MAX_PAGES=0                    # Maksimum sayfa sayısı (0 = tümü)
HEADLESS_MODE=false            # Headless mod (true/false)

# Çıktı Ayarları
OUTPUT_DIR=website_output      # Web sitesi çıktı dizini
DOWNLOAD_MEDIA=true            # Medya dosyalarını indir (true/false)
MEDIA_DIR=downloaded_media     # Medya dosyaları dizini

# Kategorizasyon Ayarları
AUTO_CATEGORIZE=true           # Otomatik kategorizasyon (true/false)
EXTRACT_TAGS=true              # Etiket çıkarma (true/false)

# ChromeDriver Ayarları (opsiyonel)
CHROMEDRIVER_PATH=             # ChromeDriver tam yolu (boş bırakılabilir)
CHROME_BINARY_PATH=            # Chrome binary yolu (boş bırakılabilir)
```

### Kategori Kurallarını Özelleştirme

`config.py` dosyasındaki `CATEGORY_RULES` dictionary'sini düzenleyerek kategori kurallarını özelleştirebilirsiniz:

```python
CATEGORY_RULES = {
    'inceleme': {
        'keywords': ['inceleme', 'review', 'test', 'analiz'],
        'priority': 1
    },
    'rehber': {
        'keywords': ['rehber', 'guide', 'nasıl', 'tutorial'],
        'priority': 2
    },
    # Yeni kategoriler ekleyebilirsiniz...
}
```

### Diğer Ayarlar

`config.py` dosyasında şu ayarları değiştirebilirsiniz:

- `REQUEST_TIMEOUT`: HTTP istek timeout süresi (saniye)
- `MAX_RETRIES`: Başarısız istekler için maksimum deneme sayısı
- `RETRY_DELAY`: Yeniden denemeler arası bekleme süresi
- `LOG_LEVEL`: Logging seviyesi (DEBUG, INFO, WARNING, ERROR)

## 📖 Kullanım

### Temel Kullanım

```bash
# Virtual environment'ı aktifleştir
source venv/bin/activate  # Linux/macOS
# veya
.\venv\Scripts\activate   # Windows

# Tüm işlemleri yap (scraping + kategorizasyon + site oluşturma)
python main.py
```

### Adım Adım İlk Çalıştırma

1. **Yapılandırma kontrolü**:
```bash
# .env dosyasını kontrol edin
cat .env  # Linux/macOS
type .env # Windows
```

2. **İlk çalıştırma** (tüm adımlar):
```bash
python main.py
```

Programın adımları:
- ✓ Login işlemi (çerezler kaydedilir)
- ✓ Thread scraping (tüm sayfalar)
- ✓ JSON'a kaydetme
- ✓ Kategorizasyon
- ✓ Medya dosyaları indirme
- ✓ Web sitesi oluşturma

3. **Çıktıları kontrol edin**:
```bash
ls -la website_output/     # Oluşturulan web sitesi
ls -la downloaded_media/   # İndirilen medya dosyaları
```

### Komut Satırı Argümanları

#### Sadece Scraping

```bash
# Sadece forum içeriğini çek ve JSON'a kaydet
python main.py --scrape-only
```

#### Sadece Kategorizasyon

```bash
# Mevcut JSON dosyasından kategorizasyon yap
python main.py --categorize-only
```

#### Sadece Site Oluşturma

```bash
# Mevcut JSON dosyasından web sitesi oluştur
python main.py --generate-only
```

#### Medya İndirmeden

```bash
# Medya dosyalarını indirme
python main.py --no-media
```

#### Zorla Yeniden Login

```bash
# Mevcut çerezleri sil ve yeniden login yap
python main.py --force-login
```

#### Özel JSON Dosyası

```bash
# Farklı bir JSON dosyası kullan
python main.py --json-file my_data.json
```

#### Özel Çıktı Dizini

```bash
# Farklı bir çıktı dizini kullan
python main.py --output my_website
```

#### Komutları Birleştirme

```bash
# Birden fazla argüman kullanımı
python main.py --scrape-only --json-file thread_12345.json
python main.py --generate-only --json-file thread_12345.json --output site_12345
```

### İleri Düzey Kullanım

#### Çoklu Thread Arşivleme

```bash
# Her thread için ayrı JSON ve site oluşturma
python main.py --json-file thread1.json --output site1
# .env dosyasındaki THREAD_URL'yi değiştirin
python main.py --json-file thread2.json --output site2
```

#### Sadece Kategorizasyon Güncellemesi

```bash
# Mevcut veriyi yeniden kategorize et (scraping yapmadan)
python main.py --categorize-only --generate-only
```

## 📁 Çıktı Yapısı

### JSON Veri Formatı

Scraping sonucu oluşturulan JSON formatı:

```json
{
  "thread_info": {
    "url": "https://forum.example.com/threads/thread.12345/",
    "title": "Thread Başlığı",
    "total_pages": 10,
    "base_url": "https://forum.example.com"
  },
  "total_posts": 150,
  "posts": [
    {
      "post_id": "123456",
      "author": "Kullanıcı Adı",
      "author_id": "789",
      "date": "2024-01-15T10:30:00+00:00",
      "date_text": "15 Ocak 2024, 10:30",
      "content_html": "<p>Post içeriği HTML</p>",
      "content_text": "Post içeriği düz metin",
      "images": [
        {
          "src": "https://forum.example.com/image.jpg",
          "alt": "Görsel açıklaması"
        }
      ],
      "videos": [
        {
          "type": "youtube",
          "src": "https://youtube.com/watch?v=..."
        }
      ],
      "attachments": [],
      "quotes": [],
      "category": "inceleme",
      "content_type": "text",
      "tags": ["python", "tutorial"]
    }
  ]
}
```

### Oluşturulan Web Sitesi Yapısı

```
website_output/
├── index.html              # Ana sayfa
├── inceleme.html           # Kategori sayfaları
├── rehber.html
├── haber.html
├── tartisma.html
├── medya.html
├── diger.html
├── css/
│   └── style.css           # Stil dosyası
├── posts/
│   ├── post_123.html       # Tekil post sayfaları
│   ├── post_124.html
│   └── ...
└── downloaded_media/       # (kopyalanmış medya dosyaları)
    ├── images/
    ├── attachments/
    └── thumbnails/
```

### Medya Dosyaları Dizin Yapısı

```
downloaded_media/
├── images/                 # Görseller
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── attachments/            # Ek dosyalar
│   ├── document.pdf
│   ├── archive.zip
│   └── ...
└── thumbnails/             # Video thumbnail'ları
    ├── youtube_abc123.jpg
    └── ...
```

## 🔧 Sorun Giderme

### CloudFlare Engeli

**Sorun**: CloudFlare koruması nedeniyle erişim engellenirse.

**Çözüm**:
```python
# config.py dosyasında cloudscraper kullanımı
# Veya manuel olarak çerezleri tarayıcıdan dışa aktarıp forum_cookies.pkl'e kaydedin
```

### ChromeDriver Sürüm Uyumsuzluğu

**Sorun**: `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX`

**Çözüm**:
```bash
# Chrome sürümünüzü kontrol edin
google-chrome --version  # Linux
# chrome://version        # Tarayıcıda

# Uyumlu ChromeDriver'ı indirin
# https://chromedriver.chromium.org/downloads

# ChromeDriver yolunu .env dosyasında belirtin
CHROMEDRIVER_PATH=/path/to/chromedriver
```

### Login Başarısız

**Sorun**: Login işlemi başarısız oluyor.

**Çözümler**:

1. **CAPTCHA varsa**:
```bash
# Headless modu kapatın (ilk login için)
# .env dosyasında:
HEADLESS_MODE=false
```

2. **2FA (İki faktörlü doğrulama) aktifse**:
   - Manuel olarak tarayıcıda login olun
   - Çerezleri dışa aktarın
   - `forum_cookies.pkl` dosyasına kaydedin

3. **Kullanıcı adı/şifre yanlışsa**:
```bash
# .env dosyasını kontrol edin
cat .env | grep USERNAME
cat .env | grep PASSWORD
```

### Rate Limiting / IP Ban

**Sorun**: Çok fazla istek nedeniyle IP ban.

**Çözüm**:
```bash
# .env dosyasında delay'i artırın
SCRAPE_DELAY=5.0  # 5 saniyeye çıkarın

# Proxy kullanımı (gelişmiş)
# config.py'de session'a proxy ekleyin
```

### Headless Mod Sorunları

**Sorun**: Headless modda scraping çalışmıyor.

**Çözüm**:
```bash
# Xvfb kullanın (Linux)
sudo apt install xvfb
xvfb-run python main.py

# Veya headless modu kapatın
HEADLESS_MODE=false
```

### Bellek Sorunları

**Sorun**: Çok fazla sayfa/post nedeniyle bellek tükeniyor.

**Çözüm**:
```bash
# Maksimum sayfa sınırı koyun
MAX_PAGES=50  # .env dosyasında

# Veya batch halinde çekin
python main.py --scrape-only --json-file part1.json
# Thread URL'yi sonraki sayfalara değiştirin
python main.py --scrape-only --json-file part2.json
```

### Karakter Kodlama Sorunları

**Sorun**: Türkçe karakterler bozuk görünüyor.

**Çözüm**:
```bash
# Terminal encoding'ini UTF-8 yapın
export LC_ALL=tr_TR.UTF-8
export LANG=tr_TR.UTF-8

# Windows'ta:
chcp 65001
```

## ⚖️ Yasal Uyarı

Bu araç **eğitim amaçlı** geliştirilmiştir. Kullanırken şu kurallara uymalısınız:

- ✅ **Sadece kendi içeriğinizi çekin** veya izniniz olan içerikleri arşivleyin
- ✅ **Forum kurallarına uyun** - Forumun kullanım şartlarını okuyun
- ✅ **robots.txt'e saygı gösterin** - Site politikalarına uygun davranın
- ✅ **Rate limiting kullanın** - Sunucuyu aşırı yüklemeyin
- ❌ **Telif hakkı ihlali yapmayın** - Başkalarının içeriklerini izinsiz dağıtmayın
- ❌ **Kişisel verileri kötüye kullanmayın** - KVKK/GDPR kurallarına uyun

**Sorumluluk Reddi**: Bu aracın kötüye kullanımından kaynaklanan yasal sorumluluk kullanıcıya aittir. Geliştirici hiçbir şekilde sorumlu tutulamaz.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Projeye katkıda bulunmak için:

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Geliştirme Ortamı

```bash
# Geliştirme bağımlılıklarını yükleyin
pip install -r requirements.txt

# Testleri çalıştırın
python -m pytest tests/

# Veya tek bir test dosyası
python tests/test_categorizer.py

# Kod kalitesi kontrolü
pylint src/
black src/  # Code formatter
```

### Katkı Kuralları

- Kod Python PEP 8 standartlarına uygun olmalı
- Tüm fonksiyonlar docstring içermeli
- Yeni özellikler için test yazılmalı
- README güncellenebilir

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

```
MIT License

Copyright (c) 2024 cvv2com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Teşekkürler

- [Selenium](https://www.selenium.dev/) - Web automation framework
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [XenForo](https://xenforo.com/) - Forum software

---

**Not**: Bu proje XenForo Ltd. ile resmi bir ilişkisi yoktur.

Sorularınız için [GitHub Issues](https://github.com/cvv2com/xenforo-forum-archiver/issues) kullanabilirsiniz.
