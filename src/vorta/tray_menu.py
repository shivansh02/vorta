from PyQt5.QtWidgets import QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon

from .utils import get_asset
from .borg.borg_thread import BorgThread
from .models import BackupProfileModel


class TrayMenu(QSystemTrayIcon):
    def __init__(self, parent=None):
        icon = QIcon(get_asset('icons/hdd-o.png'))
        QSystemTrayIcon.__init__(self, icon, parent)
        self.app = parent
        menu = QMenu()

        # https://stackoverflow.com/questions/43657890/pyqt5-qsystemtrayicon-activated-signal-not-working
        menu.aboutToShow.connect(self.on_user_click)

        self.setContextMenu(menu)
        self.setVisible(True)
        self.show()

    def on_user_click(self):
        """
        Build system tray menu based on current status.

        """

        menu = self.contextMenu()
        menu.clear()

        status = menu.addAction(self.app.scheduler.next_job)
        status.setEnabled(False)

        profiles = BackupProfileModel.select()
        if profiles.count() > 1:
            profile_menu = menu.addMenu('Backup Now')
            for profile in profiles:
                new_item = profile_menu.addAction(profile.name)
                new_item.setData(profile.id)
                new_item.triggered.connect(lambda profile_id=profile.id: self.app.create_backup_action(profile_id))
        else:
            profile = profiles.first()
            profile_menu = menu.addAction('Backup Now')
            profile_menu.triggered.connect((lambda profile_id=profile.id: self.app.create_backup_action(profile_id)))

        if BorgThread.is_running():
            status.setText('Backup in Progress')
            profile_menu.setVisible(False)
            cancel_action = menu.addAction("Cancel Backup")
            cancel_action.triggered.connect(self.app.backup_cancelled_event.emit)
        else:
            status.setText(f'Next Task: {self.app.scheduler.next_job}')
            profile_menu.setEnabled(True)

        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.app.open_main_window_action)

        menu.addSeparator()

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.app.quit)
