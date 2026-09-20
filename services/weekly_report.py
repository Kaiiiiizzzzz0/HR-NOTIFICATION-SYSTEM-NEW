from datetime import datetime, timedelta

from sqlalchemy import text

from database import SessionLocal

from repositories.weekly_report_repository import (
    get_weekly_report_recipients
)

from services.email_creator.report_emailer import (
    send_report_email
)


def get_previous_week_summary():

    db = SessionLocal()

    try:

        today = datetime.now().date()

        current_monday = (
            today - timedelta(
                days=today.weekday()
            )
        )

        previous_monday = (
            current_monday - timedelta(days=7)
        )

        result = db.execute(
            text("""
                SELECT
                    COUNT(*) AS total,

                    COUNT(
                        CASE
                            WHEN ir.status = 'Confirmed'
                            THEN 1
                        END
                    ) AS confirmed,

                    COUNT(
                        CASE
                            WHEN ir.status = 'Declined'
                            THEN 1
                        END
                    ) AS declined,

                    COUNT(
                        CASE
                            WHEN ir.status = 'Pending'
                            THEN 1
                        END
                    ) AS pending,

                    COUNT(
                        CASE
                            WHEN ir.status = 'Reschedule Requested'
                            THEN 1
                        END
                    ) AS reschedule_requested

                FROM interview_responses ir

                INNER JOIN candidates c
                    ON ir.candidate_id = c.candidate_id

                WHERE c.scheduled_datetime >= :previous_monday
                AND c.scheduled_datetime < :current_monday
            """),
            {
                "previous_monday": previous_monday,
                "current_monday": current_monday
            }
        ).mappings().one()

        return {
            "total": result["total"],
            "confirmed": result["confirmed"],
            "declined": result["declined"],
            "pending": result["pending"],
            "reschedule_requested": result[
                "reschedule_requested"
            ],
            "start_date": previous_monday,
            "end_date": (
                current_monday - timedelta(days=1)
            )
        }

    finally:

        db.close()


def build_weekly_report():

    summary = get_previous_week_summary()

    subject = (
        f"Weekly Interview Report - "
        f"{summary['start_date']} to "
        f"{summary['end_date']}"
    )

    body = (
        "WEEKLY INTERVIEW REPORT\n\n"

        f"Reporting Period: "
        f"{summary['start_date']} to "
        f"{summary['end_date']}\n\n"

        f"Total Interviews: "
        f"{summary['total']}\n"

        f"Confirmed: "
        f"{summary['confirmed']}\n"

        f"Declined: "
        f"{summary['declined']}\n"

        f"Pending: "
        f"{summary['pending']}\n"

        f"Reschedule Requested: "
        f"{summary['reschedule_requested']}\n"
    )

    return subject, body


def send_weekly_report():

    recipients = get_weekly_report_recipients()

    if not recipients:

        return {
            "success": False,
            "message": (
                "No weekly report recipients configured."
            )
        }

    subject, body = build_weekly_report()

    results = []

    for recipient in recipients:

        result = send_report_email(
            recipient["email"],
            subject,
            body
        )

        results.append(result)

    failed = [
        result
        for result in results
        if not result.get("success")
    ]

    if failed:

        return {
            "success": False,
            "message": (
                f"Report processed with "
                f"{len(failed)} failure(s)."
            ),
            "results": results
        }

    return {
        "success": True,
        "recipients": len(results),
        "results": results
    }