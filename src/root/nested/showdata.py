#!/usr/bin/python
################################################################################
# showdata.py
#
# Display analog data from Arduino using Python (matplotlib)
# 
# electronut.in
#
################################################################################

import sys, serial
import numpy as np
from time import sleep
from collections import deque
from matplotlib import pyplot as plt

# timing stuff from udacity CS212
import time

def timedcall(fn, *args):
    "Call function with args; return the time in seconds and result."
    t0 = time.clock()
    result = fn(*args)
    t1 = time.clock()
    return t1-t0, result

def average(numbers):
    "Return the average (arithmetic mean) of a sequence of numbers."
    return sum(numbers) / float(len(numbers)) 

def timedcalls(n, fn, *args):
    """Call fn(*args) repeatedly: n times if n is an int, or up to
    n seconds if n is a float; return the min, avg, and max time"""
    if isinstance(n, int):
        times= [timedcall(fn, *args)[0] for _ in range(n)] 
    elif isinstance(n, float):
        times= []        
        t1= time.clock()
        tstop= t1 + n
        while t1 < tstop:
            t0 = time.clock()
            fn(*args)
            t1= time.clock()
            times.append(t1-t0)
    else:
        times= None
    if times:
        return min(times), average(times), max(times)


# class that holds analog data for N samples
class AnalogData:
    # constr
    def __init__(self, maxLen, channels=2):
        self.a = [deque([0.0]*maxLen) for c in range(channels)]
        self.maxLen = maxLen
        self.channels = channels

    # ring buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        assert(len(data) == self.channels)
        for c in range(self.channels):
            self.addToBuf(self.a[c], data[c])
        
# plot class
class AnalogPlot:
    # constr
    def __init__(self, analogData):
        # set plot to animated
        plt.ion() 
        self.aline = [plt.plot(aa)[0] for aa in analogData.a]
        plt.ylim([-2**23, 2**23])

    # update plot
    def update(self, analogData):
        for c in range(analogData.channels):
            self.aline[c].set_ydata(analogData.a[c])
        plt.draw()

# eeg-mouse specific data interpreter
def decodeline(line):
    signed= lambda u : u - (0 if u < 2**23 else 2**24) 
#   data= [signed(int(line[k:k+6],16)) for k in range(10, len(line)-5, 6)]
    data= signed(int(line[4:4+6],16))
    return data
    

# main() function
baudrate= 115200
def main():
    # expects 1 arg - serial port string
    if(len(sys.argv) != 2):
        print 'Example usage: python showdata.py "/dev/ttyACM0"'
        exit(1)

    #strPort = '/dev/tty.usbserial-A7006Yqh'
    strPort = sys.argv[1];

    # plot parameters
    analogData = AnalogData(100, 8)
    #  analogPlot = AnalogPlot(analogData)

    print 'plotting data...'

    # open serial port
    ser = serial.Serial(strPort, baudrate)
    tstart = time.clock()
    t = tstart
    while t-tstart < 10.:
        t = time.clock()
        try:
            line = ser.readline()
            # data = [float(val) for val in line.split()]
            data = decodeline(line)
            #print data
            # if(len(data) == 8):
                # analogData.add(data)
                # analogPlot.update(analogData)
            print data
        except KeyboardInterrupt:
            print 'exiting'
            break
    # close serial
    ser.flush()
    ser.close()

# call main
if __name__ == '__main__':
    main()
