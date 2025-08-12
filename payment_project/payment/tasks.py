# payment/tasks.py
from celery import shared_task
from .models import FileUpload, ActivityLog
from docx import Document
import os
from django.conf import settings

def count_words_in_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(content.split())

def count_words_in_docx(filepath):
    try:
        document = Document(filepath)
        return sum(len(para.text.split()) for para in document.paragraphs)
    except Exception as e:
        # Handle potential errors with docx files
        print(f"Error processing docx: {e}")
        return 0

@shared_task
def count_words_in_file(file_upload_id):
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        file_path = os.path.join(settings.MEDIA_ROOT, file_upload.file.name)

        word_count = 0
        if file_path.endswith('.txt'):
            word_count = count_words_in_txt(file_path)
        elif file_path.endswith('.docx'):
            word_count = count_words_in_docx(file_path)

        file_upload.word_count = word_count
        file_upload.status = 'completed'
        file_upload.save()

        ActivityLog.objects.create(
            user=file_upload.user,
            action='File Processed',
            metadata={'file_id': file_upload.id, 'word_count': word_count}
        )
    except FileUpload.DoesNotExist:
        # Handle case where file upload object is not found
        pass
    except Exception as e:
        # Log other exceptions
        file_upload = FileUpload.objects.get(id=file_upload_id)
        file_upload.status = 'failed'
        file_upload.save()
        ActivityLog.objects.create(
            user=file_upload.user,
            action='File Processing Failed',
            metadata={'file_id': file_upload.id, 'error': str(e)}
        )