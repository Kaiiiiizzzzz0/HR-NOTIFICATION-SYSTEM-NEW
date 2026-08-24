from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal


VALID_STATUSES = {
    "Confirmed",
    "Declined",
    "Reschedule Requested",
}

MAX_ATTEMPTS = 3


def process_response(response_token, status):

    if not response_token:
        raise ValueError("Missing response token.")

    if status not in VALID_STATUSES:
        raise ValueError("Invalid response status.")

    db = SessionLocal()

    try:

        response = db.execute(
            text("""
                SELECT
                    response_id,
                    attempts
                FROM interview_responses
                WHERE response_token = :response_token
                LIMIT 1
            """),
            {
                "response_token": response_token
            }
        ).fetchone()

        if response is None:
            raise ValueError(
                "Invalid or expired response token."
            )

        response_id = response[0]
        attempts = response[1] or 0

        # Allow up to 3 responses.
        # The latest response becomes the current saved response.
        if attempts >= MAX_ATTEMPTS:
            raise ValueError(
                "Maximum response attempts reached."
            )

        new_attempts = attempts + 1

        db.execute(
            text("""
                UPDATE interview_responses
                SET
                    status = :status,
                    responded_at = NOW(),
                    attempts = :attempts
                WHERE response_id = :response_id
            """),
            {
                "status": status,
                "attempts": new_attempts,
                "response_id": response_id
            }
        )

        db.commit()

        return {
            "success": True,
            "response_id": response_id,
            "status": status,
            "attempts": new_attempts,
        }

    except ValueError:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise ValueError(
            "Unable to process the interview response."
        )

    finally:
        db.close()