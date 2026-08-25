import secrets

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database import SessionLocal


MAX_ATTEMPTS = 3

VALID_STATUSES = (
    "Pending",
    "Confirmed",
    "Declined",
    "Reschedule Requested"
)


def select_all_responses():

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT
                    ir.response_id,
                    c.candidate_id,
                    c.first_name,
                    c.last_name,
                    c.email,
                    c.phone,
                    c.assigned_hr,
                    c.interview_type,
                    c.interview_level,
                    c.scheduled_datetime,
                    ir.status,
                    ir.reply_message,
                    ir.responded_at,
                    ir.attempts
                FROM interview_responses ir
                INNER JOIN candidates c
                    ON ir.candidate_id = c.candidate_id
                ORDER BY ir.response_id
            """)
        )

        return result.fetchall()

    except SQLAlchemyError:

        raise ValueError(
            "Unable to retrieve interview responses."
        )

    finally:

        db.close()


def select_response_status_summary():

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT
                    status,
                    COUNT(*) AS status_count
                FROM interview_responses
                GROUP BY status
            """)
        ).fetchall()

        summary = {
            "Pending": 0,
            "Confirmed": 0,
            "Declined": 0,
            "Reschedule Requested": 0,
        }

        for row in result:
            summary[row[0]] = row[1]

        return summary

    except SQLAlchemyError:

        raise ValueError(
            "Unable to retrieve response status summary."
        )

    finally:

        db.close()


def insert_interview_response(candidate_id):

    db = SessionLocal()

    try:

        existing = db.execute(
            text("""
                SELECT
                    response_id,
                    response_token
                FROM interview_responses
                WHERE candidate_id = :candidate_id
                LIMIT 1
            """),
            {
                "candidate_id": candidate_id
            }
        ).fetchone()

        if existing is not None:

            return {
                "response_id": existing[0],
                "response_token": existing[1],
            }

        response_token = secrets.token_urlsafe(32)

        result = db.execute(
            text("""
                INSERT INTO interview_responses(
                    candidate_id,
                    status,
                    reply_message,
                    sent_at,
                    responded_at,
                    response_token,
                    attempts,
                    notification_queue_date
                )
                VALUES(
                    :candidate_id,
                    'Pending',
                    NULL,
                    NULL,
                    NULL,
                    :response_token,
                    0,
                    CASE
                        WHEN TIME(NOW()) < '09:00:00'
                        THEN CURDATE()
                        ELSE DATE_ADD(CURDATE(), INTERVAL 1 DAY)
                    END
                )
            """),
            {
                "candidate_id": candidate_id,
                "response_token": response_token,
            }
        )

        db.commit()

        return {
            "response_id": result.lastrowid,
            "response_token": response_token,
        }

    except IntegrityError:

        db.rollback()

        raise ValueError(
            "Unable to create interview response record."
        )

    except SQLAlchemyError:

        db.rollback()

        raise ValueError(
            "Unable to connect to the database.\nPlease try again."
        )

    finally:

        db.close()
        
def select_pending_notification_candidates():

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT
                    c.*,
                    ir.response_id,
                    ir.status AS response_status,
                    ir.sent_at,
                    ir.response_token,
                    ir.attempts
                FROM interview_responses ir
                INNER JOIN candidates c
                    ON c.candidate_id = ir.candidate_id
                WHERE ir.status = 'Pending'
                  AND ir.sent_at IS NULL
                  AND ir.notification_processing_at IS NULL
                ORDER BY c.scheduled_datetime
            """)
        )

        return result.mappings().all()

    except SQLAlchemyError:

        raise ValueError(
            "Unable to retrieve pending notification candidates."
        )

    finally:

        db.close()
def select_recent_responses(limit=10):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT
                    ir.response_id,
                    c.first_name,
                    c.last_name,
                    ir.status,
                    c.scheduled_datetime,
                    ir.responded_at,
                    ir.attempts
                FROM interview_responses ir
                INNER JOIN candidates c
                    ON ir.candidate_id = c.candidate_id
                ORDER BY ir.response_id DESC
                LIMIT :limit
            """),
            {
                "limit": limit
            }
        )

        return result.fetchall()

    except SQLAlchemyError:

        raise ValueError(
            "Unable to retrieve recent interview responses."
        )

    finally:

        db.close()

