# -*- coding: utf-8 -*-
from winAuto.utils.d3dcapture import CaptureSession


session = CaptureSession()
title = f"screenshot for window {hwnd}"
cv2.namedWindow(title)
state_box = [None, False, False]  # frame, changed, stop


def frame_callback(_session):
    frame = _session.get_frame()
    if frame is None:
        return
    state_box[0] = frame
    state_box[1] = True


def close_callback(_session):
    state_box[2] = True


session.frame_callback = frame_callback
session.close_callback = close_callback
session.start(hwnd, True)

while not state_box[2]:
    if state_box[1]:
        state_box[1] = False
        IMAGE(state_box[0]).imshow(title)
    key = cv2.waitKey(16)
    try:
        if key == 27 or cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) != 1:
            break
    except:
        break


session.stop()