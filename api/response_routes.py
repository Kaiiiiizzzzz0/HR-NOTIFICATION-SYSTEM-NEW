from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.email_receiver.processor import (
    process_response
)


router = APIRouter()


def response_page(
    title,
    message
):

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>

        <html>

        <head>

            <meta charset="UTF-8">

            <title>{title}</title>

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin-top: 80px;
                }}

                h1 {{
                    margin-bottom: 20px;
                }}

                p {{
                    font-size: 18px;
                }}

            </style>

        </head>

        <body>

            <h1>{title}</h1>

            <p>{message}</p>

        </body>

        </html>
        """
    )


@router.get(
    "/response/{token}/{response}"
)
def receive_response(
    token: str,
    response: str
):

    response = response.lower()

    status_map = {
        "yes": "Confirmed",
        "no": "Declined",
        "reschedule": "Reschedule Requested"
    }

    if response not in status_map:

        return response_page(
            "Invalid Response",
            "The response link is invalid."
        )

    status = status_map[response]

    try:

        result = process_response(
            token,
            status
        )

        if status == "Confirmed":

            return response_page(
                "Interview Confirmed",
                "Thank you. Your interview has been confirmed."
            )

        if status == "Declined":

            return response_page(
                "Interview Declined",
                (
                    "Your interview response has been recorded. "
                    "Please reply to the email if additional "
                    "information is required."
                )
            )

        if status == "Reschedule Requested":

            return response_page(
                "Reschedule Request Sent",
                (
                    "Your request to reschedule the interview "
                    "has been recorded. HR will contact you "
                    "regarding the new schedule."
                )
            )

        return response_page(
            "Response Recorded",
            "Your interview response has been recorded."
        )

    except ValueError as error:

        return response_page(
            "Response Not Recorded",
            str(error)
        )

    except Exception:

        return response_page(
            "System Error",
            "Unable to process your interview response."
        )