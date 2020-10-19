#!/bin/env python3

# Draw a window
# Have the ctor take the processor as argument
# When the processor has a new frame ready, draw it on the window

# https://stackoverflow.com/a/3165474
import wx
import cv2
import cv2 as cv
import cv2 as gui

class CvProcessor(object):
    def __init__(self, source_path):
        pass


class CvMovieFrame(wx.Frame):
    TIMER_PLAY_ID = 101
    def __init__(self, parent):        

        wx.Frame.__init__(self, parent, -1,)        

        sizer = wx.BoxSizer(wx.VERTICAL)         

        self.capture = cv2.VideoCapture(0) 

        cap = self.capture
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.SetSize((width + 300, height + 100))

        self.paint_stuff()
        self.displayPanel= wx.StaticBitmap(self, -1, bitmap=self.bmp)
        sizer.Add(self.displayPanel, 0, wx.ALL, 10)

        self.shotbutton = wx.Button(self,-1, "Shot")
        sizer.Add(self.shotbutton,-1, wx.GROW)

        self.retrybutton = wx.Button(self,-1, "Retry")
        sizer.Add(self.retrybutton,-1, wx.GROW)     
        self.retrybutton.Hide()   

        #events
        self.Bind(wx.EVT_BUTTON, self.onShot, self.shotbutton)
        self.Bind(wx.EVT_BUTTON, self.onRetry, self.retrybutton)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.playTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onNextFrame)

        self.fps = 8;
        self.SetSizer(sizer)
        sizer.Layout()
        self.startTimer()        

    def paint_stuff(self):
        _, frame = self.capture.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        cap = self.capture
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.bmp = wx.BitmapFromBuffer(width, height, frame)

    def startTimer(self):
        if self.fps!=0: self.playTimer.Start(1000/self.fps)#every X ms
        else: self.playTimer.Start(1000/15)#assuming 15 fps        

    def onRetry(self, event):
        self.paint_stuff()
        self.startTimer()
        self.shotbutton.Show()
        self.retrybutton.Hide()
        self.hasPicture = False
        self.Layout()
        event.Skip()    

    def onShot(self, event):
        _, frame = self.capture.read()
        self.playTimer.Stop()
        gui.imwrite("foo.png", frame)        

        self.hasPicture = True
        self.shotbutton.Hide()
        self.retrybutton.Show()
        self.Layout()
        event.Skip()

    def onClose(self, event):
        try:
            self.playTimer.Stop()
        except:
            pass

        self.Show(False)
        self.Destroy()      

    def onPaint(self, evt):
        if self.bmp:
            self.displayPanel.SetBitmap(self.bmp)
        evt.Skip()

    def onNextFrame(self, evt):
        self.paint_stuff()
        self.Refresh()        
        evt.Skip()
