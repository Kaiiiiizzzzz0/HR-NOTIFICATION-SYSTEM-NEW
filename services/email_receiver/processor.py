
from repositories.response_repository import (
    update_response_status_by_token,
    select_response_by_id
)


VALID_STATUSES = {
    "Confirmed",
    "Declined",
    "Reschedule Requested"
}


def process_response(response_token, status):

    if not response_token:
        raise ValueError("Missing response token.")

    if status not in VALID_STATUSES:
        raise ValueError("Invalid response status.")

    # Update the interview response using the existing repository.
    updated = update_response_status_by_token(
        response_token,
        status
    )

    if not updated:
        raise ValueError(
            "Invalid or expired response token, "
            "or the interview response is no longer Pending."
        )

    return {
        "success": True,
        "status": status
    }
