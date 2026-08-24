from datetime import datetime


def parse_duration(duration_text):
    duration_text = duration_text.strip()

    if not duration_text:
        raise ValueError("Please enter the interview duration in HH:MM format.")

    parts = duration_text.split(":")
    if len(parts) != 2:
        raise ValueError("Interview duration must be in HH:MM format.")

    hours_text, minutes_text = parts
    if not hours_text.isdigit() or not minutes_text.isdigit():
        raise ValueError("Interview duration must be numeric in HH:MM format.")

    hours = int(hours_text)
    minutes = int(minutes_text)

    if hours < 0 or minutes < 0 or minutes >= 60:
        raise ValueError("Interview duration must be in HH:MM format with minutes from 00 to 59.")

    total_minutes = hours * 60 + minutes

    if total_minutes <= 0:
        raise ValueError("Interview duration must be greater than 0.")

    return total_minutes


def validate_candidate_fields(
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
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()
    phone = phone.strip()
    assigned_hr = assigned_hr.strip()
    position_role = position_role.strip()
    scheduled_datetime = scheduled_datetime.strip()

    if not first_name:
        raise ValueError("Please enter the candidate's first name.")

    if not last_name:
        raise ValueError("Please enter the candidate's last name.")

    if not email:
        raise ValueError("Please enter the candidate's email address.")

    if not assigned_hr:
        raise ValueError("Please enter the assigned HR.")

    if not position_role:
        raise ValueError("Please enter the position/role.")

    if not scheduled_datetime:
        raise ValueError(
            "Please enter the interview schedule.\n\nFormat:\nYYYY-MM-DD HH:MM:SS"
        )

    if "@" not in email or "." not in email:
        raise ValueError("Please enter a valid email address.")

    if not phone.isdigit():
        raise ValueError("Phone number must contain digits only.")

    if len(phone) < 10:
        raise ValueError("Phone number is too short.")

    if len(phone) > 15:
        raise ValueError("Phone number is too long.")

    if interview_type not in (
        "VIRTUAL",
        "OVER-THE-PHONE",
        "ONSITE"
    ):
        raise ValueError("Please select a valid interview type.")

    if interview_level not in (
        "Over-the-phone Interview",
        "HR Interview",
        "HR Interview + Technical Exam",
        "Technical Exam",
        "Technical Interview",
        "Level-2 Interview",
        "Level-2 Interview + Technical Exam",
        "Technical Exam + Final Interview",
        "Final Interview",
        "Next-Level Interview"
    ):
        raise ValueError("Please select a valid interview level.")

    validated_duration = parse_duration(interview_duration)

    try:
        datetime.strptime(scheduled_datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(
            "Interview schedule must follow this format: YYYY-MM-DD HH:MM:SS"
        )

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "assigned_hr": assigned_hr,
        "position_role": position_role,
        "interview_type": interview_type,
        "interview_level": interview_level,
        "interview_duration": validated_duration,
        "scheduled_datetime": scheduled_datetime,
    }
