import sys
from ui_mainwindow import Ui_MainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from calibrate import Calibrate
import serial.tools.list_ports
import serial
import multiprocessing
import os


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.exportButton.setDisabled(True)
        self.ui.surfaceButton.setDisabled(True)
        self.calibrator = Calibrate()
        self.ui.CPULabel.setText(str(multiprocessing.cpu_count()))
        self.ui.spinBox.setMaximum(multiprocessing.cpu_count())
        self.iren = self.ui.vtkWidget.GetRenderWindow().GetInteractor()
        self.ui.graphwidget.recon.vtkWidget = self.ui.vtkWidget
        self.ui.cvViewer.PosFound.connect(self.ui.graphwidget.drawScatter)
        self.ui.checkBox.stateChanged.connect(self.start_scanning)
        self.ui.surfaceButton.clicked.connect(self.ui.graphwidget.drawSurface)
        self.ui.calibrateButton.clicked.connect(self.calibrator.show)
        self.calibrator.ui.captureButton.clicked.connect(lambda: self.calibrator.run(self.ui.cvViewer.camera.img))
        self.ui.refreshButton.clicked.connect(self.serial_refresh)
        self.ui.comboBox.currentIndexChanged['int'].connect(self.serialdata_refresh)
        self.ui.cvViewer.finder.finished.connect(lambda: self.ui.checkBox.setCheckState(Qt.Unchecked))
        self.ui.cvViewer.finder.finished.connect(lambda: self.ui.surfaceButton.setDisabled(False))
        self.ui.cvViewer.motion.motionProgress['int'].connect(self.ui.progressBar.setValue)
        self.ui.cvViewer.finder.foundProgress['int'].connect(self.ui.scanprogressBar.setValue)
        self.ui.graphwidget.recon.reconstruction_status.connect(self.ui.textEdit.append)
        self.ui.graphwidget.recon.reconstruction_done.connect(self.recon_done)
        self.ui.spinBox.valueChanged.connect(self.ui.cvViewer.finder.setnump)
        self.ui.exportButton.clicked.connect(self.ui.graphwidget.export)

    def recon_done(self):
        self.iren.Initialize()
        self.ui.exportButton.setDisabled(False)

    def start_scanning(self):
        if self.ui.serialLabel.text() == '无串口' and self.ui.checkBox.isChecked():
            QMessageBox.information(self, '提示', '未连接串口', QMessageBox.Ok, QMessageBox.Ok)
            self.ui.checkBox.setCheckState(Qt.Unchecked)
            return
        if not os.path.exists('cameradata/newcameramtx.npy'):
            QMessageBox.information(self, '提示', '请先标定相机', QMessageBox.Ok, QMessageBox.Ok)
            self.ui.checkBox.setCheckState(Qt.Unchecked)
            return
        self.ui.cvViewer.finderState(self.ui.checkBox.isChecked(), self.ui.comboBox.currentText())

    def serial_refresh(self):
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems([str(x).split(' - ')[0] for x in list(serial.tools.list_ports.comports())])
        print([str(x) for x in list(serial.tools.list_ports.comports())])

    def serialdata_refresh(self, i):
        data = [str(x).split(' - ')[1] for x in list(serial.tools.list_ports.comports())][i]
        self.ui.serialLabel.setText(data)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
