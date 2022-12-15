from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime
import calendar
from .models import CompanyAccount
from .email import send_review_email

logger = get_task_logger(__name__)


@shared_task()
def send_review_email_task():
    day = datetime.now().day
    mnth = calendar.month_name[datetime.now().month]
    chk = CompanyAccount.objects.filter(date__month = mnth)
    if chk:
        return "Payslip only generate once in a month"
    else:
        if day != 1:
            return "Payslip only generate on 1st day of everymonth"
        else:
            logger.info("Sent Payslip email")
            return send_review_email()
