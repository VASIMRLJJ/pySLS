import pyqtgraph.opengl as gl
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
import pcl
import os
import vtk
import numpy as np


class pgWidget(gl.GLViewWidget):
    def __init__(self, parent=None):
        super(pgWidget, self).__init__(parent)

        self.zgrid = gl.GLGridItem()
        self.addItem(self.zgrid)

        self.points = []
        self.distance = 0

        self.sp = gl.GLScatterPlotItem(pos=np.array([[0, 0, 0]]), size=0.05, color=(1.0, 1.0, 1.0, 0.5), pxMode=False)
        self.addItem(self.sp)

        self.recon = Reconstructor()

        # self.drawSurface()

    def drawSurface(self):
        p = pcl.PointCloud(np.array(self.points, dtype=np.float32))
        # seg = p.make_segmenter()
        # seg.set_model_type(pcl.SACMODEL_PLANE)
        # seg.set_method_type(pcl.SAC_RANSAC)
        # indices, model = seg.segment()
        # print(model)
        pcl.save(p, '1.pcd', 'pcd')
        self.recon.start()

    def drawScatter(self, x, d):
        py = pz = 0
        for px in x:
            px += 200
            if px == 200:
                continue
            elif px < 320:
                px = px/640*230.94
                a = 115.47 - px
                pz = -a/(1-a/200)
                px -= pz*a/200
            elif px == 320:
                px = 115.47
            elif px > 320:
                px = px/640*230.94
                a = px - 115.47
                pz = a*200/(200+a)
                px -= pz*a/200
            self.points.append([(px-115.47+d)/10, py/640*230.94/10, pz/10])
            py += 1
        self.sp.setData(pos=np.array(self.points))
        # self.distance += 1

    def export(self):
        filename, ok = QFileDialog.getSaveFileName(self, "文件保存", "/", "STL Files(*.stl)")

        source = vtk.vtkPolyDataReader()
        source.SetFileName('2.vtk')
        source.Update()

        stlWriter = vtk.vtkSTLWriter()
        stlWriter.SetFileName(filename)
        stlWriter.SetInputConnection(source.GetOutputPort())
        stlWriter.Write()


class Reconstructor(QThread):
    reconstruction_status = pyqtSignal(str)
    reconstruction_done = pyqtSignal()

    def __init__(self, parent=None):
        super(Reconstructor, self).__init__(parent)

        self.running = False
        self.vtkWidget = None
        self.ren = vtk.vtkRenderer()

    def __del__(self):
        self.wait()

    def run(self):
        self.running = True
        self.reconstruction_status.emit('开始重建...')
        path = os.path.abspath(r'pcl_tools/pcl_normal_estimation_release.exe')
        os.system(path + ' 1.pcd 2.pcd -radius 8')
        self.reconstruction_status.emit('点云提取完成')
        path = os.path.abspath(r'pcl_tools/pcl_poisson_reconstruction_release.exe')
        os.system(path + ' 2.pcd 2.vtk')
        self.reconstruction_status.emit('重建完成')

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        source = vtk.vtkPolyDataReader()
        source.SetFileName('2.vtk')
        source.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        self.reconstruction_done.emit()
        self.running = False
