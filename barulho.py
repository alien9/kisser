#! /usr/bin/python
import pyaudio
import mad
import sys

def toca(fu):
    p = pyaudio.PyAudio()
    pu=mad.MadFile(fu)
    stream=p.open(format = p.get_format_from_width(pyaudio.paInt32), channels = 2, rate = pu.samplerate(), output = True)
    data = pu.read()
    while data != None:
        stream.write(data)
        data = pu.read()

    stream.close()
    p.terminate()

