import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from services.response_repository import save_sent_email

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM,
    SMTP_USE_TLS,
)
from .message_templates import build_email_content


def build_email_message(candidate):
    # Use edited email content if it was supplied.
    # Otherwise generate the normal email from the template.
    if candidate.get("edited_subject") is not None:
        subject = candidate.get("edited_subject")
        body = candidate.get("edited_body")

    else:
        subject, body = build_email_content(candidate)

    message = MIMEMultipart()
    message["From"] = SMTP_FROM
    message["To"] = candidate.get("email")
    message["Subject"] = subject

    message.attach(MIMEText(body, "html"))

    return message, subject, body


def send_email(candidate):
    recipient = candidate.get("email")

    if not recipient or not isinstance(recipient, str):
        return {
            "success": False,
            "error": "Missing or invalid recipient email address.",
            "candidate_id": candidate.get("candidate_id")
        }

    if not SMTP_HOST or not SMTP_PORT:
        return {
            "success": False,
            "error": "SMTP host or port is not configured.",
            "candidate_id": candidate.get("candidate_id")
        }

    if not SMTP_FROM:
        return {
            "success": False,
            "error": "SMTP_FROM is not configured.",
            "candidate_id": candidate.get("candidate_id")
        }

    if bool(SMTP_USER) ^ bool(SMTP_PASSWORD):
        return {
            "success": False,
            "error": (
                "Both SMTP_USER and SMTP_PASSWORD must be configured "
                "for authenticated SMTP."
            ),
            "candidate_id": candidate.get("candidate_id")
        }

    message, subject, body = build_email_message(candidate)

    try:
        with smtplib.SMTP(
            host=SMTP_HOST,
            port=SMTP_PORT,
            timeout=30
        ) as smtp:

            if SMTP_USE_TLS:
                smtp.starttls()

            if SMTP_USER and SMTP_PASSWORD:
                smtp.login(
                    SMTP_USER,
                    SMTP_PASSWORD
                )

            smtp.sendmail(
                SMTP_FROM,
                [recipient],
                message.as_string()
            )

            response_id = candidate.get("response_id")

            if response_id is not None:
                save_sent_email(
                    response_id,
                    subject,
                    body
                )

        return {
            "success": True,
            "candidate_id": candidate.get("candidate_id"),
            "subject": subject,
            "recipient": recipient,
            "body": body
        }

    except smtplib.SMTPException as smtp_error:
        return {
            "success": False,
            "error": str(smtp_error),
            "candidate_id": candidate.get("candidate_id")
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "candidate_id": candidate.get("candidate_id")
        }