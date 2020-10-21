#!/bin/env python3

# Create three boxes:
# 1. Input from camera
# 2. Background representation (can be null)
# 3. Revised output (camera - background)

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

        self.setup_capture()
        self.paint_stuff()
        self.setup_components()

        self.fps = 8;
        self.startTimer()        

    def setup_capture(self):
        self.capture = cv2.VideoCapture(2) 

        # https://automaticaddison.com/real-time-object-tracking-using-opencv-and-a-webcam/
        back_sub = cv2.createBackgroundSubtractorMOG2(history=7000,
            varThreshold=25, detectShadows=True)
        self.back_sub = back_sub

    def setup_components(self):
        cap = self.capture
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.SetSize((width + 300, height + 100))
        sizer = wx.BoxSizer(wx.VERTICAL)         

        ### Bitmaps
        # bitmap is required for sizes
        self.displayPanel= wx.StaticBitmap(self, -1, bitmap=self.bmp)
        bmp_background = wx.StaticBitmap(self, -1, bitmap=self.bmp)
        bmp_processed = wx.StaticBitmap(self, -1, bitmap=self.bmp)

        bmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(bmp_sizer)
        bmp_sizer.Add(self.displayPanel, 0, wx.ALL, 10)
        bmp_sizer.Add(bmp_background, 0, wx.ALL, 10)
        bmp_sizer.Add(bmp_processed, 0, wx.ALL, 10)
        sizer.Add(bmp_sizer)

        # Buttons
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

        self.SetSizer(sizer)
        sizer.Layout()

    def paint_stuff(self):
        _, frame = self.capture.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        fg_mask = self.back_sub.apply(frame)
        # bg = self.back_sub.getBackgroundImage(frame)
        frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
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
