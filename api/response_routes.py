from fastapi import APIRouter
from sqlalchemy import text

from database import SessionLocal


router = APIRouter()


@router.get("/response/{token}/yes")
def confirm_interview(token: str):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE interview_responses
                SET
                    status = 'Confirmed',
                    responded_at = NOW()
                WHERE response_token = :token
                  AND status = 'Pending'
            """),
            {"token": token}
        )

        db.commit()

        if result.rowcount == 0:
            return {"message": "Invalid or already used response."}

        return {"message": "Interview confirmed successfully."}

    finally:
        db.close()


@router.get("/response/{token}/no")
def decline_interview(token: str):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                UPDATE interview_responses
                SET
                    status = 'Declined',
                    responded_at = NOW()
                WHERE response_token = :token
                  AND status = 'Pending'
            """),
            {"token": token}
        )

        db.commit()

        if result.rowcount == 0:
            return {"message": "Invalid or already used response."}

        return {
            "message": "Interview declined. Please reply to the email with your reason."
        }

    finally:
        db.close()