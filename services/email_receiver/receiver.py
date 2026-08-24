from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from services.email_receiver.parser import parse_response_path
from services.email_receiver.processor import process_response


app = FastAPI()


@app.get("/response/{response_token}/{response}")
def receive_response(response_token: str, response: str):
    path = f"/response/{response_token}/{response}"

    try:
        parsed_response = parse_response_path(path)

        result = process_response(
            parsed_response["response_token"],
            parsed_response["status"]
        )

        if parsed_response["status"] == "Reschedule Requested":
            return HTMLResponse(
                content="""
                <html>
                    <body>
                        <h1>Reschedule Request Sent</h1>
                        <p>
                            Your request to reschedule the interview
                            has been sent to HR.
                        </p>
                        <p>
                            HR will contact you regarding your new
                            interview schedule.
                        </p>
                    </body>
                </html>
                """
            )

        return HTMLResponse(
            content="""
            <html>
                <body>
                    <h1>Response Recorded</h1>
                    <p>
                        Thank you. Your interview response has been recorded.
                    </p>
                </body>
            </html>
            """
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to process your response."
        )