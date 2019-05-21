from PyQt5.QtWidgets import QDialog, QMessageBox
import cv2
import numpy as np
from ui_calibrateDialog import Ui_CalibrateDialog


class Calibrate(QDialog):
    def __init__(self, parent=None):
        super(Calibrate, self).__init__(parent)

        self.ui = Ui_CalibrateDialog()
        self.ui.setupUi(self)
        self.ui.calibrateButton.setDisabled(True)
        self.ui.calibrateButton.clicked.connect(self.calibrate)

        self.w = 8
        self.h = 6

        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.objp = np.zeros((self.w * self.h, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.w, 0:self.h].T.reshape(-1, 2)
        self.objpoints = []
        self.imgpoints = []

        self.im2 = None
        self.gray = None

        self.pic_count = 0

    def run(self, im):
        if self.pic_count > 1:
            return
        self.im2 = im
        self.gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(self.gray, (self.w, self.h), None)
        if ret:
            cv2.cornerSubPix(self.gray, corners, (11, 11), (-1, -1), self.criteria)
            self.objpoints.append(self.objp)
            self.imgpoints.append(corners)
            cv2.drawChessboardCorners(im, (self.w, self.h), corners, ret)
            self.pic_count += 1
            self.ui.NumLabel.setText(str(self.pic_count))
            if self.pic_count > 1:
                self.ui.calibrateButton.setDisabled(False)
            cv2.imshow('success', im)
        else:
            QMessageBox.information(self, '错误', '检查棋盘格状态', QMessageBox.Ok, QMessageBox.Ok)

    def calibrate(self):
        self.ui.statusLabel.setText('正在标定')
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, self.gray.shape[::-1], None, None)
        h, w = self.im2.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
        np.save('cameradata/mtx.npy', mtx)
        np.save('cameradata/dist.npy', dist)
        np.save('cameradata/newcameramtx.npy', newcameramtx)
        self.ui.statusLabel.setText('标定成功')
        # dst = cv2.undistort(self.im2, mtx, dist, None, newcameramtx)
