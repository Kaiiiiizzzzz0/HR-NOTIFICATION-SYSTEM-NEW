from datetime import datetime


def response_buttons(response_token):
    print("RESPONSE TOKEN:", response_token)
    print(
        "RESCHEDULE URL:",
        f"http://localhost:8000/response/{response_token}/reschedule"
    )

    return (
        "<div style='margin: 20px 0;'>"
        "<p><strong>Will you attend the interview?</strong></p>"

        f"<a href='http://localhost:8000/response/{response_token}/yes' "
        "style='display:inline-block; padding:10px 18px; "
        "margin-right:8px; background-color:#28a745; color:white; "
        "text-decoration:none; border-radius:5px;'>"
        "YES"
        "</a>"

        f"<a href='http://localhost:8000/response/{response_token}/no' "
        "style='display:inline-block; padding:10px 18px; "
        "margin-right:8px; background-color:#dc3545; color:white; "
        "text-decoration:none; border-radius:5px;'>"
        "NO"
        "</a>"

        f"<a href='http://localhost:8000/response/{response_token}/reschedule' "
        "style='display:inline-block; padding:10px 18px; "
        "background-color:#ffc107; color:#212529; "
        "text-decoration:none; border-radius:5px;'>"
        "REQUEST RESCHEDULE"
        "</a>"

        "</div>"
    )


TEMPLATES = {
    "Over-the-phone Interview": {
        "subject": "Your upcoming phone interview for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name} {last_name},</p>"

            "<p>"
            "This is a reminder that your phone interview for the "
            "<strong>{position_role}</strong> position is scheduled for "
            "<strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "<li>Assigned HR: {assigned_hr}</li>"
            "</ul>"

            "<p>Please be available and join the call on time.</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Best regards,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    },

    "HR Interview": {
        "subject": "HR interview scheduled for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name},</p>"

            "<p>"
            "Your HR interview for the "
            "<strong>{position_role}</strong> position is confirmed for "
            "<strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "</ul>"

            "<p>"
            "Please arrive prepared and ensure your contact details "
            "are up to date."
            "</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Thank you,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    },

    "Technical Exam": {
        "subject": "Technical exam scheduled for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name},</p>"

            "<p>"
            "This is your reminder for the technical exam scheduled "
            "on <strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "</ul>"

            "<p>"
            "Please arrive prepared and ensure your contact details "
            "are up to date."
            "</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Thank you,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    },

    "Technical Interview": {
        "subject": "Technical interview reminder for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name},</p>"

            "<p>"
            "Your technical interview for the "
            "<strong>{position_role}</strong> position is scheduled for "
            "<strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "</ul>"

            "<p>"
            "Please arrive prepared and ensure your contact details "
            "are up to date."
            "</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Thank you,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    },

    "Level-2 Interview": {
        "subject": "Second level interview scheduled for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name},</p>"

            "<p>"
            "Your second level interview is booked for "
            "<strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "</ul>"

            "<p>"
            "Please be prepared to discuss your previous interview "
            "and next steps."
            "</p>"

            "<p>"
            "Please arrive prepared and ensure your contact details "
            "are up to date."
            "</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Thank you,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    },

    "Final Interview": {
        "subject": "Final interview invitation for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name},</p>"

            "<p>"
            "We are pleased to confirm your final interview for the "
            "<strong>{position_role}</strong> position on "
            "<strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "</ul>"

            "<p>"
            "Please ensure you are ready to discuss your fit for the "
            "role and any final questions you may have."
            "</p>"

            "<p>"
            "Please arrive prepared and ensure your contact details "
            "are up to date."
            "</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Thank you,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    },

    "Default": {
        "subject": "Interview reminder for {position_role}",
        "body": (
            "<html><body>"

            "<p>Hello {first_name},</p>"

            "<p>"
            "This is a reminder of your upcoming interview for "
            "<strong>{position_role}</strong> on "
            "<strong>{scheduled_date}</strong> at "
            "<strong>{scheduled_time}</strong>."
            "</p>"

            "<p><strong>Interview details:</strong></p>"
            "<ul>"
            "<li>Interview Level: {interview_level}</li>"
            "<li>Interview Type: {interview_type}</li>"
            "</ul>"

            "<p>"
            "If you need assistance, please contact {assigned_hr}."
            "</p>"

            "<p>"
            "Please arrive prepared and ensure your contact details "
            "are up to date."
            "</p>"

            "{response_buttons}"

            "<p>"
            "If you need to reschedule, please use the "
            "<strong>REQUEST RESCHEDULE</strong> button above. "
            "You may then reply to this email with your preferred availability."
            "</p>"

            "<p>Thank you,<br>{assigned_hr}</p>"

            "</body></html>"
        )
    }
}


def format_datetime(scheduled_datetime):
    if isinstance(scheduled_datetime, str):
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_datetime)
        except ValueError:
            return scheduled_datetime, ""

    scheduled_date = scheduled_datetime.strftime("%Y-%m-%d")
    scheduled_time = scheduled_datetime.strftime("%I:%M %p")

    return scheduled_date, scheduled_time


def get_email_template(interview_level):
    return TEMPLATES.get(
        interview_level,
        TEMPLATES["Default"]
    )


def build_email_content(candidate):
    scheduled_date, scheduled_time = format_datetime(
        candidate.get("scheduled_datetime")
    )

    template = get_email_template(
        candidate.get("interview_level", "Default")
    )

    context = {
        "first_name": candidate.get("first_name", "Candidate"),
        "last_name": candidate.get("last_name", ""),
        "candidate_email": candidate.get("email", ""),
        "position_role": candidate.get(
            "position_role",
            "your role"
        ),
        "interview_type": candidate.get(
            "interview_type",
            "Interview"
        ),
        "interview_level": candidate.get(
            "interview_level",
            "Interview"
        ),
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "assigned_hr": candidate.get(
            "assigned_hr",
            "HR Team"
        ),
        "response_token": candidate.get(
            "response_token",
            ""
        ),
        "response_buttons": response_buttons(
            candidate.get("response_token", "")
        )
    }

    subject = template["subject"].format(**context)
    body = template["body"].format(**context)

    return subject, body