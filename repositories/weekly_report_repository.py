from sqlalchemy import text
from database import SessionLocal


def get_weekly_report_recipients():
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT recipient_id, email
                FROM weekly_report_recipients
                ORDER BY recipient_id
            """)
        )

        return result.mappings().all()

    finally:
        db.close()


def add_weekly_report_recipient(email):
    db = SessionLocal()

    try:
        db.execute(
            text("""
                INSERT INTO weekly_report_recipients (email)
                VALUES (:email)
            """),
            {"email": email}
        )

        db.commit()

    finally:
        db.close()


def delete_weekly_report_recipient(recipient_id):
    db = SessionLocal()

    try:
        db.execute(
            text("""
                DELETE FROM weekly_report_recipients
                WHERE recipient_id = :recipient_id
            """),
            {"recipient_id": recipient_id}
        )

        db.commit()

    finally:
        db.close()