def mark_notification_processing(response_id):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                UPDATE interview_responses
                SET notification_processing_at = NOW()
                WHERE response_id = :response_id
                  AND sent_at IS NULL
                  AND notification_processing_at IS NULL
            """),
            {
                "response_id": response_id
            }
        )

        db.commit()

        return result.rowcount == 1

    except SQLAlchemyError:

        db.rollback()

        raise ValueError(
            "Unable to mark notification as processing."
        )

    finally:

        db.close()
        
def mark_notification_sent(response_id):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                UPDATE interview_responses
                SET sent_at = NOW()
                WHERE response_id = :response_id
            """),
            {
                "response_id": response_id
            }
        )

        if result.rowcount == 0:

            raise ValueError(
                "Interview response not found."
            )

        db.commit()

        return True

    except SQLAlchemyError:

        db.rollback()

        raise ValueError(
            "Unable to update notification sent time."
        )

    finally:

        db.close()

def save_sent_email(response_id, subject, body):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                UPDATE interview_responses
                SET
                    email_subject = :subject,
                    email_body = :body
                WHERE response_id = :response_id
            """),
            {
                "response_id": response_id,
                "subject": subject,
                "body": body
            }
        )

        if result.rowcount == 0:
            raise ValueError(
                "Interview response not found."
            )

        db.commit()

        return True

    except SQLAlchemyError:

        db.rollback()

        raise ValueError(
            "Unable to save sent email."
        )

    finally:

        db.close()


def select_sent_email(response_id):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT
                    email_subject,
                    email_body
                FROM interview_responses
                WHERE response_id = :response_id
                  AND sent_at IS NOT NULL
            """),
            {
                "response_id": response_id
            }
        )

        email = result.fetchone()

        if email is None:
            return None

        return {
            "subject": email[0],
            "body": email[1]
        }

    except SQLAlchemyError:

        raise ValueError(
            "Unable to retrieve sent email."
        )

    finally:

        db.close()

def update_response_status(response_id, status):

    if status not in VALID_STATUSES:

        raise ValueError(
            "Please select a valid interview status."
        )

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                UPDATE interview_responses
                SET status = :status
                WHERE response_id = :response_id
            """),
            {
                "response_id": response_id,
                "status": status
            }
        )

        if result.rowcount == 0:

            raise ValueError(
                "Interview response not found."
            )

        db.commit()

        return True

    except SQLAlchemyError:

        db.rollback()

        raise ValueError(
            "Unable to update the interview status."
        )

    finally:

        db.close()


def select_response_by_id(response_id):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT *
                FROM interview_responses
                WHERE response_id = :response_id
            """),
            {
                "response_id": response_id
            }
        )

        response = result.fetchone()

        if response is None:

            raise ValueError(
                "Interview response not found."
            )

        return response

    except SQLAlchemyError:

        raise ValueError(
            "Unable to retrieve interview response."
        )

    finally:


        db.close()

def save_incoming_reply(candidate_id, reply_message):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE interview_responses
                SET
                    reply_message = :reply_message,
                    responded_at = NOW()
                WHERE candidate_id = :candidate_id
                  AND sent_at IS NOT NULL
            """),
            {
                "candidate_id": candidate_id,
                "reply_message": reply_message
            }
        )

        if result.rowcount == 0:
            raise ValueError(
                "No sent interview response found for this candidate."
            )

        db.commit()

        return True

    except SQLAlchemyError:
        db.rollback()

        raise ValueError(
            "Unable to save applicant reply."
        )

    finally:
        db.close()

def find_candidate_by_email(email_address):

    db = SessionLocal()

    try:

        result = db.execute(
            text("""
                SELECT
                    candidate_id
                FROM candidates
                WHERE LOWER(email) = LOWER(:email)
                LIMIT 1
            """),
            {
                "email": email_address.strip()
            }
        )

        candidate = result.fetchone()

        if candidate is None:
            return None

        return candidate[0]

    except SQLAlchemyError:

        raise ValueError(
            "Unable to find candidate by email."
        )

    finally:

        db.close()