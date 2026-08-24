from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QCalendarWidget,
    QDialogButtonBox
)


class FilterDialog(QDialog):

    def __init__(self, parent=None, current_filters=None):
        super().__init__(parent)
        self.current_filters = current_filters or {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Filter Candidates")
        self.resize(450, 360)

        search_field = QLineEdit(self.current_filters.get("search", ""))
        search_field.setPlaceholderText(
            "Search by name, email, phone, assigned HR, or position"
        )

        self.search_field = search_field

        type_combo = QComboBox()
        type_combo.addItems(["All", "VIRTUAL", "OVER-THE-PHONE", "ONSITE"])
        type_combo.setCurrentText(self.current_filters.get("type", "All"))
        self.type_combo = type_combo

        level_combo = QComboBox()
        level_combo.addItem("All")
        level_combo.addItems([
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
        ])
        level_combo.setCurrentText(self.current_filters.get("level", "All"))
        self.level_combo = level_combo

        hr_combo = QComboBox()
        hr_combo.addItem("All")
        hr_combo.addItems(self.current_filters.get("hr_list", []))
        hr_combo.setCurrentText(self.current_filters.get("hr", "All"))
        self.hr_combo = hr_combo

        position_combo = QComboBox()
        position_combo.addItem("All")
        position_combo.addItems(self.current_filters.get("position_list", []))
        position_combo.setCurrentText(self.current_filters.get("position", "All"))
        self.position_combo = position_combo

        start_date_field = QLineEdit(self.current_filters.get("start_date", ""))
        start_date_field.setReadOnly(True)
        self.start_date_field = start_date_field

        start_date_btn = QPushButton("Start Date")
        start_date_btn.clicked.connect(lambda: self.pick_filter_date(start_date_field))

        end_date_field = QLineEdit(self.current_filters.get("end_date", ""))
        end_date_field.setReadOnly(True)
        self.end_date_field = end_date_field

        end_date_btn = QPushButton("End Date")
        end_date_btn.clicked.connect(lambda: self.pick_filter_date(end_date_field))

        form = QFormLayout()
        form.addRow("Search", search_field)
        form.addRow("Type", type_combo)
        form.addRow("Level", level_combo)
        form.addRow("HR", hr_combo)
        form.addRow("Position", position_combo)

        start_row = QHBoxLayout()
        start_row.addWidget(start_date_field)
        start_row.addWidget(start_date_btn)
        form.addRow("Start Date", start_row)

        end_row = QHBoxLayout()
        end_row.addWidget(end_date_field)
        end_row.addWidget(end_date_btn)
        form.addRow("End Date", end_row)

        clear_button = QPushButton("Clear Filters")
        clear_button.clicked.connect(self.clear_fields)
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")

        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(clear_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(button_layout)

    def pick_filter_date(self, target):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")

        calendar = QCalendarWidget()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout = QVBoxLayout(dialog)
        layout.addWidget(calendar)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            target.setText(calendar.selectedDate().toString("yyyy-MM-dd"))

    def clear_fields(self):
        self.search_field.clear()
        self.type_combo.setCurrentIndex(0)
        self.level_combo.setCurrentIndex(0)
        self.hr_combo.setCurrentIndex(0)
        self.position_combo.setCurrentIndex(0)
        self.start_date_field.clear()
        self.end_date_field.clear()

    def get_filters(self):
        return {
            "search": self.search_field.text(),
            "type": self.type_combo.currentText(),
            "level": self.level_combo.currentText(),
            "hr": self.hr_combo.currentText(),
            "position": self.position_combo.currentText(),
            "start_date": self.start_date_field.text(),
            "end_date": self.end_date_field.text()
        }
