# 🔧 المميزات المتقدمة

## 1. تحميل الفيديوهات المحمية بالفئة العمرية

### الطريقة الأولى: استخدام ملف الكوكيز

#### خطوات الحصول على ملف الكوكيز:

1. **تثبيت إضافة المتصفح:**
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **تسجيل الدخول إلى YouTube:**
   - افتح YouTube في متصفحك
   - سجل الدخول بحسابك

3. **تصدير الكوكيز:**
   - انقر على أيقونة الإضافة
   - احفظ ملف `cookies.txt`

4. **استخدام الكوكيز في API:**

```python
# في ملف youtube_downloader_api.py
def get_cookies_for_age_restricted():
    return "/path/to/your/cookies.txt"
```

### الطريقة الثانية: استخدام المصادقة البرمجية

```python
ydl_opts = {
    'username': 'your_email@gmail.com',
    'password': 'your_password',
    # أو استخدام OAuth
}
```

⚠️ **ملاحظة أمنية**: لا تشارك ملف الكوكيز أو بيانات الاعتماد الخاصة بك

---

## 2. تجاوز القيود الجغرافية

### تفعيل البروكسي

```python
ydl_opts = {
    'proxy': 'http://proxy.example.com:8080',
    # أو استخدام SOCKS5
    'proxy': 'socks5://127.0.0.1:1080',
}
```

### استخدام VPN

API يدعم تلقائياً تجاوز القيود الجغرافية:
```python
'geo_bypass': True,
'geo_bypass_country': 'US',
```

---

## 3. تحميل البث المباشر

### تحميل بث مباشر جاري

```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=LIVE_VIDEO_ID",
    "format_type": "best",
    "async": true
  }'
```

### الانتظار حتى بدء البث

API يدعم تلقائياً انتظار بدء البث:
```python
'wait_for_video': (10, 60),  # انتظار من 10 إلى 60 ثانية
'live_from_start': True,      # التسجيل من بداية البث
```

---

## 4. تحميل القوائم المتقدم

### تحميل قائمة كاملة بترتيب عكسي

```python
import requests

response = requests.post(
    "http://localhost:5000/api/download/playlist",
    json={
        "url": "https://youtube.com/playlist?list=...",
        "format_type": "best",
        "max_downloads": 100,
        "reverse": True  # يمكن إضافة هذا في الكود
    }
)
```

### تحميل فيديوهات محددة من القائمة

```python
# في get_ydl_opts()، أضف:
ydl_opts['playlist_items'] = '1-5,10,15-20'  # الفيديوهات 1-5، 10، 15-20
```

---

## 5. تحميل بجودة مخصصة

### اختيار دقة وترميز محدد

```python
# في API call:
{
    "url": "...",
    "format_type": "custom",
    "custom_format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best"
}
```

### تحميل بأعلى FPS

```python
ydl_opts['format'] = 'bestvideo[fps>=60]+bestaudio/best'
```

---

## 6. استخراج الترجمات

### الحصول على جميع الترجمات المتاحة

```python
import requests

response = requests.post(
    "http://localhost:5000/api/info",
    json={"url": "https://youtube.com/watch?v=..."}
)

info = response.json()
subtitles = info.get('subtitles', {})
print(f"الترجمات المتاحة: {list(subtitles.keys())}")
```

### تحميل ترجمات بلغة محددة

```python
ydl_opts['subtitleslangs'] = ['ar', 'en']  # عربي وإنجليزي فقط
```

---

## 7. التحكم في السرعة والأداء

### تحديد سرعة التحميل

```python
ydl_opts['ratelimit'] = 1000000  # 1 MB/s (بالبايت)
```

### تحسين الأداء للملفات الكبيرة

```python
ydl_opts.update({
    'http_chunk_size': 10485760,  # 10MB chunks
    'concurrent_fragment_downloads': 10,  # 10 تحميلات متزامنة
    'buffersize': 1024 * 1024 * 10,  # 10MB buffer
})
```

---

## 8. معالجة الأخطاء المتقدمة

### إعادة المحاولة مع تأخير تدريجي

```python
ydl_opts.update({
    'retries': 10,
    'fragment_retries': 10,
    'retry_sleep_functions': {
        'http': lambda n: 2 ** n,  # 2, 4, 8, 16, ...
    }
})
```

