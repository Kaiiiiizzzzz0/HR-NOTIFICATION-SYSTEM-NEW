
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QDialog
)

from services.candidate import (
    create_candidate,
    get_all_candidates,
    delete_candidate,
    update_candidate,
    get_hr_list,
    get_position_list
)

from services.email_creator.message_templates import build_email_content
from services.response_repository import select_sent_email
from services.email_creator.scheduler import dispatch_pending_notifications
from views.candidate_form import CandidateForm
from views.candidate_table import CandidateTable
from views.filter_dialog import FilterDialog
from views.email_preview_dialog import EmailPreviewDialog


class CandidateWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Candidate Management")
        self.resize(900, 600)

        self.filter_type = "All"
        self.filter_level = "All"
        self.filter_hr = "All"
        self.filter_position = "All"
        self.start_date = ""
        self.end_date = ""
        self.search_text = ""

        # Stores edited email messages while the application is running.
        # Key = candidate_id
        # Value = {"subject": "...", "body": "..."}
        self.edited_emails = {}

        self.setup_ui()
        self.load_candidates()

    def setup_ui(self):
        self.form = CandidateForm()

        self.add_btn = QPushButton("Add Candidate")
        self.update_btn = QPushButton("Update Candidate")
        self.refresh_btn = QPushButton("Refresh")
        self.delete_btn = QPushButton("Delete Selected")
        self.send_notifications_btn = QPushButton(
            "Send Pending Notifications"
        )
        self.preview_btn = QPushButton("Preview Email")
        self.filter_btn = QPushButton("Filter")

        self.add_btn.clicked.connect(self.add_candidate)
        self.refresh_btn.clicked.connect(self.load_candidates)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.update_btn.clicked.connect(self.update_selected)
        self.send_notifications_btn.clicked.connect(
            self.send_pending_notifications
        )
        self.preview_btn.clicked.connect(self.preview_email)
        self.filter_btn.clicked.connect(self.open_filter_dialog)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.add_btn)
        button_row.addWidget(self.update_btn)
        button_row.addWidget(self.preview_btn)
        button_row.addWidget(self.send_notifications_btn)
        button_row.addStretch()

        self.table = CandidateTable()
        self.table.table.cellClicked.connect(self.select_candidate)

        self.selected_candidate_id = None
        self.update_btn.setEnabled(False)

        bottom = QHBoxLayout()
        bottom.setSpacing(6)
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.addWidget(self.filter_btn)
        bottom.addStretch()
        bottom.addWidget(self.refresh_btn)
        bottom.addWidget(self.delete_btn)

        self.form.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum
        )

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        layout.addWidget(self.form)
        layout.addLayout(button_row)
        layout.addWidget(self.table, stretch=1)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def format_duration(self, duration_value):
        try:
            total_minutes = int(duration_value)
        except (TypeError, ValueError):
            return (
                str(duration_value)
                if duration_value is not None
                else ""
            )

        hours = total_minutes // 60
        minutes = total_minutes % 60

        return f"{hours:02d}:{minutes:02d}"

    def load_candidates(self):
        try:
            rows = get_all_candidates(
                self.filter_type,
                self.filter_level,
                self.filter_hr,
                self.filter_position,
                self.start_date,
                self.end_date,
                self.search_text
            )

            self.table.populate(
                rows,
                self.format_duration
            )

            self.table.table.clearSelection()
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    def open_filter_dialog(self):
        filters = {
            "search": self.search_text,
            "type": self.filter_type,
            "level": self.filter_level,
            "hr": self.filter_hr,
            "position": self.filter_position,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "hr_list": get_hr_list(),
            "position_list": get_position_list()
        }

        dialog = FilterDialog(
            self,
            current_filters=filters
        )

        if dialog.exec() == QDialog.Accepted:
            selected_filters = dialog.get_filters()

            self.filter_type = selected_filters["type"]
            self.filter_level = selected_filters["level"]
            self.filter_hr = selected_filters["hr"]
            self.filter_position = selected_filters["position"]
            self.start_date = selected_filters["start_date"]
            self.end_date = selected_filters["end_date"]
            self.search_text = selected_filters["search"]

            self.load_candidates()

    def add_candidate(self):
        try:
            candidate_data = self.form.get_data()

            create_candidate(
                candidate_data["first_name"],
                candidate_data["last_name"],
                candidate_data["email"],
                candidate_data["phone"],
                candidate_data["assigned_hr"],
                candidate_data["position_role"],
                candidate_data["interview_type"],
                candidate_data["interview_level"],
                candidate_data["interview_duration"],
                candidate_data["scheduled_datetime"]
            )

            QMessageBox.information(
                self,
                "Success",
                "Candidate added successfully."
            )

            self.load_candidates()
            self.clear_form()

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Input Error",
                str(e)
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    def delete_selected(self):
        row = self.table.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a candidate first."
            )
            return

        try:
            candidate_id = int(
                self.table.table.item(row, 0).text()
            )

            delete_candidate(candidate_id)

            # Remove any edited email belonging to this candidate.
            self.edited_emails.pop(candidate_id, None)

            QMessageBox.information(
                self,
                "Success",
                "Candidate deleted successfully."
            )

            self.load_candidates()
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    def select_candidate(self, row, column):
        candidate = self.table.selected_candidate_data()

        if candidate is None:
            return

        self.selected_candidate_id = candidate["candidate_id"]

        self.form.set_candidate_data(candidate)

        self.add_btn.setEnabled(False)
        self.update_btn.setEnabled(True)

    def update_selected(self):
        if self.selected_candidate_id is None:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select a candidate from the table first."
            )
            return

        try:
            candidate_data = self.form.get_data()

            update_candidate(
                self.selected_candidate_id,
                candidate_data["first_name"],
                candidate_data["last_name"],
                candidate_data["email"],
                candidate_data["phone"],
                candidate_data["assigned_hr"],
                candidate_data["position_role"],
                candidate_data["interview_type"],
                candidate_data["interview_level"],
                candidate_data["interview_duration"],
                candidate_data["scheduled_datetime"]
            )

            QMessageBox.information(
                self,
                "Success",
                "Candidate updated successfully."
            )

            self.load_candidates()
            self.clear_form()

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Input Error",
                str(e)
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    def send_pending_notifications(self):
        try:
            results = dispatch_pending_notifications(
                edited_emails=self.edited_emails
            )

            sent_count = sum(
                1
                for item in results
                if item.get("success")
            )

            failed_count = len(results) - sent_count

            message = (
                f"Notifications processed: {len(results)}\n"
                f"Sent: {sent_count}\n"
                f"Failed: {failed_count}"
            )

            if len(results) == 0:
                message = (
                    "No pending notifications were found.\n"
                    "Make sure candidates have status set to 'Pending' "
                    "and have not already been sent."
                )

            elif failed_count > 0:
                first_error = next(
                    (
                        item.get("error")
                        for item in results
                        if not item.get("success")
                    ),
                    None
                )

                if first_error:
                    message += (
                        f"\nFirst failure: {first_error}"
                    )

            QMessageBox.information(
                self,
                "Send Pending Notifications",
                message
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Send Pending Notifications Failed",
                str(e)
            )

    def get_selected_candidate_data(self):
        return self.table.selected_candidate_data()

    def preview_email(self):
        candidate = self.get_selected_candidate_data()

        if candidate is None:
            QMessageBox.warning(
                self,
                "Preview Email",
                "Please select a candidate first."
            )
            return

        candidate_id = candidate.get("candidate_id")
        response_id = candidate.get("response_id")

        # If the email has already been sent,
        # retrieve the exact email that was sent.
        if response_id is not None:

            sent_email = select_sent_email(response_id)

            if sent_email is not None:
                subject = sent_email["subject"]
                body = sent_email["body"]

                dialog = EmailPreviewDialog(
                    subject,
                    body,
                    self
                )

                dialog.exec()
                return

        # Otherwise show the generated email.
        if candidate_id in self.edited_emails:

            saved_email = self.edited_emails[candidate_id]

            subject = saved_email["subject"]
            body = saved_email["body"]

        else:

            subject, body = build_email_content(candidate)

        dialog = EmailPreviewDialog(
            subject,
            body,
            self
        )

        if dialog.exec() == QDialog.Accepted:

            edited_subject, edited_body = dialog.get_content()

            self.edited_emails[candidate_id] = {
                "subject": edited_subject,
                "body": edited_body
            }

            QMessageBox.information(
                self,
                "Email Saved",
                "The edited email has been saved."
            )
    def clear_form(self):
        self.selected_candidate_id = None

        self.form.clear()

        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)