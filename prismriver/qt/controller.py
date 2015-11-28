import random
import sys
import time
from functools import partial

from prismriver import main, util, mpris
from prismriver.mpris import MprisConnector, MprisConnectionException, MprisPlayer
from prismriver.qt.compat import pyqtSlot, QThread, pyqtSignal, QIcon, QApplication, QStyle, QSystemTrayIcon, QAction, \
    use_pyqt5
from prismriver.qt.tray import TrayIcon
from prismriver.qt.window import MainWindow, PlayerListModel


class MainController(object):
    def __init__(self, config, default_artist, default_title, default_player, connect_to_player, tray_action):
        super().__init__()

        self.config = config

        self.mpris_connect = MprisConnector()
        self.worker_search = None
        self.worker_mpris = None
        self.mpris_player = None

        self.main_window = None
        self.tray = None

        self.start_app(default_artist, default_title, default_player, connect_to_player, tray_action)

    def start_app(self, default_artist, default_title, default_player, connect_to_player, tray_action):
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon('prismriver/pixmaps/prismriver-lunasa.png'))
        app.setApplicationName('Lunasa Prismriver')

        self.main_window = MainWindow()

        self.main_window.edit_artist.setText(default_artist)
        self.main_window.edit_title.setText(default_title)

        self.main_window.btn_refresh.clicked.connect(self.refresh_players)

        self.init_layout(State.waiting)
        self.refresh_players(default_player)

        if connect_to_player:
            player = self.get_current_player()
            if player and (default_player is None or default_player == player.name):
                self.start_mpris()
        elif default_artist and default_title:
            self.start_search()

        show_tray = (tray_action != 'hide')
        show_main = (tray_action != 'minimize')

        if show_main:
            self.main_window.show()

        if show_tray:
            self.tray = TrayIcon()
            self.tray.activated.connect(self.toggle_main_window)
            self.tray.right_menu.aboutToShow.connect(self.update_tray_menu)

            self.tray.show()

        sys.exit(app.exec_())

    def init_layout(self, state):
        try:
            self.main_window.btn_search.clicked.disconnect()
        except TypeError:
            pass

        try:
            self.main_window.btn_connect.clicked.disconnect()
        except TypeError:
            pass

        if state == State.waiting:
            self.main_window.btn_search.setIcon(
                QIcon.fromTheme('edit-find', self.main_window.style().standardIcon(QStyle.SP_BrowserReload)))
            self.main_window.btn_search.setText('Search...')
            self.main_window.btn_search.clicked.connect(self.start_search)

            self.main_window.btn_connect.setText('Connect...')
            self.main_window.btn_connect.clicked.connect(self.start_mpris)

            self.main_window.btn_search.setEnabled(True)
            self.main_window.btn_connect.setEnabled(True)
            self.main_window.btn_refresh.setEnabled(True)

            self.main_window.edit_artist.setReadOnly(False)
            self.main_window.edit_title.setReadOnly(False)
            self.main_window.edit_player.setEnabled(True)

        elif state == State.searching:
            self.main_window.btn_search.setIcon(
                QIcon.fromTheme('process-stop', self.main_window.style().standardIcon(QStyle.SP_BrowserStop)))
            self.main_window.btn_search.setText('Stop')
            self.main_window.btn_search.clicked.connect(self.interrupt_search)

            self.main_window.btn_connect.setText('Connect...')
            self.main_window.btn_connect.clicked.connect(self.start_mpris)

            self.main_window.btn_search.setEnabled(True)
            self.main_window.btn_connect.setEnabled(False)
            self.main_window.btn_refresh.setEnabled(False)

            self.main_window.edit_artist.setReadOnly(True)
            self.main_window.edit_title.setReadOnly(True)
            self.main_window.edit_player.setEnabled(False)

        elif state == State.listening:
            self.main_window.btn_search.setIcon(
                QIcon.fromTheme('edit-find', self.main_window.style().standardIcon(QStyle.SP_BrowserReload)))
            self.main_window.btn_search.setText('Search...')
            self.main_window.btn_search.clicked.connect(self.start_search)

            self.main_window.btn_connect.setText('Disconnect')
            self.main_window.btn_connect.clicked.connect(self.stop_mpris)

            self.main_window.btn_search.setEnabled(False)
            self.main_window.btn_connect.setEnabled(True)
            self.main_window.btn_refresh.setEnabled(False)

            self.main_window.edit_artist.setReadOnly(True)
            self.main_window.edit_title.setReadOnly(True)
            self.main_window.edit_player.setEnabled(False)

        else:
            return

    def get_current_player(self):
        if use_pyqt5:
            return self.main_window.edit_player.currentData(PlayerListModel.DataRole)
        else:
            index = self.main_window.edit_player.currentIndex()
            return self.main_window.edit_player.itemData(index, PlayerListModel.DataRole)

    def set_status_message(self, message):
        self.main_window.statusBar().showMessage(message)

    def show_tray_notification(self, artist, title, songs):
        if self.tray:
            self.tray.showMessage(title + '\n' + artist,
                                  'Found {} results'.format(len(songs)),
                                  QSystemTrayIcon.NoIcon, 7000)

    @pyqtSlot()
    def start_search(self, background=False):
        if not background:
            self.init_layout(State.searching)

        self.set_status_message('Searching...')

        self.worker_search = SearchThread(self.main_window.edit_artist.text(), self.main_window.edit_title.text(),
                                          self.config, background)
        self.worker_search.resultReady.connect(self.finish_search)
        self.worker_search.start()

    @pyqtSlot()
    def finish_search(self, worker_id, artist, title, songs, total_time, background):
        if background:
            self.set_status_message('Listening to the player...')
            self.main_window.lyrics_table_model.update_data(songs)
        else:
            if not self.worker_search or (self.worker_search.worker_id != worker_id):
                return

            self.init_layout(State.waiting)
            self.set_status_message('Search completed in {}'.format(util.format_time_ms(total_time)))
            self.main_window.lyrics_table_model.update_data(songs)

        self.show_tray_notification(artist, title, songs)

    @pyqtSlot()
    def interrupt_search(self):
        self.init_layout(State.waiting)

        if self.worker_search:
            self.set_status_message('Search stopped')

            self.worker_search.quit()
            self.worker_search = None

    @pyqtSlot()
    def refresh_players(self, default_player):
        players = self.mpris_connect.get_players()
        self.main_window.edit_player.clear()
        self.main_window.edit_player_model.update_data(players)

        if players:
            if default_player:
                for pl in players:
                    if pl.name == default_player:
                        self.main_window.edit_player.setCurrentIndex(players.index(pl))
                        break
                else:
                    self.main_window.edit_player.setCurrentIndex(0)
            else:
                self.main_window.edit_player.setCurrentIndex(0)

    @pyqtSlot()
    def start_mpris(self, selected_player=None):
        if selected_player:
            players = self.mpris_connect.get_players()
            self.main_window.edit_player.setCurrentIndex(players.index(selected_player))

        player = self.get_current_player()
        if player:
            self.init_layout(State.listening)
            self.set_status_message('Listening to the player...')

            self.mpris_player = player
            self.worker_mpris = MprisThread(self.mpris_connect, player)

            self.worker_mpris.meta_ready.connect(self.update_mpris_results)
            self.worker_mpris.connection_closed.connect(self.stop_mpris)
            self.worker_mpris.start()

    @pyqtSlot(MprisPlayer)
    def start_mpris_from_tray(self, selected_player):
        if selected_player == self.mpris_player:
            return
        else:
            self.stop_mpris()
            self.start_mpris(selected_player)

    @pyqtSlot()
    def stop_mpris(self):
        self.init_layout(State.waiting)
        self.set_status_message('Player listener stopped')
        self.mpris_player = None
        self.worker_mpris.active = False

    @pyqtSlot()
    def update_mpris_results(self, meta):
        current_artist = self.main_window.edit_artist.text()
        current_title = self.main_window.edit_title.text()

        if (current_artist != meta[0] or current_title != meta[1]) and (meta[0] and meta[1]):
            self.main_window.edit_artist.setText(meta[0])
            self.main_window.edit_title.setText(meta[1])
            self.start_search(True)

    @pyqtSlot(QSystemTrayIcon.ActivationReason)
    def toggle_main_window(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.main_window.isHidden():
                self.main_window.show()
            else:
                self.main_window.hide()

    @pyqtSlot()
    def update_tray_menu(self):
        self.tray.right_menu.clear()

        show_action = QAction('Show &Main Window', self.tray.right_menu)
        show_action.triggered.connect(self.main_window.show)
        self.tray.right_menu.addAction(show_action)

        self.tray.right_menu.addSeparator()

        players = self.main_window.edit_player_model.players
        if players:
            for player in players:
                if player == self.mpris_player:
                    player_action = QAction(player.identity + ' [connected]', self.tray.right_menu)
                    font = player_action.font()
                    font.setBold(True)
                    player_action.setFont(font)
                else:
                    player_action = QAction(player.identity, self.tray.right_menu)

                player_action.setIcon(QIcon(mpris.get_player_icon_path(player.name)))
                player_action.triggered.connect(partial(self.start_mpris_from_tray, selected_player=player))

                self.tray.right_menu.addAction(player_action)

        self.tray.right_menu.addSeparator()

        quit_action = QAction('&Quit', self.tray.right_menu)
        quit_action.triggered.connect(QApplication.quit)
        self.tray.right_menu.addAction(quit_action)


class SearchThread(QThread):
    resultReady = pyqtSignal(int, str, str, list, float, bool)

    def __init__(self, artist, title, config, background):
        super().__init__()

        self.worker_id = random.randint(1, 999999999)

        self.artist = artist
        self.title = title
        self.config = config
        self.background = background

    def run(self):
        start_time = time.time()
        songs = main.search(self.artist, self.title, self.config)
        total_time = time.time() - start_time

        self.resultReady.emit(self.worker_id, self.artist, self.title, songs, total_time, self.background)


class MprisThread(QThread):
    meta_ready = pyqtSignal(list)
    connection_closed = pyqtSignal(bool)

    def __init__(self, connector, player):
        super().__init__()

        self.connector = connector
        self.player = player
        self.active = True

    def run(self):
        try:
            if self.connector.connect(self.player):
                while self.active:
                    meta = self.connector.get_meta()
                    self.meta_ready.emit(meta)
                    time.sleep(2)
        except MprisConnectionException:
            self.connection_closed.emit(True)


class State(object):
    waiting = 1
    searching = 2
    listening = 3
