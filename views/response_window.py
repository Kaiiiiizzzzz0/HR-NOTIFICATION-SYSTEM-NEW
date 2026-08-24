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
    QAbstractItemView
)

from services.response import (
    get_all_responses,
    update_response
)


class ResponseWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interview Responses")
        self.resize(1200, 750)

        self.selected_response_id = None
        self.response_rows = []

        self.setup_ui()
        self.load_responses()

    def setup_ui(self):

        
        # TABLE
        

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

       
        details_group = QGroupBox(
            "Applicant Details"
        )

        details_form = QFormLayout()

        self.lbl_response_id = QLabel("-")
        self.lbl_candidate_id = QLabel("-")
        self.lbl_name = QLabel("-")
        self.lbl_email = QLabel("-")
        self.lbl_phone = QLabel("-")
        self.lbl_hr = QLabel("-")
        self.lbl_type = QLabel("-")
        self.lbl_level = QLabel("-")
        self.lbl_schedule = QLabel("-")
        self.lbl_status = QLabel("-")
        self.lbl_responded_at = QLabel("-")

        details_form.addRow(
            "Response ID",
            self.lbl_response_id
        )

        details_form.addRow(
            "Candidate ID",
            self.lbl_candidate_id
        )

        details_form.addRow(
            "Applicant",
            self.lbl_name
        )

        details_form.addRow(
            "Email",
            self.lbl_email
        )
        details_form.addRow(
            "Phone",
            self.lbl_phone
        )

        details_form.addRow(
            "Assigned HR",
            self.lbl_hr
        )

        details_form.addRow(
            "Interview Type",
            self.lbl_type
        )

        details_form.addRow(
            "Interview Level",
            self.lbl_level
        )

        details_form.addRow(
            "Interview Schedule",
            self.lbl_schedule
        )

        details_form.addRow(
            "Current Status",
            self.lbl_status
        )

        details_form.addRow(
            "Responded At",
            self.lbl_responded_at
        )

        details_group.setLayout(
            details_form
        )

        
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

        
        # STATUS CONTROLS
        

        bottom = QHBoxLayout()

        self.status = QComboBox()
        self.status.addItems([
            "Pending",
            "Confirmed",
            "Declined",
            "Reschedule Requested"
        ])

        self.refresh_btn = QPushButton(
            "Refresh List"
        )

        self.update_btn = QPushButton(
            "Update Status"
        )

        self.refresh_btn.clicked.connect(
            self.load_responses
        )

        self.update_btn.clicked.connect(
            self.update_selected
        )

        bottom.addWidget(
            QLabel("Interview Status")
        )

        bottom.addWidget(
            self.status
        )

        bottom.addStretch()

        bottom.addWidget(
            self.refresh_btn
        )

        bottom.addWidget(
            self.update_btn
        )

        layout = QVBoxLayout()

        layout.addWidget(self.table)
        layout.addWidget(details_group)
        layout.addWidget(message_group)
        layout.addLayout(bottom)

        self.setLayout(layout)

    def load_responses(self):

        try:

            rows = get_all_responses()

            self.response_rows = rows

            self.table.setRowCount(len(rows))

            for row_index, row in enumerate(rows):

                display = [
    row[0],      # Response ID
    row[1],      # Candidate ID
    row[2],      # First Name
    row[3],      # Last Name
    row[4],      # Email
    row[5],      # Phone
    row[6],      # Assigned HR
    row[7],      # Interview Type
    row[8],      # Interview Level
    row[9],      # Schedule
    row[10],     # Status
    row[12] if row[12] else "-"
]

                for column, value in enumerate(display):

                    self.table.setItem(
                        row_index,
                        column,
                        QTableWidgetItem(str(value))
                    )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )

    def select_response(self, row, column):

        data = self.response_rows[row]

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

        self.lbl_name.setText(
            f"{first_name} {last_name}"
        )

        self.lbl_email.setText(
            email
        )

        self.lbl_phone.setText(phone)      

        self.lbl_hr.setText(
            assigned_hr
        )

        self.lbl_type.setText(
            interview_type
        )

        self.lbl_level.setText(
            interview_level
        )

        self.lbl_response_id.setText(
            str(self.selected_response_id)
        )

        self.lbl_candidate_id.setText(
            str(data[1])
        )

        self.lbl_schedule.setText(
            str(interview_schedule)
        )
        self.lbl_status.setText(
            status
        )

        self.lbl_responded_at.setText(
            str(responded_at) if responded_at else "-"
        )

        if reply_message:

            self.reply_message.setPlainText(
                reply_message
            )

        else:

            self.reply_message.setPlainText(
                "No response message was provided."
            )

        index = self.status.findText(
            status
        )

        if index >= 0:

            self.status.setCurrentIndex(
                index
            )

    def update_selected(self):

        if self.selected_response_id is None:

            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select an applicant from the table first."
            )

            return

        try:

            update_response(
                self.selected_response_id,
                self.status.currentText()
            )

            QMessageBox.information(
                self,
                "Success",
                "Interview status updated successfully."
            )

            self.load_responses()

            if self.table.currentRow() >= 0:
                 self.select_response(self.table.currentRow(), 0)

        except Exception as e:

            QMessageBox.critical(
                self,
                "Database Error",
                str(e)
            )