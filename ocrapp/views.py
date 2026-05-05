import os
import datetime
from django.shortcuts import render
from django.conf import settings
from PIL import Image
import pytesseract
from docx import Document

def home(request):
    return render(request, 'ocrapp/home.html')

def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        print("✔ فایل دریافت شد:", image_file.name)

        # ساخت مسیر پوشه
        today = datetime.date.today()
        relative_folder = os.path.join(str(today.year), str(today.month), str(today.day))
        full_folder = os.path.join(settings.MEDIA_ROOT, relative_folder)
        os.makedirs(full_folder, exist_ok=True)

        # نام‌گذاری یکتا
        original_name = image_file.name.rsplit('.', 1)[0]
        extension = image_file.name.rsplit('.', 1)[-1]
        unique_name = f"{original_name}_{datetime.datetime.now().strftime('%H%M%S')}.{extension}"
        file_path = os.path.join(full_folder, unique_name)

        # ذخیره فایل تصویر
        with open(file_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # OCR
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='fas+eng')
            print("✔ متن استخراج‌شده:\n", text[:100], "...")
        except Exception as e:
            return render(request, 'ocrapp/result.html', {
                'text': f'❌ خطا در OCR: {str(e)}',
                'download_link': None
            })

        # ساخت فایل Word
        doc = Document()
        doc.add_paragraph(text)
        word_name = unique_name.rsplit('.', 1)[0] + '.docx'
        word_path = os.path.join(full_folder, word_name)
        doc.save(word_path)

        # آدرس برای لینک دانلود
        download_link = os.path.join(settings.MEDIA_URL, str(today.year), str(today.month), str(today.day), word_name)
        download_link = download_link.replace('\\', '/')

        return render(request, 'ocrapp/result.html', {
            'text': text,
            'download_link': download_link
        })

    return render(request, 'ocrapp/home.html')
