"""
أمثلة على استخدام YouTube Downloader API
"""

import requests
import time
import json

# عنوان API
API_BASE_URL = "http://localhost:5000"


def get_video_info(url):
    """الحصول على معلومات الفيديو"""
    print(f"\n📋 الحصول على معلومات الفيديو...")
    response = requests.post(
        f"{API_BASE_URL}/api/info",
        json={"url": url}
    )
    
    if response.status_code == 200:
        info = response.json()
        print(f"✅ العنوان: {info['title']}")
        print(f"⏱️ المدة: {info['duration']} ثانية")
        print(f"👁️ المشاهدات: {info['views']:,}")
        print(f"📺 المنشئ: {info['uploader']}")
        print(f"🔞 محمي عمرياً: {'نعم' if info['age_limited'] else 'لا'}")
        print(f"🔴 بث مباشر: {'نعم' if info['is_live'] else 'لا'}")
        return info
    else:
        print(f"❌ خطأ: {response.json()}")
        return None


def download_video_best_quality(url):
    """تحميل فيديو بأفضل جودة"""
    print(f"\n⬇️ تحميل الفيديو بأفضل جودة...")
    response = requests.post(
        f"{API_BASE_URL}/api/download",
        json={
            "url": url,
            "format_type": "best",
            "async": True
        }
    )
    
    if response.status_code == 202:
        result = response.json()
        download_id = result['download_id']
        print(f"✅ بدأ التحميل - ID: {download_id}")
        
        # متابعة حالة التحميل
        monitor_download(download_id)
        return download_id
    else:
        print(f"❌ خطأ: {response.json()}")
        return None


def download_audio_only(url):
    """تحميل الصوت فقط (MP3)"""
    print(f"\n🎵 تحميل الصوت فقط...")
    response = requests.post(
        f"{API_BASE_URL}/api/download",
        json={
            "url": url,
            "format_type": "audio",
            "async": True
        }
    )
    
    if response.status_code == 202:
        result = response.json()
        download_id = result['download_id']
        print(f"✅ بدأ التحميل - ID: {download_id}")
        monitor_download(download_id)
        return download_id
    else:
        print(f"❌ خطأ: {response.json()}")
        return None


def download_specific_quality(url, quality="720"):
    """تحميل بجودة محددة"""
    print(f"\n📹 تحميل بجودة {quality}p...")
    response = requests.post(
        f"{API_BASE_URL}/api/download",
        json={
            "url": url,
            "format_type": "specific_quality",
            "quality": quality,
            "async": True
        }
    )
    
    if response.status_code == 202:
        result = response.json()
        download_id = result['download_id']
        print(f"✅ بدأ التحميل - ID: {download_id}")
        monitor_download(download_id)
        return download_id
    else:
        print(f"❌ خطأ: {response.json()}")
        return None


def download_playlist(url, max_videos=10):
    """تحميل قائمة تشغيل"""
    print(f"\n📑 تحميل قائمة التشغيل (حد أقصى {max_videos} فيديو)...")
    response = requests.post(
        f"{API_BASE_URL}/api/download/playlist",
        json={
            "url": url,
            "format_type": "best",
            "max_downloads": max_videos
        }
    )
    
    if response.status_code == 202:
        result = response.json()
        download_id = result['download_id']
        print(f"✅ بدأ تحميل القائمة - ID: {download_id}")
        monitor_download(download_id)
        return download_id
    else:
        print(f"❌ خطأ: {response.json()}")
        return None


def get_available_formats(url):
    """عرض جميع الصيغ المتاحة"""
    print(f"\n📊 الحصول على الصيغ المتاحة...")
    response = requests.post(
        f"{API_BASE_URL}/api/formats",
        json={"url": url}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ الفيديو: {data['title']}")
        print(f"\n📋 الصيغ المتاحة ({len(data['formats'])} صيغة):")
        
        for idx, fmt in enumerate(data['formats'][:10], 1):  # عرض أول 10 صيغ
            print(f"  {idx}. ID: {fmt['format_id']} | "
                  f"دقة: {fmt['resolution']} | "
                  f"نوع: {fmt['ext']} | "
                  f"حجم: {fmt.get('filesize', 'غير معروف')}")
        
        return data['formats']
    else:
        print(f"❌ خطأ: {response.json()}")
        return None


def monitor_download(download_id):
    """متابعة حالة التحميل"""
    print(f"\n🔄 متابعة التحميل...")
    
    while True:
        response = requests.get(f"{API_BASE_URL}/api/status/{download_id}")
        
        if response.status_code == 200:
            status = response.json()
            
            if status['status'] == 'completed':
                print(f"\n✅ اكتمل التحميل!")
                print(f"📁 الملف: {status.get('filename', 'غير معروف')}")
                break
            elif status['status'] == 'error':
                print(f"\n❌ خطأ في التحميل: {status.get('error')}")
                break
            else:
                print(f"⏳ التقدم: {status['progress']} | "
                      f"السرعة: {status.get('speed', 'N/A')} | "
                      f"الوقت المتبقي: {status.get('eta', 'N/A')}", 
                      end='\r')
        
        time.sleep(2)


def check_api_health():
    """فحص صحة API"""
    print("\n🏥 فحص صحة API...")
    response = requests.get(f"{API_BASE_URL}/api/health")
    
    if response.status_code == 200:
        health = response.json()
        print(f"✅ الحالة: {health['status']}")
        print(f"📊 التحميلات النشطة: {health['active_downloads']}")
        return True
    else:
        print("❌ API غير متاح")
        return False


# أمثلة على الاستخدام
if __name__ == "__main__":
    print("=" * 60)
    print("🎬 أمثلة على استخدام YouTube Downloader API")
    print("=" * 60)
    
    # تأكد من تشغيل API أولاً
    if not check_api_health():
        print("\n⚠️ يرجى تشغيل API أولاً بالأمر:")
        print("   python youtube_downloader_api.py")
        exit(1)
    
    # مثال على رابط فيديو
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print("\n" + "=" * 60)
    print("اختر العملية:")
    print("1. الحصول على معلومات الفيديو")
    print("2. تحميل بأفضل جودة")
    print("3. تحميل الصوت فقط")
    print("4. تحميل بجودة محددة (720p)")
    print("5. عرض جميع الصيغ المتاحة")
    print("6. تحميل قائمة تشغيل")
    print("=" * 60)
    
    choice = input("\nأدخل رقم العملية (أو اضغط Enter للخروج): ")
    
    if not choice:
        print("👋 إلى اللقاء!")
        exit(0)
    
    if choice not in ['6']:
        video_url = input(f"أدخل رابط الفيديو (أو اضغط Enter لاستخدام المثال): ").strip()
        if not video_url:
            video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    if choice == '1':
        get_video_info(video_url)
    elif choice == '2':
        download_video_best_quality(video_url)
    elif choice == '3':
        download_audio_only(video_url)
    elif choice == '4':
        download_specific_quality(video_url, "720")
    elif choice == '5':
        get_available_formats(video_url)
    elif choice == '6':
        playlist_url = input("أدخل رابط قائمة التشغيل: ").strip()
        if playlist_url:
            download_playlist(playlist_url, max_videos=5)
        else:
            print("❌ رابط غير صحيح")
    else:
        print("❌ خيار غير صحيح")
    
    print("\n" + "=" * 60)
    print("✅ انتهت العملية")
    print("=" * 60)
