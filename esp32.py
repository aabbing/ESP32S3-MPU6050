import sys  # 是一个从程序外部获取参数的桥梁
import time
import pyqtgraph as pg  # 是一个纯python的图形和GUI库
import threading  # 多线程模块
import serial  # 串口通信模块
from PyQt5.QtCore import *  # 包含了核心的非GUI功能。处理时间、文件和目录、各种数据类型、流、线程等
from PyQt5.QtGui import *  # 包含了多种基本图形功能的类。窗口集、事件处理、2d图形、基本图像和界面以及字体文本。
from PyQt5.QtWidgets import *  # 包含了一整套UI元素组件，用于建立符合系统风格的classic界面
import datetime  # 表示日期时间，年月日时分秒
from pyqtgraph import DateAxisItem

# 版本1.0
__version__ = '1.0'


# 创建一个主窗口的类
class MainWindow(QMainWindow):
    newdata = pyqtSignal(object)  # 创建信号

    # 初始化、实例化对象
    def __init__(self, filename=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('健身动作监测')  # 设置窗口标题
        #self.setWindowIcon(QIcon(r"C:\Users\Administrator\Desktop\毕业设计及论文\毕业设计\数据绘图\fitness"))  # 设置窗体图标

        self.t = []
        self.acx = []
        self.acy = []
        self.acz = []
        self.gyx = []
        self.gyy = []
        self.gyz = []
        self.pitch = []
        self.roll = []
        self.yaw = []
        self.history = 3600  # 历史保存数据的数量

        self.connected = False
        self.port = 'COM9'
        self.baud = 115200

        # 启动线程
        # QTimer.singleShot(0, self.startThread)
        self.btn = QPushButton('点击运行！')
        font = QFont()
        font.setPointSize(16)
        self.label = QLabel("实时获取健身动作数据")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.data_label = QLabel("Data")
        # self.data_label.setAlignment(Qt.AlignCenter)

        self.pw = pg.PlotWidget()
        self.pw_angular = pg.PlotWidget()
        self.pw_angle = pg.PlotWidget()

        self.init_pg_accel()
        self.init_pg_angular()
        self.init_pg_angle()

        # 设置布局
        vb = QVBoxLayout()
        hb = QHBoxLayout()

        vb.addWidget(self.label)
        vb.addWidget(self.btn)

        # 控制图表显示个数
        hb.addWidget(self.pw)
        hb.addWidget(self.pw_angular)
        hb.addWidget(self.pw_angle)

        vb.addLayout(hb)
        vb.addWidget(self.data_label)

        self.cwidget = QWidget()
        self.cwidget.setLayout(vb)
        self.setCentralWidget(self.cwidget)

        self.btn.clicked.connect(self.startThread)
        self.newdata.connect(self.updatePlot)

    # 设置图表：加速度变化趋势
    def init_pg_accel(self):
        # 设置图表标题
        self.pw.setTitle("加速度变化趋势",
                         color='008080',
                         size='12pt')
        # 设置上下左右的label
        self.pw.setLabel("left", "米/秒^2")
        self.pw.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw.setYRange(min=10,max=50)  # 最大值
        # 显示表格线
        self.pw.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw)
        axis = DateAxisItem()  # 设置时间轴，主要此时x的数据为时间戳time.time()
        self.pw.setAxisItems({'bottom': axis})
        self.curve_acx = self.pw.getPlotItem().plot(
            pen=pg.mkPen('r', width=2)
        )
        self.curve_acy = self.pw.getPlotItem().plot(pen=pg.mkPen('b', width=2))
        self.curve_acz = self.pw.getPlotItem().plot(pen=pg.mkPen('y', width=2))

    def init_pg_angular(self):
        # 设置图表标题
        self.pw_angular.setTitle("角速度变化趋势",
                                 color='008080',
                                 size='12pt')
        # 设置上下左右的label
        self.pw_angular.setLabel("left", "弧度/秒")
        self.pw_angular.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw.setYRange(min=10,max=50)  # 最大值
        # 显示表格线
        self.pw_angular.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw_angular.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw)
        axis = DateAxisItem()  # 设置时间轴，主要此时x的数据为时间戳time.time()
        self.pw_angular.setAxisItems({'bottom': axis})
        self.curve_gyx = self.pw_angular.getPlotItem().plot(
            pen=pg.mkPen('r', width=2)
        )
        self.curve_gyy = self.pw_angular.getPlotItem().plot(pen=pg.mkPen('b', width=2))
        self.curve_gyz = self.pw_angular.getPlotItem().plot(pen=pg.mkPen('y', width=2))

    def init_pg_angle(self):
        # 设置图表标题
        self.pw_angle.setTitle("角度变化趋势",
                               color='008080',
                               size='12pt')
        # 设置上下左右的label
        self.pw_angle.setLabel("left", "度")
        self.pw_angle.setLabel("bottom", "时间")
        # 设置Y轴 刻度 范围
        # self.pw.setYRange(min=10,max=50)  # 最大值
        # 显示表格线
        self.pw_angle.showGrid(x=True, y=True)
        # 背景色改为白色
        self.pw_angle.setBackground('w')
        # 居中显示 PlotWidget
        # self.setCentralWidget(self.pw)
        axis = DateAxisItem()  # 设置时间轴，主要此时x的数据为时间戳time.time()
        self.pw_angle.setAxisItems({'bottom': axis})
        self.curve_pitch = self.pw_angle.getPlotItem().plot(
            pen=pg.mkPen('r', width=2)
        )
        self.curve_roll = self.pw_angle.getPlotItem().plot(pen=pg.mkPen('b', width=2))
        self.curve_yaw = self.pw_angle.getPlotItem().plot(pen=pg.mkPen('y', width=2))

    def startThread(self):
        '''
        这里使用python的threading.Thread构造线程，并将线程设置为守护线程，这样
        主线程退出后守护线程也会跟着销毁
        '''
        self.btn.setEnabled(False)
        print('Start lisnening to the COM-port')
        # timeout参数很重要！可以结合波特率和传输的数据量计算出数据发送所需的时间
        serial_port = serial.Serial(self.port, self.baud, timeout=0.1)
        thread = threading.Thread(target=self.read_from_port, args=(serial_port,))
        # thread.setDaemon(True)  # 守护线程
        thread.start()  # 启动线程

    # 更新绘图
    def updatePlot(self, signal):

        # self.curve_pitch.getViewBox().enableAutoRange()
        # self.curve_pitch.getViewBox().setAutoVisible()
        self.curve_acx.setData(signal[0], signal[1][0])

        self.curve_acy.setData(signal[0], signal[1][1])

        self.curve_acz.setData(signal[0], signal[1][2])

        self.curve_gyx.setData(signal[0], signal[1][3])

        self.curve_gyy.setData(signal[0], signal[1][4])

        self.curve_gyz.setData(signal[0], signal[1][5])

        self.curve_pitch.setData(signal[0], signal[1][6])

        self.curve_roll.setData(signal[0], signal[1][7])

        self.curve_yaw.setData(signal[0], signal[1][8])

    # 处理数据
    def process_data(self, data: str):
        ''''处理数据，注意原来通过串口发送的数据格式'''

        if len(self.t) >= self.history:  # 保证存储数量为设定的历史长度数量
            self.t.pop(0)
            self.acx.pop(0)
            self.acy.pop(0)
            self.acz.pop(0)
            self.gyx.pop(0)
            self.gyy.pop(0)
            self.gyz.pop(0)
            self.pitch.pop(0)
            self.roll.pop(0)
            self.yaw.pop(0)

        if data.startswith('acx'):
            try:
                # ['Temperature:28.00\r', 'Humidity:28.00']
                # strip()清除
                data = data.strip().replace(' ', '').replace('\r', '').replace('\r', '').replace('\r', '').replace('\r',
                                                                                                                   '').replace(
                    '\r', '').replace('\r', '').replace('\r', '').replace('\r', '').split('\n')
                print(data)
                self.data_label.setText('Time:' + str(datetime.datetime.now()) + ', ' +
                                        data[0] + ', ' + data[1] + ', ' + data[2] + ', ' + data[3] + ', ' + data[
                                            4] + ', ' + data[5] + ', ' + data[6] + ', ' + data[7] + ', ' + data[8])
                self.t.append(time.time())
                self.acx.append(float(data[0].split(':')[1].strip()))
                self.acy.append(float(data[1].split(':')[1].strip()))
                self.acz.append(float(data[2].split(':')[1].strip()))
                self.gyx.append(float(data[3].split(':')[1].strip()))
                self.gyy.append(float(data[4].split(':')[1].strip()))
                self.gyz.append(float(data[5].split(':')[1].strip()))
                self.pitch.append(float(data[6].split(':')[1].strip()))
                self.roll.append(float(data[7].split(':')[1].strip()))
                self.yaw.append(float(data[8].split(':')[1].strip()))
            except:
                print('No valid data')

            signal = (
            self.t, (self.acx, self.acy, self.acz, self.gyx, self.gyy, self.gyz, self.pitch, self.roll, self.yaw))
            self.newdata.emit(signal)
        else:
            print('数据格式错误，接收到的数据为：', data)

    def read_all(self, port, chunk_size=200):
        """Read all characters on the serial port and return them.
        参考：https://stackoverflow.com/questions/19161768/pyserial-inwaiting-returns-incorrect-number-of-bytes
        """
        if not port.timeout:
            raise TypeError('Port needs to have a timeout set!')

        read_buffer = b''
        while True:
            # Read in chunks. Each chunk will wait as long as specified by
            # timeout. Increase chunk_size to fail quicker
            byte_chunk = port.read(size=chunk_size)
            read_buffer += byte_chunk
            if not len(byte_chunk) == chunk_size:
                break

        return read_buffer

    # 从串口读取数据
    def read_from_port(self, ser):
        while True:
            bytedata = self.read_all(ser)
            if bytedata:
                self.process_data(bytedata.decode())  # 处理数据

    # 停止线程
    def stopThread(self):
        print('Stop the thread...')

    def closeEvent(self, event):
        if self.okToContinue():
            event.accept()
            self.stopThread()
        else:
            event.ignore()

    def okToContinue(self):
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    app.exec_()
