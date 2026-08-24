VALID_RESPONSES = {
    "yes": "Confirmed",
    "no": "Declined",
    "reschedule": "Reschedule Requested",
}


def parse_response_path(path):

    parts = path.strip("/").split("/")

    if len(parts) != 3:
        raise ValueError("Invalid response URL.")

    if parts[0] != "response":
        raise ValueError("Invalid response URL.")

    response_token = parts[1]
    response = parts[2].lower()

    if not response_token:
        raise ValueError("Missing response token.")

    if response not in VALID_RESPONSES:
        raise ValueError("Invalid response.")

    return {
        "response_token": response_token,
        "status": VALID_RESPONSES[response],
    }