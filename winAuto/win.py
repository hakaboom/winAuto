# -*- coding: utf-8 -*-
import numpy
import win32gui
import win32api
import win32ui
import win32con
import numpy as np
import ctypes

from .constant import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
# TODO: 通过文件名,进程名获取hwnd
# TODO: 窗口操作(点击,大小缩放后的坐标)


class Win(object):
    def __init__(self, hwnd: int = None):
        """

        Args:
            hwnd: 窗口句柄
        """
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()

    def screenshot(self, hwnd: int = None) -> np.ndarray:
        """
        Take the screenshot of Windows app
        Args:
            hwnd: 窗口句柄
        Returns:
            bitmap screenshot file
        """
        if hwnd is None:
            """all screens"""
            hwnd = win32gui.GetDesktopWindow()
            # get complete virtual screen including all monitors
            w = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            h = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN)
            x = win32api.GetSystemMetrics(SM_XVIRTUALSCREEN)
            y = win32api.GetSystemMetrics(SM_YVIRTUALSCREEN)

        else:
            """window"""
            rect = win32gui.GetWindowRect(hwnd)
            w = abs(rect[2] - rect[0])
            h = abs(rect[3] - rect[1])
            x, y = 0, 0

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (x, y), win32con.SRCCOPY)

        bmpstr = saveBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (h, w, 4)
        mfcDC.DeleteDC()
        saveDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())

        return img
