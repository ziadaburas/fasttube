"""
YouTube Downloader API - نسخة Render.com
واجهة برمجية متقدمة لتحميل الفيديوهات من YouTube
معدّلة للعمل على منصة Render.com
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

# الحصول على المنفذ من متغيرات البيئة (Render يستخدم PORT)
PORT = int(os.environ.get('PORT', 5000))

# مجلد التحميلات - استخدام /tmp على Render
DOWNLOAD_DIR = Path(os.environ.get('DOWNLOAD_DIR', '/tmp/downloads'))
DOWNLOAD_DIR.mkdir(exist_ok=True, parents=True)

# تتبع حالة التحميلات
downloads_status = {}

# تحديد حد أقصى لحجم التحميلات على الخطة المجانية
MAX_FILE_SIZE_MB = 100  # 100MB للخطة المجانية


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
    على Render، يمكنك إضافة الكوكيز كمتغير بيئة
    """
    #cookies_path = os.environ.get('COOKIES_FILE')
    cookies_path = "cookies.txt"
    if cookies_path and os.path.exists(cookies_path):
        return cookies_path
    return None

def get_ydl_opts2(download_id, format_type='best', quality='best', output_path=None):
    """
    إعدادات yt-dlp المتقدمة - معدّلة حسب طلبك الخاص
    الأمر المقابل:
    yt-dlp -f "bestaudio+bestvideo[height<=480]" --continue \
    -o "/sdcard/Youtube/%(title)s_%(format_id)s.%(ext)s" \
    --merge-output-format mp4 \
    --embed-thumbnail --no-mtime \
    --cookies ~/cookies.txt url
    """
    progress_tracker = DownloadProgress(download_id)
    
    # ملاحظة هامة: لا يوجد /sdcard/ في سيرفرات Render
    # سنستخدم مجلد DOWNLOAD_DIR المحدد في بداية السكريبت بدلاً منه
    if output_path is None:
        # -o ".../%(title)s_%(format_id)s.%(ext)s"
        output_path = str(DOWNLOAD_DIR / "%(title)s_%(format_id)s.%(ext)s")
    
    ydl_opts = {
        # 1. مسار واسم الملف
        'outtmpl': output_path,
        'progress_hooks': [progress_tracker.update],
        
        # 2. الجودة: -f "bestaudio+bestvideo[height<=480]"
        # يقوم بدمج أفضل صوت مع أفضل فيديو (لا يتجاوز 480p)
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        
        # 3. الصيغة النهائية: --merge-output-format mp4
        'merge_output_format': 'mp4',
        
        # 4. استكمال التحميل: --continue
        'continuedl': True,
        
        # 5. الصورة المصغرة: --embed-thumbnail
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'EmbedThumbnail'}, # دمج الصورة
            {'key': 'FFmpegMetadata'}, # إضافة الميتاداتا (يساعد في توافق الصورة)
        ],
        
        # 6. الوقت: --no-mtime (استخدام وقت التحميل بدلاً من وقت رفع الفيديو)
        'updatetime': False,
        
        # 7. الكوكيز: --cookies ~/cookies.txt
        'cookiefile': 'cookies.txt',
        
        # إعدادات إضافية لضمان استقرار السيرفر
        'quiet': False,
        'ignoreerrors': True,
        'geo_bypass': True,
        
        # إذا أردت إبقاء حد الحجم (اختياري، احذفه إذا لا تريده)
        'max_filesize': MAX_FILE_SIZE_MB * 1024 * 1024,
    }
    
    return ydl_opts

