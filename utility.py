"""
   Copyright 2011 Shao-Chuan Wang <shaochuan.wang AT gmail.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

import numpy
import Image
from PyQt4.QtGui import *
from PIL import Image
from PIL.ImageQt import ImageQt

def PIL2array(img):
    return numpy.array(img.getdata(),
                    numpy.uint8).reshape(img.size[1], img.size[0], 3)
def PILimageToQImage(pilimage):
    #converts a PIL image to QImage
    imageq = ImageQt(pilimage) #convert PIL image to a PIL.ImageQt object
    qimage = QImage(imageq) #cast PIL.ImageQt object to QImage object -that's the trick!!!
    return qimage
def array2PIL(arr, size):
    mode = 'RGBA'
    arr = arr.reshape(arr.shape[0]*arr.shape[1], arr.shape[2])
    if len(arr[0]) == 3:
        arr = numpy.c_[arr, 255*numpy.ones((len(arr),1), numpy.uint8)]
    return Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)

def main():
    img = loadImage('foo.jpg')
    arr = PIL2array(img)
    img2 = array2PIL(arr, img.size)
    img2.save('out.jpg')
def numpy2qimage(array):
    if numpy.ndim(array) == 2:
        return gray2qimage(array)
    elif numpy.ndim(array) == 3:
        return rgb2qimage(array)
    raise ValueError("can only convert 2D or 3D arrays")
def gray2qimage(gray):
    """Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
    colormap.  The first dimension represents the vertical image axis."""
    if len(gray.shape) != 2:
        raise ValueError("gray2QImage can only convert 2D arrays")

    gray = numpy.require(gray, numpy.uint8, 'C')

    h, w = gray.shape

    result = QImage(gray.data, w, h, QImage.Format_Indexed8)
    result.ndarray = gray
    for i in range(256):
        result.setColor(i, QColor(i, i, i).rgb())
    return result
    
def rgb2qimage(rgb):
    """Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
    have three dimensions with the vertical, horizontal and RGB image axes."""
    if len(rgb.shape) != 3:
        raise ValueError("rgb2QImage can expects the first (or last) dimension to contain exactly three (R,G,B) channels")
    if rgb.shape[2] != 3:
        raise ValueError("rgb2QImage can only convert 3D arrays")

    h, w, channels = rgb.shape

    # Qt expects 32bit BGRA data for color images:
    bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
    bgra[...,0] = rgb[...,2]
    bgra[...,1] = rgb[...,1]
    bgra[...,2] = rgb[...,0]
    bgra[...,3].fill(255)

    result = QImage(bgra.data, w, h, QImage.Format_RGB32)
    result.ndarray = bgra
    return result
if __name__ == '__main__':
    main()
