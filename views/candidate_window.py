
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
    update_candidate_application_count,
    get_hr_list,
    get_position_list
)

from services.email_creator.message_templates import (
    build_email_content
)

from services.response_repository import (
    select_sent_email,
    update_response_status_by_candidate
)

from services.email_creator.scheduler import (
    dispatch_pending_notifications
)

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

        self.select_candidates_btn = QPushButton(
            "Select Candidates"
        )

        self.select_all_btn = QPushButton(
            "Select All"
        )

        self.send_selected_btn = QPushButton(
            "Send Selected (0)"
        )

        self.cancel_selection_btn = QPushButton(
            "Cancel Selection"
        )

        self.add_btn.clicked.connect(
            self.add_candidate
        )

        self.refresh_btn.clicked.connect(
            self.load_candidates
        )

        self.delete_btn.clicked.connect(
            self.delete_selected
        )

        self.update_btn.clicked.connect(
            self.update_selected
        )

        self.send_notifications_btn.clicked.connect(
            self.send_pending_notifications
        )

        self.preview_btn.clicked.connect(
            self.preview_email
        )

        self.filter_btn.clicked.connect(
            self.open_filter_dialog
        )

        self.select_candidates_btn.clicked.connect(
            self.enter_selection_mode
        )

        self.select_all_btn.clicked.connect(
            self.select_all_candidates
        )

        self.send_selected_btn.clicked.connect(
            self.send_selected_notifications
        )

        self.cancel_selection_btn.clicked.connect(
            self.exit_selection_mode
        )

        button_row = QHBoxLayout()
        button_row.addStretch()

        button_row.addWidget(self.add_btn)
        button_row.addWidget(self.update_btn)
        button_row.addWidget(self.preview_btn)
        button_row.addWidget(self.send_notifications_btn)
        button_row.addWidget(self.select_candidates_btn)
        button_row.addWidget(self.select_all_btn)
        button_row.addWidget(self.send_selected_btn)
        button_row.addWidget(self.cancel_selection_btn)

        button_row.addStretch()

        self.select_all_btn.setVisible(False)
        self.send_selected_btn.setVisible(False)
        self.cancel_selection_btn.setVisible(False)

        self.table = CandidateTable()

        self.table.table.cellClicked.connect(
            self.select_candidate
        )

        self.table.table.itemChanged.connect(
            self.selection_checkbox_changed
        )

        self.table.status_changed.connect(
            self.status_changed
        )

        # Application Count editing.
        self.table.application_count_changed.connect(
            self.application_count_changed
        )

        self.selected_candidate_id = None

        self.update_btn.setEnabled(False)

        bottom = QHBoxLayout()

        bottom.setSpacing(6)

        bottom.setContentsMargins(
            0,
            0,
            0,
            0
        )

        bottom.addWidget(
            self.filter_btn
        )

        bottom.addStretch()

        bottom.addWidget(
            self.refresh_btn
        )

        bottom.addWidget(
            self.delete_btn
        )

        self.form.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum
        )

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        layout = QVBoxLayout()

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        layout.setSpacing(4)

        layout.addWidget(
            self.form
        )

        layout.addLayout(
            button_row
        )

        layout.addWidget(
            self.table,
            stretch=1
        )

        layout.addLayout(
            bottom
        )

        self.setLayout(
            layout
        )

    def format_duration(
        self,
        duration_value
    ):

        try:

            total_minutes = int(
                duration_value
            )

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

        if self.table.selection_mode:
            return

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

    def application_count_changed(
        self,
        candidate_id,
        application_count
    ):

        try:

            update_candidate_application_count(
                candidate_id,
                application_count
            )

        except ValueError as e:

            QMessageBox.warning(
                self,
                "Application Count",
                str(e)
            )

            self.load_candidates()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Application Count",
                str(e)
            )

            self.load_candidates()

    def status_changed(
        self,
        candidate_id,
        status
    ):

        if self.table.selection_mode:
            return

        try:

            update_response_status_by_candidate(
                candidate_id,
                status
            )

        except ValueError as e:

            QMessageBox.warning(
                self,
                "Update Status",
                str(e)
            )

            self.load_candidates()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Update Status",
                str(e)
            )

            self.load_candidates()

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

            selected_filters = (
                dialog.get_filters()
            )

            self.filter_type = (
                selected_filters["type"]
            )

            self.filter_level = (
                selected_filters["level"]
            )

            self.filter_hr = (
                selected_filters["hr"]
            )

            self.filter_position = (
                selected_filters["position"]
            )

            self.start_date = (
                selected_filters["start_date"]
            )

            self.end_date = (
                selected_filters["end_date"]
            )

            self.search_text = (
                selected_filters["search"]
            )

            self.load_candidates()

    def add_candidate(self):

        try:

            candidate_data = (
                self.form.get_data()
            )

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

        candidate = (
            self.table.selected_candidate_data()
        )

        if candidate is None:

            QMessageBox.warning(
                self,
                "Warning",
                "Please select a candidate first."
            )

            return

        try:

            candidate_id = (
                candidate["candidate_id"]
            )

            delete_candidate(
                candidate_id
            )

            self.edited_emails.pop(
                candidate_id,
                None
            )

            QMessageBox.information(
                self,
                "Success",
                "Candidate deleted successfully."
            )

            self.load_candidates()
            self.clear_form()

        except ValueError as e:

            QMessageBox.warning(
                self,
                "Delete Candidate",
                str(e)
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    def select_candidate(
        self,
        row,
        column
    ):

        if column == 0 or column == 12:
            return

        if self.table.selection_mode:
            return

        candidate = (
            self.table.selected_candidate_data()
        )

        if candidate is None:
            return

        self.selected_candidate_id = (
            candidate["candidate_id"]
        )

        self.form.set_candidate_data(
            candidate
        )

        self.add_btn.setEnabled(
            False
        )

        self.update_btn.setEnabled(
            True
        )

    def update_selected(self):

        if self.selected_candidate_id is None:

            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select a candidate from the table first."
            )

            return

        try:

            candidate_data = (
                self.form.get_data()
            )

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

            results = (
                dispatch_pending_notifications(
                    edited_emails=self.edited_emails
                )
            )

            sent_count = sum(
                1
                for item in results
                if item.get("success")
            )

            failed_count = (
                len(results) - sent_count
            )

            message = (
                f"Notifications processed: {len(results)}\n"
                f"Sent: {sent_count}\n"
                f"Failed: {failed_count}"
            )

            if len(results) == 0:

                message = (
                    "No pending notifications were found.\n"
                    "Make sure candidates have status set to "
                    "'Pending' and have not already been sent."
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

            self.load_candidates()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Send Pending Notifications Failed",
                str(e)
            )

    def get_selected_candidate_data(self):

        return (
            self.table.selected_candidate_data()
        )

    def preview_email(self):

        candidate = (
            self.get_selected_candidate_data()
        )

        if candidate is None:

            QMessageBox.warning(
                self,
                "Preview Email",
                "Please select a candidate first."
            )

            return

        candidate_id = candidate.get(
            "candidate_id"
        )

        response_id = candidate.get(
            "response_id"
        )

        if response_id is not None:

            sent_email = select_sent_email(
                response_id
            )

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

        if candidate_id in self.edited_emails:

            saved_email = (
                self.edited_emails[candidate_id]
            )

            subject = saved_email["subject"]
            body = saved_email["body"]

        else:

            subject, body = (
                build_email_content(candidate)
            )

        dialog = EmailPreviewDialog(
            subject,
            body,
            self
        )

        if dialog.exec() == QDialog.Accepted:

            edited_subject, edited_body = (
                dialog.get_content()
            )

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

        self.add_btn.setEnabled(
            True
        )

        self.update_btn.setEnabled(
            False
        )

    def enter_selection_mode(self):

        self.table.set_selection_mode(
            True
        )

        self.set_status_dropdowns_enabled(
            False
        )

        self.add_btn.setEnabled(
            False
        )

        self.update_btn.setEnabled(
            False
        )

        self.preview_btn.setEnabled(
            False
        )

        self.send_notifications_btn.setEnabled(
            False
        )

        self.delete_btn.setEnabled(
            False
        )

        self.refresh_btn.setEnabled(
            False
        )

        self.filter_btn.setEnabled(
            False
        )

        self.select_candidates_btn.setVisible(
            False
        )

        self.select_all_btn.setVisible(
            True
        )

        self.send_selected_btn.setVisible(
            True
        )

        self.cancel_selection_btn.setVisible(
            True
        )

        self.send_selected_btn.setEnabled(
            False
        )

    def exit_selection_mode(self):

        self.table.set_selection_mode(
            False
        )

        self.set_status_dropdowns_enabled(
            True
        )

        self.add_btn.setEnabled(
            True
        )

        self.update_btn.setEnabled(
            False
        )

        self.preview_btn.setEnabled(
            True
        )

        self.send_notifications_btn.setEnabled(
            True
        )

        self.delete_btn.setEnabled(
            False
        )

        self.refresh_btn.setEnabled(
            True
        )

        self.filter_btn.setEnabled(
            True
        )

        self.select_candidates_btn.setVisible(
            True
        )

        self.select_all_btn.setVisible(
            False
        )

        self.send_selected_btn.setVisible(
            False
        )

        self.cancel_selection_btn.setVisible(
            False
        )

        self.clear_form()

    def set_status_dropdowns_enabled(
        self,
        enabled
    ):

        for row in range(
            self.table.table.rowCount()
        ):

            combo = self.table.table.cellWidget(
                row,
                13
            )

            if combo is not None:

                combo.setEnabled(
                    enabled
                )

    def select_all_candidates(self):

        if not self.table.selection_mode:
            return

        self.table.check_all_candidates()

        self.update_send_selected_button()

    def selection_checkbox_changed(
        self,
        item
    ):

        if item.column() != 0:
            return

        if not self.table.selection_mode:
            return

        self.update_send_selected_button()

    def update_send_selected_button(self):

        count = (
            self.table.checked_count()
        )

        self.send_selected_btn.setText(
            f"Send Selected ({count})"
        )

        self.send_selected_btn.setEnabled(
            count > 0
        )

    def send_selected_notifications(self):

        if not self.table.selection_mode:
            return

        candidate_ids = (
            self.table.get_checked_candidate_ids()
        )

        if not candidate_ids:

            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select at least one candidate."
            )

            return

        reply = QMessageBox.question(
            self,
            "Confirm Send",
            (
                f"Send notifications to "
                f"{len(candidate_ids)} selected "
                f"candidate(s)?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:

            results = (
                dispatch_pending_notifications(
                    edited_emails=self.edited_emails,
                    candidate_ids=candidate_ids
                )
            )

            sent_count = sum(
                1
                for item in results
                if item.get("success")
            )

            failed_count = (
                len(results) - sent_count
            )

            QMessageBox.information(
                self,
                "Send Selected Notifications",
                (
                    f"Notifications processed: "
                    f"{len(results)}\n"
                    f"Sent: {sent_count}\n"
                    f"Failed: {failed_count}"
                )
            )

            self.exit_selection_mode()
            self.load_candidates()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Send Selected Notifications Failed",
                str(e)
            )
