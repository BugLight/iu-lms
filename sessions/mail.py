from contextlib import contextmanager
from smtplib import SMTP_SSL

from sessions.settings import settings


@contextmanager
def smtp_client() -> SMTP_SSL:
    smtp = SMTP_SSL(host=settings.SMTP_SERVER, port=settings.SMTP_PORT)
    smtp.login(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
    try:
        yield smtp
    finally:
        smtp.quit()
