#!/bin/env python3

# processsor can be in "background learning mode" or "prod mode"
# If in background learning mode, each frame is treated as background and is used to feed the background detection matrix
# If in prod mode, negate the bakground frame from each frame and return the result

# https://stackoverflow.com/a/3165474
import wx
import cv2
import cv2 as cv
import cv2 as gui

from typing import NamedTuple
from enum import Enum

class CvProcessorMode(Enum):
    BACKGROUND_LEARNING = 1
    PROD = 2

class CvProcessorResult(NamedTuple):
    raw_image: wx.BitmapFromBuffer
    background: wx.BitmapFromBuffer
    processed: wx.BitmapFromBuffer

class CvProcessor(object):
    def __init__(self):
        cap = cv2.VideoCapture(2)
        self.capture = cap

        # https://automaticaddison.com/real-time-object-tracking-using-opencv-and-a-webcam/
        back_sub = cv2.createBackgroundSubtractorMOG2(history=7000,
            varThreshold=25, detectShadows=True)
        self.back_sub = back_sub

        self.set_mode(CvProcessorMode.PROD)

    def set_mode(self, mode: CvProcessorMode) -> None:
        self.mode = mode

    def read(self) -> CvProcessorResult:
        _, frame = self.capture.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        fg_mask = self.back_sub.apply(frame)
        processed_frame = cv2.bitwise_and(frame, frame, mask=fg_mask)
        cap = self.capture
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        img_raw = wx.BitmapFromBuffer(width, height, frame)
        white = cv2.bitwise_not(frame - frame)
        frame_background = cv2.bitwise_and(white, white, mask = 255-fg_mask)
        img_background = wx.BitmapFromBuffer(width, height, frame_background)
        img_processed = wx.BitmapFromBuffer(width, height, processed_frame)
        return CvProcessorResult(
            raw_image=img_raw,
            background=img_background,
            processed=img_processed,
        )



class CvMovieFrame(wx.Frame):
    def __init__(self, parent):        
        wx.Frame.__init__(self, parent, -1,)

        self.processor = CvProcessor()

        self.mode = None
        self.flipMode()

        self.setup_components()
        self.paint_stuff()

        self.fps = 8;
        self.startTimer()        

    def setup_components(self):
        sizer = wx.BoxSizer(wx.VERTICAL)         

        ### Bitmaps
        # bitmap is required for sizes
        self.displayPanel= wx.StaticBitmap(self, -1,)
        self.bmp_background = wx.StaticBitmap(self, -1,)
        self.bmp_processed = wx.StaticBitmap(self, -1,)

        bmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(bmp_sizer)
        bmp_sizer.Add(self.displayPanel, 0, wx.ALL, 10)
        bmp_sizer.Add(self.bmp_background, 0, wx.ALL, 10)
        bmp_sizer.Add(self.bmp_processed, 0, wx.ALL, 10)
        sizer.Add(bmp_sizer)

        # My buttons
        self.btn_background = wx.Button(self,-1, "Background Learning")
        sizer.Add(self.btn_background,-1, wx.GROW)
        self.Bind(wx.EVT_BUTTON, self.onModeChange, self.btn_background)
        self.btn_prod = wx.Button(self,-1, "Prod")
        sizer.Add(self.btn_prod,-1, wx.GROW)     
        self.btn_prod.Hide()   
        self.Bind(wx.EVT_BUTTON, self.onModeChange, self.btn_prod)

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.playTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onNextFrame)

        self.SetSizer(sizer)
        sizer.Layout()

    def paint_stuff(self):
        read_result = self.processor.read()
        self.displayPanel.SetBitmap(read_result.raw_image)
        self.bmp_background.SetBitmap(read_result.background)
        self.bmp_processed.SetBitmap(read_result.processed)

    def startTimer(self):
        if self.fps!=0: self.playTimer.Start(1000/self.fps)#every X ms
        else: self.playTimer.Start(1000/15)#assuming 15 fps        

    def onClose(self, event):
        try:
            self.playTimer.Stop()
        except:
            pass

        self.Show(False)
        self.Destroy()      

    def onNextFrame(self, evt):
        self.paint_stuff()
        self.Refresh()        
        evt.Skip()

    def flipMode(self):
        if self.mode == CvProcessorMode.PROD:
            self.mode = CvProcessorMode.BACKGROUND_LEARNING
        else:
            self.mode = CvProcessorMode.PROD
        self.processor.set_mode(self.mode)

    def onModeChange(self, event):
        self.flipMode()
        if self.mode == CvProcessorMode.PROD:
            self.btn_prod.Hide()
            self.btn_background.Show()
        else:
            self.btn_prod.Show()
            self.btn_background.Hide()
        self.Layout()
        event.Skip()