### تسجيل الأخطاء

```python
import logging

logging.basicConfig(level=logging.DEBUG)
ydl_opts['verbose'] = True
```

---

## 9. التحميل بتنسيقات خاصة

### تحميل فيديو بدون صوت

```python
ydl_opts['format'] = 'bestvideo'
```

### تحميل صوت بجودة محددة

```python
ydl_opts.update({
    'format': 'bestaudio',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',  # 320 kbps
    }]
})
```

### تحويل إلى تنسيق محدد

```python
ydl_opts.update({
    'format': 'best',
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'avi',  # أو mkv, flv, webm
    }]
})
```

---

## 10. استخدامات خاصة

### تحميل قناة كاملة

```python
response = requests.post(
    "http://localhost:5000/api/download/playlist",
    json={
        "url": "https://www.youtube.com/@channel_name/videos",
        "max_downloads": 200
    }
)
```

### تحميل نتائج بحث

```python
url = "ytsearch10:python programming"  # أول 10 نتائج
# أو
url = "ytsearchdate:python programming"  # مرتبة حسب التاريخ
```

### تحميل من خدمات أخرى

yt-dlp يدعم أكثر من 1000 موقع:

```python
# Vimeo
url = "https://vimeo.com/..."

# Dailymotion
url = "https://www.dailymotion.com/video/..."

# TikTok
url = "https://www.tiktok.com/@user/video/..."

# Twitter
url = "https://twitter.com/user/status/..."
```

---

## 11. أمثلة برمجية متقدمة

### تحميل فيديو مع معالجة مخصصة

```python
import requests
import time

def download_with_retry(url, max_retries=3):
    """تحميل مع إعادة محاولة تلقائية"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:5000/api/download",
                json={
                    "url": url,
                    "format_type": "best",
                    "async": True
                },
                timeout=10
            )
            
            if response.status_code == 202:
                return response.json()
            
        except Exception as e:
            print(f"المحاولة {attempt + 1} فشلت: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # تأخير تدريجي
    
    return None
```

### معالجة دفعة من الفيديوهات

```python
def batch_download(urls, format_type="best"):
    """تحميل عدة فيديوهات دفعة واحدة"""
    download_ids = []
    
    for url in urls:
        response = requests.post(
            "http://localhost:5000/api/download",
            json={
                "url": url,
                "format_type": format_type,
                "async": True
            }
        )
        
        if response.status_code == 202:
            download_ids.append(response.json()['download_id'])
    
    return download_ids

# الاستخدام
urls = [
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=...",
    "https://youtube.com/watch?v=..."
]

download_ids = batch_download(urls)
print(f"بدأ تحميل {len(download_ids)} فيديو")
```

---

## 12. نصائح للأداء الأمثل

### 1. استخدام قاعدة بيانات للتتبع
```python
import sqlite3

# تخزين معلومات التحميلات
conn = sqlite3.connect('downloads.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS downloads (
        id TEXT PRIMARY KEY,
        url TEXT,
        status TEXT,
        filename TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
```

### 2. التنظيف التلقائي للملفات القديمة
```python
import os
from datetime import datetime, timedelta

def cleanup_old_downloads(days=7):
    """حذف الملفات الأقدم من أسبوع"""
    cutoff = datetime.now() - timedelta(days=days)
    
    for file in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, file)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if file_time < cutoff:
                os.remove(filepath)
```

### 3. استخدام Redis للتخزين المؤقت
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def cache_video_info(url, info, expire=3600):
    """تخزين معلومات الفيديو لساعة واحدة"""
    r.setex(f"video:{url}", expire, json.dumps(info))
```

---

## 🔐 الأمان وأفضل الممارسات

1. **لا تشارك ملفات الكوكيز**
2. **استخدم HTTPS للاتصالات**
3. **قم بتحديث yt-dlp بانتظام**
4. **احذف الملفات المؤقتة بانتظام**
5. **استخدم متغيرات البيئة للمعلومات الحساسة**
6. **قيّد الوصول إلى API بجدار ناري**

---

## 📊 المراقبة والصيانة

### إعداد Logging متقدم

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'youtube_api.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

---

للمزيد من المعلومات، راجع:
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp#readme)
- [YouTube API Guidelines](https://developers.google.com/youtube/terms/api-services-terms-of-service)
