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

from winAuto.utils.window import GetWindowInfo
from winAuto.cap_methods import BitBlt, WindowGraphicsCapture

from pywinauto.application import Application
from pywinauto import mouse, keyboard, win32structures
from pywinauto.win32functions import SetFocus
from baseImage import Rect, Point, Size, Image
from .constant import SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN, SCREENSHOT_MODE
from .exceptions import WinBaseError, WinConnectError

from typing import Dict, Union, Tuple, List


class Win(object):
    def __init__(self, handle: int = None, handle_title: str = None, handle_class: str = None,
                 window_border: Union[Tuple, List, None] = None, cap_method=SCREENSHOT_MODE.WindowsGraphicsCapture):
        """

        Args:
            handle: 窗口句柄
            handle_title: 窗口名
            handle_class: 窗口类名
            window_border: 是否存在带有窗口名称的顶部栏
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
        self._screenshot_size = Size(0, 0)
        self._window_size = Size(win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN),  # 全屏幕尺寸大小
                                 win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        if self._hwnd is None:
            self._hwnd = win32gui.GetDesktopWindow()
            self._screenshot_size = self._window_size
        else:
            rect = win32gui.GetClientRect(self._hwnd)
            self._screenshot_size.width = rect[2]
            self._screenshot_size.height = rect[3]

        self._window_border = window_border or self.get_window_border()  # 上,下,左,右
        self.cap_fun = None
        self.cap_method = cap_method
        if self.cap_method == SCREENSHOT_MODE.BitBlt:
            self.cap_fun = BitBlt(hwnd=self._hwnd, border=self._window_border,
                                  screenshot_size=self._screenshot_size)
        elif self.cap_method == SCREENSHOT_MODE.WindowsGraphicsCapture:
            self.cap_fun = WindowGraphicsCapture(hwnd=self._hwnd)
        else:
            raise ValueError('未填写cap_method参数')

        self.keyboard = keyboard
        self.mouse = mouse
        print(f'设备分辨率:{self._window_size}, 窗口所用句柄: {self._hwnd}')
        # self.connect()

    def start_app(self, path, **kwargs):
        """
        根据路径启动应用

        Args:
            path: 应用路径

        Returns:
            None
        """
        self.app = self._app.start(path, **kwargs)

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

        # self.set_foreground(self._hwnd)

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

        if isinstance(point, (tuple, list)):
            point = Point(x=point[0], y=point[1])

        point = self._windowpos_to_screenpos(point)

        self.mouse.press(button=button, coords=(point.x, point.y))
        time.sleep(duration)
        self.mouse.release(button=button, coords=(point.x, point.y))

    def swipe(self, point1: Union[Tuple[int, int], List, Point], point2: Union[Tuple[int, int], List, Point],
              duration: Union[float, int, None] = 0.01, steps=5):
        """
        滑动一段距离

        Args:
            point1: 起始点
            point2: 终点
            duration: 滑动结束后延迟多久抬起
            steps: 步长

        Returns:

        """
        if isinstance(point1, (tuple, list)):
            point1 = Point(x=point1[0], y=point1[1])

        if isinstance(point2, (tuple, list)):
            point2 = Point(x=point2[0], y=point2[1])

        start = self._windowpos_to_screenpos(point1)
        end = self._windowpos_to_screenpos(point2)

        interval = float(duration) / (steps + 1)
        self.mouse.press(coords=(start.x, start.y))
        time.sleep(interval)
        for i in range(1, steps):
            x = int(start.x + (end.x - start.x) * i / steps)
            y = int(start.y + (end.y - start.y) * i / steps)
            self.mouse.move(coords=(x, y))
            time.sleep(interval)
        self.mouse.move(coords=(end.x, end.y))
        self.mouse.release(coords=(end.x, end.y))

        # # -----------
        # if isinstance(point1, (tuple, list)):
        #     point1 = Point(x=point1[0], y=point1[1])
        #
        # if isinstance(point1, (tuple, list)):
        #     point2 = Point(x=point2[0], y=point2[1])
        #
        # start = self._windowpos_to_screenpos(point1)
        # end = self._windowpos_to_screenpos(point2)
        # interval = float(duration) / (steps + 1)
        # self.mouse.press(coords=(start.x, start.x))
        # time.sleep(interval)
        # for i in range(1, steps):
        #     x = int(start.x + (end.x - start.x) * i / steps)
        #     y = int(start.y + (end.y - start.y) * i / steps)
        #     self.mouse.move(coords=(x, y))
        #     time.sleep(interval)
        # self.mouse.move(coords=(end.x, end.y))
        # self.mouse.release(coords=(end.x, end.y))

    def keyevent(self, keycode: str):
        """
        Perform a key event

        References:
            https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html

        Args:
            keycode: key code number or name

        Returns:
            None

        """
        self.keyboard.send_keys(keycode)

    def text(self, text: str):
        """
        输入文字

        Args:
            text: 待输入的文字

        Returns:
            None
        """
        self.keyevent(text)

    def screenshot(self):
        img = Image(self.cap_fun.screenshot())
        if self.cap_method == SCREENSHOT_MODE.WindowsGraphicsCapture:
            # 上,下,左,右 self._window_border
            rect = Rect(x=self._window_border[2],
                        y=self._window_border[0],
                        width=self._screenshot_size.width,
                        height=self._screenshot_size.height)
            return img.crop(rect)
        return img

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
        获取窗口客户端区域当前所在屏幕的位置

        Returns:
            窗口的位置(以全屏左上角开始为原点的坐标)
        """
        clientRect = win32gui.GetClientRect(self._hwnd)
        point = win32gui.ScreenToClient(self._hwnd, (0, 0))
        rect = Rect(x=abs(point[0]), y=abs(point[1]), width=clientRect[2], height=clientRect[3])
        return rect

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

    def _windowpos_to_screenpos(self, pos: Point):
        """
        转换相对坐标为屏幕的绝对坐标

        Args:
            pos: 需要转换的坐标

        Returns:
            Point
        """
        windowpos = self.rect.tl
        pos = pos + windowpos
        return pos

    def get_window_border(self):
        info = GetWindowInfo(self._hwnd)
        # print(f'rcWindow: {info.rcWindow.left} {info.rcWindow.top} {info.rcWindow.right} {info.rcWindow.bottom}')
        # print(f'rcClient: {info.rcClient.left} {info.rcClient.top} {info.rcClient.right} {info.rcClient.bottom}')
        # 上,下,左,右
        border = (abs(info.rcWindow.top - info.rcClient.top) + 1, 1, 1, 1)
        return border

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
