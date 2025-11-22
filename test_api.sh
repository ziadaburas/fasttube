#!/bin/bash

# اختبار YouTube Downloader API باستخدام cURL
# تأكد من تشغيل API أولاً: python youtube_downloader_api.py

API_URL="http://localhost:5000"
VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

echo "=================================="
echo "🎬 اختبار YouTube Downloader API"
echo "=================================="

# اختبار 1: فحص صحة API
echo -e "\n1️⃣ فحص صحة API..."
curl -s "${API_URL}/api/health" | python3 -m json.tool

# اختبار 2: الحصول على معلومات الفيديو
echo -e "\n\n2️⃣ الحصول على معلومات الفيديو..."
curl -s -X POST "${API_URL}/api/info" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${VIDEO_URL}\"}" | python3 -m json.tool | head -30

# اختبار 3: عرض الصيغ المتاحة
echo -e "\n\n3️⃣ عرض الصيغ المتاحة..."
curl -s -X POST "${API_URL}/api/formats" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${VIDEO_URL}\"}" | python3 -m json.tool | head -40

# اختبار 4: بدء تحميل فيديو (غير متزامن)
echo -e "\n\n4️⃣ بدء تحميل فيديو..."
DOWNLOAD_RESPONSE=$(curl -s -X POST "${API_URL}/api/download" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${VIDEO_URL}\", \"format_type\": \"best\", \"async\": true}")

echo "$DOWNLOAD_RESPONSE" | python3 -m json.tool

DOWNLOAD_ID=$(echo "$DOWNLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['download_id'])" 2>/dev/null)

if [ -n "$DOWNLOAD_ID" ]; then
    echo -e "\n5️⃣ متابعة حالة التحميل (ID: ${DOWNLOAD_ID})..."
    
    # متابعة الحالة لمدة 30 ثانية
    for i in {1..15}; do
        sleep 2
        STATUS=$(curl -s "${API_URL}/api/status/${DOWNLOAD_ID}")
        echo -e "\n⏱️ المحاولة ${i}:"
        echo "$STATUS" | python3 -m json.tool
        
        # التحقق من اكتمال التحميل
        if echo "$STATUS" | grep -q '"status": "completed"'; then
            echo -e "\n✅ اكتمل التحميل بنجاح!"
            break
        elif echo "$STATUS" | grep -q '"status": "error"'; then
            echo -e "\n❌ حدث خطأ في التحميل"
            break
        fi
    done
fi

# اختبار 6: عرض جميع التحميلات
echo -e "\n\n6️⃣ عرض جميع التحميلات..."
curl -s "${API_URL}/api/downloads" | python3 -m json.tool | head -50

echo -e "\n=================================="
echo "✅ انتهى الاختبار"
echo "=================================="
