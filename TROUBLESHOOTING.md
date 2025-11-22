# 🔧 دليل حل المشاكل الشائعة

## المشاكل الشائعة وحلولها

### 1. خطأ: "Video unavailable" (الفيديو غير متاح)

#### الأسباب المحتملة:
- الفيديو محذوف أو خاص
- قيود جغرافية
- قيود عمرية
- فيديو مقيد في بلدك

#### الحلول:

**أ) للقيود الجغرافية:**
```python
# أضف في ydl_opts:
'geo_bypass': True,
'geo_bypass_country': 'US',  # جرب دول مختلفة: US, UK, CA, AU
```

**ب) للقيود العمرية:**
```bash
# احصل على ملف cookies من متصفحك بعد تسجيل الدخول
# ثم أضف المسار في الكود:
def get_cookies_for_age_restricted():
    return "/path/to/cookies.txt"
```

**ج) استخدام VPN:**
```bash
# شغل VPN على جهازك ثم حاول مرة أخرى
```

---

### 2. خطأ: "HTTP Error 403: Forbidden"

#### الأسباب:
- YouTube اكتشف أن الطلب من برنامج آلي
- IP محظور مؤقتاً
- تجاوز معدل الطلبات

#### الحلول:

**أ) إضافة تأخير بين الطلبات:**
```python
ydl_opts['sleep_interval'] = 3
ydl_opts['max_sleep_interval'] = 10
```

**ب) تغيير User Agent:**
```python
ydl_opts['user_agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
```

**ج) استخدام كوكيز:**
```python
ydl_opts['cookiefile'] = '/path/to/cookies.txt'
```

**د) تحديث yt-dlp:**
```bash
pip install --upgrade yt-dlp
```

---

### 3. خطأ: "ffmpeg not found"

#### الأسباب:
- ffmpeg غير مثبت
- ffmpeg غير موجود في PATH

#### الحلول:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
# قم بتحميل ffmpeg من:
# https://ffmpeg.org/download.html
# ثم أضف المجلد إلى PATH
```

**التحقق من التثبيت:**
```bash
ffmpeg -version
```

---

### 4. خطأ: "Requested format not available"

#### الأسباب:
- الجودة المطلوبة غير متاحة
- تنسيق غير مدعوم

#### الحلول:

**أ) التحقق من الصيغ المتاحة أولاً:**
```bash
curl -X POST http://localhost:5000/api/formats \
  -H "Content-Type: application/json" \
  -d '{"url": "YOUR_VIDEO_URL"}'
```

**ب) استخدام format احتياطي:**
```python
ydl_opts['format'] = 'bestvideo+bestaudio/best'
```

**ج) تجنب تحديد جودة محددة:**
```python
# بدلاً من:
'format': 'bestvideo[height=1080]'

# استخدم:
'format': 'bestvideo[height<=1080]'  # أو أقل
```

---

### 5. التحميل بطيء جداً

#### الأسباب:
- سرعة الإنترنت
- تحديد rate limit
- خادم YouTube بطيء

#### الحلول:

**أ) إزالة rate limit:**
```python
# احذف أو علّق هذا السطر:
# ydl_opts['ratelimit'] = 1000000
```

**ب) زيادة concurrent downloads:**
```python
ydl_opts['concurrent_fragment_downloads'] = 10
```

**ج) استخدام CDN أسرع:**
```python
ydl_opts['prefer_free_formats'] = False
```

---

### 6. خطأ: "Connection timeout" أو "Network error"

#### الحلول:

**أ) زيادة timeout:**
```python
ydl_opts['socket_timeout'] = 60
```

**ب) زيادة عدد المحاولات:**
```python
ydl_opts['retries'] = 20
ydl_opts['fragment_retries'] = 20
```

**ج) استخدام proxy:**
```python
ydl_opts['proxy'] = 'http://proxy.example.com:8080'
```

---

### 7. الملف المحمل تالف أو لا يعمل

#### الأسباب:
- انقطاع التحميل
- مشكلة في دمج الصوت والفيديو
- ترميز غير مدعوم

#### الحلول:

**أ) التحقق من اكتمال التحميل:**
```bash
# تحقق من حجم الملف
ls -lh /path/to/file.mp4

