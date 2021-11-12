# -*- coding: utf-8 -*-
import ctypes

import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui
from airtest.aircv.utils import Image, pil_2_cv2

from .constant import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN

from typing import Dict

# TODO: 窗口操作(点击,大小缩放后的坐标)


class Win(object):
    def __init__(self, hwnd: int = None, hwnd_title: str = None, hwnd_class: str = None):
        """

        Args:
            hwnd: 窗口句柄
        """
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()

        if hwnd:
            self._hwnd = int(hwnd)
        elif hwnd_class and hwnd_title:
            self._hwnd = self.find_window(hwnd_class=hwnd_class, hwnd_title=hwnd_title)
        elif hwnd_title:
            self._hwnd = self.find_window(hwnd_title=hwnd_title)
        elif hwnd_class:
            self._hwnd = self.find_window(hwnd_class=hwnd_class)
        else:
            self._hwnd = None

        self._hwnd = None if self._hwnd == 0 else self._hwnd
        self.rect = ctypes.wintypes.RECT()

        if self._hwnd is None:
            self._hwnd = win32gui.GetDesktopWindow()
            self.rect.left = 0
            self.rect.top = 0
            self.rect.right = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            self.rect.bottom = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN)
        else:
            # 由于windows窗口存在一些边界
            # 截图是会带上带有窗口名称的顶部栏
            # 因此写死了x,y坐标解决
            # 这个方案不是很稳定,需要假设每个窗口都有一个顶部栏
            rect = win32gui.GetClientRect(self._hwnd)
            self.rect.left = 8
            self.rect.top = 31
            self.rect.right = 8 + rect[2]
            self.rect.bottom = 31 + rect[3]

    def screenshot(self) -> np.ndarray:
        widget = self.rect.right - self.rect.left
        height = self.rect.bottom - self.rect.top
        # 根据窗口句柄获取设备的上下文device context
        windowDC: int = win32gui.GetWindowDC(self._hwnd)

        # 根据上下文device context获取mfDC
        dcObject = win32ui.CreateDCFromHandle(windowDC)

        # mfcDC创建可兼容的DC
        compatibleDC = dcObject.CreateCompatibleDC()

        # 创建bitmap准备保存图片
        bitmap = win32ui.CreateBitmap()

        # 为bitmap开辟空间
        bitmap.CreateCompatibleBitmap(dcObject, widget, height)
        compatibleDC.SelectObject(bitmap)

        # 将截图保存到saveBitMap中
        compatibleDC.BitBlt((0, 0), (widget, height), dcObject, (self.rect.left, self.rect.top), win32con.SRCCOPY)

        img = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
        img.shape = (height, widget, 4)

        win32gui.DeleteObject(bitmap.GetHandle())
        dcObject.DeleteDC()
        compatibleDC.DeleteDC()

        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    @staticmethod
    def find_window(hwnd_class: str = None, hwnd_title: str = None):
        return win32gui.FindWindow(hwnd_class, hwnd_title)

    @staticmethod
    def get_all_hwnd() -> Dict[int, str]:
        hwnd_title = {}

        def _fun(hwnd, mouse):
            if (win32gui.IsWindow(hwnd) and
                    win32gui.IsWindowEnabled(hwnd) and
                    win32gui.IsWindowVisible(hwnd)):
                hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

        win32gui.EnumWindows(_fun, 0)

        return hwnd_title
