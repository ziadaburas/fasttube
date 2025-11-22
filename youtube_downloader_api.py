"""
YouTube Downloader API - واجهة برمجية متقدمة لتحميل الفيديوهات من YouTube
يدعم جميع أنواع الفيديوهات بما في ذلك المحمية بالفئة العمرية والمباشرة والقوائم
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import json
from datetime import datetime
import threading
import uuid
from pathlib import Path

app = Flask(__name__)
CORS(app)

# مجلد التحميلات
DOWNLOAD_DIR = Path("/home/user/downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
# DOWNLOAD_DIR = Path("/home/user/downloads")
# DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# تتبع حالة التحميلات
downloads_status = {}


class DownloadProgress:
    """متتبع تقدم التحميل"""
    def __init__(self, download_id):
        self.download_id = download_id
        self.status = "initializing"
        self.progress = 0
        self.speed = ""
        self.eta = ""
        self.filename = ""
        self.error = None
    
    def update(self, d):
        """تحديث معلومات التقدم"""
        downloads_status[self.download_id] = {
            'status': d.get('status', 'downloading'),
            'progress': d.get('_percent_str', '0%'),
            'speed': d.get('_speed_str', 'N/A'),
            'eta': d.get('_eta_str', 'N/A'),
            'filename': d.get('filename', self.filename),
            'downloaded': d.get('_downloaded_bytes_str', '0'),
            'total': d.get('_total_bytes_str', 'Unknown'),
            'error': None
        }


def get_cookies_for_age_restricted():
    """
    إعداد الكوكيز للوصول إلى المحتوى المحمي بالفئة العمرية
    يمكنك إضافة كوكيز حقيقية من متصفحك إذا لزم الأمر
    """
    # يمكن استخدام ملف كوكيز من المتصفح
    # لتصدير الكوكيز: استخدم إضافة "Get cookies.txt" في Chrome/Firefox
    return None  # أو مسار ملف الكوكيز


def get_ydl_opts(download_id, format_type='best', quality='best', output_path=None):
    """
    إعدادات yt-dlp المتقدمة
    
    Args:
        download_id: معرف التحميل
        format_type: نوع الصيغة (best, audio, video, playlist)
        quality: الجودة المطلوبة
        output_path: مسار الحفظ
    """
    progress_tracker = DownloadProgress(download_id)
    
    # المسار الافتراضي
    if output_path is None:
        output_path = str(DOWNLOAD_DIR / "%(title)s.%(ext)s")
    
    # الإعدادات الأساسية
    ydl_opts = {
        'outtmpl': output_path,
        'progress_hooks': [progress_tracker.update],
        'quiet': False,
        'no_warnings': False,
        
        # تجاوز القيود الجغرافية والعمرية
        'age_limit': None,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        
        # معالجة الأخطاء
        'ignoreerrors': False,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        
        # تحسين الأداء
        'concurrent_fragment_downloads': 5,
        'http_chunk_size': 10485760,  # 10MB chunks
        
        # معلومات إضافية
        'writeinfojson': True,
        'writethumbnail': True,
        'writedescription': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'allsubtitles': True,
        
        # دعم البث المباشر
        'live_from_start': True,
        'wait_for_video': (10, 60),  # انتظار حتى 60 ثانية
        
        # دعم القوائم
        'yes_playlist': True,
        
        # تجنب الحظر
        'sleep_interval': 1,
        'max_sleep_interval': 5,
        'sleep_interval_requests': 1,
        
        # User agent متنوع
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # استخراج البيانات المسطحة للقوائم
        'extract_flat': False,
    }
    
    # إعدادات حسب نوع التحميل
    if format_type == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif format_type == 'video_audio':
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })
    elif format_type == 'specific_quality':
        ydl_opts.update({
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        })
    else:  # best
        ydl_opts.update({
            'format': 'best',
        })
    
    # إضافة كوكيز إذا كانت متوفرة
    cookies = get_cookies_for_age_restricted()
    if cookies:
        ydl_opts['cookiefile'] = cookies
    
    return ydl_opts


def download_video_thread(url, download_id, options):
    """تنزيل الفيديو في خيط منفصل"""
    print("+"*100)
    try:
        ydl_opts = get_ydl_opts(
            download_id,
            format_type=options.get('format_type', 'best'),
            quality=options.get('quality', 'best')
        )
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # حفظ معلومات الفيديو
            downloads_status[download_id].update({
                'status': 'completed',
                'progress': '100%',
                'filename': ydl.prepare_filename(info),
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
            })
            
    except Exception as e:
        downloads_status[download_id] = {
            'status': 'error',
            'error': str(e),
            'progress': '0%'
        }


@app.route('/api/info', methods=['POST'])
def get_video_info():
    """
    الحصول على معلومات الفيديو بدون تحميل
    
    Body:
    {
        "url": "https://youtube.com/watch?v=..."
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'age_limit': None,
            'geo_bypass': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # استخراج الصيغ المتاحة
            formats = []
            if 'formats' in info:
                for f in info['formats']:
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'quality': f.get('format_note'),
                        'resolution': f.get('resolution'),
                        'filesize': f.get('filesize'),
                        'fps': f.get('fps'),
                        'vcodec': f.get('vcodec'),
                        'acodec': f.get('acodec'),
                    })
            
            result = {
                'title': info.get('title'),
                'description': info.get('description'),
                'duration': info.get('duration'),
                'views': info.get('view_count'),
                'likes': info.get('like_count'),
                'uploader': info.get('uploader'),
                'upload_date': info.get('upload_date'),
                'thumbnail': info.get('thumbnail'),
                'age_limited': info.get('age_limit', 0) > 0,
                'is_live': info.get('is_live', False),
                'formats': formats,
                'categories': info.get('categories', []),
                'tags': info.get('tags', []),
            }
            
            return jsonify(result), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download_video():
    """
    تحميل فيديو
    
    Body:
    {
        "url": "https://youtube.com/watch?v=...",
        "format_type": "best|audio|video_audio|specific_quality",
        "quality": "1080|720|480|360",
        "async": true|false
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format_type', 'best')
        quality = data.get('quality', 'best')
        is_async = data.get('async', True)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # إنشاء معرف فريد للتحميل
        download_id = str(uuid.uuid4())
        downloads_status[download_id] = {
            'status': 'starting',
            'progress': '0%',
            'url': url
        }
        
        options = {
            'format_type': format_type,
            'quality': quality
        }
        
        if is_async:
            # تحميل غير متزامن
            thread = threading.Thread(
                target=download_video_thread,
                args=(url, download_id, options)
            )
            thread.start()
            
            return jsonify({
                'download_id': download_id,
                'message': 'Download started',
                'status_url': f'/api/status/{download_id}'
            }), 202
        else:
            # تحميل متزامن
            download_video_thread(url, download_id, options)
            return jsonify(downloads_status[download_id]), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/playlist', methods=['POST'])
def download_playlist():
    """
    تحميل قائمة تشغيل كاملة
    
    Body:
    {
        "url": "https://youtube.com/playlist?list=...",
        "format_type": "best|audio",
        "max_downloads": 50
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format_type', 'best')
        max_downloads = data.get('max_downloads', 50)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        download_id = str(uuid.uuid4())
        downloads_status[download_id] = {
            'status': 'starting',
            'progress': '0%',
            'type': 'playlist'
        }
        
        def download_playlist_thread():
            try:
                ydl_opts = get_ydl_opts(download_id, format_type=format_type)
                ydl_opts['max_downloads'] = max_downloads
                ydl_opts['playlist_items'] = f'1:{max_downloads}'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    downloads_status[download_id].update({
                        'status': 'completed',
                        'progress': '100%',
                        'playlist_title': info.get('title'),
                        'playlist_count': len(info.get('entries', [])),
                    })
                    
            except Exception as e:
                downloads_status[download_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        thread = threading.Thread(target=download_playlist_thread)
        thread.start()
        
        return jsonify({
            'download_id': download_id,
            'message': 'Playlist download started',
            'status_url': f'/api/status/{download_id}'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    """الحصول على حالة التحميل"""
    if download_id not in downloads_status:
        return jsonify({'error': 'Download ID not found'}), 404
    
    return jsonify(downloads_status[download_id]), 200


@app.route('/api/downloads', methods=['GET'])
def list_downloads():
    """قائمة جميع التحميلات"""
    return jsonify(downloads_status), 200


@app.route('/api/formats', methods=['POST'])
def get_available_formats():
    """
    الحصول على جميع الصيغ المتاحة للفيديو
    
    Body:
    {
        "url": "https://youtube.com/watch?v=..."
    }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        ydl_opts = {
            'quiet': True,
            'listformats': True,
            'age_limit': None,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats_list = []
            for f in info.get('formats', []):
                formats_list.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution', 'audio only'),
                    'fps': f.get('fps'),
                    'filesize': f.get('filesize'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'format_note': f.get('format_note'),
                })
            
            return jsonify({
                'title': info.get('title'),
                'formats': formats_list
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_downloads': len([d for d in downloads_status.values() if d.get('status') == 'downloading'])
    }), 200


@app.route('/', methods=['GET'])
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        'name': 'YouTube Downloader API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'API Information',
            'GET /api/health': 'Health check',
            'POST /api/info': 'Get video information',
            'POST /api/download': 'Download video',
            'POST /api/download/playlist': 'Download playlist',
            'GET /api/status/<id>': 'Get download status',
            'GET /api/downloads': 'List all downloads',
            'POST /api/formats': 'Get available formats',
        },
        'documentation': 'https://github.com/yt-dlp/yt-dlp'
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 YouTube Downloader API")
    print("=" * 60)
    print(f"📁 Download Directory: {DOWNLOAD_DIR}")
    print("🌐 Server starting on http://0.0.0.0:5000")
    print("=" * 60)
    print("\n📖 Available Endpoints:")
    print("  - GET  /api/health")
    print("  - POST /api/info")
    print("  - POST /api/download")
    print("  - POST /api/download/playlist")
    print("  - GET  /api/status/<download_id>")
    print("  - POST /api/formats")
    print("\n" + "=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
