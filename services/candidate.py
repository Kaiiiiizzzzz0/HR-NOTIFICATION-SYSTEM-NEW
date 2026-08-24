from .validation import validate_candidate_fields
from .candidate_repository import (
    delete_candidate as repo_delete_candidate,
    insert_candidate,
    select_all_candidates,
    select_candidate_by_id,
    select_dashboard_summary,
    select_hr_list,
    select_position_list,
    select_upcoming_interviews,
    update_candidate_record,
)
from .response_repository import insert_interview_response


def create_candidate(
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
):
    candidate_data = validate_candidate_fields(
        first_name,
        last_name,
        email,
        phone,
        assigned_hr,
        position_role,
        interview_type,
        interview_level,
        interview_duration,
        scheduled_datetime,
    )

    candidate_id = insert_candidate(candidate_data)

    try:
        if candidate_id:
            insert_interview_response(candidate_id)
    except Exception:
        pass

    return True


def get_all_candidates(
    interview_type="All",
    interview_level="All",
    assigned_hr="All",
    position_role="All",
    start_date="",
    end_date="",
    search_text=""
):
    return select_all_candidates(
        interview_type,
        interview_level,
        assigned_hr,
        position_role,
        start_date,
        end_date,
        search_text,
    )


def get_hr_list():
    return select_hr_list()


def get_position_list():
    return select_position_list()


def get_dashboard_summary():
    return select_dashboard_summary()


def get_upcoming_interviews(limit=10):
    return select_upcoming_interviews(limit)


def get_candidate_by_id(candidate_id):
    return select_candidate_by_id(candidate_id)


def update_candidate(
    candidate_id,
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
):
    candidate_data = validate_candidate_fields(
        first_name,
        last_name,
        email,
        phone,
        assigned_hr,
        position_role,
        interview_type,
        interview_level,
        interview_duration,
        scheduled_datetime,
    )

    return update_candidate_record(candidate_id, candidate_data)


def delete_candidate(candidate_id):
    return repo_delete_candidate(candidate_id)
