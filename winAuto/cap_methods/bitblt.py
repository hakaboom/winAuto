# -*- coding: utf-8 -*-
import win32gui
import win32api
import win32ui

import numpy as np
import cv2


class BitBlt(object):
    def __init__(self, hwnd: int):
        self._hwnd = hwnd

    def screenshot(self):
        windowDC: int = win32gui.GetWindowDC(self._hwnd)

        dcObject = win32ui.CreateDCFromHandle(windowDC)
        compatibleDC = dcObject.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()

        bitmap.CreateCompatibleBitmap(dcObject, widget, height)
        compatibleDC.SelectObject(bitmap)

        compatibleDC.BitBlt((0, 0), (widget, height), dcObject, (self._window_border[1], self._window_border[0]),
                            win32con.SRCCOPY)

        img = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
        img.shape = (height, widget, 4)

        win32gui.DeleteObject(bitmap.GetHandle())
        dcObject.DeleteDC()
        compatibleDC.DeleteDC()

        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)