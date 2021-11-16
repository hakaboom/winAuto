# -*- coding: utf-8 -*-
import pywintypes


class WinBaseError(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return repr(self.message)


class WinConnectTimeout(WinBaseError):
    """ connect hwnd time out """


# -*- coding: utf-8 -*-
import ctypes
import time

import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui
import pywintypes

from pywinauto.application import Application
from pywinauto import mouse, keyboard, win32structures
from pywinauto.win32functions import SetFocus
from baseImage.coordinate import Rect, Point, Size
from .constant import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
from .exceptions import WinBaseError, WinConnectTimeout

from typing import Dict, Union, Tuple, List

# TODO: 窗口操作(点击,大小缩放后的坐标)


class __Win(object):
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

        self.app = None
        self._app = Application()
        self._top_window = None
        self._window_border = [0, 0, 0, 0]  # 上,下,左,右
        self._screenshot_size = Size(0, 0)
        self._window_size = Size(win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN),  # 全屏幕尺寸大小
                                 win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        if self._hwnd is None:
            self._hwnd = win32gui.GetDesktopWindow()
            self._screenshot_size = self._window_size
        else:
            rect = win32gui.GetClientRect(self._hwnd)
            if window_topBar:
                self._window_border = [31, 0, 8, 8]
            self._screenshot_size.width = rect[2] + 8
            self._screenshot_size.height = rect[3]
        self.keyboard = keyboard
        self.mouse = mouse
        print(self._screenshot_size)
        print(f'设备分辨率:{self._window_size}, 窗口所用句柄: {self._hwnd}')
        self.connect()

    def connect(self, timeout: int = 5):
        """

        Args:
            timeout: 设定超时时长

        Returns:
            None
        """
        # TODO: 检测对应句柄是否在前台
        try:
            self.app = self._app.connect(handle=self._hwnd, timeout=timeout)
        except pywintypes.error as err:
            raise WinConnectTimeout(f"连接句柄:'{self._hwnd}'超时, error={err}")

        self._top_window = self.app.window(handle=self._hwnd)
        self.set_foreground(self._hwnd)

    def click(self, point: Union[Tuple[int, int], List, Point], duration: Union[float, int, None] = 0.01,
              button: str = 'left'):
        """
        点击屏幕(以连接窗口为准的相对坐标, self.screen_rects)

        Args:
            point: 需要点击的坐标(相对于已连接屏幕的坐标)
            duration: 延迟
            button: 左右键 left/right

        Returns:

        """
        end_x, end_y = None, None
        if isinstance(point, Point):
            end_x, end_y = point.x, point.y
        elif isinstance(point, (tuple, list)):
            end_x, end_y = point[0], point[1]

        self.mouse.press(button=button, coords=(end_x, end_y))
        time.sleep(duration)
        self.mouse.release(button=button, coords=(end_x, end_y))

    def screenshot(self) -> np.ndarray:
        """
        截取图片

        Returns:
            图片的numpy类型数据
        """
        # 根据窗口句柄获取设备的上下文device context
        windowDC: int = win32gui.GetWindowDC(self._hwnd)

        # 根据上下文device context获取mfDC
        dcObject = win32ui.CreateDCFromHandle(windowDC)

        # mfcDC创建可兼容的DC
        compatibleDC = dcObject.CreateCompatibleDC()

        # 创建bitmap准备保存图片
        bitmap = win32ui.CreateBitmap()

        # 为bitmap开辟空间
        bitmap.CreateCompatibleBitmap(dcObject, self._screenshot_size.width, self._screenshot_size.height)
        compatibleDC.SelectObject(bitmap)

        # 将截图保存到saveBitMap中
        compatibleDC.BitBlt((0, 0), (self._screenshot_size.width, self._screenshot_size.height), dcObject,
                            (self._window_border[1], self._window_border[0]), win32con.SRCCOPY)

        img = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
        img.shape = (self._screenshot_size.height, self._screenshot_size.width, 4)

        win32gui.DeleteObject(bitmap.GetHandle())
        dcObject.DeleteDC()
        compatibleDC.DeleteDC()

        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
