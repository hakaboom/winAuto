# -*- coding: utf-8 -*-
import cv2.cv2
import win32gui
import win32api
import time
import ctypes
from winAuto.win import Win
from baseImage import IMAGE
from pywinauto import mouse, keyboard
from pywinauto.win32functions import GetSystemMetrics
from pywinauto.application import Application

a = Win(handle=264086, window_topBar=False)
IMAGE(a.screenshot()).save2path('test.png')
print(a.rect)
