# استخدام صورة Python الرسمية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DOWNLOAD_DIR=/app/downloads

# تثبيت ffmpeg والمتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الملفات
COPY youtube_downloader_api.py .

# إنشاء مجلد التحميلات
RUN mkdir -p /app/downloads

# فتح المنفذ
EXPOSE 5000

# تشغيل التطبيق
CMD ["python", "youtube_downloader_api.py"]
