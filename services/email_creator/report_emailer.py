import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM,
    SMTP_USE_TLS,
)


def send_report_email(
    recipient,
    subject,
    body
):

    if not recipient or not isinstance(recipient, str):

        return {
            "success": False,
            "error": "Missing or invalid recipient email address.",
            "recipient": recipient
        }

    if not SMTP_HOST or not SMTP_PORT:

        return {
            "success": False,
            "error": "SMTP host or port is not configured.",
            "recipient": recipient
        }

    if not SMTP_FROM:

        return {
            "success": False,
            "error": "SMTP_FROM is not configured.",
            "recipient": recipient
        }

    if bool(SMTP_USER) ^ bool(SMTP_PASSWORD):

        return {
            "success": False,
            "error": (
                "Both SMTP_USER and SMTP_PASSWORD must be configured "
                "for authenticated SMTP."
            ),
            "recipient": recipient
        }

    message = MIMEMultipart()

    message["From"] = SMTP_FROM
    message["To"] = recipient
    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain"
        )
    )

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

        return {
            "success": True,
            "recipient": recipient,
            "subject": subject
        }

    except smtplib.SMTPException as smtp_error:

        return {
            "success": False,
            "error": str(smtp_error),
            "recipient": recipient
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc),
            "recipient": recipient
        }