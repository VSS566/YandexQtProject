import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from interface import Ui_MainWindow


class AudioPlayer(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.music_name = None
        self.offset = None
        self.timer = QTimer()
        duration_timer = QTimer(self, timeout=self.on_timeout, interval=1000)
        duration_timer.start()
        self.setupUi(self)
        self.InitQt()
        self.playlist = []
        self.state = "Play"
        self.path = "D:/"

    def InitQt(self):
        self.position = 0
        self.player = QMediaPlayer()
        self.modes = {"mp3", "wav"}
        self.recentOpened = {}
        self.loadBtn.clicked.connect(self.load)
        self.playBtn.clicked.connect(self.play)
        self.clearrecentBtn.clicked.connect(self.clearRecent)
        self.dirList.clicked.connect(self.scanDir)
        self.recentList.clicked.connect(self.scanRecent)
        self.moveLeftBtn.clicked.connect(self.move_backward)
        self.moveRightBtn.clicked.connect(self.move_forward)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.stateChanged.connect(self.state_changed)
        self.listDir(self.searchstrLineEdit.text())
        self.horizontalSlider.setValue(100)
        self.horizontalSlider.valueChanged.connect(self.setVolume)

    def setVolume(self, v):
        self.player.setVolume(v)

    def closeEvent(self, a0, QCloseEvent=None):
        exit()

    def on_timeout(self):
        self.position = self.getDurationOfMusic()
        seconds = self.position // 1000
        minutes = str(seconds // 60)
        seconds = str(seconds % 60)
        seconds = "0" + seconds if len(seconds) == 1 else seconds
        minutes = "0" + minutes if len(minutes) == 1 else minutes
        res = f"{minutes}:{seconds}"
        self.durationNum.display(res)

    def scanRecent(self):
        name = self.recentList.currentItem().text()
        self.searchstrLineEdit.setText(self.recentOpened[name])

    def clearRecent(self):
        self.recentOpened = {}
        self.recentList.clear()

    def play(self):
        music_path = self.searchstrLineEdit.text()
        music_fullname = music_path.split('/')[-1].split('.')
        music_name = '.'.join(music_fullname[:-1])
        if music_name and self.state == "Play":
            self.playBtn.setText("Pause")
            self.state = "Pause"
            if self.path != music_path:
                self.position = 0
                self.path = music_path
            self.label_playing_music.setText(music_name)
            print(music_path, music_fullname[-1], sep='\n')
            file_url = QUrl.fromLocalFile(music_path)
            self.player.setMedia(QMediaContent(file_url))
            self.player.setPosition(self.position)
            self.player.play()
        else:
            self.playBtn.setText("Play")
            self.state = "Play"
            self.player.pause()
            paused = self.getDurationOfMusic()
            self.position = paused

        self.recentOpened[music_name] = music_path
        self.recentList.clear()
        for i in reversed(self.recentOpened.keys()):
            self.recentList.addItem(i)
        self.timer.timeout.connect(self.update)
        self.timer.start(150)

        self.music_name = music_name + "     "
        self.offset = 0

    def state_changed(self, state):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def getDurationOfMusic(self):
        return self.player.position()

    def listDir(self, path: str):
        self.dirList.addItem("..")
        if os.path.isfile(path):
            path = '/'.join(path.split('/')[:-1])
        dfs = os.listdir(path)
        lst = []
        if dfs:
            for df in dfs:
                if df.split('.')[-1] in self.modes:
                    lst.append(df)
                elif os.path.isdir(path + '/' + df):
                    print(df)
                    self.dirList.addItem(df)
        for i in lst:
            self.dirList.addItem(i)

    def scanDir(self):
        name = self.dirList.currentItem().text()
        if name != "..":
            sos_path = self.searchstrLineEdit.text()
            if os.path.isfile(self.searchstrLineEdit.text()):
                self.searchstrLineEdit.setText('/'.join(self.searchstrLineEdit.text().split('/')[:-1]))
            self.searchstrLineEdit.setText(f"{self.searchstrLineEdit.text()}/{name}")
            if os.path.isdir(self.searchstrLineEdit.text()):
                self.dirList.clear()
                self.listDir(self.searchstrLineEdit.text())
            else:
                self.searchstrLineEdit.setText('/'.join(self.searchstrLineEdit.text().split('/')[:-1] + [name]))
            if not os.path.exists(self.searchstrLineEdit.text()):
                self.searchstrLineEdit.setText(sos_path)
        else:
            self.searchstrLineEdit.setText('/'.join(self.searchstrLineEdit.text().split('/')[:-1]))
            self.dirList.clear()
            self.listDir(self.searchstrLineEdit.text())

    def backPath(self):
        self.searchstrLineEdit.setText('/'.join(self.searchstrLineEdit.text().split('/')[:-1]))

    def load(self):
        audio_formats = f"Audio ({', '.join(f'*.{x}' for x in self.modes)})"
        filenames, _ = QFileDialog.getOpenFileNames(self, "Выберите несколько файлов", ".", audio_formats)

        self.dirList.clear()
        if filenames:
            if len(filenames) > 1:
                for i in filenames:
                    music_name = i.split('/')[-1]
                    self.dirList.addItem(music_name)
            else:
                self.searchstrLineEdit.setText(filenames[0])
                self.listDir(self.searchstrLineEdit.text())
            self.player.stop()
            self.state = "Play"
            self.playBtn.setText(self.state)

    def update(self):
        display_text = self.music_name[self.offset:] + self.music_name[:self.offset]
        self.label_playing_music.setText(display_text)
        self.offset = (self.offset + 1) % len(self.music_name)

    def position_changed(self, position):
        self.musicTimeBar.setValue(position)

    def duration_changed(self, duration):
        self.musicTimeBar.setRange(0, duration)

    def state_changed(self, state):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def move_forward(self):
        self.player.setPosition(int(self.player.position()) + 2000)

    def move_backward(self):
        self.player.setPosition(int(self.player.position()) - 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AudioPlayer()
    ex.show()
    sys.exit(app.exec())
