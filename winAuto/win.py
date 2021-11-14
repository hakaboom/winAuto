# -*- coding: utf-8 -*-
import ctypes

import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui

from pywinauto.application import Application
from pywinauto import mouse, keyboard
from pywinauto.win32functions import SetFocus
from .constant import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN

from typing import Dict

# TODO: 窗口操作(点击,大小缩放后的坐标)


class Win(object):
    def __init__(self, handle: int = None, handle_title: str = None, handle_class: str = None,
                 window_topBar: bool = True):
        """

        Args:
            handle: 窗口句柄
            handle_title: 窗口名
            handle_class: 窗口类名
            window_topBar: 是否存在带有窗口名称的顶部栏
        """

        # user32 = ctypes.windll.user32
        # user32.SetProcessDPIAware()

        if handle:
            self._hwnd = int(handle)
        elif handle_class and handle_title:
            self._hwnd = self.find_window(hwnd_class=handle_class, hwnd_title=handle_title)
        elif handle_title:
            self._hwnd = self.find_window(hwnd_title=handle_title)
        elif handle_class:
            self._hwnd = self.find_window(hwnd_class=handle_class)
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
            if window_topBar:
                self.rect.left = 8
                self.rect.top = 31
            else:
                self.rect.left = 0
                self.rect.top = 0
            self.rect.right = self.rect.left + rect[2]
            self.rect.bottom = self.rect.top + rect[3]

        self.app = None
        self._app = Application()
        self._top_window = None
        self.keyboard = keyboard
        self.mouse = mouse
        self.connect()
        print(f'窗口所用句柄: {self._hwnd}')

    def connect(self, timeout: int = 5):
        """

        Args:
            timeout: 设定超时时长

        Returns:
            None
        """
        # TODO: 检测对应句柄是否在前台
        self.app = self._app.connect(handle=self._hwnd)
        self._top_window = self.app.window(handle=self._hwnd).wrapper_object()
        win32gui.SetForegroundWindow(self._hwnd)

    def screenshot(self) -> np.ndarray:
        """
        截取图片

        Returns:
            图片的numpy类型数据
        """
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

    # def rect(self):
    #     """
    #
    #     Returns:
    #
    #     """
    #     return self._top_window.rectangle()

    @property
    def title(self):
        return self._top_window.texts()

    @staticmethod
    def find_window(hwnd_class: str = None, hwnd_title: str = None) -> int:
        """
        根据窗口名或窗口类名获取对应窗口句柄

        Args:
            hwnd_class:
            hwnd_title:

        Returns:

        """
        return win32gui.FindWindow(hwnd_class, hwnd_title)

    @staticmethod
    def get_all_hwnd() -> Dict[int, str]:
        """
        获取所有句柄

        Returns:

        """
        hwnd_title = {}

        def _fun(hwnd, mouse):
            if (win32gui.IsWindow(hwnd) and
                    win32gui.IsWindowEnabled(hwnd) and
                    win32gui.IsWindowVisible(hwnd)):
                hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

        win32gui.EnumWindows(_fun, 0)

        return hwnd_title
