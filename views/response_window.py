from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QAbstractItemView,
    QHeaderView
)

from services.response import (
    get_all_responses
)

from services.email_receiver.imap_receiver import check_inbox
from PySide6.QtCore import QTimer


class ResponseWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interview Responses")
        self.resize(1200, 750)

        self.selected_response_id = None
        self.response_rows = []
        self.filtered_rows = []

        self.setup_ui()
        self.load_responses()

        self.imap_timer = QTimer(self)
        self.imap_timer.timeout.connect(
            self.check_incoming_emails
        )
        self.imap_timer.start(30000)

    def setup_ui(self):

        # =========================
        # TABLE
        # =========================

        self.table = QTableWidget()
        self.table.setColumnCount(12)

        self.table.setHorizontalHeaderLabels([
            "Response ID",
            "Candidate ID",
            "First Name",
            "Last Name",
            "Email",
            "Phone",
            "Assigned HR",
            "Interview Type",
            "Interview Level",
            "Interview Schedule",
            "Status",
            "Responded At"
        ])

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.table.cellClicked.connect(
            self.select_response
        )

        # Make all columns use the full
        # horizontal space of the table.
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # =========================
        # APPLICANT DETAILS
        # =========================

        details_group = QGroupBox(
            "Applicant Details"
        )

        details_layout = QHBoxLayout()

        # LEFT SIDE

        left_form = QFormLayout()

        self.lbl_response_id = QLabel("-")
        self.lbl_candidate_id = QLabel("-")
        self.lbl_name = QLabel("-")
        self.lbl_email = QLabel("-")
        self.lbl_phone = QLabel("-")

        left_form.addRow(
            "Response ID",
            self.lbl_response_id
        )

        left_form.addRow(
            "Candidate ID",
            self.lbl_candidate_id
        )

        left_form.addRow(
            "Applicant",
            self.lbl_name
        )

        left_form.addRow(
            "Email",
            self.lbl_email
        )

        left_form.addRow(
            "Phone",
            self.lbl_phone
        )

        # RIGHT SIDE

        right_form = QFormLayout()

        self.lbl_hr = QLabel("-")
        self.lbl_type = QLabel("-")
        self.lbl_level = QLabel("-")
        self.lbl_schedule = QLabel("-")
        self.lbl_status = QLabel("-")
        self.lbl_responded_at = QLabel("-")

        right_form.addRow(
            "Assigned HR",
            self.lbl_hr
        )

        right_form.addRow(
            "Interview Type",
            self.lbl_type
        )

        right_form.addRow(
            "Interview Level",
            self.lbl_level
        )

        right_form.addRow(
            "Interview Schedule",
            self.lbl_schedule
        )

        right_form.addRow(
            "Current Status",
            self.lbl_status
        )

        right_form.addRow(
            "Responded At",
            self.lbl_responded_at
        )

        details_layout.addLayout(
            left_form
        )

        details_layout.addLayout(
            right_form
        )

        details_group.setLayout(
            details_layout
        )

        # =========================
        # APPLICANT RESPONSE
        # =========================

        message_group = QGroupBox(
            "Applicant Response"
        )

        self.reply_message = QTextEdit()
        self.reply_message.setReadOnly(True)

        message_layout = QVBoxLayout()

        message_layout.addWidget(
            self.reply_message
        )

        message_group.setLayout(
            message_layout
        )

        # =========================
        # FILTER CONTROLS
        # =========================

        bottom = QHBoxLayout()

        bottom.addWidget(
            QLabel("Interview Status")
        )

        self.status = QComboBox()

        self.status.addItems([
            "All",
            "Pending",
            "Confirmed",
            "Declined",
            "Reschedule Requested"
        ])

        self.status.currentTextChanged.connect(
            self.filter_responses
        )

        bottom.addWidget(
            self.status
        )

        bottom.addStretch()

        self.refresh_btn = QPushButton(
            "Refresh List"
        )

        self.refresh_btn.clicked.connect(
            self.load_responses
        )

        bottom.addWidget(
            self.refresh_btn
        )

        # =========================
        # MAIN LAYOUT
        # =========================

        layout = QVBoxLayout()

        layout.addWidget(
            self.table,
            6
        )

        layout.addWidget(
            details_group,
            0
        )

        layout.addWidget(
            message_group,
            3
        )

        layout.addLayout(
            bottom,
            0
        )

        self.setLayout(
            layout
        )

    # =========================
    # LOAD RESPONSES
    # =========================

    def load_responses(self):

        try:

            rows = get_all_responses()

            self.response_rows = rows

            self.filter_responses(
                self.status.currentText()
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    # =========================
    # FILTER RESPONSES
    # =========================

    def filter_responses(
        self,
        selected_status
    ):

        if selected_status == "All":

            filtered_rows = self.response_rows

        else:

            filtered_rows = [
                row
                for row in self.response_rows
                if row[10] == selected_status
            ]

        self.filtered_rows = filtered_rows

        self.table.clearContents()

        self.table.setRowCount(
            len(filtered_rows)
        )

        for row_index, row in enumerate(
            filtered_rows
        ):

            display = [
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[12] if row[12] else "-"
            ]

            for column, value in enumerate(
                display
            ):

                self.table.setItem(
                    row_index,
                    column,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        self.clear_details()

    # =========================
    # CLEAR DETAILS
    # =========================

    def clear_details(self):

        self.selected_response_id = None

        self.lbl_response_id.setText("-")
        self.lbl_candidate_id.setText("-")
        self.lbl_name.setText("-")
        self.lbl_email.setText("-")
        self.lbl_phone.setText("-")
        self.lbl_hr.setText("-")
        self.lbl_type.setText("-")
        self.lbl_level.setText("-")
        self.lbl_schedule.setText("-")
        self.lbl_status.setText("-")
        self.lbl_responded_at.setText("-")

        self.reply_message.clear()

    # =========================
    # SELECT RESPONSE
    # =========================

    def select_response(
        self,
        row,
        column
    ):

        if row < 0 or row >= len(
            self.filtered_rows
        ):
            return

        data = self.filtered_rows[row]

        self.selected_response_id = data[0]

        first_name = data[2]
        last_name = data[3]
        email = data[4]
        phone = data[5]
        assigned_hr = data[6]
        interview_type = data[7]
        interview_level = data[8]
        interview_schedule = data[9]
        status = data[10]
        reply_message = data[11]
        responded_at = data[12]

        self.lbl_response_id.setText(
            str(self.selected_response_id)
        )

        self.lbl_candidate_id.setText(
            str(data[1])
        )

        self.lbl_name.setText(
            f"{first_name} {last_name}"
        )

        self.lbl_email.setText(
            email
        )

        self.lbl_phone.setText(
            phone
        )

        self.lbl_hr.setText(
            assigned_hr
        )

        self.lbl_type.setText(
            interview_type
        )

        self.lbl_level.setText(
            interview_level
        )

        self.lbl_schedule.setText(
            str(interview_schedule)
        )

        self.lbl_status.setText(
            status
        )

        self.lbl_responded_at.setText(
            str(responded_at)
            if responded_at
            else "-"
        )

        if reply_message:

            self.reply_message.setPlainText(
                reply_message
            )

        else:

            self.reply_message.setPlainText(
                "No response message was provided."
            )

    # =========================
    # CHECK INCOMING EMAILS
    # =========================

    def check_incoming_emails(self):

        try:

            processed = check_inbox()

            if processed:

                self.load_responses()

                current_row = (
                    self.table.currentRow()
                )

                if current_row >= 0:

                    self.select_response(
                        current_row,
                        0
                    )

        except Exception as e:

            print(
                f"IMAP check failed: {e}"
            )