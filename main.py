# -*- coding: utf-8 -*-
import cv2.cv2
import win32gui
import win32api
import time
import ctypes
from winAuto.win import Win
from baseImage import IMAGE
from image_registration.api import Findit


a = Win(handle=264086, window_topBar=False)

match = Findit()
print(match.find_best_result(im_source='test2.png', im_search='test2.png'))