def get_ydl_opts(download_id, format_type='best', quality='best', output_path=None):
    """
    إعدادات yt-dlp المتقدمة - معدّلة لـ Render.com
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
        
        # تجاوز القيود
        'age_limit': None,
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        
        # معالجة الأخطاء
        'ignoreerrors': False,
        'retries': 2,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        
        # تحسين الأداء
        'concurrent_fragment_downloads': 3,  # تقليل للخطة المجانية
        'http_chunk_size': 5242880,  # 5MB chunks
        
        # تقليل المعلومات المحفوظة لتوفير المساحة
        'writeinfojson': False,
        'writethumbnail': False,
        'writedescription': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        
        # دعم البث المباشر
        'live_from_start': True,
        'wait_for_video': (10, 60),
        
        # دعم القوائم
        'yes_playlist': True,
        
        # تجنب الحظر
        'sleep_interval': 1,
        'max_sleep_interval': 5,
        'sleep_interval_requests': 1,

        # مسار الكوكيز
        'cookies':'cookies.txt',
        
        # User agent
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # حد أقصى لحجم الملف (للخطة المجانية)
        'max_filesize': MAX_FILE_SIZE_MB * 1024 * 1024,
        
        'extract_flat': False,
    }
    
    # إعدادات حسب نوع التحميل
    # if format_type == 'audio':
    #     ydl_opts.update({
    #         'format': 'bestaudio[filesize<{}M]/best[filesize<{}M]'.format(MAX_FILE_SIZE_MB, MAX_FILE_SIZE_MB),
    #         'postprocessors': [{
    #             'key': 'FFmpegExtractAudio',
    #             'preferredcodec': 'mp3',
    #             'preferredquality': '192',
    #         }],
    #     })
    # elif format_type == 'video_audio':
    #     ydl_opts.update({
    #         'format': 'bestvideo[filesize<{}M]+bestaudio[filesize<{}M]/best[filesize<{}M]'.format(
    #             MAX_FILE_SIZE_MB//2, MAX_FILE_SIZE_MB//2, MAX_FILE_SIZE_MB
    #         ),
    #         'merge_output_format': 'mp4',
    #     })
    # elif format_type == 'specific_quality':
    #     ydl_opts.update({
    #         'format': 'bestvideo[height<={}][filesize<{}M]+bestaudio/best[height<={}][filesize<{}M]'.format(
    #             quality, MAX_FILE_SIZE_MB//2, quality, MAX_FILE_SIZE_MB
    #         ),
    #     })
    # else:  # best
    #     ydl_opts.update({
    #         'format': 'best[filesize<{}M]'.format(MAX_FILE_SIZE_MB),
    #     })
    
    # إضافة كوكيز إذا كانت متوفرة
    cookies = get_cookies_for_age_restricted()
    if cookies:
        ydl_opts['cookiefile'] = cookies
    
    return ydl_opts


def cleanup_old_downloads():
    """تنظيف الملفات القديمة لتوفير المساحة"""
    try:
        import time
        current_time = time.time()
        
        for file in DOWNLOAD_DIR.glob('*'):
            if file.is_file():
                # حذف الملفات الأقدم من ساعة
                if current_time - file.stat().st_mtime > 3600:
                    file.unlink()
    except Exception as e:
        print(f"Error cleaning up: {e}")

@app.route('/api/get-file/<download_id>', methods=['GET'])
def get_file(download_id):
    """رابط لتحميل الملف فعلياً من السيرفر للمستخدم"""
    if download_id not in downloads_status:
        return jsonify({'error': 'Download ID not found'}), 404
    
    status = downloads_status[download_id]
    if status.get('status') != 'completed':
        return jsonify({'error': 'File not ready yet'}), 400
        
    file_path = status.get('filename')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File deleted or not found'}), 404

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def download_video_thread(url, download_id, options):
    """تنزيل الفيديو في خيط منفصل"""
    try:
        # تنظيف الملفات القديمة قبل البدء
        cleanup_old_downloads()
        
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


@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        'name': 'YouTube Downloader API',
        'version': '1.0.0 (Render.com)',
        'status': 'running',
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
        'limits': {
            'max_file_size_mb': MAX_FILE_SIZE_MB,
            'storage': '/tmp (ephemeral)',
        },
        'note': 'Files are automatically deleted after 1 hour'
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_downloads': len([d for d in downloads_status.values() if d.get('status') == 'downloading']),
        'storage_path': str(DOWNLOAD_DIR),
        'port': PORT
    }), 200


@app.route('/api/info', methods=['POST'])
def get_video_info():
    """الحصول على معلومات الفيديو بدون تحميل"""
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
                    filesize = f.get('filesize', 0)
                    # تصفية الصيغ الكبيرة جداً
                    if filesize and filesize > MAX_FILE_SIZE_MB * 1024 * 1024:
                        continue
                        
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
                'formats': formats[:20],  # الحد من عدد الصيغ
                'categories': info.get('categories', []),
                'tags': info.get('tags', [])[:10],  # أول 10 وسوم فقط
            }
            
            return jsonify(result), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download_video():
    """تحميل فيديو"""
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
            thread.daemon = True  # مهم لـ Render
            thread.start()
            
            return jsonify({
                'download_id': download_id,
                'message': 'Download started',
                'status_url': f'/api/status/{download_id}',
                'note': 'Files will be automatically deleted after 1 hour'
            }), 202
        else:
            # تحميل متزامن
            download_video_thread(url, download_id, options)
            return jsonify(downloads_status[download_id]), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/playlist', methods=['POST'])
def download_playlist():
    """تحميل قائمة تشغيل - محدود للخطة المجانية"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format_type', 'best')
        max_downloads = min(data.get('max_downloads', 10), 10)  # حد أقصى 10 على الخطة المجانية
        
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
                cleanup_old_downloads()
                
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
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'download_id': download_id,
            'message': f'Playlist download started (max {max_downloads} videos)',
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
    """الحصول على جميع الصيغ المتاحة للفيديو"""
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
                filesize = f.get('filesize', 0)
                
                formats_list.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution', 'audio only'),
                    'fps': f.get('fps'),
                    'filesize': f.get('filesize'),
                    'filesize_mb': round(filesize / (1024 * 1024), 2) if filesize else None,
                    'within_limit': filesize < MAX_FILE_SIZE_MB * 1024 * 1024 if filesize else True,
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'format_note': f.get('format_note'),
                })
            
            return jsonify({
                'title': info.get('title'),
                'formats': formats_list,
                'max_file_size_mb': MAX_FILE_SIZE_MB
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 YouTube Downloader API (Render.com)")
    print("=" * 60)
    print(f"📁 Download Directory: {DOWNLOAD_DIR}")
    print(f"🌐 Server starting on 0.0.0.0:{PORT}")
    print(f"📊 Max file size: {MAX_FILE_SIZE_MB}MB")
    print("=" * 60)
    
    # تنظيف الملفات القديمة عند البدء
    cleanup_old_downloads()
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
