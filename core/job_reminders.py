from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import ImportantJobReminder


NOTIFICATION_LEVELS = {
    "": 0,
    "normal": 1,
    "important": 2,
    "urgent": 3,
    "critical": 4,
    "overdue": 5,
}


def send_job_reminders(dry_run=False):

    recipients = getattr(
        settings,
        "JOB_REMINDER_EMAILS",
        [],
    )

    if not recipients and not dry_run:
        raise ValueError(
            "JOB_REMINDER_EMAILS is not configured."
        )

    job_ids = list(
        ImportantJobReminder.objects
        .filter(completed=False)
        .order_by("deadline", "id")
        .values_list("id", flat=True)
    )

    sent_count = 0

    for job_id in job_ids:

        with transaction.atomic():

            job = (
                ImportantJobReminder.objects
                .select_for_update()
                .select_related("customer")
                .filter(
                    pk=job_id,
                    completed=False,
                )
                .first()
            )

            if job is None:
                continue

            if not job.email_required:
                continue

            current_level = str(job.importance)

            previous_level = job.last_notification_level

            current_score = NOTIFICATION_LEVELS.get(
                current_level, 0
            )

            previous_score = NOTIFICATION_LEVELS.get(
                previous_level, 0
            )

            # Prevent duplicate notifications
            if current_score <= previous_score:
                continue

            subject = (
                f"[{current_level.upper()}] "
                f"Job Reminder - {job.customer}"
            )

            message = (
                "IMPORTANT JOB REMINDER\n\n"

                f"Customer: {job.customer}\n\n"

                f"Description:\n{job.description}\n\n"

                f"Deadline: "
                f"{job.deadline:%d/%m/%Y}\n"

                f"Procedure duration: "
                f"{job.procedure_days} days\n"

                f"Days remaining: "
                f"{job.days_remaining}\n"

                f"Recommended start: "
                f"{job.recommended_start_date:%d/%m/%Y}\n"

                f"Latest start: "
                f"{job.latest_start_date:%d/%m/%Y}\n"

                f"Spare days: "
                f"{job.spare_days}\n"

                f"Importance: "
                f"{current_level.upper()}\n\n"

                "Please review this important job."
            )

            if dry_run:
                print(subject)
                print(message)
                continue

            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )

            if result != 1:
                raise RuntimeError("Email was not sent.")

            job.last_notification_level = current_level
            job.last_notification_at = timezone.now()

            job.save(
                update_fields=[
                    "last_notification_level",
                    "last_notification_at",
                ]
            )

            sent_count += 1

            print(f"Email sent: {job}")

    print(f"Total emails sent: {sent_count}")

    return sent_count