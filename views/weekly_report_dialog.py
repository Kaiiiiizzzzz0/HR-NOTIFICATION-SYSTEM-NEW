import re

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QWidget
)

from repositories.weekly_report_repository import (
    get_weekly_report_recipients,
    add_weekly_report_recipient,
    delete_weekly_report_recipient
)


class WeeklyReportDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Weekly Report Recipients"
        )

        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # =========================
        # EMAIL INPUT
        # =========================

        layout.addWidget(
            QLabel("Recipient Email")
        )

        input_layout = QHBoxLayout()

        self.email_input = QLineEdit()

        self.email_input.setPlaceholderText(
            "Enter email address"
        )

        add_button = QPushButton("Add")

        add_button.clicked.connect(
            self.add_recipient
        )

        input_layout.addWidget(
            self.email_input
        )

        input_layout.addWidget(
            add_button
        )

        layout.addLayout(
            input_layout
        )

        # =========================
        # RECIPIENT LIST
        # =========================

        layout.addWidget(
            QLabel("Saved Recipients")
        )

        self.recipient_list = QListWidget()

        layout.addWidget(
            self.recipient_list
        )

        # =========================
        # CLOSE
        # =========================

        close_button = QPushButton("Close")

        close_button.clicked.connect(
            self.accept
        )

        layout.addWidget(
            close_button
        )

        self.load_recipients()

    # =========================
    # LOAD RECIPIENTS
    # =========================

    def load_recipients(self):

        self.recipient_list.clear()

        recipients = (
            get_weekly_report_recipients()
        )

        for recipient in recipients:

            item = QListWidgetItem()

            row = QHBoxLayout()

            label = QLabel(
                recipient["email"]
            )

            delete_button = QPushButton("X")

            delete_button.setFixedWidth(35)

            recipient_id = (
                recipient["recipient_id"]
            )

            delete_button.clicked.connect(
                lambda checked=False,
                rid=recipient_id:
                self.delete_recipient(rid)
            )

            row.addWidget(
                label
            )

            row.addStretch()

            row.addWidget(
                delete_button
            )

            container = QWidget()

            container.setLayout(
                row
            )

            item.setSizeHint(
                container.sizeHint()
            )

            self.recipient_list.addItem(
                item
            )

            self.recipient_list.setItemWidget(
                item,
                container
            )

    # =========================
    # ADD RECIPIENT
    # =========================

    def add_recipient(self):

        email = (
            self.email_input.text().strip()
        )

        if not email:

            QMessageBox.warning(
                self,
                "Invalid Email",
                "Please enter an email address."
            )

            return

        if not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            email
        ):

            QMessageBox.warning(
                self,
                "Invalid Email",
                "Please enter a valid email address."
            )

            return

        try:

            add_weekly_report_recipient(
                email
            )

            self.email_input.clear()

            self.load_recipients()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Unable to Add Recipient",
                str(error)
            )

    # =========================
    # DELETE RECIPIENT
    # =========================

    def delete_recipient(
        self,
        recipient_id
    ):

        try:

            delete_weekly_report_recipient(
                recipient_id
            )

            self.load_recipients()

        except Exception as error:

            QMessageBox.warning(
                self,
                "Unable to Delete Recipient",
                str(error)
            )