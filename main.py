import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout
)

from services.email_creator.scheduler import (
    start_daily_scheduler
)

from views.candidate_window import (
    CandidateWindow
)

from views.response_window import (
    ResponseWindow
)

from views.dashboard import (
    DashboardWindow
)


class MainMenu(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "HR Notification System"
        )

        self.resize(
            400,
            300
        )

        layout = QVBoxLayout()

        title = QLabel(
            "HR Notification System"
        )

        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            padding: 15px;
        """)

        layout.addWidget(
            title
        )

        self.candidate_btn = QPushButton(
            "Candidate Management"
        )

        self.response_btn = QPushButton(
            "Interview Responses"
        )

        self.dashboard_btn = QPushButton(
            "Dashboard"
        )

        self.exit_btn = QPushButton(
            "Exit"
        )

        self.candidate_btn.setMinimumHeight(
            45
        )

        self.response_btn.setMinimumHeight(
            45
        )

        self.dashboard_btn.setMinimumHeight(
            45
        )

        self.exit_btn.setMinimumHeight(
            45
        )

        layout.addWidget(
            self.candidate_btn
        )

        layout.addWidget(
            self.response_btn
        )

        layout.addWidget(
            self.dashboard_btn
        )

        layout.addWidget(
            self.exit_btn
        )

        layout.addStretch()

        self.setLayout(
            layout
        )

        self.candidate_btn.clicked.connect(
            self.open_candidates
        )

        self.response_btn.clicked.connect(
            self.open_responses
        )

        self.dashboard_btn.clicked.connect(
            self.open_dashboard
        )

        self.exit_btn.clicked.connect(
            self.close
        )

    def open_candidates(self):

        self.candidate_window = (
            CandidateWindow()
        )

        self.candidate_window.show()

    def open_responses(self):

        self.response_window = (
            ResponseWindow()
        )

        self.response_window.show()

    def open_dashboard(self):

        self.dashboard_window = (
            DashboardWindow()
        )

        self.dashboard_window.show()


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = MainMenu()

    window.show()

    window.scheduler_timer = (
        start_daily_scheduler(
            window
        )
    )

    sys.exit(
        app.exec()
    )