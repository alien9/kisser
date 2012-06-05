#!/usr/bin/env python
from freenect import sync_get_depth as get_depth, sync_get_video as get_video

import cv
import numpy
from utility import *
import sys, os, re
import thread
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, SIGNAL, QEvent, QPoint, QSize
from kisser import Ui_MainWindow
from PyQt4.QtGui import *
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import barulho
from choose import Ui_Dialog
from subprocess import call

class StartSub2(QtGui.QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
    def getValues(self):
        return self.ui.alone.isChecked()
class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.ui.setupUi(self)
        self.label = self.ui.label
        #values=self.sozinho()
        #self.trick()
        self.loop=Loop(True)
        but=self.ui.pushButton
        but.clicked.connect(self.sozinho)
        self.label.setScaledContents(True) 
    def keyPressEvent(self, e):
        print e.key()
        if e.key() == QtCore.Qt.Key_Escape or e.key()==16777227:
            self.loop.stop()
            #self.close()
        if e.key()==16777221: # ENTER
            self.sozinho()
        if e.key()==45: # -
            self.sarva(3)

            
    def sozinho(self):
        self.loop.stop()
        dlg = StartSub2(self)
        if dlg.exec_():
            self.trick(dlg.getValues()) #sozinho ou acompanhado
    def photo(self, a, b):
        self.loop.refresh(a, b)
    def update(self,  pic):
        pix=QPixmap.fromImage(pic)
        
        self.label.setPixmap(pix)
    def trick(self, solo):
        storage = cv.CreateMemStorage()
        haar=cv.Load('haarcascades/haarcascade_profileface.xml')
        self.loop=Loop(solo)
        self.connect(self.loop,  QtCore.SIGNAL('update(QImage)'),  self.update)
        self.connect(self.loop,  QtCore.SIGNAL('save()'),  self.sarva)
        self.loop.start()
    def sarva(self,veces=3):
        self.loop.stop()
        time.sleep(1)
        capture = cv.CaptureFromCAM(0)
        files=os.listdir("output/")
        files.sort()
        u=0
        if len(files) > 0:
            s=re.search("_(\d+)_", files[len(files)-1])
            if s:
                u=1+int(s.group(1))
        for i in range(0,veces):
            cc = cv.QueryFrame(capture)
            cv.SaveImage("output/photo_"+str('%05d' % u)+"_"+str(int(time.time()))+".png",cc)
            time.sleep(1)
            barulho.toca("camera.mp3")
        call(["eject","/dev/sr0"])
        call(["eject","-t","/dev/sr0"])
        
class Loop(QtCore.QThread):
    def __init__(self, solo):
        self.solo=solo
        self._stop = False
        QtCore.QThread.__init__(self)
        self.rgb=None
        self.dep=None        
    def stop(self):
        self._stop = True
    def refresh(self, a, b):
        self.rgb=a
        self.dep=b
    def run(self):
        heat=0
        storage = cv.CreateMemStorage()
        if not self.solo:
            haar=cv.Load('haarcascades/haarcascade_profileface.xml') 
        else:
            haar=cv.Load('haarcascades/haarcascade_frontalface_default.xml') 
        while not self._stop:
            # Get a fresh framepython
            (depth,_), (rgb,_) = get_depth(), get_video()
            
            #if self.dep and self.rgb:
        
            image=array2PIL(rgb, (640, 480))
            
            #o=rgb.astype(numpy.uint8)
            w=depth.astype(numpy.uint8)
            o=cv.fromarray(rgb)
            grayscale = cv.CreateImage((640,  480), 8, 1)
            cv.CvtColor(o, grayscale, cv.CV_BGR2GRAY)
            storage = cv.CreateMemStorage(0)
            #cv.ClearMemStorage(storage)
            # equalize histogram
            cv.EqualizeHist(grayscale, grayscale)
            
            faces = cv.HaarDetectObjects(grayscale, haar, storage, 1.1, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (30, 30))
            left=None
            right=None
            if faces:
                draw=ImageDraw.Draw(image)
                for face in faces:
                    #print "left"
                    #print face
                    r=face[0]
                    draw.rectangle((r[0], r[1],  r[0]+r[2],  r[1]+r[3]), outline="green")
                    left=(r[0]+r[2]/2, r[1]+r[3]/2)
                    #barulho.toca("sweep1.mp3")
            if not self.solo:
                cv.Flip(grayscale, grayscale, 1)
                faces = cv.HaarDetectObjects(grayscale, haar, storage, 1.1, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (30, 30))
                if faces:
                    draw=ImageDraw.Draw(image)
                    for face in faces:
                        #print "right"
                        #print face
                        r=face[0]
                        draw.rectangle((640-r[0]-r[2], r[1],  640-r[0], r[1]+r[3]), outline="yellow")
                        right=(640-r[0]-r[2]/2, r[1]+r[3]/2)
                        #barulho.toca("sweep_medium.mp3")
            else:
                right=left
            if left and right:
                #print "distancia esquerda:"
                #print w[left[1]][left[0]]
                #print "distancia direita:"
                #print w[right[1]][right[0]]
                print heat
                print str(w[left[1]][left[0]]) + "_"+ str(w[right[1]][right[0]])
                if w[left[1]][left[0]] - w[right[1]][right[0]] < 50:
                    heat+=1
                    if not self.solo:
                        heat+=10
                    if heat>10:
                    #barulho.toca("sweep1.mp3")
                        self.emit(QtCore.SIGNAL('save()'))
                        return
            else:
                heat-=1
            if heat<0:
                heat=0
            qi=ImageQt(image.transpose(Image.FLIP_LEFT_RIGHT)) #PILimageToQImage(image)
            self.emit(QtCore.SIGNAL('update(QImage)'), qi)
        return


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
    
    


"""
IPython usage:
 ipython
 [1]: run -i demo_freenect
 #<ctrl -c>  (to interrupt the loop)
 [2]: %timeit -n100 get_depth(), get_rgb() # profile the kinect capture

"""
