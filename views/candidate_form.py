from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QCalendarWidget
)


class CandidateForm(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        form = QFormLayout()

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.assigned_hr = QLineEdit()
        self.position_role = QLineEdit()

        self.interview_type = QComboBox()
        self.interview_type.addItems(["VIRTUAL", "OVER-THE-PHONE", "ONSITE"])

        self.interview_level = QComboBox()
        self.interview_level.addItems([
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

        self.interview_duration = QLineEdit()
        self.interview_duration.setPlaceholderText("HH:MM")
        self.interview_duration.editingFinished.connect(self.normalize_duration_input)

        self.datetime = QLineEdit()
        self.datetime.setPlaceholderText("YYYY-MM-DD")
        self.datetime.setReadOnly(True)

        self.pick_date_btn = QPushButton("Pick Date")
        self.pick_date_btn.clicked.connect(self.open_calendar_dialog)

        self.hour_combo = QComboBox()
        self.hour_combo.addItems([str(hour) for hour in range(1, 13)])
        self.hour_combo.setCurrentIndex(0)
        self.hour_combo.currentIndexChanged.connect(self.update_schedule_display)

        self.minute_combo = QComboBox()
        self.minute_combo.addItems(["00", "15", "30", "45"])
        self.minute_combo.currentIndexChanged.connect(self.update_schedule_display)

        self.meridiem_combo = QComboBox()
        self.meridiem_combo.addItems(["AM", "PM"])
        self.meridiem_combo.currentIndexChanged.connect(self.update_schedule_display)

        self.schedule_display = QLabel("No date selected")

        form.addRow("First Name", self.first_name)
        form.addRow("Last Name", self.last_name)
        form.addRow("Email", self.email)
        form.addRow("Phone Number", self.phone)
        form.addRow("Assigned HR", self.assigned_hr)
        form.addRow("Position/Role", self.position_role)
        form.addRow("Interview Duration", self.interview_duration)
        form.addRow("Interview Modality", self.interview_type)
        form.addRow("Interview Level", self.interview_level)

        schedule_row = QHBoxLayout()
        schedule_row.addWidget(self.datetime)
        schedule_row.addWidget(self.pick_date_btn)
        form.addRow("Schedule", schedule_row)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("Hour"))
        time_row.addWidget(self.hour_combo)
        time_row.addWidget(QLabel("Minute"))
        time_row.addWidget(self.minute_combo)
        time_row.addWidget(QLabel("AM/PM"))
        time_row.addWidget(self.meridiem_combo)
        form.addRow("Time", time_row)
        form.addRow("Selected Schedule", self.schedule_display)

        self.setLayout(form)

    def normalize_duration_input(self):
        text = self.interview_duration.text().strip()
        if not text:
            return

        if ":" in text:
            parts = text.split(":")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                hours = int(parts[0])
                minutes = int(parts[1])
                if 0 <= minutes < 60 and hours >= 0:
                    self.interview_duration.setText(f"{hours:02d}:{minutes:02d}")
                    return
        elif text.isdigit():
            total_minutes = int(text)
            if total_minutes >= 0:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                self.interview_duration.setText(f"{hours:02d}:{minutes:02d}")
                return

        self.interview_duration.setText(text)

    def update_schedule_display(self):
        if not self.datetime.text():
            self.schedule_display.setText("No date selected")
            return

        hour = self.hour_combo.currentText()
        minute = self.minute_combo.currentText()
        meridiem = self.meridiem_combo.currentText()

        if meridiem == "PM" and hour != "12":
            hour_value = int(hour) + 12
        elif meridiem == "AM" and hour == "12":
            hour_value = 0
        else:
            hour_value = int(hour)

        self.schedule_display.setText(
            f"{self.datetime.text()} {hour_value:02d}:{minute}:00"
        )

    def open_calendar_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Interview Date")
        dialog.resize(320, 280)

        calendar = QCalendarWidget(dialog)
        calendar.setGridVisible(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout = QVBoxLayout(dialog)
        layout.addWidget(calendar)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            selected_date = calendar.selectedDate()
            self.datetime.setText(selected_date.toString("yyyy-MM-dd"))
            self.update_schedule_display()

    def get_data(self):
        self.update_schedule_display()
        return {
            "first_name": self.first_name.text(),
            "last_name": self.last_name.text(),
            "email": self.email.text(),
            "phone": self.phone.text(),
            "assigned_hr": self.assigned_hr.text(),
            "position_role": self.position_role.text(),
            "interview_type": self.interview_type.currentText(),
            "interview_level": self.interview_level.currentText(),
            "interview_duration": self.interview_duration.text(),
            "scheduled_datetime": self.schedule_display.text()
        }

    def set_candidate_data(self, candidate):
        self.first_name.setText(candidate.get("first_name", ""))
        self.last_name.setText(candidate.get("last_name", ""))
        self.email.setText(candidate.get("email", ""))
        self.phone.setText(candidate.get("phone", ""))
        self.assigned_hr.setText(candidate.get("assigned_hr", ""))
        self.position_role.setText(candidate.get("position_role", ""))
        self.interview_duration.setText(candidate.get("interview_duration", ""))

        type_text = candidate.get("interview_type", "")
        type_index = self.interview_type.findText(type_text)
        if type_index >= 0:
            self.interview_type.setCurrentIndex(type_index)

        level_text = candidate.get("interview_level", "")
        level_index = self.interview_level.findText(level_text)
        if level_index >= 0:
            self.interview_level.setCurrentIndex(level_index)

        schedule_text = candidate.get("scheduled_datetime", "")
        if schedule_text and schedule_text != "-":
            self.schedule_display.setText(schedule_text)
            try:
                date_part, time_part = schedule_text.split(" ")
                self.datetime.setText(date_part)
                hh, mm, ss = time_part.split(":")
                hour = int(hh)

                if hour == 0:
                    self.hour_combo.setCurrentText("12")
                    self.meridiem_combo.setCurrentText("AM")
                elif hour == 12:
                    self.hour_combo.setCurrentText("12")
                    self.meridiem_combo.setCurrentText("PM")
                elif hour > 12:
                    self.hour_combo.setCurrentText(str(hour - 12))
                    self.meridiem_combo.setCurrentText("PM")
                else:
                    self.hour_combo.setCurrentText(str(hour))
                    self.meridiem_combo.setCurrentText("AM")

                self.minute_combo.setCurrentText(mm)
            except Exception:
                pass
        else:
            self.datetime.clear()
            self.schedule_display.setText("No date selected")

    def clear(self):
        self.first_name.clear()
        self.last_name.clear()
        self.email.clear()
        self.phone.clear()
        self.assigned_hr.clear()
        self.position_role.clear()
        self.interview_duration.clear()
        self.datetime.clear()
        self.schedule_display.setText("No date selected")
        self.interview_type.setCurrentIndex(0)
        self.interview_level.setCurrentIndex(0)
        self.hour_combo.setCurrentIndex(0)
        self.minute_combo.setCurrentIndex(0)
        self.meridiem_combo.setCurrentIndex(0)
