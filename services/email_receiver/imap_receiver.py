import imaplib
import email
import os
from datetime import datetime, timedelta

from email.header import decode_header
from email.utils import parseaddr

from services.response_repository import (
    find_candidate_by_email as find_candidate_id_by_email,
    save_incoming_reply
)


IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")


def decode_text(value):
    if not value:
        return ""

    decoded = decode_header(value)

    result = []

    for part, encoding in decoded:

        if isinstance(part, bytes):

            result.append(
                part.decode(
                    encoding or "utf-8",
                    errors="replace"
                )
            )

        else:
            result.append(part)

    return "".join(result)

def get_email_body(message):

    body = ""

    if message.is_multipart():

        for part in message.walk():

            content_type = part.get_content_type()

            content_disposition = str(
                part.get("Content-Disposition", "")
            )

            if (
                content_type == "text/plain"
                and "attachment" not in content_disposition
            ):

                payload = part.get_payload(
                    decode=True
                )

                if payload:

                    body = payload.decode(
                        part.get_content_charset()
                        or "utf-8",
                        errors="replace"
                    )

                    break

    else:

        payload = message.get_payload(
            decode=True
        )

        if payload:

            body = payload.decode(
                message.get_content_charset()
                or "utf-8",
                errors="replace"
            )

    body = body.strip()

    if not body:
        return "No response provided."

    return body
def find_candidate_by_email(sender_email):

    candidate_id = find_candidate_id_by_email(
        sender_email
    )

    return candidate_id


def check_inbox():

    if not IMAP_HOST:
        raise ValueError(
            "IMAP_HOST is not configured."
        )

    if not IMAP_USER:
        raise ValueError(
            "IMAP_USER is not configured."
        )

    if not IMAP_PASSWORD:
        raise ValueError(
            "IMAP_PASSWORD is not configured."
        )

    mailbox = imaplib.IMAP4_SSL(
        IMAP_HOST,
        IMAP_PORT
    )

    try:

        mailbox.login(
            IMAP_USER,
            IMAP_PASSWORD
        )

        mailbox.select("INBOX")

        # Only check recent emails.
        since_date = (
            datetime.now() - timedelta(days=2)
        ).strftime("%d-%b-%Y")

        status, data = mailbox.search(
            None,
            "SINCE",
            since_date
        )

        if status != "OK":
            return []

        message_ids = data[0].split()

        processed = []

        for message_id in message_ids:

            try:

                status, message_data = mailbox.fetch(
                    message_id,
                    "(RFC822)"
                )

                if status != "OK":
                    continue

                if not message_data:
                    continue

                raw_email = message_data[0][1]

                message = email.message_from_bytes(
                    raw_email
                )

                sender_name, sender_email = parseaddr(
                    message.get("From", "")
                )

                sender_email = sender_email.strip()

                if not sender_email:
                    continue

                # Check whether the sender is an applicant.
                candidate_id = find_candidate_by_email(
                    sender_email
                )

                # Ignore emails from Facebook,
                # Microsoft, newsletters, etc.
                if candidate_id is None:
                    continue

                reply_message = get_email_body(
                    message
                )

                if not reply_message:
                    continue

                # Save the applicant's actual email reply.
                save_incoming_reply(
                    candidate_id,
                    reply_message
                )

                processed.append({
                    "candidate_id": candidate_id,
                    "sender": sender_email,
                    "subject": decode_text(
                        message.get("Subject")
                    ),
                    "reply": reply_message
                })

                # Only mark as read AFTER successfully
                # saving the applicant's reply.
                mailbox.store(
                    message_id,
                    "+FLAGS",
                    "\\Seen"
                )

            except Exception as error:

                print(
                    f"Failed to process email {message_id}: {error}"
                )

                continue

        return processed

    finally:

        try:
            mailbox.close()
        except Exception:
            pass

        try:
            mailbox.logout()
        except Exception:
            pass