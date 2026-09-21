from PySide6.QtCore import (
    QDateTime,
    QTime,
    QTimer
)

from PySide6.QtWidgets import QMessageBox

from .notification import (
    dispatch_pending_notifications
)

def start_daily_scheduler(
    parent=None,
    hour=9,
    minute=0
):

    scheduler_time = QTime(
        hour,
        minute
    )

    now = QDateTime.currentDateTime()

    today_run = QDateTime(
        now.date(),
        scheduler_time
    )

    if today_run <= now:

        today_run = (
            today_run.addDays(1)
        )

    interval_ms = now.msecsTo(
        today_run
    )

    timer = QTimer(parent)

    timer.setSingleShot(True)

    def on_timeout():

        results = (
            dispatch_pending_notifications()
        )

        sent_count = sum(
            1
            for item in results
            if item.get("success")
        )

        failed_count = (
            len(results) - sent_count
        )

        message = (
            f"Daily scheduler processed: "
            f"{len(results)}\n"
            f"Sent: {sent_count}\n"
            f"Failed: {failed_count}"
        )

        print(message)

        if failed_count > 0:

            first_error = next(
                (
                    item.get("error")
                    for item in results
                    if not item.get("success")
                ),
                None
            )

            if first_error:

                print(
                    f"First failure: {first_error}"
                )

        if parent is not None:

            QMessageBox.information(
                parent,
                "Daily Notification Scheduler",
                message
            )

            parent.scheduler_timer = (
                start_daily_scheduler(
                    parent,
                    hour,
                    minute
                )
            )

        else:

            start_daily_scheduler(
                None,
                hour,
                minute
            )

    timer.timeout.connect(
        on_timeout
    )

    timer.start(
        interval_ms
    )

    return timer


if __name__ == "__main__":

    summary = (
        dispatch_pending_notifications()
    )

    for item in summary:

        print(item)