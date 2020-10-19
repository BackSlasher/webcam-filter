from ui import CvMovieFrame
import wx

if __name__=="__main__":
    app = wx.App()
    f = CvMovieFrame(None)
    f.Centre()
    f.Show(True)
    app.MainLoop()

