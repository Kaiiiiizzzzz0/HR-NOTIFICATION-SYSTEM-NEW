import time

from .emailer import send_email

from services.response_repository import (
    select_pending_notification_candidates,
    mark_notification_processing,
    mark_notification_sent,
)


SEND_DELAY = 3


def dispatch_pending_notifications(
    edited_emails=None,
    candidate_ids=None
):

    if edited_emails is None:
        edited_emails = {}

    candidates = (
        select_pending_notification_candidates()
    )

    # If specific candidates were selected manually,
    # keep only those candidates.
    if candidate_ids is not None:

        candidate_ids = set(candidate_ids)

        candidates = [
            candidate
            for candidate in candidates
            if candidate.get("candidate_id")
            in candidate_ids
        ]

    results = []

    processed_count = 0

    for candidate in candidates:

        candidate_data = dict(candidate)

        response_id = (
            candidate_data.get("response_id")
        )

        candidate_id = (
            candidate_data.get("candidate_id")
        )

        if response_id is None:
            continue

        # Use the edited email if HR saved one
        # for this candidate.
        if candidate_id in edited_emails:

            edited_email = (
                edited_emails[candidate_id]
            )

            candidate_data["edited_subject"] = (
                edited_email.get("subject")
            )

            candidate_data["edited_body"] = (
                edited_email.get("body")
            )

        try:

            processing_started = (
                mark_notification_processing(
                    response_id
                )
            )

        except Exception as e:

            results.append({
                "success": False,
                "candidate_id": candidate_id,
                "response_id": response_id,
                "error": (
                    "Failed to mark notification "
                    f"as processing: {e}"
                )
            })

            continue

        if not processing_started:

            results.append({
                "success": False,
                "candidate_id": candidate_id,
                "response_id": response_id,
                "error": (
                    "Notification could not be marked "
                    "as processing."
                )
            })

            continue

        try:

            send_result = send_email(
                candidate_data
            )

        except Exception as e:

            send_result = {
                "success": False,
                "candidate_id": candidate_id,
                "response_id": response_id,
                "error": str(e)
            }

        if send_result.get("success"):

            try:

                mark_notification_sent(
                    response_id
                )

            except Exception as update_error:

                send_result["success"] = False

                send_result["error"] = (
                    "Email sent, but failed to update "
                    "notification status: "
                    f"{update_error}"
                )

        results.append(
            send_result
        )

        processed_count += 1

        # Wait between actual processing attempts
        # to avoid sending emails too rapidly.
        if processed_count < len(candidates):

            time.sleep(
                SEND_DELAY
            )

    return results