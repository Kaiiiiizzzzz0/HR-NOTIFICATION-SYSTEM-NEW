from PySide6.QtWidgets import QMessageBox


class CandidateSelection:

    def __init__(self, window):
        self.window = window

    def set_status_dropdowns_enabled(self, enabled):
        for row in range(self.window.table.table.rowCount()):
            combo = self.window.table.table.cellWidget(row, 13)
            if combo is not None:
                combo.setEnabled(enabled)

    def enter_selection_mode(self):
        self.window.table.set_selection_mode(True)
        self.set_status_dropdowns_enabled(False)

        self.window.add_btn.setEnabled(False)
        self.window.update_btn.setEnabled(False)
        self.window.preview_btn.setEnabled(False)
        self.window.send_notifications_btn.setEnabled(False)
        self.window.delete_btn.setEnabled(False)
        self.window.refresh_btn.setEnabled(False)
        self.window.filter_btn.setEnabled(False)

        self.window.select_candidates_btn.setVisible(False)
        self.window.select_all_btn.setVisible(True)
        self.window.send_selected_btn.setVisible(True)
        self.window.cancel_selection_btn.setVisible(True)
        self.window.send_selected_btn.setEnabled(False)

    def exit_selection_mode(self):
        self.window.table.set_selection_mode(False)
        self.set_status_dropdowns_enabled(True)

        self.window.add_btn.setEnabled(True)
        self.window.update_btn.setEnabled(False)
        self.window.preview_btn.setEnabled(True)
        self.window.send_notifications_btn.setEnabled(True)
        self.window.delete_btn.setEnabled(False)
        self.window.refresh_btn.setEnabled(True)
        self.window.filter_btn.setEnabled(True)

        self.window.select_candidates_btn.setVisible(True)
        self.window.select_all_btn.setVisible(False)
        self.window.send_selected_btn.setVisible(False)
        self.window.cancel_selection_btn.setVisible(False)

        self.window.clear_form()

    def select_all_candidates(self):
        if not self.window.table.selection_mode:
            return

        self.window.table.check_all_candidates()
        self.update_send_selected_button()

    def selection_checkbox_changed(self, item):
        if item.column() != 0:
            return

        if not self.window.table.selection_mode:
            return

        self.update_send_selected_button()

    def update_send_selected_button(self):
        count = self.window.table.checked_count()

        self.window.send_selected_btn.setText(
            f"Send Selected ({count})"
        )
        self.window.send_selected_btn.setEnabled(count > 0)

    def send_selected_notifications(self):
        if not self.window.table.selection_mode:
            return

        candidate_ids = self.window.table.get_checked_candidate_ids()

        if not candidate_ids:
            QMessageBox.warning(
                self.window,
                "Selection Required",
                "Please select at least one candidate."
            )
            return

        reply = QMessageBox.question(
            self.window,
            "Confirm Send",
            (
                f"Send notifications to "
                f"{len(candidate_ids)} selected "
                f"candidate(s)?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            results = self.dispatch_selected_notifications(candidate_ids)

            sent_count = sum(
                1
                for item in results
                if item.get("success")
            )
            failed_count = len(results) - sent_count

            QMessageBox.information(
                self.window,
                "Send Selected Notifications",
                (
                    f"Notifications processed: "
                    f"{len(results)}\n"
                    f"Sent: {sent_count}\n"
                    f"Failed: {failed_count}"
                )
            )

            self.exit_selection_mode()
            self.window.load_candidates()

        except Exception as e:
            QMessageBox.critical(
                self.window,
                "Send Selected Notifications Failed",
                str(e)
            )

    def dispatch_selected_notifications(self, candidate_ids):
        from services.email_creator.scheduler import dispatch_pending_notifications

        return dispatch_pending_notifications(
            edited_emails=self.window.edited_emails,
            candidate_ids=candidate_ids
        )