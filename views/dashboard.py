
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QAbstractItemView,
    QMessageBox,
    QHeaderView,
    QDialog
)

from sqlalchemy import text

from database import SessionLocal

from services.candidate import (
    get_dashboard_summary,
    get_upcoming_interviews,
    get_hr_list,
    get_position_list
)

from views.filter_dialog import FilterDialog
class DashboardWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filter_type = "All"
        self.filter_level = "All"
        self.filter_hr = "All"
        self.filter_position = "All"
        self.start_date = ""
        self.end_date = ""
        self.search_text = ""

        self.setup_ui()
        self.load_data()

    def setup_ui(self):

        self.setWindowTitle("Dashboard")

        layout = QVBoxLayout(self)

        # =========================
        # SUMMARY
        # =========================

        summary_group = QGroupBox("Monthly Summary")
        summary_layout = QGridLayout()

        self.total_label = QLabel("0")
        self.confirmed_label = QLabel("0")
        self.declined_label = QLabel("0")
        self.pending_label = QLabel("0")
        self.reschedule_label = QLabel("0")

        summary_layout.addWidget(
            QLabel("Total Interviews"), 0, 0
        )
        summary_layout.addWidget(
            self.total_label, 0, 1
        )

        summary_layout.addWidget(
            QLabel("Confirmed"), 0, 2
        )
        summary_layout.addWidget(
            self.confirmed_label, 0, 3
        )

        summary_layout.addWidget(
            QLabel("Declined"), 1, 0
        )
        summary_layout.addWidget(
            self.declined_label, 1, 1
        )

        summary_layout.addWidget(
            QLabel("Pending"), 1, 2
        )
        summary_layout.addWidget(
            self.pending_label, 1, 3
        )

        summary_layout.addWidget(
            QLabel("Reschedule Requested"), 2, 0
        )
        summary_layout.addWidget(
            self.reschedule_label, 2, 1
        )

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # =========================
        # UPCOMING INTERVIEWS
        # =========================

        upcoming_group = QGroupBox("Upcoming Interviews")
        upcoming_layout = QVBoxLayout()

        self.upcoming_table = QTableWidget()

        self.upcoming_table.setColumnCount(8)

        self.upcoming_table.setHorizontalHeaderLabels([
            "Candidate ID",
            "First Name",
            "Last Name",
            "Email",
            "Assigned HR",
            "Position",
            "Interview Type",
            "Scheduled Date/Time"
        ])

        self.upcoming_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.upcoming_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.upcoming_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        upcoming_layout.addWidget(
            self.upcoming_table
        )

        upcoming_group.setLayout(
            upcoming_layout
        )

        layout.addWidget(
            upcoming_group
        )

        # =========================
        # RECENT INTERVIEWS
        # =========================

        recent_group = QGroupBox("Recent Interviews")
        recent_layout = QVBoxLayout()

        self.recent_table = QTableWidget()

        self.recent_table.setColumnCount(13)

        self.recent_table.setHorizontalHeaderLabels([
            "Candidate ID",
            "First Name",
            "Last Name",
            "Email",
            "Assigned HR",
            "Position",
            "Interview Type",
            "Interview Level",
            "Interview Duration",
            "Scheduled Date/Time",
            "Status",
            "Responded At",
            "Attempts"
        ])

        self.recent_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.recent_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.recent_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        recent_layout.addWidget(
            self.recent_table
        )

        recent_group.setLayout(
            recent_layout
        )

        layout.addWidget(
            recent_group
        )

        # =========================
        # BUTTONS
        # =========================

        self.filter_btn = QPushButton(
            "Filter"
        )

        self.filter_btn.clicked.connect(
            self.open_filter_dialog
        )

        self.refresh_btn = QPushButton(
            "Refresh Dashboard"
        )

        self.refresh_btn.clicked.connect(
            self.load_data
        )

        bottom_buttons = QHBoxLayout()

        bottom_buttons.addStretch()

        bottom_buttons.addWidget(
            self.filter_btn
        )

        bottom_buttons.addWidget(
            self.refresh_btn
        )

        layout.addLayout(
            bottom_buttons
        )

    # =========================
    # FILTER
    # =========================

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

            self.load_data()

    # =========================
    # LOAD DATA
    # =========================

    def load_data(self):

        try:

            # =========================
            # MONTHLY SUMMARY
            # =========================

            summary = get_dashboard_summary()

            self.total_label.setText(
                str(summary["total"])
            )

            self.confirmed_label.setText(
                str(summary["confirmed"])
            )

            self.declined_label.setText(
                str(summary["declined"])
            )

            self.pending_label.setText(
                str(summary["pending"])
            )

            self.reschedule_label.setText(
                str(summary["reschedule_requested"])
            )

            # =========================
            # UPCOMING INTERVIEWS
            # =========================

            upcoming = get_upcoming_interviews(
                15,
                self.filter_type,
                self.filter_level,
                self.filter_hr,
                self.filter_position,
                self.start_date,
                self.end_date,
                self.search_text
            )

            self.upcoming_table.setRowCount(
                len(upcoming)
            )

            for row_index, row in enumerate(upcoming):

                for column_index, value in enumerate(row):

                    item = QTableWidgetItem(
                        str(value)
                        if value is not None
                        else ""
                    )

                    self.upcoming_table.setItem(
                        row_index,
                        column_index,
                        item
                    )

            # =========================
            # RECENT INTERVIEWS
            # =========================

            recent = self.get_recent_interviews()

            self.recent_table.setRowCount(
                len(recent)
            )

            for row_index, row in enumerate(recent):

                for column_index, value in enumerate(row):

                    item = QTableWidgetItem(
                        str(value)
                        if value is not None
                        else ""
                    )

                    self.recent_table.setItem(
                        row_index,
                        column_index,
                        item
                    )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Dashboard Error",
                str(e)
            )

    # =========================
    # RECENT INTERVIEWS
    # =========================

    def get_recent_interviews(self):

        db = SessionLocal()

        try:

            query = text("""
                SELECT
                    c.candidate_id,
                    c.first_name,
                    c.last_name,
                    c.email,
                    c.assigned_hr,
                    c.position_role,
                    c.interview_type,
                    c.interview_level,
                    c.interview_duration,
                    c.scheduled_datetime,
                    ir.status,
                    ir.responded_at,
                    ir.attempts

                FROM interview_responses ir

                INNER JOIN candidates c
                    ON ir.candidate_id = c.candidate_id

                ORDER BY ir.response_id DESC

                LIMIT 15
            """)

            result = db.execute(query)

            return result.fetchall()

        finally:

            db.close()

