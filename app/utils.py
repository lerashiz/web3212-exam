import os
import hashlib
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_disposal_pdf(filename, equipment_name, reason, path='static/disposals/'):
    os.makedirs(path, exist_ok=True)
    c = canvas.Canvas(os.path.join(path, filename))
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, f"Акт списания оборудования")
    c.drawString(100, 770, f"Наименование: {equipment_name}")
    c.drawString(100, 740, f"Причина: {reason}")
    c.drawString(100, 710, f"Дата: {datetime.today().strftime('%d.%m.%Y')}")
    c.save()

def generate_md5(file_data):
    return hashlib.md5(file_data).hexdigest()


def save_file_with_hash(file_data, original_filename, folder='static/uploads/'):
    os.makedirs(folder, exist_ok=True)
    hash_value = generate_md5(file_data)
    extension = os.path.splitext(original_filename)[1].lower()
    filename = f"{hash_value}{extension}"
    path = os.path.join(folder, filename)

    # сохранить, если файл ещё не существует
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(file_data)

    mime_type = 'application/pdf' if extension == '.pdf' else 'image/' + extension.strip('.')
    return filename, mime_type, hash_value