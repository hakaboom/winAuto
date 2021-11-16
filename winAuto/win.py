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
from baseImage import Rect, Point, Size
from .constant import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
from .exceptions import WinBaseError, WinConnectError

from typing import Dict, Union, Tuple, List


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
            # 由于windows窗口存在一些边界
            # 截图是会带上带有窗口名称的顶部栏
            # 因此写死了x,y坐标解决
            # 这个方案不是很稳定,需要假设每个窗口都有一个顶部栏
            rect = win32gui.GetClientRect(self._hwnd)
            self._screenshot_size.width = rect[2]
            self._screenshot_size.height = rect[3]
            if window_topBar:
                self._window_border[0] = 31
                self._window_border[1] = 8
        self.keyboard = keyboard
        self.mouse = mouse
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
            self._top_window = self.app.window(handle=self._hwnd)
        except pywintypes.error as err:
            raise WinConnectError(f"连接句柄:'{self._hwnd}'超时, error={err}")

        self.set_foreground(self._hwnd)

    def click(self, point: Union[Tuple[int, int], List, Point], duration: Union[float, int, None] = 0.01,
              button: str = 'left'):
        """
        点击连接窗口的指定位置 ps:相对坐标,以连接的句柄窗口左上角为原点

        Args:
            point: 需要点击的坐标
            duration: 延迟
            button: 左右键 left/right

        Returns:
            None
        """

        end_x, end_y = None, None
        if isinstance(point, Point):
            end_x, end_y = point.x, point.y
        elif isinstance(point, (tuple, list)):
            end_x, end_y = point[0], point[1]

        window_start_point = self.rect.tl  # 以连接的窗口左上角为原点,转为相对坐标
        end_x += window_start_point.x
        end_y += window_start_point.y

        self.mouse.press(button=button, coords=(end_x, end_y))
        time.sleep(duration)
        self.mouse.release(button=button, coords=(end_x, end_y))

    def screenshot(self) -> np.ndarray:
        """
        截取图片

        Returns:
            图片的numpy类型数据
        """
        widget = self._screenshot_size.width
        height = self._screenshot_size.height
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
        compatibleDC.BitBlt((0, 0), (widget, height), dcObject, (self._window_border[1], self._window_border[0]),
                            win32con.SRCCOPY)

        img = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
        img.shape = (height, widget, 4)

        win32gui.DeleteObject(bitmap.GetHandle())
        dcObject.DeleteDC()
        compatibleDC.DeleteDC()

        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    @staticmethod
    def set_foreground(handle) -> None:
        """
        将指定句柄的窗口带到前台并激活该窗口

        Returns:
            None
        """
        win32gui.SetForegroundWindow(handle)

    @property
    def rect(self) -> Rect:
        """
        获取窗口当前所在屏幕的位置

        Returns:
            窗口的位置(以全屏左上角开始为原点的坐标)
        """
        rect = self._top_window.rectangle()
        return Rect(x=rect.left + self._window_border[1],
                    y=rect.top + self._window_border[0],
                    width=self._screenshot_size.width,
                    height=self._screenshot_size.height)

    @property
    def title(self) -> str:
        """
        获取窗口名

        Returns:
            窗口名
        """
        return self._top_window.texts()

    def kill(self) -> None:
        """
        关闭窗口

        Returns:
            None
        """
        self.app.kill()

    @staticmethod
    def find_window(hwnd_class: str = None, hwnd_title: str = None) -> int:
        """
        根据窗口名或窗口类名获取对应窗口句柄

        Args:
            hwnd_class: 窗口类名
            hwnd_title: 窗口名

        Returns:
            窗口句柄
        """
        return win32gui.FindWindow(hwnd_class, hwnd_title)

    @staticmethod
    def get_all_hwnd() -> Dict[int, str]:
        """
        获取所有句柄

        Returns:

        """
        hwnd_title = {}

        def _fun(hwnd, *args):
            if (win32gui.IsWindow(hwnd) and
                    win32gui.IsWindowEnabled(hwnd) and
                    win32gui.IsWindowVisible(hwnd)):
                hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

        win32gui.EnumWindows(_fun, 0)

        return hwnd_title
