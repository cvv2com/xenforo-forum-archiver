# Katkıda Bulunma Rehberi

XenForo Forum Archiver projesine katkıda bulunduğunuz için teşekkür ederiz! 🎉

## Nasıl Katkıda Bulunabilirsiniz?

### 1. Bug Raporlama

Bir hata bulduysanız:

1. [Issues](https://github.com/cvv2com/xenforo-forum-archiver/issues) sayfasında benzer bir issue olup olmadığını kontrol edin
2. Yoksa yeni bir issue açın ve şunları ekleyin:
   - Hatanın açık bir tanımı
   - Hatayı yeniden oluşturma adımları
   - Beklenen ve gerçekleşen davranış
   - Sistem bilgileri (OS, Python versiyonu, vs.)
   - Hata mesajları ve log'lar

### 2. Özellik Önerisi

Yeni bir özellik öneriniz varsa:

1. Önce [Issues](https://github.com/cvv2com/xenforo-forum-archiver/issues) sayfasında benzer bir öneri olup olmadığını kontrol edin
2. Yeni bir feature request issue'su açın
3. Özelliğin ne işe yarayacağını ve nasıl kullanılacağını açıklayın

### 3. Kod Katkısı

#### Adım 1: Fork ve Clone

```bash
# Projeyi fork edin (GitHub'da "Fork" butonuna tıklayın)

# Fork'u klonlayın
git clone https://github.com/YOUR_USERNAME/xenforo-forum-archiver.git
cd xenforo-forum-archiver

# Upstream remote ekleyin
git remote add upstream https://github.com/cvv2com/xenforo-forum-archiver.git
```

#### Adım 2: Geliştirme Ortamı Kurulumu

```bash
# Virtual environment oluşturun
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# veya
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Geliştirme bağımlılıkları (opsiyonel)
pip install pylint black pytest
```

#### Adım 3: Feature Branch Oluşturun

```bash
# Ana branch'i güncelleyin
git checkout main
git pull upstream main

# Yeni branch oluşturun
git checkout -b feature/your-feature-name
```

#### Adım 4: Değişiklikleri Yapın

- Kod Python PEP 8 standartlarına uygun olmalı
- Tüm fonksiyonlar docstring içermeli
- Type hints kullanılmalı
- Kod Türkçe yorumlar içerebilir

```python
def example_function(param: str) -> bool:
    """
    Fonksiyonun açıklaması.
    
    Args:
        param: Parametre açıklaması
    
    Returns:
        Dönüş değeri açıklaması
    """
    # Türkçe yorum
    return True
```

#### Adım 5: Testler Yazın

Yeni özellikler için test yazın:

```bash
# Testleri çalıştırın
python -m pytest tests/

# Veya belirli bir test dosyası
python tests/test_categorizer.py
```

#### Adım 6: Kod Kalitesi Kontrolü

```bash
# Linting
pylint src/

# Code formatting
black src/ tests/
```

#### Adım 7: Commit ve Push

```bash
# Değişiklikleri stage'e ekleyin
git add .

# Commit yapın (anlamlı commit mesajı)
git commit -m "Add: Yeni özellik açıklaması"

# Push yapın
git push origin feature/your-feature-name
```

#### Adım 8: Pull Request Açın

1. GitHub'da fork'unuza gidin
2. "Pull Request" butonuna tıklayın
3. Ana branch olarak `main` seçin
4. PR açıklamasında şunları ekleyin:
   - Ne değiştirildi?
   - Neden değiştirildi?
   - Nasıl test edildi?
   - Varsa ilgili issue numarası (#123)

## Commit Mesajı Formatı

Commit mesajları açık ve anlamlı olmalı:

```
Add: Yeni özellik ekleme
Fix: Hata düzeltme
Update: Mevcut kodu güncelleme
Refactor: Kod yeniden yapılandırma
Docs: Dokümantasyon değişikliği
Test: Test ekleme/güncelleme
```

Örnekler:
```
Add: YouTube Shorts video desteği
Fix: ChromeDriver sürüm uyumsuzluğu hatası
Update: README kurulum talimatları
Refactor: Scraper modülü kod optimizasyonu
Docs: API dokümantasyonu güncellendi
Test: Categorizer için yeni test senaryoları
```

## Kod Stili

### Python Kod Stili

- **PEP 8** standartlarına uyun
- Satır uzunluğu: Maksimum 100 karakter
- Indentation: 4 boşluk
- Docstring: Google style docstrings

### İsimlendirme Kuralları

```python
# Değişkenler ve fonksiyonlar: snake_case
user_name = "test"
def calculate_total():
    pass

# Sınıflar: PascalCase
class ContentCategorizer:
    pass

# Sabitler: UPPER_SNAKE_CASE
MAX_RETRIES = 3
```

### Docstring Örneği

```python
def fetch_data(url: str, timeout: int = 30) -> dict:
    """
    URL'den veri çeker.
    
    Args:
        url: Çekilecek URL
        timeout: Timeout süresi (saniye)
    
    Returns:
        JSON verisi dictionary olarak
    
    Raises:
        ValueError: URL geçersizse
        requests.RequestException: İstek başarısızsa
    
    Example:
        >>> data = fetch_data("https://example.com/api")
        >>> print(data['status'])
        'success'
    """
    pass
```

## Test Yazma

### Test Yapısı

```python
import unittest

class TestYourFeature(unittest.TestCase):
    """Your Feature test senaryoları"""
    
    def setUp(self):
        """Her testten önce çalışır"""
        pass
    
    def test_specific_case(self):
        """Belirli bir durum testi"""
        result = your_function()
        self.assertEqual(result, expected_value)
    
    def tearDown(self):
        """Her testten sonra çalışır"""
        pass
```

## Dokümantasyon

### README Güncellemeleri

Yeni özellikler eklerken README.md'yi güncelleyin:

- Özellikler bölümüne ekleyin
- Gerekirse kullanım örneği ekleyin
- Configuration değişikliklerini belirtin

### Kod Yorumları

```python
# İyi yorum: NEDEN yapıldığını açıklar
# Türkçe karakterler için encoding kontrolü gerekli
text = text.encode('utf-8')

# Kötü yorum: NE yapıldığını açıklar (zaten açık)
# Text'i encode et
text = text.encode('utf-8')
```

## Review Süreci

Pull Request'iniz:

1. Otomatik testlerden geçmelidir
2. En az bir maintainer tarafından review edilmelidir
3. Çakışma (conflict) içermemelidir
4. Anlamlı commit mesajları içermelidir

## Davranış Kuralları

- Saygılı ve profesyonel olun
- Yapıcı eleştiri yapın
- Farklı görüşlere açık olun
- Yardımsever olun

## Sorularınız mı Var?

- [Issues](https://github.com/cvv2com/xenforo-forum-archiver/issues) üzerinden soru sorun
- Veya maintainer'lara ulaşın

## Teşekkürler! 🙏

Katkılarınız projeyi daha iyi hale getiriyor. Teşekkür ederiz!
