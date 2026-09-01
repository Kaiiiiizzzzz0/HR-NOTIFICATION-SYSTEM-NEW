from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QAbstractItemView,
    QMessageBox
)

from services.candidate import (
    get_dashboard_summary,
    get_upcoming_interviews
)

from services.response import (
    get_response_status_summary,
    get_recent_responses
)

from services.email_creator.scheduler import (
    dispatch_pending_notifications
)


class DashboardWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("HR Dashboard")
        self.resize(1200, 750)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):

        # ---------------------------------------------------------
        # MONTHLY SUMMARY
        # ---------------------------------------------------------

        self.monthly_summary_label = QLabel(
            "Current Month"
        )

        self.total_candidates = QLabel("0")
        self.virtual_count = QLabel("0")
        self.phone_count = QLabel("0")
        self.onsite_count = QLabel("0")

        self.upcoming_today = QLabel("0")
        self.upcoming_week = QLabel("0")

        summary_layout = QGridLayout()

        summary_layout.addWidget(
            self.monthly_summary_label,
            0,
            0,
            1,
            6
        )

        summary_layout.addWidget(
            QLabel("Candidates Added This Month"),
            1,
            0
        )

        summary_layout.addWidget(
            self.total_candidates,
            1,
            1
        )

        summary_layout.addWidget(
            QLabel("Virtual Interviews"),
            1,
            2
        )

        summary_layout.addWidget(
            self.virtual_count,
            1,
            3
        )

        summary_layout.addWidget(
            QLabel("Over-the-Phone"),
            1,
            4
        )

        summary_layout.addWidget(
            self.phone_count,
            1,
            5
        )

        summary_layout.addWidget(
            QLabel("Onsite Interviews"),
            2,
            0
        )

        summary_layout.addWidget(
            self.onsite_count,
            2,
            1
        )

        summary_layout.addWidget(
            QLabel("Upcoming Today"),
            2,
            2
        )

        summary_layout.addWidget(
            self.upcoming_today,
            2,
            3
        )

        summary_layout.addWidget(
            QLabel("Upcoming This Week"),
            2,
            4
        )

        summary_layout.addWidget(
            self.upcoming_week,
            2,
            5
        )

        summary_group = QGroupBox(
            "Monthly Summary"
        )

        summary_group.setLayout(
            summary_layout
        )

        # ---------------------------------------------------------
        # RESPONSE STATUS
        # ---------------------------------------------------------

        self.pending_count = QLabel("0")
        self.confirmed_count = QLabel("0")
        self.declined_count = QLabel("0")
        self.reschedule_count = QLabel("0")

        status_layout = QGridLayout()

        status_layout.addWidget(
            QLabel("Pending Responses"),
            0,
            0
        )

        status_layout.addWidget(
            self.pending_count,
            0,
            1
        )

        status_layout.addWidget(
            QLabel("Confirmed"),
            0,
            2
        )

        status_layout.addWidget(
            self.confirmed_count,
            0,
            3
        )

        status_layout.addWidget(
            QLabel("Declined"),
            1,
            0
        )

        status_layout.addWidget(
            self.declined_count,
            1,
            1
        )

        status_layout.addWidget(
            QLabel("Reschedule Requested"),
            1,
            2
        )

        status_layout.addWidget(
            self.reschedule_count,
            1,
            3
        )

        response_group = QGroupBox(
            "Response Status"
        )

        response_group.setLayout(
            status_layout
        )

        # ---------------------------------------------------------
        # UPCOMING INTERVIEWS TABLE
        # ---------------------------------------------------------

        self.upcoming_table = QTableWidget()

        self.upcoming_table.setColumnCount(7)

        self.upcoming_table.setHorizontalHeaderLabels([
            "ID",
            "Candidate",
            "Position",
            "Email",
            "Assigned HR",
            "Modality",
            "Schedule"
        ])

        self.upcoming_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.upcoming_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.upcoming_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        # ---------------------------------------------------------
        # RECENT RESPONSES TABLE
        # ---------------------------------------------------------

        self.recent_table = QTableWidget()

        self.recent_table.setColumnCount(5)

        self.recent_table.setHorizontalHeaderLabels([
            "Response ID",
            "Candidate",
            "Status",
            "Schedule",
            "Responded At"
        ])

        self.recent_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.recent_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.recent_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        # ---------------------------------------------------------
        # REFRESH
        # ---------------------------------------------------------

        self.refresh_btn = QPushButton(
            "Refresh Dashboard"
        )

        self.refresh_btn.clicked.connect(
            self.load_data
        )

        # ---------------------------------------------------------
        # MAIN LAYOUT
        # ---------------------------------------------------------

        layout = QVBoxLayout()

        layout.addWidget(
            summary_group
        )

        layout.addWidget(
            response_group
        )

        layout.addWidget(
            QLabel("Upcoming Interviews")
        )

        layout.addWidget(
            self.upcoming_table
        )

        layout.addWidget(
            QLabel("Recent Interview Responses")
        )

        layout.addWidget(
            self.recent_table
        )

        layout.addWidget(
            self.refresh_btn
        )

        self.setLayout(
            layout
        )

    def load_data(self):

        try:

            # -----------------------------------------------------
            # MONTHLY SUMMARY
            # -----------------------------------------------------

            summary = get_dashboard_summary()

            self.total_candidates.setText(
                str(
                    summary["total_candidates"]
                )
            )

            self.virtual_count.setText(
                str(
                    summary["virtual_count"]
                )
            )

            self.phone_count.setText(
                str(
                    summary["phone_count"]
                )
            )

            self.onsite_count.setText(
                str(
                    summary["onsite_count"]
                )
            )

            self.upcoming_today.setText(
                str(
                    summary["upcoming_today"]
                )
            )

            self.upcoming_week.setText(
                str(
                    summary["upcoming_week"]
                )
            )

            # -----------------------------------------------------
            # RESPONSE STATUS
            # -----------------------------------------------------

            response_summary = (
                get_response_status_summary()
            )

            self.pending_count.setText(
                str(
                    response_summary.get(
                        "Pending",
                        0
                    )
                )
            )

            self.confirmed_count.setText(
                str(
                    response_summary.get(
                        "Confirmed",
                        0
                    )
                )
            )

            self.declined_count.setText(
                str(
                    response_summary.get(
                        "Declined",
                        0
                    )
                )
            )

            self.reschedule_count.setText(
                str(
                    response_summary.get(
                        "Reschedule Requested",
                        0
                    )
                )
            )

            # -----------------------------------------------------
            # UPCOMING INTERVIEWS
            # -----------------------------------------------------

            upcoming_rows = (
                get_upcoming_interviews(15)
            )

            self.upcoming_table.setRowCount(
                len(upcoming_rows)
            )

            for row_index, row in enumerate(
                upcoming_rows
            ):

                (
                    candidate_id,
                    first_name,
                    last_name,
                    email,
                    assigned_hr,
                    position_role,
                    interview_type,
                    schedule
                ) = row

                self.upcoming_table.setItem(
                    row_index,
                    0,
                    QTableWidgetItem(
                        str(candidate_id)
                    )
                )

                self.upcoming_table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem(
                        f"{first_name} {last_name}"
                    )
                )

                self.upcoming_table.setItem(
                    row_index,
                    2,
                    QTableWidgetItem(
                        position_role
                    )
                )

                self.upcoming_table.setItem(
                    row_index,
                    3,
                    QTableWidgetItem(
                        email
                    )
                )

                self.upcoming_table.setItem(
                    row_index,
                    4,
                    QTableWidgetItem(
                        assigned_hr
                    )
                )

                self.upcoming_table.setItem(
                    row_index,
                    5,
                    QTableWidgetItem(
                        interview_type
                    )
                )

                self.upcoming_table.setItem(
                    row_index,
                    6,
                    QTableWidgetItem(
                        str(schedule)
                    )
                )

            # -----------------------------------------------------
            # RECENT RESPONSES
            # -----------------------------------------------------

            recent_rows = (
                get_recent_responses(10)
            )

            self.recent_table.setRowCount(
                len(recent_rows)
            )

            for row_index, row in enumerate(
                recent_rows
            ):

                (
                    response_id,
                    first_name,
                    last_name,
                    status,
                    schedule,
                    responded_at
                ) = row

                self.recent_table.setItem(
                    row_index,
                    0,
                    QTableWidgetItem(
                        str(response_id)
                    )
                )

                self.recent_table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem(
                        f"{first_name} {last_name}"
                    )
                )

                self.recent_table.setItem(
                    row_index,
                    2,
                    QTableWidgetItem(
                        status
                    )
                )

                self.recent_table.setItem(
                    row_index,
                    3,
                    QTableWidgetItem(
                        str(schedule)
                    )
                )

                self.recent_table.setItem(
                    row_index,
                    4,
                    QTableWidgetItem(
                        str(responded_at)
                        if responded_at
                        else "-"
                    )
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Dashboard Error",
                f"Unable to load dashboard:\n{e}"
            )

    def send_pending_notifications(self):

        try:

            results = (
                dispatch_pending_notifications()
            )

            sent_count = sum(
                1
                for item in results
                if item.get("success")
            )

            failed_count = (
                len(results) - sent_count
            )

            if len(results) == 0:

                message = (
                    "No pending notifications were found.\n"
                    "Make sure candidates have status set to "
                    "'Pending' and have not already been sent."
                )

            else:

                message = (
                    f"Notifications processed: "
                    f"{len(results)}\n"
                    f"Sent: {sent_count}\n"
                    f"Failed: {failed_count}"
                )

                if failed_count > 0:

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
                            f"\nFirst failure: "
                            f"{first_error}"
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