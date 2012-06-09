#!/usr/bin/env python
from freenect import sync_get_depth as get_depth, sync_get_video as get_video

import cv
import numpy
from utility import *
import sys, os, re
import thread
import time
from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import Qt, SIGNAL, QEvent, QPoint, QSize, QUrl
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
        #self.setWindowState(Qt.WindowFullScreen)
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.ui.setupUi(self)
        #self.ui.setPixmap('sistema_detecta.jpg')
        self.setStyleSheet("QMainWindow {font-size : 400px; color : blue; background-image: url('sistema_detecta.jpg'); background-repeat:no-repeat;} \n QLabel#label_2 {background-image: url('boca.jpg')}");
        webview=self.ui.webView
        websettings = webview.settings()
        websettings.setAttribute(QtWebKit.QWebSettings.PluginsEnabled,True)
        webview.load(QUrl('http://localhost/~tiago/works/nivea/standby.html'))
        webview.setAttribute(Qt.WA_TranslucentBackground)
        # Works with and without that following line
        webview.setAttribute(Qt.WA_OpaquePaintEvent, False)
        page = webview.page()
        palette = page.palette()
        palette.setBrush(QtGui.QPalette.Base, Qt.transparent)
        page.setPalette(palette)
        page.currentFrame().documentElement().setInnerXml("text")
        self.label = self.ui.label
        #values=self.sozinho()
        #self.trick()
        self.loop=Loop(True)
        self.label.setScaledContents(True) 
    def keyPressEvent(self, e):
        k=e.key()
        print e.key()
        if k == QtCore.Qt.Key_Escape or k==16777227:
            self.loop.stop()
            #self.close()
            self.setKinect(False)
        if k==16777221 or k==16777220: # ENTER
            self.sozinho()
        if k==45: # -
            self.sarva(3)
        if k==16777233 or k==49: #so
            self.setKinect(True)
            self.loop.stop()
            self.trick(True)
        if k==16777237 or k==50: #acompanhado
            self.setKinect(True)
            self.loop.stop()
            self.trick(False)
        if k==32 or k==42: # '*', comece a disparar...
            self.loop.wakeup()
    def setKinect(self,kinect):
        if kinect:
            self.ui.webView.setMinimumSize(QtCore.QSize(647, 694))
            self.ui.webView.setMaximumSize(QtCore.QSize(647, 694))
            self.label.setMinimumSize(QtCore.QSize(640, 480))
            self.label.setMaximumSize(QtCore.QSize(640, 480))

        else:
            self.label.setMinimumSize(QtCore.QSize(0, 480))
            self.label.setMaximumSize(QtCore.QSize(0, 480))
            self.ui.webView.setMinimumSize(QtCore.QSize(640, 480))
            self.ui.webView.setMaximumSize(QtCore.QSize(640, 480))       
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
        #self.ui.label_2.setMinimumSize(QtCore.QSize(0, 96))
        #self.ui.label_2.setMaximumSize(QtCore.QSize(0, 96))
        self.ui.label_2.setText("")
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
        self.ui.label_2.setText(str('%05d' % u))
        self.ui.label_2.setMinimumSize(QtCore.QSize(338, 96))
        self.ui.label_2.setMaximumSize(QtCore.QSize(338, 96))
        call(["eject","/dev/sr0"])
        call(["eject","-t","/dev/sr0"])
        self.trick(True)
class Loop(QtCore.QThread):
    def __init__(self, solo):
        self.solo=solo
        self._stop = False
        QtCore.QThread.__init__(self)
        self.rgb=None
        self.dep=None
        self.online=False
    def stop(self):
        self._stop = True
    def refresh(self, a, b):
        self.rgb=a
        self.dep=b
    def wakeup(self):
        self.online=True
    def run(self):
        heat=0
        storage = cv.CreateMemStorage()
        if not self.solo:
            haar=cv.Load('haarcascades/haarcascade_profileface.xml') 
        else:
            haar=cv.Load('haarcascades/haarcascade_frontalface_default.xml')
        threshold=10
        while not self._stop:
            # Get a fresh framepython
            (depth,_), (rgb,_) = get_depth(), get_video()
            
            #if self.dep and self.rgb:
        
            #image=array2PIL(rgb, (640, 480))
            
            #o=rgb.astype(numpy.uint8)
            w=depth.astype(numpy.uint8)
            o=cv.fromarray(rgb)
            if self.online:
                grayscale = cv.CreateImage((640,  480), 8, 1)
                cv.CvtColor(o, grayscale, cv.CV_BGR2GRAY)
                storage = cv.CreateMemStorage(0)
                #cv.ClearMemStorage(storage)
                # equalize histogram
                cv.EqualizeHist(grayscale, grayscale)
                
                faces = cv.HaarDetectObjects(grayscale, haar, storage, 1.1, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (30, 30))
                left=None
                right=None
                if self.solo:
                    threshold=20
                if faces:
                    #draw=ImageDraw.Draw(image)
                    for face in faces:
                        print "FORCE "+str(face[1])
                        if face[1] > threshold:
                        #face=faces[0]
                            r=face[0]
                            i=face[0]
                            #draw.rectangle((r[0], r[1],  r[0]+r[2],  r[1]+r[3]), outline="green")
                            #cv.Rectangle(o, ( int(r[0]), int(r[1])),
                            #         (int(r[0]+r[2]), int(r[1]+r[3])),
                            #         cv.RGB(0, 255, 0), 3, 8, 0)
                            cv.Circle(o, (int(r[0]+r[3]/2), int(r[1]+r[3]/2)),r[3]/2,cv.RGB(255, 50, 50), 3, 8, 0)
                            #cv.EllipseBox(o, r, cv.RGB(0, 255, 0))
                            #draw.ellipse((r[0], r[1],  r[0]+r[2],  r[1]+r[3]), fill="green")
                            #draw.ellipse((r[0]+3, r[1]+3,  r[0]+r[2]-3,  r[1]+r[3]-3), fill=None)
                            left=(r[0]+r[2]/2, r[1]+r[3]/2)
                if not self.solo:
                    cv.Flip(grayscale, grayscale, 1)
                    faces = cv.HaarDetectObjects(grayscale, haar, storage, 1.1, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (30, 30))
                    if faces:
                        #draw=ImageDraw.Draw(image)
                        for face in faces:
                            if face[1] > threshold:
                                face=faces[0]
                                r=face[0]
                                cv.Circle(o, (int(640-r[0]-r[3]/2), int(r[1]+r[3]/2)),r[3]/2,cv.RGB(255, 50, 50), 3, 8, 0)
                                #draw.rectangle((640-r[0]-r[2], r[1],  640-r[0], r[1]+r[3]), outline="yellow")
                                right=(640-r[0]-r[2]/2, r[1]+r[3]/2)
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
            qi=toQImage(numpy.asarray(o),True) #array2PIL(rgb, (640, 480))
            #qi=ImageQt(image.transpose(Image.FLIP_LEFT_RIGHT)) #PILimageToQImage(image)
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
