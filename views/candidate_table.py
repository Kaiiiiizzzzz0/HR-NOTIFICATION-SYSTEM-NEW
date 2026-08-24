from PySide6.QtWidgets import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QVBoxLayout,
    QLabel
)


class CandidateTable(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(12)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Phone",
            "Assigned HR",
            "Position/Role",
            "Type",
            "Level",
            "Duration",
            "Schedule",
            "Notification Status"
        ])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.table)

    def populate(self, rows, format_duration):
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            response_status = None
            response_sent_at = None

            try:
                response_status = row.response_status
                response_sent_at = row.response_sent_at
            except Exception:
                if len(row) > 11:
                    response_status = row[11]
                if len(row) > 12:
                    response_sent_at = row[12]

            if response_status == "Pending":
                notification_status = "Already Sent" if response_sent_at else "Pending"
            else:
                notification_status = response_status or ""

            values = [
                row.candidate_id,
                row.first_name,
                row.last_name,
                row.email,
                row.phone,
                row.assigned_hr,
                row.position_role,
                row.interview_type,
                row.interview_level,
                format_duration(row.interview_duration),
                row.scheduled_datetime,
                notification_status
            ]

            for column_index, value in enumerate(values):
                self.table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(str(value))
                )

    def selected_candidate_row(self):
        return self.table.currentRow()

    def selected_candidate_data(self):
        row = self.selected_candidate_row()
        if row < 0:
            return None

        try:
            return {
                "candidate_id": int(self.table.item(row, 0).text()),
                "first_name": self.table.item(row, 1).text(),
                "last_name": self.table.item(row, 2).text(),
                "email": self.table.item(row, 3).text(),
                "phone": self.table.item(row, 4).text(),
                "assigned_hr": self.table.item(row, 5).text(),
                "position_role": self.table.item(row, 6).text(),
                "interview_type": self.table.item(row, 7).text(),
                "interview_level": self.table.item(row, 8).text(),
                "scheduled_datetime": self.table.item(row, 10).text(),
            }
        except Exception:
            return None
