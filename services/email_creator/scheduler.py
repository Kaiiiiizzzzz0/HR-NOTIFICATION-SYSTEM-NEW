from PySide6.QtCore import (
    QDateTime,
    QTime,
    QTimer
)

from PySide6.QtWidgets import QMessageBox

from .notification import (
    dispatch_pending_notifications
)

from services.weekly_report import (
    send_weekly_report
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


def start_weekly_report_scheduler(
    parent=None,
    weekday=0,
    hour=17,
    minute=0
):

    now = QDateTime.currentDateTime()

    target_date = now.date()

    # Qt:
    # Monday = 1
    # Tuesday = 2
    # ...
    # Sunday = 7
    target_day = weekday + 1

    days_until_target = (
        target_day
        - target_date.dayOfWeek()
    ) % 7

    target_date = target_date.addDays(
        days_until_target
    )

    target_time = QTime(
        hour,
        minute
    )

    target_datetime = QDateTime(
        target_date,
        target_time
    )

    if target_datetime <= now:

        target_datetime = (
            target_datetime.addDays(7)
        )

    interval_ms = now.msecsTo(
        target_datetime
    )

    timer = QTimer(parent)

    timer.setSingleShot(True)

    def on_timeout():

        try:

            result = send_weekly_report()

            if result.get("success"):

                message = (
                    "Weekly report sent successfully.\n"
                    f"Recipients: "
                    f"{result.get('recipients', 0)}"
                )

            else:

                message = (
                    "Weekly report failed.\n"
                    f"{result.get('message', 'Unknown error.')}"
                )

            print(message)

            if parent is not None:

                QMessageBox.information(
                    parent,
                    "Weekly Report Scheduler",
                    message
                )

        except Exception as error:

            message = (
                "Weekly report failed.\n"
                f"{error}"
            )

            print(message)

            if parent is not None:

                QMessageBox.critical(
                    parent,
                    "Weekly Report Scheduler",
                    message
                )

        finally:

            if parent is not None:

                parent.weekly_report_timer = (
                    start_weekly_report_scheduler(
                        parent,
                        weekday,
                        hour,
                        minute
                    )
                )

            else:

                start_weekly_report_scheduler(
                    None,
                    weekday,
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