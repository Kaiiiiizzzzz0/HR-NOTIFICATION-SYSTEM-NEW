import imaplib
import email
import os
import re
from datetime import datetime, timedelta

from email.header import decode_header
from email.utils import parseaddr

from repositories.response_repository import (
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

    result = []

    for part, encoding in decode_header(value):

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

    plain_text = ""
    html_text = ""

    if message.is_multipart():

        for part in message.walk():

            content_type = part.get_content_type()
            disposition = str(
                part.get("Content-Disposition", "")
            ).lower()

            if "attachment" in disposition:
                continue

            payload = part.get_payload(decode=True)

            if not payload:
                continue

            charset = (
                part.get_content_charset()
                or "utf-8"
            )

            text = payload.decode(
                charset,
                errors="replace"
            ).strip()

            if content_type == "text/plain" and not plain_text:
                plain_text = text

            elif content_type == "text/html" and not html_text:
                html_text = text

    else:

        payload = message.get_payload(decode=True)

        if payload:

            charset = (
                message.get_content_charset()
                or "utf-8"
            )

            text = payload.decode(
                charset,
                errors="replace"
            ).strip()

            if message.get_content_type() == "text/plain":
                plain_text = text

            elif message.get_content_type() == "text/html":
                html_text = text

    return plain_text or html_text


def extract_new_reply(body):

    if not body:
        return ""

    body = body.strip()

    # Remove common quoted-reply sections.
    patterns = [
        r"\nOn .+?wrote:\s*\n",
        r"\nFrom:\s*.+?\nSent:\s*.+?\n",
        r"\n-{2,}\s*Original Message\s*-{2,}",
        r"\n>+"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            body,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:
            body = body[:match.start()].strip()

    return body


def find_candidate_by_email(sender_email):

    return find_candidate_id_by_email(
        sender_email.strip()
    )


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

        status, _ = mailbox.select("INBOX")

        if status != "OK":
            raise RuntimeError(
                "Unable to open INBOX."
            )

        since_date = (
            datetime.now() - timedelta(days=2)
        ).strftime("%d-%b-%Y")

        # Only check recent emails.
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

                if status != "OK" or not message_data:
                    continue

                raw_email = message_data[0][1]

                message = email.message_from_bytes(
                    raw_email
                )

                _, sender_email = parseaddr(
                    message.get("From", "")
                )

                sender_email = sender_email.strip()

                print(
                    f"Incoming email from: {sender_email}"
                )

                if not sender_email:
                    print("Skipped: no sender email.")
                    continue

                candidate_id = find_candidate_by_email(
                    sender_email
                )

                if candidate_id is None:

                    print(
                        f"Skipped: no candidate found "
                        f"for {sender_email}"
                    )

                    continue

                body = get_email_body(message)

                reply_message = extract_new_reply(body)

                if not reply_message:

                    print(
                        f"Skipped: empty reply from "
                        f"{sender_email}"
                    )

                    continue

                print(
                    f"Saving reply for candidate "
                    f"{candidate_id}: {reply_message}"
                )

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

                # Mark as read only after successful save.
                mailbox.store(
                    message_id,
                    "+FLAGS",
                    "\\Seen"
                )

            except Exception as error:

                print(
                    f"Failed to process email "
                    f"{message_id}: {error}"
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