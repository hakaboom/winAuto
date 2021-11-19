# -*- coding: utf-8 -*-
import cv2
import win32gui
import win32api
import time
import ctypes
from winAuto.win import Win
from baseImage import IMAGE, Rect, Point
from image_registration.findit import Findit


a = Win(handle_title='retire', window_topBar=True)

a.swipe(point1=Point(1103, 270), point2=Point(860, 270))
