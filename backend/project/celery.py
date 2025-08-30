from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(name="project.debug_task", bind=True)
def debug_task(self):
    print(f"Hello World | {self.request!r}")
    return "Debug task executed successfully"

@app.task(name="project.send_email_task", bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, subject, message, recipient_list, email_from=None):
    """
    Envia e-mail de forma assíncrona.
    - recipient_list: lista de e-mails
    - email_from: opcional; usa DEFAULT_FROM_EMAIL se não informado
    """
    try:
        from_email = email_from or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@hotel.local")
        
        print(f"[send_email_task] Attempting to send email:")
        print(f"  Subject: {subject}")
        print(f"  From: {from_email}")
        print(f"  To: {recipient_list}")
        
        sent = send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        
        print(f"[send_email_task] Email sent successfully to {recipient_list}")
        return bool(sent)
        
    except Exception as e:
        print(f"[send_email_task] Error sending email: {e}")
        print(f"[send_email_task] Retry attempt {self.request.retries + 1}/{self.max_retries}")
        
        if self.request.retries < self.max_retries:
            # Re-tenta automaticamente
            raise self.retry(exc=e)
        else:
            # Esgotou as tentativas - log do erro final
            print(f"[send_email_task] Max retries exceeded. Email failed permanently.")
            return False
