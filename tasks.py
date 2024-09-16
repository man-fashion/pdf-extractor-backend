from pdf_parser import process_pdf_data
from celery_config import make_celery
from app import app

celery = make_celery(app)

@celery.task(name='tasks.process_pdf')
def process_pdf(pdf_path):
    process_pdf_data(pdf_path)
    return process_pdf.request.id
    

