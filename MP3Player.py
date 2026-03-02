from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtWidgets import QWidget

class MP3Player(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.playList = QMediaPlaylist()
        self.playList.setPlaybackMode(3)  # 设置列表播放模式--顺序循环

        # self.play_thread = QThread()
        # self.player.moveToThread(self.play_thread)
        # self.play_thread.start()

    def getList(self, file_path):
        self.playList.clear()
        play_content = list()  # 存放媒体源列表
        for j in file_path:
            url = QUrl.fromLocalFile(j)  # 获取媒体地址
            content = QMediaContent(url)  # 激活媒体源
            play_content.append(content)  # 媒体源存至play_content列表
        self.playList.addMedia(play_content)  # 把媒体源列表加入播放列表
        self.player.setPlaylist(self.playList)  # 把播放列表加入播放器

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def next_music(self):
        self.playList.next()
        self.player.play()

    def previous_music(self):
        self.playList.previous()
        self.player.play()

    def change_volume(self, num):
        # 修改音量
        self.player.setVolume(num)

    def change_time(self, num):
        t = int(num / 1000 * self.player.duration())
        self.player.setPosition(t)

    def get_time(self):
        return self.player.duration(), self.player.position()

    def state(self):
        return self.player.state()

    def currentIndex(self):
        return self.playList.currentIndex()

    def setCurrentIndex(self, num):
        self.playList.setCurrentIndex(num - 1)
