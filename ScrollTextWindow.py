import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QLabel


class ScrollTextWindow(QLabel):
    """ 滚动字幕 """

    def __init__(self, songName, height=50,width=950, fontsize=20, color=QColor(0, 0, 0), parent=None,spacing=50):
        super().__init__(parent)
        self.songName = songName
        # 实例化定时器
        self.timer = QTimer(self)
        # 设置刷新时间和移动距离
        self.timeStep = int(2*width/100)
        self.moveStep = 1
        self.songCurrentIndex = 0
        self.songerCurrentIndex = 0
        # 设置字符串溢出标志位
        self.isSongNameAllOut = False
        # 设置两段字符串之间留白的宽度
        self.spacing = spacing
        # 设置字体大小
        self.fontsize = fontsize
        self.height = height
        self.width = width
        # 设置字体颜色
        self.color = color
        # 初始化界面
        self.initWidget(height,width)
        # 初始化定时器
        self.timer.setInterval(self.timeStep)
        self.timer.timeout.connect(self.updateIndex)

    def initWidget(self,height,width):
        """ 初始化界面 """
        self.setFixedHeight(height)
        # self.setAttribute(Qt.WA_StyledBackground)
        # 调整窗口宽度
        self.adjustWindowWidth(width)
        # 只要有一个字符串宽度大于窗口宽度就开启滚动：
        if self.isSongNameTooLong:
            self.timer.start()

    def getTextWidth(self):
        """ 计算文本的总宽度 """
        songFontMetrics = QFontMetrics(QFont('Microsoft YaHei', self.fontsize, 400))
        self.songNameWidth = songFontMetrics.width(self.songName)

    def adjustWindowWidth(self,width):
        """ 根据字符串长度调整窗口宽度 """
        self.getTextWidth()
        maxWidth = self.songNameWidth
        # 判断是否有字符串宽度超过窗口的最大宽度
        self.isSongNameTooLong = self.songNameWidth > width
        # 设置窗口的宽度
        self.setFixedWidth(width)

    def updateIndex(self):
        """ 更新下标 """
        self.update()
        self.songCurrentIndex += 1
        self.songerCurrentIndex += 1
        # 设置下标重置条件
        resetSongIndexCond = self.songCurrentIndex * \
            self.moveStep >= self.songNameWidth + self.spacing * self.isSongNameAllOut
        # 只要条件满足就要重置下标并将字符串溢出置位，保证在字符串溢出后不会因为留出的空白而发生跳变
        if resetSongIndexCond:
            self.songCurrentIndex = 0
            self.isSongNameAllOut = True

    def paintEvent(self, e):
        """ 绘制文本 """
        # super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(self.color)
        # 绘制歌名
        painter.setFont(QFont('Microsoft YaHei', self.fontsize))
        if self.isSongNameTooLong:
            # 实际上绘制了两段完整的字符串
            # 从负的横坐标开始绘制第一段字符串
            painter.drawText(self.spacing * self.isSongNameAllOut - self.moveStep *
                             self.songCurrentIndex, int((self.height+self.fontsize)/2), self.songName)
            # 绘制第二段字符串
            painter.drawText(self.songNameWidth - self.moveStep * self.songCurrentIndex +
                             self.spacing * (1 + self.isSongNameAllOut), int((self.height+self.fontsize)/2), self.songName)
        else:
            painter.drawText(int((self.width-self.songNameWidth)/2), int((self.height+self.fontsize)/2), self.songName)

    def changeSongName(self, songName):
        """ 更改歌曲名 """
        self.songName = songName
        # self.timer.stop()
        self.initWidget(self.height,self.width)
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # songInfo = {
    #     'songName': 'ハッピーでバッドな眠りは浅い',
    #     'album': [r'resource\Album Cover\ハッピーでバッドな眠りは浅い\ハッピーでバッドな眠りは浅い.png']}
    # demo = SongInfoCard(songInfo)
    demo = ScrollTextWindow('ハッピいーでバッドな眠りは浅ハッピいーでバッドな眠りは浅ハッピいーでバッドな眠りは浅ハッピいーでバッドな眠りは浅',height=70,width=950,fontsize=20)
    # demo.setStyleSheet('background:rgb(129,133,137)')
    demo.show()
    # time.sleep(10)
    demo.changeSongName('ハッピーでバッドな眠りは浅い')
    sys.exit(app.exec_())