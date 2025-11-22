# 📚 أمثلة شاملة لاستخدام API

## جدول المحتويات
1. [أمثلة Python](#python-examples)
2. [أمثلة cURL](#curl-examples)
3. [أمثلة JavaScript](#javascript-examples)
4. [أمثلة PHP](#php-examples)
5. [أمثلة حالات استخدام واقعية](#real-world-use-cases)

---

## Python Examples

### مثال 1: تحميل فيديو واحد بسيط

```python
import requests

API_URL = "http://localhost:5000"
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# تحميل فيديو
response = requests.post(
    f"{API_URL}/api/download",
    json={
        "url": video_url,
        "format_type": "best",
        "async": True
    }
)

result = response.json()
print(f"Download ID: {result['download_id']}")
print(f"Status URL: {result['status_url']}")
```

### مثال 2: تحميل مع متابعة التقدم

```python
import requests
import time

def download_with_progress(video_url):
    # بدء التحميل
    response = requests.post(
        "http://localhost:5000/api/download",
        json={
            "url": video_url,
            "format_type": "best",
            "async": True
        }
    )
    
    download_id = response.json()['download_id']
    
    # متابعة التقدم
    while True:
        status_response = requests.get(
            f"http://localhost:5000/api/status/{download_id}"
        )
        status = status_response.json()
        
        print(f"\rProgress: {status['progress']} | "
              f"Speed: {status.get('speed', 'N/A')} | "
              f"ETA: {status.get('eta', 'N/A')}", end='')
        
        if status['status'] == 'completed':
            print(f"\n✅ Download complete: {status['filename']}")
            return status
        elif status['status'] == 'error':
            print(f"\n❌ Error: {status['error']}")
            return None
        
        time.sleep(2)

# استخدام
download_with_progress("https://youtube.com/watch?v=...")
```

### مثال 3: تحميل صوت MP3

```python
import requests

def download_audio(video_url):
    response = requests.post(
        "http://localhost:5000/api/download",
        json={
            "url": video_url,
            "format_type": "audio",
            "async": True
        }
    )
    return response.json()

# تحميل أغنية
result = download_audio("https://youtube.com/watch?v=...")
print(result)
```

### مثال 4: تحميل قائمة تشغيل كاملة

```python
import requests

def download_playlist(playlist_url, max_videos=50):
    response = requests.post(
        "http://localhost:5000/api/download/playlist",
        json={
            "url": playlist_url,
            "format_type": "best",
            "max_downloads": max_videos
        }
    )
    return response.json()

# تحميل playlist
playlist = "https://youtube.com/playlist?list=PLxxx"
result = download_playlist(playlist, max_videos=10)
print(f"Playlist download started: {result['download_id']}")
```

### مثال 5: الحصول على معلومات الفيديو

```python
import requests

def get_video_info(video_url):
    response = requests.post(
        "http://localhost:5000/api/info",
        json={"url": video_url}
    )
    
    if response.status_code == 200:
        info = response.json()
        print(f"Title: {info['title']}")
        print(f"Duration: {info['duration']} seconds")
        print(f"Views: {info['views']:,}")
        print(f"Uploader: {info['uploader']}")
        print(f"Age restricted: {info['age_limited']}")
        return info
    else:
        print(f"Error: {response.json()}")
        return None

# استخدام
info = get_video_info("https://youtube.com/watch?v=...")
```

### مثال 6: تحميل بجودة محددة

```python
import requests

def download_specific_quality(video_url, quality="720"):
    response = requests.post(
        "http://localhost:5000/api/download",
        json={
            "url": video_url,
            "format_type": "specific_quality",
            "quality": quality,
            "async": True
        }
    )
    return response.json()

# تحميل بجودة 1080p
result = download_specific_quality("https://youtube.com/watch?v=...", "1080")
```

### مثال 7: تحميل متعدد بالتوازي

```python
import requests
import concurrent.futures

def download_video(url):
    response = requests.post(
        "http://localhost:5000/api/download",
        json={"url": url, "format_type": "best", "async": True}
    )
    return response.json()

# قائمة الفيديوهات
video_urls = [
    "https://youtube.com/watch?v=video1",
    "https://youtube.com/watch?v=video2",
    "https://youtube.com/watch?v=video3"
]

# تحميل بالتوازي
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(download_video, video_urls))

print(f"Started {len(results)} downloads")
for result in results:
    print(f"Download ID: {result['download_id']}")
```

---

## cURL Examples

### مثال 1: الحصول على معلومات الفيديو

```bash
curl -X POST http://localhost:5000/api/info \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
  }' | jq
```

### مثال 2: تحميل فيديو بأفضل جودة

```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "format_type": "best",
    "async": true
  }' | jq
```

### مثال 3: تحميل صوت فقط

```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "format_type": "audio",
    "async": true
  }' | jq
```

### مثال 4: الحصول على حالة التحميل

```bash
# احفظ download_id من الأمر السابق
DOWNLOAD_ID="your-download-id-here"

curl http://localhost:5000/api/status/$DOWNLOAD_ID | jq
```

### مثال 5: عرض جميع الصيغ المتاحة

```bash
curl -X POST http://localhost:5000/api/formats \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
  }' | jq '.formats[] | {format_id, resolution, ext, filesize}'
```

---

## JavaScript Examples

### مثال 1: تحميل فيديو (Node.js)

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:5000';

async function downloadVideo(videoUrl) {
    try {
        const response = await axios.post(`${API_URL}/api/download`, {
            url: videoUrl,
            format_type: 'best',
            async: true
        });
        
        console.log('Download ID:', response.data.download_id);
        return response.data;
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// استخدام
downloadVideo('https://youtube.com/watch?v=...');
```

### مثال 2: متابعة التقدم (Node.js)

```javascript
async function monitorDownload(downloadId) {
    const maxAttempts = 100;
    let attempt = 0;
    
    while (attempt < maxAttempts) {
        try {
            const response = await axios.get(
                `${API_URL}/api/status/${downloadId}`
            );
            
            const status = response.data;
            
            process.stdout.write(
                `\rProgress: ${status.progress} | ` +
                `Speed: ${status.speed || 'N/A'} | ` +
                `ETA: ${status.eta || 'N/A'}`
            );
            
            if (status.status === 'completed') {
                console.log('\n✅ Download complete!');
                return status;
            } else if (status.status === 'error') {
                console.log('\n❌ Error:', status.error);
                return null;
            }
            
            await new Promise(resolve => setTimeout(resolve, 2000));
            attempt++;
        } catch (error) {
            console.error('Error:', error.message);
            break;
        }
    }
}
```

### مثال 3: تحميل بالمتصفح (Fetch API)

```javascript
// في المتصفح
async function downloadVideo(videoUrl) {
    try {
        const response = await fetch('http://localhost:5000/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: videoUrl,
                format_type: 'best',
                async: true
            })
        });
        
        const data = await response.json();
        console.log('Download started:', data.download_id);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}
```

---

## PHP Examples

### مثال 1: تحميل فيديو

```php
<?php
$api_url = 'http://localhost:5000';
$video_url = 'https://youtube.com/watch?v=dQw4w9WgXcQ';

$data = array(
    'url' => $video_url,
    'format_type' => 'best',
    'async' => true
);

$options = array(
    'http' => array(
        'header'  => "Content-type: application/json\r\n",
        'method'  => 'POST',
        'content' => json_encode($data)
    )
);

$context = stream_context_create($options);
$result = file_get_contents($api_url . '/api/download', false, $context);
$response = json_decode($result);

echo "Download ID: " . $response->download_id . "\n";
?>
```

### مثال 2: الحصول على معلومات الفيديو

```php
<?php
function getVideoInfo($video_url) {
    $api_url = 'http://localhost:5000/api/info';
    
    $data = array('url' => $video_url);
    
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($data)
        )
    );
    
    $context = stream_context_create($options);
    $result = file_get_contents($api_url, false, $context);
    
    return json_decode($result);
}

$info = getVideoInfo('https://youtube.com/watch?v=...');
echo "Title: " . $info->title . "\n";
echo "Duration: " . $info->duration . " seconds\n";
?>
```

---

## Real-world Use Cases

### حالة 1: تطبيق ويب لتحميل الفيديوهات

```python
from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)
DOWNLOADER_API = "http://localhost:5000"

@app.route('/')
def index():
    return render_template('download.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.json.get('url')
    quality = request.json.get('quality', 'best')
    
    # إرسال طلب للـ API
    response = requests.post(
        f"{DOWNLOADER_API}/api/download",
        json={
            "url": video_url,
            "format_type": "specific_quality" if quality != 'best' else 'best',
            "quality": quality,
            "async": True
        }
    )
    
    return jsonify(response.json())

@app.route('/status/<download_id>')
def status(download_id):
    response = requests.get(f"{DOWNLOADER_API}/api/status/{download_id}")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=3000)
```

### حالة 2: بوت Telegram لتحميل الفيديوهات

```python
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests

API_URL = "http://localhost:5000"

def start(update: Update, context):
    update.message.reply_text(
        'أرسل لي رابط فيديو YouTube وسأقوم بتحميله لك!'
    )

def download_video(update: Update, context):
    url = update.message.text
    
    # التحقق من أنه رابط YouTube
    if 'youtube.com' not in url and 'youtu.be' not in url:
        update.message.reply_text('الرجاء إرسال رابط YouTube صحيح')
        return
    
    update.message.reply_text('جاري التحميل... ⏳')
    
    # تحميل الفيديو
    response = requests.post(
        f"{API_URL}/api/download",
        json={"url": url, "format_type": "best", "async": True}
    )
    
    download_id = response.json()['download_id']
    
    # متابعة التحميل
    import time
    while True:
        status = requests.get(f"{API_URL}/api/status/{download_id}").json()
        
        if status['status'] == 'completed':
            update.message.reply_text(
                f"✅ اكتمل التحميل!\n"
                f"📁 الملف: {status['filename']}"
            )
            break
        elif status['status'] == 'error':
            update.message.reply_text(f"❌ خطأ: {status['error']}")
            break
        
        time.sleep(3)

def main():
    updater = Updater("YOUR_BOT_TOKEN")
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
```

### حالة 3: نظام تحميل تلقائي من قوائم

```python
import requests
import schedule
import time

API_URL = "http://localhost:5000"

def download_new_videos_from_channel():
    """تحميل الفيديوهات الجديدة من قناة"""
    
    channel_url = "https://www.youtube.com/@channel_name/videos"
    
    # الحصول على معلومات القناة
    response = requests.post(
        f"{API_URL}/api/info",
        json={"url": channel_url}
    )
    
    # تحميل الفيديوهات
    response = requests.post(
        f"{API_URL}/api/download/playlist",
        json={
            "url": channel_url,
            "format_type": "best",
            "max_downloads": 5  # آخر 5 فيديوهات
        }
    )
    
    print(f"Started downloading new videos: {response.json()['download_id']}")

# جدولة التحميل كل 6 ساعات
schedule.every(6).hours.do(download_new_videos_from_channel)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### حالة 4: أرشفة دورات تعليمية

```python
import requests
import os

def archive_course_playlist(playlist_url, course_name):
    """أرشفة دورة تعليمية كاملة"""
    
    # إنشاء مجلد للدورة
    course_dir = f"./courses/{course_name}"
    os.makedirs(course_dir, exist_ok=True)
    
    # تحميل القائمة
    response = requests.post(
        "http://localhost:5000/api/download/playlist",
        json={
            "url": playlist_url,
            "format_type": "video_audio",
            "max_downloads": 100
        }
    )
    
    download_id = response.json()['download_id']
    
    print(f"Archiving course: {course_name}")
    print(f"Download ID: {download_id}")
    
    # متابعة التقدم
    import time
    while True:
        status = requests.get(
            f"http://localhost:5000/api/status/{download_id}"
        ).json()
        
        print(f"Status: {status['status']} - {status.get('progress', '0%')}")
        
        if status['status'] in ['completed', 'error']:
            break
        
        time.sleep(10)
    
    print(f"Course archived in: {course_dir}")

# استخدام
archive_course_playlist(
    "https://youtube.com/playlist?list=PLxxx",
    "Python Programming"
)
```

---

## نصائح للاستخدام الفعال

1. **استخدم async: true** للتحميلات الطويلة
2. **راقب حالة التحميل** بشكل دوري
3. **تعامل مع الأخطاء** بشكل صحيح
4. **استخدم cookies** للمحتوى المحمي
5. **حدد الجودة المناسبة** لاحتياجاتك

---

للمزيد من الأمثلة، راجع:
- `example_usage.py` - أمثلة تفاعلية
- `README_AR.md` - توثيق شامل
