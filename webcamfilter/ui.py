#!/bin/env python3

# processsor can be in "background learning mode" or "prod mode"
# If in background learning mode, each frame is treated as background and is used to feed the background detection matrix
# If in prod mode, negate the bakground frame from each frame and return the result

# https://stackoverflow.com/a/3165474
import wx
import cv2
import cv2 as cv
import cv2 as gui
import numpy as np

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
        cap = cv2.VideoCapture(0)
        self.capture = cap

        self.set_mode(CvProcessorMode.PROD)

        self.avg_background_frame = None

    def set_mode(self, mode: CvProcessorMode) -> None:
        self.mode = mode
        if mode == CvProcessorMode.BACKGROUND_LEARNING:
            self.avg_background_frame = None


    def to_bitmap(self, frame):
        cap = self.capture
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return wx.BitmapFromBuffer(width, height, frame)

    def read_learning(self) -> CvProcessorResult:
        # avg this with the rest of the background frames
        # return the following:
        # raw image: raw image
        # background: avg'd background frame
        # processed: raw image
        _, frame = self.capture.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        if self.avg_background_frame is None:
            self.avg_background_frame = frame.astype(np.float64)
        else:
            cv.accumulateWeighted(frame, self.avg_background_frame,0.1)

        background = self.avg_background_frame.astype(np.uint8)

        return CvProcessorResult(
            raw_image=self.to_bitmap(frame),
            background = self.to_bitmap(background),
            processed=self.to_bitmap(frame),
        )

    def process_image(self, frame, background):
        import scipy.special

        """
        mask = frame - background
        gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        gray_single = gray[0]
        gray_single[gray_single < 50] = 0
        gray_single[gray_single > 0] = 255
        gray_single = gray_single.astype(np.uint8)
        print(gray_single)
        processed = cv2.bitwise_and(frame, frame, mask=gray_single)
        processed = mask
        """
        return scipy.special.expit(frame-background)
        return processed

    def read_prod(self) -> CvProcessorResult:
        _, frame = self.capture.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        background = self.avg_background_frame

        # TODO a lot to be desired
        if self.avg_background_frame is None:
            processed = frame
            background = (frame - frame)
        else:
            background = self.avg_background_frame.astype(np.uint8)
            processed = self.process_image(frame, background)

        return CvProcessorResult(
            raw_image=self.to_bitmap(frame),
            background=self.to_bitmap(background),
            processed=self.to_bitmap(processed),
        )

    def read(self):
        if self.mode == CvProcessorMode.BACKGROUND_LEARNING:
            return self.read_learning()
        else:
            return self.read_prod()



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
