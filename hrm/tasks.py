from celery import shared_task
from celery.utils.log import get_task_logger

from .email import send_review_email

logger = get_task_logger(__name__)


@shared_task()
def send_review_email_task():
    logger.info("Sent Payslip email")
    return send_review_email()
