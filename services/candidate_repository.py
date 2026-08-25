from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import SessionLocal


def insert_candidate(candidate_data):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                INSERT INTO candidates(
                    first_name,
                    last_name,
                    email,
                    phone,
                    assigned_hr,
                    position_role,
                    interview_type,
                    interview_level,
                    interview_duration,
                    scheduled_datetime
                )
                VALUES(
                    :first_name,
                    :last_name,
                    :email,
                    :phone,
                    :assigned_hr,
                    :position_role,
                    :interview_type,
                    :interview_level,
                    :interview_duration,
                    :scheduled_datetime
                )
            """),
            candidate_data
        )

        db.commit()
        return result.lastrowid

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to save the candidate because the data violates a database rule."
        )

    except SQLAlchemyError:
        db.rollback()
        raise ValueError(
            "Unable to connect to the database.\nPlease try again."
        )

    finally:
        db.close()


def update_candidate_record(candidate_id, candidate_data):
    db = SessionLocal()

    params = candidate_data.copy()
    params["candidate_id"] = candidate_id

    try:
        result = db.execute(
            text("""
                UPDATE candidates
                SET
                    first_name = :first_name,
                    last_name = :last_name,
                    email = :email,
                    phone = :phone,
                    assigned_hr = :assigned_hr,
                    position_role = :position_role,
                    interview_type = :interview_type,
                    interview_level = :interview_level,
                    interview_duration = :interview_duration,
                    scheduled_datetime = :scheduled_datetime
                WHERE candidate_id = :candidate_id
            """),
            params
        )

        if result.rowcount == 0:
            raise ValueError("Candidate not found.")

        db.commit()
        return True

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to update the candidate because the data violates a database rule."
        )

    except SQLAlchemyError:
        db.rollback()
        raise ValueError(
            "Unable to connect to the database.\nPlease try again."
        )

    finally:
        db.close()


def delete_candidate(candidate_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                DELETE FROM candidates
                WHERE candidate_id = :candidate_id
            """),
            {"candidate_id": candidate_id}
        )

        if result.rowcount == 0:
            raise ValueError("Candidate not found.")

        db.commit()
        return True

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to delete the candidate because it is referenced by other records."
        )

    except SQLAlchemyError:
        db.rollback()
        raise ValueError(
            "Unable to connect to the database.\nPlease try again."
        )

    finally:
        db.close()


def select_all_candidates(
    interview_type="All",
    interview_level="All",
    assigned_hr="All",
    position_role="All",
    start_date="",
    end_date="",
    search_text=""
):
    db = SessionLocal()

    try:
        params = {}
        where = []

        if interview_type != "All":
            where.append("interview_type = :interview_type")
            params["interview_type"] = interview_type

        if interview_level != "All":
            where.append("interview_level = :interview_level")
            params["interview_level"] = interview_level

        if assigned_hr != "All":
            where.append("assigned_hr = :assigned_hr")
            params["assigned_hr"] = assigned_hr

        if position_role != "All":
            where.append("position_role = :position_role")
            params["position_role"] = position_role

        if start_date:
            where.append("DATE(scheduled_datetime) >= :start_date")
            params["start_date"] = start_date

        if end_date:
            where.append("DATE(scheduled_datetime) <= :end_date")
            params["end_date"] = end_date

        if search_text.strip():
            params["q"] = f"%{search_text}%"
            where.append("""
                (
                    first_name LIKE :q
                    OR last_name LIKE :q
                    OR email LIKE :q
                    OR phone LIKE :q
                )
            """)

        where_sql = ""
        if where:
            where_sql = "WHERE " + " AND ".join(where)

        sql = f"""
            SELECT
                c.candidate_id,
                c.first_name,
                c.last_name,
                c.email,
                c.phone,
                c.assigned_hr,
                c.position_role,
                c.interview_type,
                c.interview_level,
                c.interview_duration,
                c.scheduled_datetime,
                ir.response_id,
                ir.status AS response_status,
                ir.sent_at AS response_sent_at
            FROM candidates c
            LEFT JOIN interview_responses ir
                ON c.candidate_id = ir.candidate_id
            {where_sql}
            ORDER BY c.candidate_id
        """

        result = db.execute(text(sql), params)
        return result.fetchall()

    except SQLAlchemyError as e:
        raise ValueError(
            "Unable to retrieve candidates from the database.\nPlease try again."
        )

    finally:
        db.close()


def select_hr_list():
    db = SessionLocal()

    try:
        result = db.execute(text("""
            SELECT DISTINCT assigned_hr
            FROM candidates
            ORDER BY assigned_hr
        """))

        return [row[0] for row in result.fetchall()]

    finally:
        db.close()


def select_position_list():
    db = SessionLocal()

    try:
        result = db.execute(text("""
            SELECT DISTINCT position_role
            FROM candidates
            ORDER BY position_role
        """))

        return [row[0] for row in result.fetchall()]

    finally:
        db.close()


def select_dashboard_summary():
    db = SessionLocal()

    try:
        summary = db.execute(
            text("""
                SELECT
                    COUNT(*) AS total_candidates,
                    COUNT(CASE WHEN interview_type = 'VIRTUAL' THEN 1 END) AS virtual_count,
                    COUNT(CASE WHEN interview_type = 'OVER-THE-PHONE' THEN 1 END) AS phone_count,
                    COUNT(CASE WHEN interview_type = 'ONSITE' THEN 1 END) AS onsite_count
                FROM candidates
            """)
        ).mappings().one()

        upcoming_today = db.execute(
            text("""
                SELECT COUNT(*)
                FROM candidates
                WHERE scheduled_datetime BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 DAY)
            """
        )).scalar_one()

        upcoming_week = db.execute(
            text("""
                SELECT COUNT(*)
                FROM candidates
                WHERE scheduled_datetime BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
            """
        )).scalar_one()

        return {
            "total_candidates": summary["total_candidates"],
            "virtual_count": summary["virtual_count"],
            "phone_count": summary["phone_count"],
            "onsite_count": summary["onsite_count"],
            "upcoming_today": upcoming_today,
            "upcoming_week": upcoming_week,
        }

    except SQLAlchemyError:
        raise ValueError("Unable to retrieve dashboard metrics.")

    finally:
        db.close()


def select_upcoming_interviews(limit=10):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT
                    candidate_id,
                    first_name,
                    last_name,
                    email,
                    assigned_hr,
                    position_role,
                    interview_type,
                    scheduled_datetime
                FROM candidates
                WHERE scheduled_datetime >= NOW()
                ORDER BY scheduled_datetime
                LIMIT :limit
            """),
            {"limit": limit}
        )

        return result.fetchall()

    except SQLAlchemyError:
        raise ValueError("Unable to retrieve upcoming interviews.")

    finally:
        db.close()


def select_candidate_by_id(candidate_id):
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM candidates
                WHERE candidate_id = :candidate_id
            """),
            {"candidate_id": candidate_id}
        )

        candidate = result.fetchone()
        if candidate is None:
            raise ValueError("Candidate not found.")

        return candidate

    except SQLAlchemyError:
        raise ValueError("Unable to retrieve candidate.")

    finally:
        db.close()
