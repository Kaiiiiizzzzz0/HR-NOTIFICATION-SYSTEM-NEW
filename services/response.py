from repositories.response_repository import (
    insert_interview_response,
    mark_notification_sent,
    select_all_responses,
    select_pending_notification_candidates,
    select_recent_responses,
    select_response_by_id,
    select_response_status_summary,
    update_response_status_by_token,
    update_response_status,
)


def get_all_responses():

    return select_all_responses()


def get_response_status_summary():

    return select_response_status_summary()


def create_interview_response(
    candidate_id
):

    return insert_interview_response(
        candidate_id
    )


def get_pending_notification_candidates():

    return select_pending_notification_candidates()


def get_recent_responses(
    limit=10
):

    return select_recent_responses(
        limit
    )


def mark_notification_sent(
    response_id
):

    return mark_notification_sent(
        response_id
    )


def update_response(
    response_id,
    status
):

    return update_response_status(
        response_id,
        status
    )


def confirm_interview(
    response_token
):

    return update_response_status_by_token(
        response_token,
        "Confirmed"
    )


def decline_interview(
    response_token
):

    return update_response_status_by_token(
        response_token,
        "Declined"
    )


def get_response_by_id(
    response_id
):

    return select_response_by_id(
        response_id
    )