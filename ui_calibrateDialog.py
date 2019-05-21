# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calibrateDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CalibrateDialog(object):
    def setupUi(self, CalibrateDialog):
        CalibrateDialog.setObjectName("CalibrateDialog")
        CalibrateDialog.resize(400, 128)
        CalibrateDialog.setSizeGripEnabled(False)
        self.captureButton = QtWidgets.QPushButton(CalibrateDialog)
        self.captureButton.setGeometry(QtCore.QRect(220, 50, 75, 23))
        self.captureButton.setObjectName("captureButton")
        self.groupBox = QtWidgets.QGroupBox(CalibrateDialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 171, 101))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 20, 131, 101))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(CalibrateDialog)
        self.label_2.setGeometry(QtCore.QRect(220, 20, 81, 16))
        self.label_2.setObjectName("label_2")
        self.NumLabel = QtWidgets.QLabel(CalibrateDialog)
        self.NumLabel.setGeometry(QtCore.QRect(300, 20, 54, 16))
        self.NumLabel.setObjectName("NumLabel")
        self.calibrateButton = QtWidgets.QPushButton(CalibrateDialog)
        self.calibrateButton.setGeometry(QtCore.QRect(220, 90, 75, 23))
        self.calibrateButton.setObjectName("calibrateButton")
        self.statusLabel = QtWidgets.QLabel(CalibrateDialog)
        self.statusLabel.setGeometry(QtCore.QRect(310, 90, 71, 21))
        self.statusLabel.setObjectName("statusLabel")

        self.retranslateUi(CalibrateDialog)
        QtCore.QMetaObject.connectSlotsByName(CalibrateDialog)

    def retranslateUi(self, CalibrateDialog):
        _translate = QtCore.QCoreApplication.translate
        CalibrateDialog.setWindowTitle(_translate("CalibrateDialog", "相机标定"))
        self.captureButton.setText(_translate("CalibrateDialog", "捕获图片"))
        self.groupBox.setTitle(_translate("CalibrateDialog", "使用方法"))
        self.label.setText(_translate("CalibrateDialog", "标定需要捕获两张棋盘格图片，两张图片棋盘格角度和位置不能相同，同时务必保证图像中包含完整的棋盘格"))
        self.label_2.setText(_translate("CalibrateDialog", "捕获图片数："))
        self.NumLabel.setText(_translate("CalibrateDialog", "0"))
        self.calibrateButton.setText(_translate("CalibrateDialog", "标定"))
        self.statusLabel.setText(_translate("CalibrateDialog", "未标定"))

