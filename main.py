import configparser
import ctypes
import time

import py7zr
import qtawesome
import requests
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *  # 包名为 PyQt-Fluent-Widgets
import socket

from baidunet import *
from format_conversion import *
from list_export import *
from tablewidget import *
from song_info import *
from MP3Player import *
from tag_modify import *
from show_window import *


def is_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)  # 设置超时时间 1s
    try:
        s.connect((ip, int(port)))
        return True
    except:
        return False


def week_day(y, m, d):
    week_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return week_cn[datetime.date(int(y), int(m), int(d)).weekday()]


class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


def s2hms(time):
    # 将时长从秒数转换为 XX:XX:XX 的形式
    hour = time // 3600
    time += - hour * 3600
    if time // 60 < 10:
        min = '0' + str(time // 60)
    else:
        min = str(time // 60)
    if time % 60 < 10:
        sec = '0' + str((time % 60) // 1)
    else:
        sec = str((time % 60) // 1)
    if hour > 0:
        times = str(hour) + ':' + min + ':' + sec
    else:
        times = min + ':' + sec
    return times


class CreatThread(QThread):
    # 生成舞曲png文件
    def __init__(self, input):
        super().__init__()
        self.stop_status = False
        self.info = input

    def run(self):
        path = './'
        path_html_phone = path + '\\song-list.html'
        path_wk = './/wkhtmltopdf//bin//wkhtmltopdf.exe'
        if self.info.list_dist['club'] == "华中大国际标准交谊舞俱乐部":
            path_css_phone = ".\\css\\wuqu_phone.css"
            path_hbdc = ".\\css\\HBDC.png"
        else:
            path_css_phone = ".\\css\\wuqu_phone_other.css"
            path_hbdc = ".\\css\\other.png"

        # path = self.info.list_dist['path']
        filename = path + '\\song-list'

        html(self.info.list_dist, path)
        txt(self.info.list_dist, path)
        html2pdf(path_html_phone, path_css_phone, path_hbdc, path_wk, width='103', height='700',
                 filename=filename)
        pdf2png(filename + '.pdf', filename=filename)
        corp_margin(path + '\\song-list.png')

        os.remove(path + '\\song-list.html')
        os.remove(path + '\\song-list.pdf')

        self.info.previewList()


class CreatUpThread(QThread):
    # 生成舞曲png文件
    def __init__(self, input, newPath):
        super().__init__()
        self.info = input
        self.path = newPath

    def run(self):
        if os.path.exists(self.path):
            for filename in os.listdir(self.path):
                filePath = os.path.join(self.path, filename)
                dance_new = filename[0:filename.find('-')]
                back = self.info.bai.upload_new_music(filePath, dance_new)
                if back:
                    self.info.text.append(filename + '新舞曲上传成功！')
                else:
                    self.info.text.append(filename + '新舞曲上传失败！')
                time.sleep(2)
            self.info.text.append("===============")
            self.info.text.append('舞曲文件上传完成！')
        else:
            self.info.text.append('无新舞曲需要上传！')


def movefile(srcfile, dstpath, method="copy"):
    if not os.path.isfile(srcfile):
        out = "%s not exist!".format(srcfile)
    else:
        fpath, _ = os.path.split(dstpath)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        if method == "copy":
            shutil.copy(srcfile, dstpath)  # 复制文件
        elif method == "move":
            shutil.move(srcfile, dstpath)  # 复制文件
        out = "move %s -> %s".format(srcfile, dstpath)
    return out


def getVersion(path):
    # 检查版本更新
    config = configparser.ConfigParser()  # 类实例化
    config.read(path)
    value_totle = float(config['totle']['version'])  # 获取版本号
    value_main = float(config['main']['version'])  # 获取版本号
    value_css_phone = float(config['css_phone']['version'])  # 获取版本号
    value_ui = float(config['ui']['version'])  # 获取版本号

    return [value_totle, value_main, value_css_phone, value_ui]


def writeUpgrade():
    # 编写bat脚本，删除旧程序，运行新程序
    b = open("upgrade.bat", 'w')
    TempList = "@echo off\n"
    TempList += "echo 正在更新至最新版本...\n"
    TempList += "timeout /t 2 /nobreak\n"
    TempList += 'taskkill /im 舞曲列表生成器.exe /f \n'  # 关闭当前程序
    TempList += "timeout /t 2 /nobreak\n"  # 等待2秒
    TempList += "xcopy \"" + os.path.realpath('.\\') + '\\cache\" /S /Y \n'  # 复制 cache 文件夹下的所有文件至父文件夹
    TempList += "rd /s /q \"" + os.path.realpath('.\\') + '\\cache"\n'  # 删除 cache 文件夹
    TempList += "echo 更新完成，正在启动...\n"
    TempList += "timeout /t 2 /nobreak\n"
    TempList += "start " + '舞曲列表生成器.exe' + '\n'  # "start 1.bat\n"
    TempList += "timeout /t 2 /nobreak\n"
    TempList += "exit"
    b.write(TempList)
    b.close()
    os.system('start upgrade.bat')  # 显示cmd窗口


class MyWindow(QWidget):

    resized = pyqtSignal()

    def __init__(self, path):
        super().__init__()
        self.ui = None
        self.col_num = 6
        self.list_path = "song-list.png"
        self.creat_thread = False  # 监视检测子进程是否开启
        self.init_ui(path)
        self.list_dist = {}
        self.volume = 50  # 初始音量值
        self.num = 0  # 初始播放曲目
        self.showWnd = None
        client_id = 'FSSKhNGwkSzrLf3E6BlcmcE54PSEFeaa'
        client_secret = 'vWM6ADj5cEPLojzkGAZWrv9iGWWaZp91'

        # # 登录百度网盘账号，获取 token
        self.bai = BaiduNet(client_id, client_secret)

    def init_ui(self, path):
        self.ui = uic.loadUi(path)
        self.ui.closeEvent = self.closeEvent

        self.ui.setWindowTitle('舞曲列表生成器 7.05 By Guokr')
        self.ui.setWindowIcon(QIcon("./css/HBDC.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self.ui.resizeEvent = self.resizeEvent

        # 提取要操作的控件
        self.listTitle = self.ui.LineEdit_1  # 列表标题
        self.name = self.ui.LineEdit_2  # 排曲人
        self.club = self.ui.EditableComboBox  # 舞协名
        self.path = self.ui.LineEdit_3  # 路径
        self.startTime = self.ui.TimeEdit  # 舞会开始时间
        self.place = self.ui.EditableComboBox_2  # 舞会地点

        self.delpartBtn = self.ui.pushButton_6  # 删除分场按钮
        self.calendar = self.ui.CalendarPicker  # 日期选择器
        self.pathBtn = self.ui.PushButton_1  # 打开路径按钮
        self.saveBtn = self.ui.pushButton_2  # 保存修改按钮
        self.checkBtn = self.ui.pushButton_3  # 检查规则按钮
        self.createBtn = self.ui.pushButton_4  # 生成按钮
        self.addpartBtn = self.ui.pushButton_5  # 增加分场按钮
        self.delpartBtn = self.ui.pushButton_6  # 删除分场按钮
        self.addsongBtn = self.ui.pushButton_7  # 增加分场按钮
        self.delsongBtn = self.ui.pushButton_8  # 删除分场按钮
        self.refreshBtn = self.ui.pushButton_9  # 删除分场按钮
        self.TagBtn = self.ui.pushButton_14  # 修改标签按钮
        self.showWndBtn = self.ui.pushButton_15  # 显示舞曲展示窗口按钮

        self.tab = self.ui.tabWidget  # 选项卡
        self.tab.setCurrentIndex(0)  # 设置默认选项卡为0（列表）
        self.table = self.ui.TableWidget  # 列表表格
        self.graphics = self.ui.graphicsView  # 图片预览
        self.graphics.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)

        self.durationdisplay = self.ui.LineEdit_4  # 总时长label
        self.countdisplay = self.ui.LineEdit_5  # 总曲数label
        self.framedisplay = self.ui.lcdNumber_1  # 架型舞总数
        self.mansidisplay = self.ui.lcdNumber_2  # 慢四总数
        self.mansandisplay = self.ui.lcdNumber_3  # 慢三总数
        self.bingsidisplay = self.ui.lcdNumber_4  # 并四总数
        self.kuaisandisplay = self.ui.lcdNumber_5  # 快三总数
        self.zhongsandisplay = self.ui.lcdNumber_6  # 中三总数
        self.zhongsidisplay = self.ui.lcdNumber_7  # 中四总数
        self.handledisplay = self.ui.lcdNumber_8  # 拉手舞总数
        self.lunbadisplay = self.ui.lcdNumber_9  # 伦巴总数
        self.pingsidisplay = self.ui.lcdNumber_10  # 平四总数
        self.jitebadisplay = self.ui.lcdNumber_11  # 吉特巴总数
        self.ballroomdisplay = self.ui.lcdNumber_12  # 摩登舞总数
        self.huaerzidisplay = self.ui.lcdNumber_13  # 华尔兹总数
        self.tagedisplay = self.ui.lcdNumber_14  # 探戈总数
        self.weiyinadisplay = self.ui.lcdNumber_15  # 维也纳总数
        self.hubudisplay = self.ui.lcdNumber_16  # 狐步总数
        self.kuaibudisplay = self.ui.lcdNumber_17  # 快步总数
        self.agentingdisplay = self.ui.lcdNumber_19
        self.collectivedisplay = self.ui.lcdNumber_18  # 集体舞总数

        self.text = self.ui.textBrowser  # 文本框
        # self.text.setText(update())  # 设置文本框文字

        self.listTitle.setText("青春舞会舞曲")
        self.name.setText("Guokr")
        self.club.addItems(["华中大国际标准交谊舞俱乐部", "武汉大学交谊舞协会",
                            "中国地质大学（武汉）交谊舞协会", "华中农业大学国标舞俱乐部",
                            "华中师范大学交谊舞协会", "武汉理工大学舞蹈协会",
                            "武汉理工大学社交舞协会", "中南民族大学交谊舞俱乐部"])
        self.club.setCurrentIndex(0)
        self.calendar.setDate(QDate.currentDate())
        self.date = QDate.currentDate().toPyDate().strftime("%Y年%m月%d日")
        self.place.addItems(["老年活动中心","紫菘活动中心" , "博士生之家", 
                            "韵苑体育馆", "西教工西厅", "东教工二楼"])
        self.place.setCurrentIndex(0)

        # 列表初始化
        self.tableinit()

        # 绑定信号与槽函数
        self.saveBtn.clicked.connect(self.savelist)
        self.createBtn.clicked.connect(self.creatlist)
        self.checkBtn.clicked.connect(self.checkrule)
        self.calendar.dateChanged.connect(self.qdate2str)
        self.pathBtn.clicked.connect(self.pathselect)
        self.addpartBtn.clicked.connect(self.addpart)
        self.delpartBtn.clicked.connect(self.delpart)
        self.addsongBtn.clicked.connect(self.addsong)
        self.delsongBtn.clicked.connect(self.delsong)
        self.refreshBtn.clicked.connect(self.tableAdict)
        self.TagBtn.clicked.connect(self.changTag)
        # self.table.itemSelectionChanged.connect(self.tableAdict)
        self.table.cellDoubleClicked.connect(self.doubleClickPlay)
        self.showWndBtn.clicked.connect(self.openShowWnd)
        self.resized.connect(self.changeSize)

        # 播放器初始化
        self.startTimeLabel = self.ui.label_23
        self.endTimeLabel = self.ui.label_24
        self.palyLabel = self.ui.label_25
        self.slider = self.ui.horizontalSlider
        self.playBtn = self.ui.pushButton
        self.prevBtn = self.ui.pushButton_11
        self.nextBtn = self.ui.pushButton_10
        self.volumeUpbtn = self.ui.pushButton_12
        self.volumeDownbtn = self.ui.pushButton_13

        self.playBtn.setIcon(qtawesome.icon('fa5s.play'))
        self.prevBtn.setIcon(qtawesome.icon('fa5s.backward'))
        self.nextBtn.setIcon(qtawesome.icon('fa5s.forward'))
        self.volumeUpbtn.setIcon(qtawesome.icon('fa5s.volume-up'))
        self.volumeDownbtn.setIcon(qtawesome.icon('fa5s.volume-down'))

        self.player = MP3Player()
        self.slider.setRange(0, 1000)

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.refreshBar)

        self.playBtn.clicked.connect(self.play)
        self.volumeUpbtn.clicked.connect(self.up_volume)
        self.volumeDownbtn.clicked.connect(self.down_volume)
        self.prevBtn.clicked.connect(self.previous_music)
        self.nextBtn.clicked.connect(self.next_music)
        self.slider.sliderMoved.connect(self.player.change_time)

    def resizeEvent(self, event):
        # self.ui.resizeEvent(event)
        self.resized.emit()
        super(MyWindow, self).resizeEvent(event)
        
        
        # self.resized.emit()

    def pathselect(self):
        # if self.check_thread:  # 避免打开两个检查子线程
        #     self.my_thread.stop_status = True
        directoryPath = QFileDialog.getExistingDirectory(self, "选取文件夹", "./")  # 起始路径
        if directoryPath:
            self.path.setText(directoryPath)
            self.list_dist = (list_info(directoryPath))

            # 重置表格显示内容
            self.table.setRowCount(0)
            self.table.clearContents()

            # 根据文件信息字典 生成表格信息

            self.dict2table()
            self.tableAdict()
            # self.refreshinfo()
            # 启动检测检测、检测表格内容更改
        else:
            self.text.append('请先选择舞曲路径！')

    def savelist(self):
        if not self.list_dist:
            return

        self.table2dict()
        self.dict2table()

        # 修改舞曲标签
        # 更改舞曲 change 属性
        # for i in self.list_dist['list']:
        #     for j in i['music']:
        #         Tag = GetTag(j['filepath'])
        #         if j['dance'] + '-' + j['title'] != Tag['title'] or '华中科技大学' not in Tag['album']:
        #             SetTag(j['filepath'], j['dance'] + '-' + j['title'], j['dance'])
        #             j['is_change'] = True
        self.list_dist['title'] = self.listTitle.text()
        self.list_dist['name'] = self.name.text()
        self.list_dist['date'] = self.date
        # 以 self.title 新建文件夹，并将舞曲进行重命名后移动到新文件夹下
        name = self.list_dist['date'].replace('年', '').replace('月', '').replace('日', '') \
               + ' ' + self.list_dist['title'] + 'by' + self.list_dist['name']
        newPath = os.path.join('./', name)
        # 增加新舞曲路径
        name = self.list_dist['date'].replace('年', '').replace('月', '').replace('日', '') + ' 新舞曲'
        # newPath2 = os.path.join('./', name)

        messageBox = QMessageBox()
        messageBox.setWindowTitle('警告')
        messageBox.setText('请选择舞曲保存模式。复制将保留原有文件，移动将不保存原有文件。')
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        buttonY = messageBox.button(QMessageBox.Yes)
        buttonY.setText('复  制')
        buttonN = messageBox.button(QMessageBox.No)
        buttonN.setText('移  动')
        buttonC = messageBox.button(QMessageBox.Cancel)
        buttonC.setText('取  消')
        messageBox.exec_()
        if messageBox.clickedButton() == buttonY:
            method = 'copy'
        elif messageBox.clickedButton() == buttonN:
            method = "move"
        elif messageBox.clickedButton() == buttonC:
            return
        else:
            return

        if os.path.exists(newPath):
            reply = QMessageBox.warning(self.ui, '警告', '警告：目标路径已有舞曲将会被删除，是否继续',
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
            # reply = QMessageBox.question(self.ui, '是否保存修改', '是否保存修改？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            else:
                shutil.rmtree(newPath)
                # if os.path.exists(newPath2):
                # shutil.rmtree(newPath2)

        # 根据 dict 数据移动文件并重命名
        for i in self.list_dist['list']:
            for j in i['music']:
                if j['num'] < 10:
                    num = '0' + str(j['num'])
                else:
                    num = str(j['num'])
                ext = j['filename'][j['filename'].rfind('.'):len(j['filename'])]
                if j['choose']:
                    filename = num + '-' + j['dance'] + '-' + j['title'] + '-' + '点播' + ext
                else:
                    filename = num + '-' + j['dance'] + '-' + j['title'] + ext
                if i['part_title']:
                    partname = str(self.list_dist['list'].index(i) + 1) + ' ' + i['part_title']
                    newFilePath = os.path.join(newPath, partname, filename)
                else:
                    newFilePath = os.path.join(newPath, filename)
                movefile(j['filepath'], newFilePath, method)
                j['filepath'] = newFilePath
                Tag = GetTag(j['filepath'])
                # check = self.bai.check_new(j['filepath'], j['title'], j['dance'])
                if j['dance'] + '-' + j['title'] != Tag['title'] or '华中科技大学' not in Tag['album']:
                    SetTag(j['filepath'], j['dance'] + '-' + j['title'], j['dance'])
                    j['is_change'] = True
                # if j['is_change']:
                #     filename = j['dance'] + '-' + j['title'] + ext
                #     newFilePath = os.path.join(newPath2, filename)
                #     movefile(j['filepath'], newFilePath, 'copy')

        self.list_dist = (list_info(newPath))
        self.path.setText(newPath)
        # 重置表格显示内容
        self.table.setRowCount(0)
        self.table.clearContents()

        # 根据文件信息字典 生成表格信息

        self.dict2table()
        self.tableAdict()
        self.text.setText('舞曲文件保存成功')
        # 上传新舞曲路径文件
        # 上传 newPath2 路径的所有文件

        # 测试、登录网盘 token
        var = self.bai.test_connection()
        # print(var[0])
        if not var[0]:
            text, okPressed = QInputDialog.getText(self,
                                                   '登录百度网盘',
                                                   "(1)请将下方链接复制到浏览器中 \n(2)登录百度网盘，显示”OAuth2.0“字样 \n(3)将新网址复制到文本框并确认",
                                                   QLineEdit.Normal, var[2])
            if okPressed and text != '':
                self.bai.get_access_token(text)
                # 上传文件
            else:
                self.text.append('百度网盘登录失败')
                return
        self.up_thread = CreatUpThread(self, newPath)  # 创建上传线程
        self.up_thread.start()

    def creatlist(self):
        if self.list_dist == None:
            return

        # 更新 字典 数据，并询问是否保存
        # reply = QMessageBox.warning(self.ui, '警告', '警告：请先进行保存！是否继续生成舞曲列表？',
        #                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # if reply == QMessageBox.Yes:

        self.list_dist['title'] = self.listTitle.text()
        self.list_dist['name'] = self.name.text()
        self.list_dist['date'] = self.date
        self.list_dist['club'] = self.club.currentText()
        self.list_dist['place'] = self.place.currentText()
        date = self.list_dist['date'].replace('年', '').replace('月', '').replace('日', '')
        self.list_dist['time'] = [week_day(int(date[0:4]), int(date[4:6]), int(date[6:8])),
                                  QTime.toString(self.startTime.time(), "hh:mm")]
        self.refreshinfo()

        # =========== 生成舞曲列表 ================
        self.my_thread = CreatThread(self)  # 创建线程
        self.my_thread.start()

        # else:
        #     self.text.append("请先保存修改！")

    def tableinit(self):
        self.table.setColumnCount(self.col_num)
        self.table.verticalHeader().setVisible(False)  # 水平方向表格头的显示与隐藏
        self.table.setHorizontalHeaderLabels(['序号', '舞曲', '舞种', '点播', '时长', 'MD5'])
        # 列宽设置
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 40)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(5, 110)

        self.table.setAlternatingRowColors(True)
        # self.table.setColumnWidth(6, 30)

        # 设置 不可编辑列
        for i in [3, 4, 5]:
            self.table.setItemDelegateForColumn(i, EmptyDelegate(self.ui))
    
    def changeRowHeight(self,spacing=0):
        for row in range(self.table.rowCount()):# 设置每一行的高度为基础高度+间距
            self.table.setRowHeight(row, 35+spacing)

    def table2dict(self):
        if self.list_dist is None:
            return
        newlist = []
        duration_tot = 0
        song_num = 0
        for i in range(self.table.rowCount()):
            if not (self.table.item(i, 0) or self.table.item(i, 1)):
                # 最后一行为空，停止读取
                self.text.append('更新信息失败！')
                self.text.append('存在没有内容的行！')
                return False
            if not self.table.item(i, 1):
                newlist.append({
                    'part_title': self.table.item(i, 0).text(),
                    'count': 0,
                    'music': [],
                })
            else:
                if i == 0:
                    newlist.append({
                        'part_title': None,
                        'count': 0,
                        'music': [],
                    })
                song = {
                    'num': song_num + 1,
                    'dance': self.table.item(i, 2).text() if self.table.item(i, 0) else None,
                    'title': self.table.item(i, 1).text() if self.table.item(i, 0) else None,
                    'choose': self.table.cellWidget(i, 3).children()[1].isChecked() if self.table.cellWidget(i,
                                                                                                             3) else False,
                    'MD5': self.table.item(i, 5).text() if self.table.item(i, 0) else None,
                }
                newlist[-1]['music'].append(song)
                newlist[-1]['count'] += 1
                song_num += 1

        # 从 self.list_dist['list'] 中查找其他信息
        # 将 Music 放在一个变量中方便查找MD5
        Tem = []
        for i in self.list_dist['list']:
            for j in i['music']:
                Tem.append(j)

        for i in range(0, len(newlist)):
            for j in range(0, len(newlist[i]['music'])):
                for k in Tem:
                    if newlist[i]['music'][j]['MD5'] == k['MD5']:
                        for m in k.keys():
                            if m not in newlist[i]['music'][j]:
                                newlist[i]['music'][j][m] = k[m]

        for i in range(0, len(newlist)):
            newlist[i]['duration'] = 0
            for j in range(0, len(newlist[i]['music'])):
                newlist[i]['duration'] += newlist[i]['music'][j]['duration']
                duration_tot += newlist[i]['music'][j]['duration']

        self.list_dist['list'] = newlist
        self.list_dist['duration'] = duration_tot
        self.list_dist['count'] = song_num

        dances = []
        for i in self.list_dist['list']:
            for j in i['music']:
                dances.append(j['dance'])
        self.list_dist['distribution'] = dance_counts(dances)
        # print(self.list_dist)
        self.refreshinfo()

        return True

    def dict2table(self):
        self.table.setRowCount(0)
        if self.list_dist == None:
            return
        row = 0
        if len(self.list_dist['list']) == 1:
            row_section = 0
        else:
            row_section = len(self.list_dist['list'])

        row_tot = self.list_dist['count'] + row_section
        self.table.setRowCount(row_tot)
        part_num = 1
        for i in self.list_dist['list']:
            # print(i['part_title'])
            if len(self.list_dist['list']) > 1:  # 'part_title' in i.keys()
                if not i['part_title']:
                    i['part_title'] = "分场%s" % part_num
                    part_num = part_num + 1
                self.table.setSpan(row, 0, 1, 2)
                self.table.setItem(row, 0, QTableWidgetItem(i['part_title']))
                self.table.setSpan(row, 2, 1, self.col_num - 2)
                self.table.setItem(row, 2, QTableWidgetItem('分场时长：' + s2hms(i['duration'])))
                row = row + 1
            for j in i['music']:
                number = QTableWidgetItem(str(j['num']))
                number.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                number.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(row, 0, number)
                title = QTableWidgetItem(j['title'])
                title.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(row, 1, title)
                self.table.setItem(row, 2, QTableWidgetItem(j['dance']))

                checkbox = QCheckBox()
                if j['choose']:
                    checkbox.setCheckState(Qt.Checked)  # 把checkBox设为未选中状态
                else:
                    checkbox.setCheckState(Qt.Unchecked)  # 把checkBox设为未选中状态
                hLayout = QtWidgets.QHBoxLayout()
                hLayout.addWidget(checkbox, 0, Qt.AlignCenter)
                widget = QtWidgets.QWidget()
                widget.setLayout(hLayout)
                self.table.setCellWidget(row, 3, widget)

                duration = QTableWidgetItem(s2hms(j['duration']))
                duration.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table.setItem(row, 4, duration)
                self.table.setItem(row, 5, QTableWidgetItem(j['MD5']))
                row = row + 1

    def tableAdict(self):
        # b = self.table2dict()
        # # print(b)
        if not self.table2dict():
            return
        self.dict2table()
        self.checkrule()
        self.refreshinfo()

    def addsong(self):
        if self.list_dist == None:
            self.text.append('请先选择舞曲路径！')
            return
        path = QFileDialog.getOpenFileName(self, "选取文件夹", "./")  # 起始路径
        if not path[0]:
            self.text.append('请选择舞曲路径！')
            return

        a = music_info(path[0].replace("/", "\\"))
        self.list_dist['list'][-1]['music'].append(a)
        self.list_dist['count'] += 1
        self.list_dist['list'][-1]['music'][-1]['num'] = self.list_dist['count']
        self.dict2table()
        self.tableAdict()

    def delsong(self):
        row_cur = self.table.currentRow()
        if self.table.item(row_cur, 1):
            self.table.removeRow(row_cur)
        else:
            self.text.append('请选择舞曲单元格！')
        self.tableAdict()

    def addpart(self):
        row_cur = self.table.currentRow()
        self.table.insertRow(row_cur)
        self.table.setSpan(row_cur, 0, 1, 2)
        self.table.setSpan(row_cur, 2, 1, self.col_num)

    def delpart(self):
        row_cur = self.table.currentRow()
        if not self.table.item(row_cur, 1):
            self.table.removeRow(row_cur)
        else:
            self.text.append('请选择分场单元格！')
        self.tableAdict()

    def refreshinfo(self):
        # 更新总时长
        self.durationdisplay.setText(s2hms(self.list_dist['duration']))

        self.countdisplay.setText(str(self.list_dist['count']))
        self.framedisplay.display(sum(self.list_dist['distribution']['frame']))  # 架型舞总数
        self.mansidisplay.display(self.list_dist['distribution']['frame'][0])  # 慢四总数
        self.mansandisplay.display(self.list_dist['distribution']['frame'][1])  # 慢三总数
        self.bingsidisplay.display(self.list_dist['distribution']['frame'][2])  # 并四总数
        self.kuaisandisplay.display(self.list_dist['distribution']['frame'][3])  # 快三总数
        self.zhongsandisplay.display(self.list_dist['distribution']['frame'][4])  # 中三总数
        self.zhongsidisplay.display(self.list_dist['distribution']['frame'][5])  # 中四总数
        self.handledisplay.display(sum(self.list_dist['distribution']['handle']))  # 拉手舞总数
        self.lunbadisplay.display(self.list_dist['distribution']['handle'][0])  # 伦巴总数
        self.pingsidisplay.display(self.list_dist['distribution']['handle'][1])  # 平四总数
        self.jitebadisplay.display(self.list_dist['distribution']['handle'][2])  # 吉特巴总数
        self.ballroomdisplay.display(sum(self.list_dist['distribution']['ballroom']))  # 摩登舞总数
        self.huaerzidisplay.display(self.list_dist['distribution']['ballroom'][0])  # 华尔兹总数
        self.tagedisplay.display(self.list_dist['distribution']['ballroom'][1])  # 探戈总数
        self.weiyinadisplay.display(self.list_dist['distribution']['ballroom'][2])  # 维也纳总数
        self.hubudisplay.display(self.list_dist['distribution']['ballroom'][3])  # 狐步总数
        self.kuaibudisplay.display(self.list_dist['distribution']['ballroom'][4])  # 快步总数
        self.agentingdisplay.display(self.list_dist['distribution']['ballroom'][10])  # 阿根廷探戈总数
        self.collectivedisplay.display(sum(self.list_dist['distribution']['collective']))  # 集体舞总数

        navText = '本次舞会共 ' + str(self.list_dist['count']) + ' 首曲子，总时长为 ' + str(
            self.list_dist['duration'] // 3600) + ' 小时 ' + str(
                (self.list_dist['duration'] % 3600) // 60) + ' 分 ' + str(self.list_dist['duration'] % 60) + ' 秒'
        
        info = []
        for i in self.list_dist['list']:
            for j in i['music']:
                if j['choose'] and j['other']:
                    info.append((str(j['num']) if j['num'] >= 10 else '0' + str(j['num'])) + ' ' + j['dance'] + '-' + j['title'] + '-' + j['other'])
                else:
                    info.append((str(j['num']) if j['num'] >= 10 else '0' + str(j['num'])) + ' '  + j['dance'] + '-' + j['title'])
        if self.showWnd is not None:
            self.showWnd.changeText(navText=navText,titleText=self.listTitle.text(),text=info)
        self.getList()

    def checkrule(self):
        if self.list_dist == None:
            return
        collective_dis = self.list_dist['distribution']['collective']
        collective = ['青春16步', '花火16步', '32步', '64步', '兔子舞', '集体恰恰', '阿拉伯之夜',
                      '马卡琳娜', '玛卡琳娜', '蒙古舞']
        # 将N个舞曲列表拼在一起
        list = []
        md5s = []
        for i in self.list_dist['list']:
            for j in i['music']:
                list.append(j)
                md5s.append(j['MD5'])
        self.text.setText('')
        self.text.append("===============")
        # 判断集体舞是否重复
        for i in range(0, len(collective_dis)):
            if collective_dis[i] > 1:
                # print('\33[0;31m{}   {}\33[0m'.format(collective[i], '重复！'))
                self.text.append("<font color='red'>{}  '重复！<font>'".format(collective[i]))
                # 寻找collective[i]对应舞曲所在单元格并标红
                for j in self.table.findItems(collective[i], Qt.MatchFixedString):
                    if j.column() == 2:
                        j.setBackground(QColor(167, 83, 90))

        for i in list:
            if i['speed'] == 'quick':
                if 240 <= i['duration']:
                    self.text.append("<font color='red'>{}   时长超过 4min！<font>".format(i['title']))
                    for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                        self.table.item(j.row(), 4).setBackground(QColor(167, 83, 90))
            else:
                if 240 <= i['duration'] < 270:
                    self.text.append("<font color='blue'>{}   时长超过 4min！<font>'".format(i['title']))
                    for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                        self.table.item(j.row(), 4).setBackground(QColor(210, 180, 44))
                elif i['duration'] >= 270:
                    self.text.append("<font color='red'>{}   时长超过 4min！30s！<font>".format(i['title']))
                    for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                        self.table.item(j.row(), 4).setBackground(QColor(167, 83, 90))

            # if i != list[0]:  # 不检查最后一个舞曲
            if i['dancetype'] == None:
                self.text.append("<font color='red'>{}   无舞曲类型！<font>".format(i['title']))
                for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                    self.table.item(j.row(), 2).setBackground(QColor(167, 83, 90))
            elif i != list[0]:  # 不检查最后一个舞曲
                if i['dancetype'] == i0['dancetype'] and i['dancetype'] != 'collective':
                    self.text.append("<font color='red'>{}   违反舞种相间规则！<font>".format(i['title']))
                    for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                        self.table.item(j.row(), 2).setBackground(QColor(167, 83, 90))
                if i['speed'] == i0['speed'] and i['speed'] is not None:
                    if i['speed'] == 'slow':
                        self.text.append("<font color='blue'>{}   违反快慢相间规则！<font>".format(i['title']))
                        for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                            self.table.item(j.row(), 2).setBackground(QColor(210, 180, 44))
                    elif i['speed'] == 'quick':
                        self.text.append("<font color='red'>{}   违反快慢相间规则！<font>".format(i['title']))
                        for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                            self.table.item(j.row(), 2).setBackground(QColor(167, 83, 90))
            i0 = i

            if md5s.count(i['MD5']) > 1:  # 检查舞曲是非重复
                self.text.append("<font color='red'>{}   重复！".format(i['title']))
                for j in self.table.findItems(i['MD5'], Qt.MatchFixedString):
                    self.table.item(j.row(), 5).setBackground(QColor(167, 83, 90))
        self.text.append("===============")
        self.table.viewport().update()

    def qdate2str(self, qdata):
        date = qdata.toPyDate()
        self.date = date.strftime("%Y年%m月%d日")

    def previewList(self):
        frame = QImage('.\\song-list.png')
        pix = QPixmap.fromImage(frame)
        item = QGraphicsPixmapItem(pix)
        scene = QGraphicsScene()
        scene.addItem(item)
        self.graphics.setScene(scene)
        self.graphics.show()
        self.graphics.update()
        self.graphics.centerOn(0, 0)
        self.tab.setCurrentIndex(1)

    def closeEvent(self, event):
        reply = QMessageBox.question(self.ui, 'Warning', '警告：如果修改了舞曲信息，请在保存文件后退出。是否保存后退出？',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.savelist()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def versionUpdate(self):
        try:
            path_old = r'.\\version.ini'
            old_version = getVersion(path_old)
            if os.path.exists('.\\cache'):
                shutil.rmtree('.\\cache')
            self.startDownload('version.ini', '.\\cache\\', bar=False)  # 下载配置文件
            path_new = r'.\\cache\\version.ini'
            new_version = getVersion(path_new)
            if new_version[0] > old_version[0] or new_version[1] > old_version[1] or new_version[2] > old_version[2] or new_version[3] > old_version[3]:
                reply = QMessageBox.warning(self.ui, '更新', '发现新版本，是否更新？',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.No:
                    self.text.append('退出更新！')
                else:
                    if new_version[0] > old_version[0]:
                        bo = self.startDownload('舞曲列表生成器.7z')
                        if bo:
                            with py7zr.SevenZipFile('.\\cache\\舞曲列表生成器.7z', mode='r') as z:
                                z.extractall('.\\cache\\')
                            os.remove(".\\cache\舞曲列表生成器.7z")
                    else:
                        if new_version[1] > old_version[1]:
                            bo = self.startDownload('舞曲列表生成器.exe')
                        if new_version[2] > old_version[2]:
                            bo = self.startDownload(filename='wuqu_phone.css', path=".\\cache\\css\\",
                                                    url="https://foot.guokr.work:888/HBDC/css/", bar=True)
                        if new_version[3] > old_version[3]:
                            bo = self.startDownload(filename='SongList.ui', path=".\\cache\\css\\",
                                                    url="https://foot.guokr.work:888/HBDC/css/", bar=True)
                    if bo:
                        writeUpgrade()
                        app = QApplication.instance()
                        app.quit()
                    else:
                        self.text('更新失败！无法下载更新！')
            else:
                os.remove(".\\cache\\version.ini")
                os.removedirs(".\\cache")
                self.text.append('已是最新版本！')
        except Exception as e:
            self.text.append('更新失败！' + str(e))

    def startDownload(self, filename='舞曲列表生成器.exe', path=".\\cache\\", url="http://guokr.work:5004/HBDC/",
                      bar=True):
        # 下载最新版本的程序
        file_url = url + filename
        if not os.path.exists(path):  # 看是否有该文件夹，没有则创建文件夹
            os.mkdir(path)
        if is_open('guokr.work', '5004'):
            response = requests.get(file_url, stream=True)  # stream=True必须写上
        else:
            # if response.status_code != 200:  # 是否可以使用校园网
            url = 'https://foot.guokr.work:888/HBDC/'
            file_url = url + filename
            response = requests.get(file_url, stream=True)
        chunk_size = 1024  # 每次下载的数据大小
        content_size = int(response.headers['content-length'])  # 下载文件总大小

        # 新建进度条

        # try:
        if response.status_code == 200:  # 判断是否响应成功
            file_path = path + filename
            # 构建QProgressBar类

            # 开始下载
            if bar:
                i = 0
                progress = QProgressDialog(self.ui)
                progress.setWindowTitle("更新下载")
                progress.setMinimumDuration(5)
                progress.setWindowModality(Qt.WindowModal)
                progress.setRange(0, content_size)
                progress.setCancelButtonText(None)
                progress.setWindowFlags(progress.windowFlags() | Qt.WindowSystemMenuHint)
                progress.setFixedSize(500, 90)
                time0 = time.time()
                with open(file_path, 'wb+') as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        i += 1024
                        time1 = time.time() - time0
                        if time1 == 0:
                            speed = 1024
                        else:
                            speed = i / 1024 / time1
                        remainTime = (content_size - i) / 1024 / speed
                        text = "正在下载更新...  " + "下载速度: {:.2f} kB/s".format(speed) + '剩余时间：{:.2f}s'.format(
                            remainTime)
                        progress.setLabelText(text)
                        progress.setValue(i)
                progress.setValue(content_size)
                self.text.append('下载完成!')
            else:
                with open(file_path, 'wb') as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
            return True
        else:
            self.text.append('网络错误！')
            return False
        #
        # except Exception as e:
        #     self.text.append('下载失败！ ' + str(e))

    def getList(self):
        file_path = []
        for i in self.list_dist['list']:
            for j in i['music']:
                file_path.append(j['filepath'].replace('\\', '/'))
        # print(file_path)
        self.player.getList(file_path)
        self.playBtn.setIcon(qtawesome.icon('fa5s.play'))

    def up_volume(self, num):
        self.volume = self.volume + 5
        if self.volume > 100:
            self.volume = 100
        self.player.change_volume(self.volume)
        self.text.append('当前音量：' + str(self.volume))

    def down_volume(self):
        self.volume = self.volume - 5
        if self.volume < 0:
            self.volume = 0
        self.player.change_volume(self.volume)
        self.text.append('当前音量：' + str(self.volume))

    def next_music(self):
        num = self.player.next_music()

    def previous_music(self):
        num = self.player.previous_music()

    def play(self):
        if self.player.state() == 1:
            self.player.pause()
            self.playBtn.setIcon(qtawesome.icon('fa5s.play'))
        else:
            self.player.play()
            self.playBtn.setIcon(qtawesome.icon('fa5s.pause'))

    def refreshBar(self):
        if self.player.state() == 1:
            duration, position = self.player.get_time()
            if duration != 0:
                self.startTimeLabel.setText(s2hms(position // 1000))
                self.slider.setValue(int(position / duration * 1000))
            if self.num != self.player.currentIndex() + 1:
                self.num = self.player.currentIndex() + 1
                if duration != 0:
                    self.endTimeLabel.setText(s2hms(duration // 1000))
                for i in self.list_dist['list']:
                    for j in i['music']:
                        if j['num'] == self.num:
                            self.palyLabel.setText(j['title'])
                            break
                item = self.table.findItems(str(self.num), Qt.MatchExactly)
                for j in range(self.table.rowCount()):
                    self.table.item(j, 0).setBackground(QColor(255, 255, 255))
                if item:
                    row = item[0].row()
                    # print(row)
                    item[0].setBackground(QColor(167, 83, 90))
        if self.showWnd is not None:
            self.showWnd.changeLabel(self.num-1)

    def doubleClickPlay(self, row, col):
        if col in [0, 3, 4, 5]:
            if self.table.item(row, 1):  # 判断是否为舞曲
                num = int(self.table.item(row, 0).text())
                self.player.setCurrentIndex(num)
                self.player.play()
                self.playBtn.setIcon(qtawesome.icon('fa5s.pause'))

    def changTag(self):
        self.table2dict()
        for i in self.list_dist['list']:
            for j in i['music']:
                try:
                    Tag = GetTag(j['filepath'])
                    # check = self.bai.check_new(j['filepath'], j['title'], j['dance'])
                    if j['dance'] + '-' + j['title'] != Tag['title'] or '华中科技大学' not in Tag['album']:
                        if '点播' in j['filepath']:
                            SetTag(j['filepath'], j['dance'] + '-' + j['title'], j['dance'])
                        else:
                            SetTag(j['filepath'], j['dance'] + '-' + j['title'], j['dance'])
                        j['is_change'] = True
                    path = os.path.dirname(j['filepath'])
                    filename = os.path.basename(j['filepath'])
                    name, extname = os.path.splitext(filename)
                    newname = j['dance'] + '-' + j['title'] + extname
                    if filename != newname:
                        # if filename[0:2].isdigit() and not filename[2] == '步':
                        #     newname = filename[3:]  # 把logo-替换成空白
                        os.rename(j['filepath'], os.path.join(path, newname))
                        j['filepath'] = os.path.join(path, newname)
                except Exception as e:
                    self.text.append(j['filepath'] + ' 修改失败!')
                    self.text.append(e)
    
    def openShowWnd(self):
        self.showWnd = FramelessWindow()
        if 'count' in self.list_dist.keys():
            navText = '本次舞会共 ' + str(self.list_dist['count']) + ' 首曲子，总时长为 ' + str(
                self.list_dist['duration'] // 3600) + ' 小时 ' + str(
                    (self.list_dist['duration'] % 3600) // 60) + ' 分 ' + str(self.list_dist['duration'] % 60) + ' 秒'
            info = []
            for i in self.list_dist['list']:
                for j in i['music']:
                    if j['choose'] and j['other']:
                        info.append((str(j['num']) if j['num'] >= 10 else '0' + str(j['num'])) + '  ' + j['dance'] + '-' + j['title'] + '-' + j['other'] + '  ' + s2hms(j['duration']))
                    else:
                        info.append((str(j['num']) if j['num'] >= 10 else '0' + str(j['num'])) + '  '  + j['dance'] + '-' + j['title'] + '  ' + s2hms(j['duration']))
            if self.showWnd is not None:
                self.showWnd.changeText(navText=navText,titleText=self.listTitle.text(),text=info)
            self.showWnd.show()

    def changeSize(self):
        size = self.ui.size()
        self.ui.QFrame_1.resize(self.ui.size())
        # print(self.ui.tabWidget.size().width()-15, self.ui.tabWidget.size().height()-5)
        width0 = 660
        height0 = 510
        width = self.ui.tabWidget.size().width()-15 if self.ui.tabWidget.size().width()-15 > width0 else width0
        height = self.ui.tabWidget.size().height()-35 if self.ui.tabWidget.size().height()-35 > height0 else height0
        size = QSize(width, height)
        self.table.resize(size)
        self.graphics.resize(size)

        self.table.setColumnWidth(1, int(250 + (width-width0)*0.3))
        self.table.setColumnWidth(2, int(120 + (width-width0)*0.1))
        self.table.setColumnWidth(3, int(40 + (width-width0)*0.1))
        self.table.setColumnWidth(4, int(70 + (width-width0)*0.1))
        self.table.setColumnWidth(5, int(102 + (width-width0)*0.4))

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    w = MyWindow(".\\css\\SongList.ui")
    w.ui.show()
    w.versionUpdate()  # 版本更新
    app.exec()
    # sys.exit(app.exec_())
    