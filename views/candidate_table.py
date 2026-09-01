from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QVBoxLayout,
    QComboBox
)


class CandidateTable(QWidget):

    # Emits:
    # candidate_id, new_status
    status_changed = Signal(int, str)

    # Emits:
    # candidate_id, new_application_count
    application_count_changed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selection_mode = False

        self.setup_ui()

    def setup_ui(self):
        self.table = QTableWidget()

        # Select + candidate columns + application count
        # + timestamp + notification status
        self.table.setColumnCount(15)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.table.setHorizontalHeaderLabels([
            "Select",
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
            "Application Count",
            "Timestamp",
            "Notification Status"
        ])

        # Hide checkbox column until selection mode is enabled.
        self.table.setColumnHidden(
            0,
            True
        )

        # Only Application Count should be editable.
        self.table.itemChanged.connect(
            self.on_item_changed
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(0)

        layout.addWidget(
            self.table
        )

    def set_selection_mode(self, enabled):
        self.selection_mode = enabled

        self.table.setColumnHidden(
            0,
            not enabled
        )

        if not enabled:
            self.clear_checked_candidates()

    def populate(self, rows, format_duration):

        # Prevent itemChanged from firing while
        # the table is being populated.
        self.table.blockSignals(True)

        try:
            self.table.setRowCount(
                len(rows)
            )

            for row_index, row in enumerate(rows):

                # -------------------------------------------------
                # Select checkbox
                # -------------------------------------------------
                checkbox = QTableWidgetItem()

                checkbox.setFlags(
                    Qt.ItemIsUserCheckable |
                    Qt.ItemIsEnabled
                )

                checkbox.setCheckState(
                    Qt.Unchecked
                )

                self.table.setItem(
                    row_index,
                    0,
                    checkbox
                )

                # -------------------------------------------------
                # Candidate information
                # -------------------------------------------------
                values = [
                    row.candidate_id,       # 1
                    row.first_name,         # 2
                    row.last_name,          # 3
                    row.email,              # 4
                    row.phone,              # 5
                    row.assigned_hr,        # 6
                    row.position_role,      # 7
                    row.interview_type,     # 8
                    row.interview_level,    # 9
                    format_duration(
                        row.interview_duration
                    ),                      # 10
                    row.scheduled_datetime, # 11
                    row.application_count,  # 12
                    row.created_at,         # 13
                ]

                for column_index, value in enumerate(values):

                    item = QTableWidgetItem(
                        str(value)
                    )

                    # Everything except Application Count
                    # is read-only.
                    if column_index != 11:
                        item.setFlags(
                            item.flags()
                            & ~Qt.ItemIsEditable
                        )

                    self.table.setItem(
                        row_index,
                        column_index + 1,
                        item
                    )

                # -------------------------------------------------
                # Notification Status
                # -------------------------------------------------
                status_combo = QComboBox()

                status_combo.addItems([
                    "Pending",
                    "Confirmed",
                    "Declined",
                    "Reschedule Requested"
                ])

                current_status = (
                    row.response_status
                    if row.response_status
                    else "Pending"
                )

                status_combo.blockSignals(
                    True
                )

                status_combo.setCurrentText(
                    current_status
                )

                status_combo.blockSignals(
                    False
                )

                status_combo.setProperty(
                    "candidate_id",
                    row.candidate_id
                )

                status_combo.currentTextChanged.connect(
                    lambda status,
                    combo=status_combo:
                    self.on_status_changed(
                        combo,
                        status
                    )
                )

                # Notification Status is now column 14.
                self.table.setCellWidget(
                    row_index,
                    14,
                    status_combo
                )

        finally:
            self.table.blockSignals(
                False
            )

    def on_item_changed(self, item):

        # Application Count is column 12.
        if item.column() != 12:
            return

        candidate_id_item = self.table.item(
            item.row(),
            1
        )

        if candidate_id_item is None:
            return

        candidate_id_text = (
            candidate_id_item.text().strip()
        )

        if not candidate_id_text:
            return

        try:
            application_count = int(
                item.text().strip()
            )

        except ValueError:

            # Restore the previous valid value.
            item.setText(
                "1"
            )

            return

        if application_count < 1:

            item.setText(
                "1"
            )

            return

        self.application_count_changed.emit(
            int(candidate_id_text),
            application_count
        )

    def on_status_changed(
        self,
        combo,
        status
    ):

        candidate_id = combo.property(
            "candidate_id"
        )

        if candidate_id is None:
            return

        self.status_changed.emit(
            int(candidate_id),
            status
        )

    def selected_candidate_row(self):
        return self.table.currentRow()

    def selected_candidate_data(self):

        row = self.selected_candidate_row()

        if row < 0:
            return None

        candidate_id_item = self.table.item(
            row,
            1
        )

        if candidate_id_item is None:
            return None

        candidate_id_text = (
            candidate_id_item.text().strip()
        )

        if not candidate_id_text:
            return None

        return {
            "candidate_id": int(
                candidate_id_text
            ),

            "first_name": self.table.item(
                row,
                2
            ).text(),

            "last_name": self.table.item(
                row,
                3
            ).text(),

            "email": self.table.item(
                row,
                4
            ).text(),

            "phone": self.table.item(
                row,
                5
            ).text(),

            "assigned_hr": self.table.item(
                row,
                6
            ).text(),

            "position_role": self.table.item(
                row,
                7
            ).text(),

            "interview_type": self.table.item(
                row,
                8
            ).text(),

            "interview_level": self.table.item(
                row,
                9
            ).text(),

            "scheduled_datetime": self.table.item(
                row,
                11
            ).text(),

            "application_count": int(
                self.table.item(
                    row,
                    12
                ).text()
            ),

            "created_at": self.table.item(
                row,
                13
            ).text(),
        }

    def get_checked_candidate_ids(self):

        selected_ids = set()

        for row in range(
            self.table.rowCount()
        ):

            checkbox = self.table.item(
                row,
                0
            )

            if checkbox is None:
                continue

            if checkbox.checkState() == Qt.Checked:

                candidate_id_item = self.table.item(
                    row,
                    1
                )

                if candidate_id_item is not None:

                    candidate_id_text = (
                        candidate_id_item.text().strip()
                    )

                    if candidate_id_text:

                        selected_ids.add(
                            int(candidate_id_text)
                        )

        return selected_ids

    def check_all_candidates(self):

        for row in range(
            self.table.rowCount()
        ):

            checkbox = self.table.item(
                row,
                0
            )

            if checkbox is not None:

                checkbox.setCheckState(
                    Qt.Checked
                )

    def uncheck_all_candidates(self):

        for row in range(
            self.table.rowCount()
        ):

            checkbox = self.table.item(
                row,
                0
            )

            if checkbox is not None:

                checkbox.setCheckState(
                    Qt.Unchecked
                )

    def clear_checked_candidates(self):
        self.uncheck_all_candidates()

    def checked_count(self):

        return len(
            self.get_checked_candidate_ids()
        )