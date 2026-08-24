from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox
)


class EmailPreviewDialog(QDialog):

    def __init__(self, subject, body, parent=None):
        super().__init__(parent)

        self.subject = subject
        self.body = body

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Email Preview")
        self.resize(700, 600)

        subject_label = QLabel("Subject")

        self.subject_edit = QLineEdit(self.subject)

        self.body_edit = QTextEdit()

        # Render the email as HTML while keeping it editable.
        self.body_edit.setHtml(self.body)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.save_changes)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)

        layout.addWidget(subject_label)
        layout.addWidget(self.subject_edit)

        layout.addWidget(QLabel("Email Body"))
        layout.addWidget(self.body_edit)

        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_changes(self):
        self.subject = self.subject_edit.text()
        self.body = self.body_edit.toHtml()

        self.accept()

    def get_content(self):
        return (
            self.subject,
            self.body
        )