#!/usr/bin/env python
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
import cv
import numpy
from utility import *
import sys
import thread
import time
from PyQt4 import QtCore, QtGui
from kisser import Ui_MainWindow
from PyQt4.QtGui import *
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import barulho

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        
        
        self.ui.setupUi(self)
        self.label = self.ui.label
        #self.scene = QGraphicsScene()
        
        #grview.setScene(self.scene)
        self.trick()
        
        #thread.start_new_thread ( self.trick, (1,) )
        #(depth,_), (rgb,_) = get_depth(), get_video()
        #self.update(rgb)
        
    def update(self,  pic):
        pix=QPixmap.fromImage(pic)
        self.label.setPixmap(pix)
    def trick(self):
        storage = cv.CreateMemStorage()
        haar=cv.Load('haarcascades/haarcascade_profileface.xml')
        self.loop=Loop()
        self.connect(self.loop,  QtCore.SIGNAL('update(QImage)'),  self.update)
        self.loop.start()
        #scene.addPixmap(QPixmap('pic.jpg'))
"""
        while True:
            # Get a fresh frame
            (depth,_), (rgb,_) = get_depth(), get_video()
            img=array2PIL(rgb, (640, 480))
            print "a"
            self.emit(QtCore.SIGNAL('update(QImage)'), rgb)
"""

class Loop(QtCore.QThread):
    def __init__(self):
        print "init"
        QtCore.QThread.__init__(self)
 
    def run(self):
        storage = cv.CreateMemStorage()
        haar=cv.Load('haarcascades/haarcascade_profileface.xml') 
        while True:
            # Get a fresh framepython
            (depth,_), (rgb,_) = get_depth(), get_video()
            #o=rgb.astype(numpy.uint8)
            o=cv.fromarray(rgb)
            #grayscale = cv.CreateImage(o.size, 8, 1)
            grayscale = cv.CreateImage((640,  480), 8, 1)
            cv.CvtColor(o, grayscale, cv.CV_BGR2GRAY)
            storage = cv.CreateMemStorage(0)
            #cv.ClearMemStorage(storage)
            # equalize histogram
            cv.EqualizeHist(grayscale, grayscale)
            image=array2PIL(rgb, (640, 480))
            #image=numpy2qimage(rgb)
            
            faces = cv.HaarDetectObjects(grayscale, haar, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50, 50))
            if faces:
                draw=ImageDraw.Draw(image)
                for face in faces:
                    print face
                    r=face[0]
                    draw.rectangle((r[0], r[1],  r[0]+r[2],  r[1]+r[3]), outline="green")
                    barulho.toca("sweep1.mp3")
            cv.Flip(grayscale, grayscale, 1)
            faces = cv.HaarDetectObjects(grayscale, haar, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50, 50))
            if faces:
                draw=ImageDraw.Draw(image)
                for face in faces:
                    print face
                    r=face[0]
                    draw.rectangle((640-r[0], 480-r[1],  640-r[0]+r[2],  480-r[1]+r[3]), outline="yellow")
                    barulho.toca("sweep_medium.mp3")
            
            
            qi=ImageQt(image) #PILimageToQImage(image)
            self.emit(QtCore.SIGNAL('update(QImage)'), qi)
        return


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())
    
    

def doloop():
    global depth, rgb
    storage = cv.CreateMemStorage()
    haar=cv.Load('haarcascades/haarcascade_profileface.xml')
    while True:
        # Get a fresh frame
        (depth,_), (rgb,_) = get_depth(), get_video()
        
        # Build a two panel color image
        #depth = numpy.dstack((depth,depth,depth)).astype(numpy.uint8)
        
        
        depth=depth.astype(numpy.uint8)
        rgb=rgb.astype(numpy.uint8)
        detected = cv.HaarDetectObjects(array2PIL(rgb,(640,480)), haar, storage, 1.2, 2,cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))
        if detected:
            for face in detected:
                print face
        
        cv.Threshold(depth,depth,180, 255, cv.CV_THRESH_BINARY)
        cv.Not(depth,depth)
        #image2 = numpy.copy( rgb );
        #cv.Zero(image2)
        u=cv.CreateImage(cv.GetSize(rgb), 8, 3)
        cv.Copy(rgb,u,depth)
        cv.Flip(u,None,1)
        cv.ShowImage("depth",u)
        
        #cv.ShowImage("depth",rgb)
        
        #da = numpy.hstack((d3,rgb))
        
        # Simple Downsample
        #cv.ShowImage('both',numpy.array(da[::2,::2,::-1]))
        cv.WaitKey(5)
        
#doloop()

"""
IPython usage:
 ipython
 [1]: run -i demo_freenect
 #<ctrl -c>  (to interrupt the loop)
 [2]: %timeit -n100 get_depth(), get_rgb() # profile the kinect capture

"""

