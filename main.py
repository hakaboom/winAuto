# -*- coding: utf-8 -*-
import cv2
import win32gui
import win32api
import time
import ctypes
from winAuto.win import Win
from baseImage import IMAGE, Rect
from image_registration.findit import Findit


a = Win(handle=461326, window_topBar=False)
a.text('%{F5}')