# قارن مع الحجم المتوقع من API
```

**ب) إعادة التحميل مع خيارات مختلفة:**
```python
ydl_opts.update({
    'format': 'best',  # بدلاً من bestvideo+bestaudio
    'merge_output_format': 'mp4',
})
```

**ج) استخدام postprocessor للتحقق:**
```python
ydl_opts['postprocessors'].append({
    'key': 'FFmpegFixupM4a',
})
```

---

### 8. خطأ: "Sign in to confirm your age"

#### الحلول:

**الحل الوحيد الفعال - استخدام cookies:**

1. **تثبيت إضافة متصفح:**
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/firefox/addon/cookies-txt/)

2. **تسجيل الدخول إلى YouTube**

3. **تصدير الكوكيز:**
   ```bash
   # احفظ الملف باسم: youtube_cookies.txt
   ```

4. **استخدام الكوكيز في API:**
   ```python
   def get_cookies_for_age_restricted():
       return "/path/to/youtube_cookies.txt"
   ```

---

### 9. خطأ: "Postprocessing failed"

#### الأسباب:
- مشكلة في ffmpeg
- صلاحيات الملفات
- مساحة القرص ممتلئة

#### الحلول:

**أ) التحقق من ffmpeg:**
```bash
ffmpeg -version
which ffmpeg
```

**ب) التحقق من المساحة المتاحة:**
```bash
df -h
```

**ج) إعطاء صلاحيات الكتابة:**
```bash
chmod -R 755 /path/to/download/dir
```

**د) تخطي postprocessing:**
```python
ydl_opts['skip_download'] = False
ydl_opts['postprocessors'] = []
```

---

### 10. خطأ في تحميل playlist

#### المشاكل:
- بعض الفيديوهات تفشل
- القائمة كبيرة جداً

#### الحلول:

**أ) تجاهل الأخطاء والاستمرار:**
```python
ydl_opts['ignoreerrors'] = True
```

**ب) تحديد نطاق الفيديوهات:**
```python
ydl_opts['playlist_items'] = '1-50'  # أول 50 فيديو فقط
```

**ج) تقسيم القائمة:**
```python
# المجموعة الأولى
ydl_opts['playlist_items'] = '1-50'

# المجموعة الثانية
ydl_opts['playlist_items'] = '51-100'
```

---

### 11. استهلاك عالي للذاكرة/CPU

#### الحلول:

**أ) تقليل التحميلات المتزامنة:**
```python
ydl_opts['concurrent_fragment_downloads'] = 3
```

**ب) تحديد جودة أقل:**
```python
ydl_opts['format'] = 'best[height<=720]'
```

**ج) تحميل متتالي بدلاً من متوازي:**
```python
# في API:
"async": False
```

---

### 12. خطأ: "Unable to extract video data"

#### الأسباب:
- YouTube غيّر هيكل الصفحة
- yt-dlp قديم

#### الحلول:

**أ) تحديث yt-dlp:**
```bash
pip install --upgrade yt-dlp
```

**ب) استخدام نسخة nightly:**
```bash
pip install --upgrade --pre yt-dlp
```

**ج) التحقق من الإصدار:**
```bash
yt-dlp --version
```

---

## أوامر التشخيص المفيدة

### 1. اختبار تحميل فيديو مباشر

```bash
# باستخدام yt-dlp مباشرة:
yt-dlp -F "https://youtube.com/watch?v=VIDEO_ID"  # عرض الصيغ
yt-dlp "https://youtube.com/watch?v=VIDEO_ID"     # تحميل

# مع cookies:
yt-dlp --cookies cookies.txt "URL"

# مع verbose للتشخيص:
yt-dlp -v "URL"
```

### 2. التحقق من اتصال API

```bash
# فحص صحة API:
curl http://localhost:5000/api/health

# اختبار endpoint معين:
curl -X POST http://localhost:5000/api/info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### 3. مراقبة السجلات

```bash
# عرض سجلات Flask:
tail -f youtube_api.log

# مراقبة نشاط الشبكة:
netstat -an | grep 5000
```

---

## نصائح عامة

### 1. احتفظ بنسخة احتياطية

```bash
# نسخ ملفات التكوين:
cp youtube_downloader_api.py youtube_downloader_api.py.backup
cp cookies.txt cookies.txt.backup
```

### 2. استخدم بيئة افتراضية

```bash
# إنشاء بيئة افتراضية:
python -m venv venv

# تفعيلها:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# تثبيت المتطلبات:
pip install -r requirements.txt
```

### 3. التحديث المنتظم

```bash
# تحديث جميع المكتبات:
pip install --upgrade -r requirements.txt

# تحديث yt-dlp فقط:
pip install --upgrade yt-dlp
```

---

## الحصول على مساعدة إضافية

### 1. تفعيل وضع verbose

```python
ydl_opts['verbose'] = True
ydl_opts['print_traffic'] = True
```

### 2. حفظ debug log

```python
ydl_opts['logger'] = MyLogger()  # أضف logger مخصص
```

### 3. البحث في المشاكل المعروفة

- [yt-dlp Issues](https://github.com/yt-dlp/yt-dlp/issues)
- [yt-dlp Wiki](https://github.com/yt-dlp/yt-dlp/wiki)

---

## متى تطلب المساعدة

إذا جربت كل الحلول أعلاه ولم تنجح:

1. جمع المعلومات التالية:
   - نسخة yt-dlp
   - نسخة Python
   - نظام التشغيل
   - رسالة الخطأ الكاملة
   - الأمر/الكود المستخدم

2. ابحث في GitHub Issues

3. أنشئ issue جديد مع كل التفاصيل

---

**💡 تذكر:** معظم المشاكل تُحل بـ:
- تحديث yt-dlp
- استخدام ملف cookies
- إضافة تأخير بين الطلبات
- التحقق من تثبيت ffmpeg
