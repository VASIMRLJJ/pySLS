from PyQt5.QtCore import pyqtSignal, QThread, Qt, QPoint, QRect, QMutex
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtWidgets import QLabel
import cv2
import serial
from queue import Empty
import multiprocessing
import numpy as np


class CVWidget(QLabel):
    PosFound = pyqtSignal(list, int)

    def __init__(self, parent=None):
        super(CVWidget, self).__init__(parent)

        self.mm = 100

        self.camera = CamThread()
        self.camera.CaptureFinished.connect(self.pictureUpdate)
        self.camera.NoCamera.connect(self.pictureUpdate)
        self.camera.start()

        self.finder = CenterFinder(self.mm)
        self.finder.centerFound.connect(self.lineUpdate)

        self.motion = Motion(self.mm)
        self.motion.finished.connect(self.finder_start)

        self.fifo = multiprocessing.JoinableQueue()

        self.x = []
        self.img = None
        self.distance = 0

    def finder_start(self):
        self.camera.CaptureFinished.disconnect(self.worker)
        self.camera.CaptureFinished.connect(self.pictureUpdate)

        self.finder.img = self.fifo
        self.finder.start()

    def finderState(self, checked, port):
        if checked:
            self.camera.CaptureFinished.disconnect(self.pictureUpdate)
            self.camera.CaptureFinished.connect(self.worker)
            self.motion.port = port
            self.camera.mtx = np.load('cameradata/mtx.npy')
            self.camera.dist = np.load('cameradata/dist.npy')
            self.camera.newcameramtx = np.load('cameradata/newcameramtx.npy')
            self.distance = 0
            self.motion.start()

        else:
            if self.finder.isRunning():
                self.camera.CaptureFinished.disconnect(self.worker)
                self.camera.CaptureFinished.connect(self.pictureUpdate)

    def worker(self):
        if self.motion.home:
            self.motion.trigger = True
            print(self.distance)
            self.fifo.put((self.camera.th1, self.distance))
            self.distance += 1
            self.pictureUpdate()

    def pictureIdle(self):
        self.img = None
        self.resize(100, 100)
        self.setText('no camera')

    def pictureUpdate(self):
        try:
            height, width = self.camera.img.shape[:2]
            # print(height, width)
            self.resize(width, height)
            self.img = QImage(self.camera.img,
                              width,
                              height,
                              QImage.Format_RGB888)
            self.update()
            self.setScaledContents(True)
        except:
            pass

    def lineUpdate(self, d):
        self.x = self.finder.x
        self.PosFound.emit(self.x, d)

    def paintEvent(self, QPaintEvent):
        if self.img is None:
            return
        py = 0
        width = self.width()
        height = self.height()
        target = QRect(0, 0, width, height)
        sourse = QRect(0, 0, width, height)
        painter = QPainter(self)
        painter.drawImage(target, self.img, sourse)
        qp = QPainter()
        qp.begin(self)
        qp.setPen(Qt.blue)
        for px in self.x:
            qp.drawPoint(px, py)
            py += 1
        qp.end()


class Motion(QThread):
    motionProgress = pyqtSignal(int)

    def __init__(self, mm: int, parent=None):
        super(Motion, self).__init__(parent)

        self.trigger = False
        self.mm = mm
        self.port = ''
        self.home = False

    def __del__(self):
        self.wait()

    def run(self):
        self.home = False
        with serial.Serial(self.port, 9600) as s:
            s.write(b'h')
            s.read(2)
            self.home = True
            for i in range(self.mm):
                while not self.trigger:
                    self.sleep(0.01)
                s.write(b's')
                self.motionProgress.emit(int((i+1)/self.mm*100))
                self.trigger = False


class CamThread(QThread):
    CaptureFinished = pyqtSignal()
    NoCamera = pyqtSignal()

    def __init__(self, parent=None):
        super(CamThread, self).__init__(parent)

        self.point_size = 1
        self.point_color = (0, 255, 0)  # BGR
        self.thickness = 4  # 可以为 0 、4、8

        self.cap = cv2.VideoCapture(0)
        self.img = None
        self.th1 = None

        self.mtx = None
        self.dist = None
        self.newcameramtx = None

    def __del__(self):
        self.wait()

    def run(self):
        while self.cap.isOpened():
            ret, img = self.cap.read()
            if img is None:
                break
            img = img[0:480, 200:600]
            if self.mtx is not None:
                img = cv2.undistort(img, self.mtx, self.dist, None, self.newcameramtx)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.th1 = cv2.GaussianBlur(gray, (3, 3), 1)
            self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.CaptureFinished.emit()
            cv2.waitKey(30)
        self.NoCamera.emit()


class CenterFinder(QThread):
    centerFound = pyqtSignal(int)
    foundProgress = pyqtSignal(int)

    def __init__(self, mm: int, parent=None):
        super(CenterFinder, self).__init__(parent)
        self.img = None
        self.mm = mm
        self.x = []
        self.finding = False
        self.func = Cvpointgray
        self.lock = multiprocessing.Lock()
        self.conn_p, self.conn_c = multiprocessing.Pipe(False)
        self.nump = 2

    def __del__(self):
        self.wait()

    def setnump(self, nump: int):
        self.nump = nump

    def run(self):
        while not self.img:
            self.sleep(0.1)
        for i in range(self.nump):
            p = multiprocessing.Process(target=self.func,
                                        args=(self.img, self.conn_c, self.lock))
            p.daemon = True
            p.start()
        for i in range(self.mm):
            rec = self.conn_p.recv()
            print(i)
            self.x = rec[1]
            self.foundProgress.emit(int((i + 1) / self.mm * 100))
            self.centerFound.emit(rec[0])
        self.img.join()


def Cvpointgray(imgs: multiprocessing.JoinableQueue, conn, l: multiprocessing.Lock):
    while True:
        try:
            img, d = imgs.get()
        except Empty:
            break
        x = []
        mean = np.mean(img)
        for j in range(img.shape[0]):
            x0 = 0
            y0 = 0
            ym = []
            for i in range(1, img.shape[1]):
                ym.append(img[j, i])
                x0 = x0 + int(img[j, i]) ** 4
                y0 = y0 + int(img[j, i]) ** 4 * i
            if x0 == 0 or np.mean(ym) < mean:
                y = 0
            else:
                y = y0 / x0
            y = round(y)
            x.append(y)
        print(d)
        l.acquire()
        conn.send([d, x])
        l.release()
        imgs.task_done()
